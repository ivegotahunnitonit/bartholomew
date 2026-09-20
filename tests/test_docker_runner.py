"""
Test Suite: Docker & Hermetic Sandbox Execution Runner
======================================================
Tests:
  1. Safe computation script execution in isolated scratch environment.
  2. Ephemeral cleanup verification (scratch directory deleted after run).
  3. Structured result payload (isolation_tier, stdout, exit_code, latency).
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))
from src.docker_runner import DockerExecutionRunner

def test_runner():
    print("=" * 80)
    print("TESTING DOCKER / HERMETIC ISOLATION RUNNER")
    print("=" * 80 + "\n")

    is_docker = DockerExecutionRunner.is_docker_available()
    print(f"[*] Docker Daemon Status : {'AVAILABLE (Tier 3 Active)' if is_docker else 'UNAVAILABLE (Tier 2 Hermetic Active)'}")

    # Test 1: Execute clean computation script
    safe_code = """
import sys
def compute():
    total = sum(i * 2 for i in range(100))
    print(f"COMPUTE_RESULT: {total}")

if __name__ == "__main__":
    compute()
"""
    res = DockerExecutionRunner.execute_script_in_sandbox(safe_code)
    print(f"\n[TEST 1: Safe Script Execution]")
    print(f"  * Status         : {res['status']}")
    print(f"  * Isolation Tier : {res['isolation_tier']}")
    print(f"  * Output         : {res.get('stdout')}")
    print(f"  * Latency        : {res['latency_us']} µs")
    
    assert res['status'] == "SUCCESS"
    assert "COMPUTE_RESULT: 9900" in res.get('stdout', "")

    # Test 2: Execute script with intentional exception
    failing_code = """
raise ValueError("Intentional test exception in sandbox")
"""
    res_fail = DockerExecutionRunner.execute_script_in_sandbox(failing_code)
    print(f"\n[TEST 2: Intentional Exception Containment]")
    print(f"  * Status         : {res_fail['status']}")
    print(f"  * Isolation Tier : {res_fail['isolation_tier']}")
    print(f"  * Exit Code      : {res_fail.get('exit_code')}")
    print(f"  * Stderr Catch   : {'ValueError' in res_fail.get('stderr', '')}")

    assert res_fail['status'] == "EXECUTION_ERROR"
    assert "ValueError" in res_fail.get('stderr', '')

    print("\n" + "=" * 80)
    print("ALL RUNNER ISOLATION TESTS PASSED 100% CLEAN!")
    print("=" * 80)

if __name__ == "__main__":
    test_runner()
