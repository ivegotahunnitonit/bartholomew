"""
Cookbook Recipe: Docker & Container Sandboxing (Defense-in-Depth)
================================================================
Enforces in-process AST gating inside isolated Docker / container runtimes,
pairing Layer-7 semantic interception with OS-level namespace sandboxing.

Run:
    python cookbook/container_defense/docker_agent_guard.py
"""

import sys
import os

# Add repository root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from btp_guard import Guard
from src.container_sandbox import ContainerSandboxEngine


class DockerAgentSandbox(ContainerSandboxEngine):
    """Convenience subclass matching the enterprise cookbook API."""
    def __init__(self, image: str = "alpine:latest", read_only_root: bool = True):
        super().__init__(base_image=image, network_enabled=False)
        self.read_only_root = read_only_root

    def run(self, command: str, workspace_dir: str = "./scratch"):
        code, stdout, stderr, mode = self.run_isolated_command(command, workspace_dir=workspace_dir)
        return {"exit_code": code, "stdout": stdout, "stderr": stderr, "mode": mode}


def main():
    print("=" * 75)
    print("  BTP Global Cookbook: Docker & Container Defense-in-Depth")
    print("=" * 75)

    guard = Guard(strict=True)
    sandbox = DockerAgentSandbox(image="python:3.11-slim", read_only_root=True)

    test_commands = [
        ("Legitimate Read", "cat /app/config.json"),
        ("Catastrophic Mutation", "rm -rf /app/data"),
        ("Destructive SQL Drop", "DROP TABLE users CASCADE;"),
    ]

    for label, tool_call in test_commands:
        print(f"\n[Evaluating Action] {label}: '{tool_call}'")

        # 1. Evaluate tool call AST in-process before touching container/OS
        res = guard.check(tool_call)

        if not res.get("allowed"):
            print(f"  [X] BLOCKED by BTP AST Gate (Latency: {res.get('latency_us', 0)}us)")
            print(f"      Reason: {res.get('reason')}")
            print("      Action safely rejected before touching OS kernel or container.")
        else:
            print(f"  [v] PASSED AST Gate (Latency: {res.get('latency_us', 0)}us)")
            sig = res.get('receipt', {}).get('signature', '')
            print(f"      Signed Ed25519 Receipt Stamped: {sig[:24]}...")
            print("      Dispatching to isolated container sandbox...")
            exec_res = sandbox.run(tool_call)
            print(f"      Execution Mode: {exec_res.get('mode')}")

    print("\n" + "=" * 75)
    print("  Enterprise Defense-in-Depth Demonstration Complete.")
    print("=" * 75)
    return True


if __name__ == "__main__":
    main()
