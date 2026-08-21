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
        ("4. Test Hermetic Command & File Sandbox", ["python", "test_hermetic_command_sandbox.py"]),
        ("5. Test Docker / Hermetic Execution Runner", ["python", "test_docker_runner.py"]),
        ("6. Test TypeScript SDK", ["node", "test_ts_sdk.js"], "sdk_typescript"),
        ("7. Test Go Microsecond Engine", ["go", "test", "-v", "./..."], "sdk_go"),
        ("8. Execute Swarm Concurrency Verification", ["python", "test_multi_agent_swarm_stress.py"]),
        ("9. Test AgentMesh Social & Task Network", ["python", "test_agent_social_network.py"]),
        ("10. Test Autonomous Bounty Solver & PR Engine", ["python", "test_autonomous_bounty_solver.py"]),
        ("11. Test IssueHunt & Open VRP Hunter Engine", ["python", "test_issuehunt_vrp_hunter.py"]),
        ("12. Test Invariant Fuzzing & Bounty Crawler", ["python", "test_fuzzing_bounty_crawler.py"]),
        ("13. Test 1-Line Drop-In Client Wrapper", ["python", "test_client_wrapper.py"]),
        ("14. Test Native LangChain & CrewAI Guard", ["python", "test_langchain_guard.py"]),
        ("15. Test Enterprise Agent Scout & M2M Settlement", ["python", "test_enterprise_agent_scout.py"]),
        ("16. Test Fund Legitimacy & Financial Invariants", ["python", "test_fund_legitimacy_verifier.py"])
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
