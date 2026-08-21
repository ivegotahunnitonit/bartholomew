"""
Test Suite: Hermetic Command Sandbox & Allowlist Execution
==========================================================
Tests:
  1. Permitted command execution (git status) via argv (shell=False).
  2. Shell injection chaining rejection (git status; rm -rf /).
  3. Newline separator rejection (git status\nrm -rf /).
  4. Unlisted command rejection (curl http://evil.com, rm -rf).
  5. File sandbox path traversal containment (../../etc/shadow).
  6. Protected config file overwrite rejection (.env).
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))
from src.hermetic_sandbox import HermeticCommandSandbox, HermeticFileSandbox

def test_hermetic_sandbox():
    print("=" * 80)
    print("TESTING HERMETIC COMMAND & FILE SANDBOX ENGINE")
    print("=" * 80 + "\n")

    # Test 1: Permitted Command (git status)
    res1 = HermeticCommandSandbox.execute_bounded_command("git status")
    print(f"[TEST 1: Permitted Command (git status)]")
    print(f"  * Verdict          : {res1['verdict']}")
    print(f"  * Command Executed : {res1['command_executed']}")
    print(f"  * Status           : {res1['status']}")
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
    assert "Forbidden character or separator" in res2['reason']

    # Test 3: Newline Separator Injection (git status\nrm -rf /)
    res3 = HermeticCommandSandbox.execute_bounded_command("git status\nrm -rf /")
    print(f"\n[TEST 3: Newline Separator Injection (git status\\nrm -rf /)]")
    print(f"  * Verdict          : {res3['verdict']}")
    print(f"  * Command Executed : {res3['command_executed']}")
    print(f"  * Reason           : {res3['reason']}")
    assert res3['verdict'] == "DENY"
    assert res3['command_executed'] is False

    # Test 4: Unapproved Dangerous Command (rm -rf /var/data)
    res4 = HermeticCommandSandbox.execute_bounded_command("rm -rf /var/data")
    print(f"\n[TEST 4: Unapproved Dangerous Command (rm -rf)]")
    print(f"  * Verdict          : {res4['verdict']}")
    print(f"  * Command Executed : {res4['command_executed']}")
    print(f"  * Reason           : {res4['reason']}")
    assert res4['verdict'] == "DENY"
    assert res4['command_executed'] is False
    assert "not in the permitted allowlist" in res4['reason']

    # Test 5: File Path Traversal Blocked
    safe_path1, reason_path1 = HermeticFileSandbox.is_safe_write_path("../../../etc/shadow")
    print(f"\n[TEST 5: File Path Traversal (../../../etc/shadow)]")
    print(f"  * Safe Path        : {safe_path1}")
    print(f"  * Reason           : {reason_path1}")
    assert safe_path1 is False
    assert "escapes workspace boundary" in reason_path1

    # Test 6: Protected File Overwrite Blocked (.env)
    safe_path2, reason_path2 = HermeticFileSandbox.is_safe_write_path(".env")
    print(f"\n[TEST 6: Protected File Overwrite (.env)]")
    print(f"  * Safe Path        : {safe_path2}")
    print(f"  * Reason           : {reason_path2}")
    assert safe_path2 is False
    assert "Protected File Blocked" in reason_path2

    print("\n" + "=" * 80)
    print("ALL HERMETIC SANDBOX & ALLOWLIST TESTS PASSED 100% CLEAN!")
    print("=" * 80)

if __name__ == "__main__":
    test_hermetic_sandbox()
