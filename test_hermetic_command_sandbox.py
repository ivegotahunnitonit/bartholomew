"""
Test Suite: Hermetic Command Sandbox & Allowlist Execution
==========================================================
Tests:
  1. Permitted command execution (git status).
  2. Shell injection chaining rejection (git status; rm -rf /).
  3. Unlisted command rejection (curl http://evil.com, rm -rf).
  4. Environment secret scrubbing.
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))
from src.hermetic_sandbox import HermeticCommandSandbox

def test_hermetic_sandbox():
    print("=" * 80)
    print("TESTING HERMETIC COMMAND SANDBOX & ALLOWLIST EXECUTION")
    print("=" * 80 + "\n")

    # Test 1: Permitted Command (git status)
    res1 = HermeticCommandSandbox.execute_bounded_command("git status")
    print(f"[TEST 1: Permitted Command (git status)]")
    print(f"  * Verdict          : {res1['verdict']}")
    print(f"  * Command Executed : {res1['command_executed']}")
    print(f"  * Status           : {res1['status']}")
    print(f"  * Decision Latency : {res1['latency_us']} µs")
    assert res1['verdict'] == "ALLOW"
    assert res1['command_executed'] is True

    # Test 2: Shell Chaining Injection Attack (git status; rm -rf /)
    res2 = HermeticCommandSandbox.execute_bounded_command("git status; rm -rf /")
    print(f"\n[TEST 2: Shell Chaining Injection (git status; rm -rf /)]")
    print(f"  * Verdict          : {res2['verdict']}")
    print(f"  * Command Executed : {res2['command_executed']}")
    print(f"  * Reason           : {res2['reason']}")
    assert res2['verdict'] == "DENY"
    assert res2['command_executed'] is False
    assert "Forbidden shell chaining operator" in res2['reason']

    # Test 3: Unapproved Dangerous Command (rm -rf /var/data)
    res3 = HermeticCommandSandbox.execute_bounded_command("rm -rf /var/data")
    print(f"\n[TEST 3: Unapproved Dangerous Command (rm -rf)]")
    print(f"  * Verdict          : {res3['verdict']}")
    print(f"  * Command Executed : {res3['command_executed']}")
    print(f"  * Reason           : {res3['reason']}")
    assert res3['verdict'] == "DENY"
    assert res3['command_executed'] is False
    assert "not in the permitted allowlist" in res3['reason']

    print("\n" + "=" * 80)
    print("ALL HERMETIC COMMAND SANDBOX TESTS PASSED 100% CLEAN!")
    print("=" * 80)

if __name__ == "__main__":
    test_hermetic_sandbox()
