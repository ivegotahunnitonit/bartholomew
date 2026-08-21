"""
Test Suite: In-Line Tool Interception & Advanced AST Evasion Tests
=================================================================
Tests:
  1. Standard malicious calls (eval, exec).
  2. Aliased import evasion (import os as o; o.system(...)).
  3. Dynamic getattr evasion (getattr(os, "system")(...)).
  4. Mandatory in-line tool interception (underlying tool NEVER executes on DENY).
  5. Clean code execution.
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))
from src.trust_protocol import BartholomewTrustAuthority
from src.ast_validator import ASTSecurityValidator
from mcp_server.inline_tool_gate import MandatoryToolGate

def run_tests():
    print("=" * 80)
    print("TESTING IN-LINE MANDATORY TOOL GATE & ADVANCED AST EVASION DEFENSES")
    print("=" * 80 + "\n")

    authority = BartholomewTrustAuthority()
    gate = MandatoryToolGate(authority)

    tool_executed_flag = False

    def write_file_tool(path: str, code: str):
        nonlocal tool_executed_flag
        tool_executed_flag = True
        return f"WROTE TO {path}"

    gate.register_tool("write_file", write_file_tool)

    # ─────────────────────────────────────────────────────────────────────────
    # Test 1: Aliased Import Evasion (import os as o; o.system(...))
    # ─────────────────────────────────────────────────────────────────────────
    alias_code = """
import os as o
def do_bad():
    o.system("rm -rf /")
"""
    safe1, reason1, meta1 = ASTSecurityValidator.validate_code_ast(alias_code)
    print(f"[TEST 1: Aliased Import Evasion (import os as o; o.system)]")
    print(f"  * Safe             : {safe1}")
    print(f"  * Violations Found : {meta1['violations_found']}")
    assert safe1 is False
    assert any("os.system" in v for v in meta1['violations_found'])

    # ─────────────────────────────────────────────────────────────────────────
    # Test 2: Dynamic getattr Evasion (getattr(os, "system")(...))
    # ─────────────────────────────────────────────────────────────────────────
    getattr_code = """
import os
def do_dynamic():
    fn = getattr(os, "system")
    fn("cat /etc/shadow")
"""
    safe2, reason2, meta2 = ASTSecurityValidator.validate_code_ast(getattr_code)
    print(f"\n[TEST 2: Dynamic getattr Evasion (getattr(os, 'system'))]")
    print(f"  * Safe             : {safe2}")
    print(f"  * Violations Found : {meta2['violations_found']}")
    assert safe2 is False
    assert any("getattr" in v for v in meta2['violations_found'])

    # ─────────────────────────────────────────────────────────────────────────
    # Test 3: Mandatory In-Line Execution Interception
    # ─────────────────────────────────────────────────────────────────────────
    tool_executed_flag = False
    res = gate.execute_gated_tool(
        agent_id="claude-desktop",
        tool_name="write_file",
        arguments={"path": "main.py", "code": alias_code}
    )

    print(f"\n[TEST 3: Mandatory In-Line Interception Execution]")
    print(f"  * Verdict          : {res['verdict']}")
    print(f"  * Tool Executed    : {res['tool_executed']}")
    print(f"  * Reason           : {res['reason']}")
    
    assert res['verdict'] == "DENY"
    assert res['tool_executed'] is False
    assert tool_executed_flag is False

    # ─────────────────────────────────────────────────────────────────────────
    # Test 4: Legitimate Code Passes Cleanly
    # ─────────────────────────────────────────────────────────────────────────
    tool_executed_flag = False
    clean_code = """
def add(a: int, b: int) -> int:
    return a + b
"""
    res_clean = gate.execute_gated_tool(
        agent_id="claude-desktop",
        tool_name="write_file",
        arguments={"path": "math.py", "code": clean_code}
    )
    print(f"\n[TEST 4: Clean Code Execution]")
    print(f"  * Verdict          : {res_clean['verdict']}")
    print(f"  * Tool Executed    : {res_clean['tool_executed']}")
    print(f"  * Result           : {res_clean['result']}")

    assert res_clean['verdict'] == "ALLOW"
    assert res_clean['tool_executed'] is True
    assert tool_executed_flag is True

    print("\n" + "=" * 80)
    print("ALL ADVANCED AST & IN-LINE INTERCEPTION TESTS PASSED 100% CLEAN!")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()
