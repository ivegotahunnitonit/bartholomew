"""
Advanced AST Evasion & Exploit Test Suite
=========================================
Tests compiler-grade defenses against:
  1. Chained import aliases (from os import system as s).
  2. String concatenation getattr (getattr(os, 'sys' + 'tem')).
  3. Dunder attribute access (().__class__.__subclasses__()).
  4. Arbitrary file write to system path (open('/etc/shadow', 'w')).
  5. Socket exfiltration import (import socket).
  6. Legitimate code execution.
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))
from src.ast_validator import ASTSecurityValidator

def run_evasion_tests():
    print("=" * 80)
    print("TESTING ADVANCED AST EVASIONS & COMPILER-GRADE DEFENSES")
    print("=" * 80 + "\n")

    test_cases = [
        {
            "name": "Chained Import Alias (from os import system as s; s(...))",
            "code": "from os import system as s\ns('rm -rf /')",
            "expect_safe": False,
            "expected_violation": "os.system"
        },
        {
            "name": "Constant-Folded getattr (getattr(os, 'sys' + 'tem'))",
            "code": "import os\nfn = getattr(os, 'sys' + 'tem')\nfn('id')",
            "expect_safe": False,
            "expected_violation": "getattr"
        },
        {
            "name": "Dunder Reflection Attack (().__class__.__subclasses__())",
            "code": "sub = ().__class__.__subclasses__()",
            "expect_safe": False,
            "expected_violation": "__subclasses__"
        },
        {
            "name": "System Path File Write (open('/etc/shadow', 'w'))",
            "code": "f = open('/etc/shadow', 'w')\nf.write('compromised')",
            "expect_safe": False,
            "expected_violation": "Forbidden Arbitrary File Write Path"
        },
        {
            "name": "Socket Module Import (import socket)",
            "code": "import socket\ns = socket.socket()",
            "expect_safe": False,
            "expected_violation": "Forbidden Module Import: 'socket'"
        },
        {
            "name": "Legitimate Algorithm & Math (Safe Code)",
            "code": "def quicksort(arr):\n    if len(arr) <= 1: return arr\n    pivot = arr[len(arr) // 2]\n    return [x for x in arr if x < pivot] + [pivot] + [x for x in arr if x > pivot]",
            "expect_safe": True,
            "expected_violation": None
        }
    ]

    all_passed = True

    for idx, tc in enumerate(test_cases, 1):
        is_safe, reason, meta = ASTSecurityValidator.validate_code_ast(tc["code"])
        status = "PASSED" if is_safe == tc["expect_safe"] else "FAILED"
        if tc["expected_violation"] and not any(tc["expected_violation"] in v for v in meta["violations_found"]):
            status = "FAILED"
            all_passed = False

        print(f"[{idx}] {tc['name']}")
        print(f"    * Result    : {status} (Safe: {is_safe})")
        print(f"    * Latency   : {meta['analysis_latency_us']} µs")
        print(f"    * Violations: {meta['violations_found']}\n")

    print("=" * 80)
    if all_passed:
        print("ALL ADVANCED AST EVASION DEFENSE TESTS PASSED 100% CLEAN!")
    else:
        print("FAILURES DETECTED IN AST EVASION TESTS")
    print("=" * 80)

    assert all_passed

if __name__ == "__main__":
    run_evasion_tests()
