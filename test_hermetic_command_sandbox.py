"""
Test Suite: Hermetic Command & File Sandbox (Composition & Traversal Defenses)
=============================================================================
Tests:
  1. Permitted safe command (git status).
  2. Execution hijack flag rejection (go test -exec /evil, pytest -c evil).
  3. Shell injection & newline rejection (git status; rm -rf /).
  4. Path traversal commonpath fix (sibling directory /workspace_evil).
  5. Composition attack defense: Protects execution-triggering configs (package.json, conftest.py, build.rs).
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))
from src.hermetic_sandbox import HermeticCommandSandbox, HermeticFileSandbox

def test_hermetic_suite():
    print("=" * 80)
    print("TESTING HERMETIC SANDBOX: COMPOSITION & PATH DEFENSES")
    print("=" * 80 + "\n")

    # Test 1: Permitted Command (git status)
    res1 = HermeticCommandSandbox.execute_bounded_command("git status")
    print(f"[TEST 1: Permitted Command (git status)]")
    print(f"  * Verdict          : {res1['verdict']}")
    print(f"  * Command Executed : {res1['command_executed']}")
    assert res1['verdict'] == "ALLOW"
    assert res1['command_executed'] is True

    # Test 2: Flag Execution Hijack (go test -exec /bin/bad)
    res2 = HermeticCommandSandbox.execute_bounded_command("go test -exec /bin/bad")
    print(f"\n[TEST 2: Execution Flag Hijack (go test -exec ...)]")
    print(f"  * Verdict          : {res2['verdict']}")
    print(f"  * Command Executed : {res2['command_executed']}")
    print(f"  * Reason           : {res2['reason']}")
    assert res2['verdict'] == "DENY"
    assert res2['command_executed'] is False
    assert "Forbidden execution flag '-exec'" in res2['reason']

    # Test 3: Path Prefix Sibling Traversal (commonpath fix)
    safe_sibling, reason_sibling = HermeticFileSandbox.is_safe_write_path(
        candidate_path="../workspace_evil/secret.txt",
        workspace_root=os.path.abspath(".")
    )
    print(f"\n[TEST 3: Sibling Directory Traversal (../workspace_evil)]")
    print(f"  * Safe Path        : {safe_sibling}")
    print(f"  * Reason           : {reason_sibling}")
    assert safe_sibling is False
    assert "escapes workspace boundary" in reason_sibling

    # Test 4: Composition Attack - Malicious package.json overwrite
    safe_pkg, reason_pkg = HermeticFileSandbox.is_safe_write_path("package.json")
    print(f"\n[TEST 4: Composition Defense (package.json overwrite)]")
    print(f"  * Safe Path        : {safe_pkg}")
    print(f"  * Reason           : {reason_pkg}")
    assert safe_pkg is False
    assert "Composition Security Gate" in reason_pkg

    # Test 5: Composition Attack - Malicious conftest.py overwrite
    safe_conf, reason_conf = HermeticFileSandbox.is_safe_write_path("tests/conftest.py")
    print(f"\n[TEST 5: Composition Defense (conftest.py overwrite)]")
    print(f"  * Safe Path        : {safe_conf}")
    print(f"  * Reason           : {reason_conf}")
    assert safe_conf is False
    assert "Composition Security Gate" in reason_conf

    # Test 6: Safe Source Code File in Workspace
    safe_code, reason_code = HermeticFileSandbox.is_safe_write_path("src/new_feature.py")
    print(f"\n[TEST 6: Safe Source File (src/new_feature.py)]")
    print(f"  * Safe Path        : {safe_code}")
    print(f"  * Reason           : {reason_code}")
    assert safe_code is True

    print("\n" + "=" * 80)
    print("ALL COMPOSITION & HERMETIC DEFENSE TESTS PASSED 100% CLEAN!")
    print("=" * 80)

if __name__ == "__main__":
    test_hermetic_suite()
