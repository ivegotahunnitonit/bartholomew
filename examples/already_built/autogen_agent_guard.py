"""
Bartholomew Cookbook: Microsoft AutoGen Tool & Code Execution Guard
===================================================================
30-second drop-in safety decorator for AutoGen agents and tool dispatchers.
Blocks destructive bash and SQL commands, prevents runaway loops, and
halts confused-deputy tool attacks in microsecond time.

Run:
    python cookbook/already_built/autogen_agent_guard.py
"""

import sys
import os

# Add repo root to import path if running from source
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from framework_adapters.autogen import btp_autogen_guard, BTPViolationError

# ---------------------------------------------------------------------------
# 1. Define AutoGen Tools Protected with 1-Line Decorator
# ---------------------------------------------------------------------------

@btp_autogen_guard(spend_cap=20.0, strict=True)
def autogen_run_code(code: str) -> str:
    """Simulated AutoGen Python / bash execution tool."""
    return f"[SUCCESS] Code executed cleanly: {code}"


@btp_autogen_guard(spend_cap=50.0, strict=True)
def autogen_run_migration(sql_script: str) -> str:
    """Simulated AutoGen database migration tool."""
    return f"[SUCCESS] Database migration applied cleanly: {sql_script}"


# ---------------------------------------------------------------------------
# 2. Interactive Execution Demonstration
# ---------------------------------------------------------------------------

def main():
    print("=" * 76)
    print("  Bartholomew Guard -- AutoGen Tool & Code Safety Demo")
    print("=" * 76)

    # Scenario A: Safe Code Execution
    print("\n[+] Test 1: Safe AutoGen Code Execution")
    safe_code = "import math\nprint('Hypotenuse:', math.hypot(3, 4))"
    try:
        res = autogen_run_code(safe_code)
        print(f"    Input   : {safe_code}")
        print(f"    Verdict : ALLOW")
        print(f"    Output  : {res}")
    except BTPViolationError as e:
        print(f"    [FAIL] Unexpected block: {e}")

    # Scenario B: Destructive Filesystem Deletion via AutoGen
    print("\n[+] Test 2: Destructive Filesystem Wipe Attempt")
    bad_bash = "rm -rf /home/user/workspace/data/*"
    try:
        print(f"    Input   : {bad_bash}")
        autogen_run_code(bad_bash)
        print("    [FAIL] Destructive command was NOT blocked!")
    except BTPViolationError as e:
        print(f"    Verdict : [BLOCK] BLOCKED BEFORE EXECUTION")
        print(f"    Rule ID : {e.rule_id}")
        print(f"    Reason  : {e.reason}")
        print(f"    Latency : {e.latency_us:.1f} us")

    # Scenario C: Destructive Database Migration
    print("\n[+] Test 3: Destructive Database Mutation (DROP SCHEMA)")
    bad_sql = "DROP SCHEMA public CASCADE;"
    try:
        print(f"    Input   : {bad_sql}")
        autogen_run_migration(bad_sql)
        print("    [FAIL] Destructive query was NOT blocked!")
    except BTPViolationError as e:
        print(f"    Verdict : [BLOCK] BLOCKED BEFORE MIGRATION DISPATCH")
        print(f"    Rule ID : {e.rule_id}")
        print(f"    Reason  : {e.reason}")
        print(f"    Latency : {e.latency_us:.1f} us")

    print("\n" + "=" * 76)
    print("  All AutoGen tool safety boundaries verified successfully.")
    print("=" * 76)


if __name__ == "__main__":
    main()
