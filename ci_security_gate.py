"""
Bartholomew CI/CD Multi-Runtime Automated Security Gate
======================================================
Executes end-to-end multi-language test suite and policy validation:
  1. Declarative policy validation (YAML/JSON).
  2. Declarative policy engine verification.
  3. Sidecar runtime E2E.
  4. Hermetic command & file sandbox boundary containment.
  5. Docker / hermetic execution runner.
  6. TypeScript/Node.js SDK verification.
  7. Go compiled microsecond engine.
  8. Multi-agent swarm concurrency verification.
  9. 1-Line drop-in client wrapper (OpenAI / Anthropic).
  10. Native LangChain & CrewAI guardrail callback plugin.
"""

import sys
import os
import subprocess
import time

def run_gate():
    print("=" * 80)
    print("RUNNING BARTHOLOMEW CORE MULTI-RUNTIME SECURITY GATE")
    print("=" * 80 + "\n")

    steps = [
        ("1. Validate Declarative Policies", ["python", "-m", "src.cli", "policy", "validate", "--file", "policies/default_security_policy.yaml"]),
        ("2. Test Declarative Policy Engine", ["python", "test_declarative_policy_engine.py"]),
        ("3. Test Sidecar Runtime E2E", ["python", "sidecar/test_sidecar_e2e.py"]),
        ("4. Test Hermetic Command & File Sandbox", ["python", "test_hermetic_command_sandbox.py"]),
        ("5. Test Docker / Hermetic Execution Runner", ["python", "test_docker_runner.py"]),
        ("6. Test TypeScript SDK", ["node", "test_ts_sdk.js"], "sdk_typescript"),
        ("7. Test Go Microsecond Engine", ["go", "test", "-v", "./..."], "sdk_go"),
        ("8. Execute Swarm Concurrency Verification", ["python", "test_multi_agent_swarm_stress.py"]),
        ("9. Test 1-Line Drop-In Client Wrapper", ["python", "test_client_wrapper.py"]),
        ("10. Test Native LangChain & CrewAI Guard", ["python", "test_langchain_guard.py"])
    ]

    all_passed = True

    for item in steps:
        name = item[0]
        cmd = item[1]
        cwd = item[2] if len(item) > 2 else "."

        print(f"[*] Running: {name}...")
        res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"    [PASSED] {name}")
        else:
            print(f"    [FAILED] {name}\n    Error: {res.stderr or res.stdout}")
            all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print("CORE CI/CD GATE STATUS: 100% ALL RUNTIMES PASSED CLEAN")
    else:
        print("CORE CI/CD GATE STATUS: FAILURES DETECTED")
    print("=" * 80)

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    run_gate()
