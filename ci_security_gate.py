"""
Bartholomew CI/CD Multi-Runtime Automated Security Gate
======================================================
Executes end-to-end multi-language test suite and policy validation:
  1. Declarative policy validation (YAML/JSON).
  2. Python cryptographic invariants & sidecar E2E.
  3. TypeScript/Node.js SDK verification.
  4. Go compiled microsecond engine.
  5. Multi-agent swarm concurrency test.
"""

import sys
import os
import subprocess
import time

def run_gate():
    print("=" * 80)
    print("RUNNING BARTHOLOMEW CI/CD MULTI-RUNTIME SECURITY GATE")
    print("=" * 80 + "\n")

    steps = [
        ("1. Validate Declarative Policies", ["python", "-m", "src.cli", "policy", "validate", "--file", "policies/default_security_policy.yaml"]),
        ("2. Test Declarative Policy Engine", ["python", "test_declarative_policy_engine.py"]),
        ("3. Test Sidecar Runtime E2E", ["python", "sidecar/test_sidecar_e2e.py"]),
        ("4. Test TypeScript SDK", ["node", "test_ts_sdk.js"], "sdk_typescript"),
        ("5. Test Go Microsecond Engine", ["go", "test", "-v", "./..."], "sdk_go"),
        ("6. Execute Swarm Concurrency Verification", ["python", "test_multi_agent_swarm_stress.py"])
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
        print("CI/CD GATE STATUS: 100% ALL RUNTIMES PASSED")
    else:
        print("CI/CD GATE STATUS: FAILURES DETECTED")
    print("=" * 80)

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    run_gate()
