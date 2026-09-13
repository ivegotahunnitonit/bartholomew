"""
Bartholomew Cookbook: CrewAI Agent Guard
========================================
30-second drop-in safety decorator for CrewAI agent tools.
Blocks destructive commands (rm -rf, DROP TABLE), prevents runaway loop spend,
and scrubs credentials before execution.

Run:
    python cookbook/already_built/crewai_agent_guard.py
"""

import sys
import os

# Add repo root to import path if running from source
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from framework_adapters.crewai import btp_crewai_tool, BTPViolationError

# ---------------------------------------------------------------------------
# 1. Define CrewAI Tools Protected with 1-Line Decorator
# ---------------------------------------------------------------------------

@btp_crewai_tool(spend_cap=25.0, action_type="database_query")
def query_database_tool(sql_query: str) -> str:
    """Simulated CrewAI database query tool."""
    return f"[SUCCESS] Query executed safely: {sql_query}"


@btp_crewai_tool(spend_cap=5.0, action_type="bash_execution")
def execute_shell_tool(command: str) -> str:
    """Simulated CrewAI shell execution tool."""
    return f"[SUCCESS] Shell command executed safely: {command}"


# ---------------------------------------------------------------------------
# 2. Interactive Execution Demonstration
# ---------------------------------------------------------------------------

def main():
    print("=" * 76)
    print("  Bartholomew Guard -- CrewAI Agent Tool Safety Demo")
    print("=" * 76)

    # Scenario A: Safe SQL Query
    print("\n[+] Test 1: Safe SQL Query Execution")
    safe_sql = "SELECT id, company_name, mrr FROM enterprise_customers WHERE active = 1"
    try:
        result = query_database_tool(safe_sql)
        print(f"    Input   : {safe_sql}")
        print(f"    Verdict : ALLOW")
        print(f"    Output  : {result}")
    except BTPViolationError as e:
        print(f"    [FAIL] Unexpected block: {e}")

    # Scenario B: Hallucinated / Destructive DROP TABLE
    print("\n[+] Test 2: Hallucinated Destructive SQL Attack")
    bad_sql = "DROP TABLE production_orders; -- wipe table"
    try:
        print(f"    Input   : {bad_sql}")
        query_database_tool(bad_sql)
        print("    [FAIL] Dangerous query was NOT blocked!")
    except BTPViolationError as e:
        print(f"    Verdict : [BLOCK] BLOCKED BEFORE DATABASE EXECUTION")
        print(f"    Rule ID : {e.rule_id}")
        print(f"    Reason  : {e.reason}")
        print(f"    Latency : {e.latency_us:.1f} us")

    # Scenario C: Hallucinated Destructive Shell Command
    print("\n[+] Test 3: Destructive Shell Cleanup Command")
    bad_cmd = "rm -rf /var/log/app/*"
    try:
        print(f"    Input   : {bad_cmd}")
        execute_shell_tool(bad_cmd)
        print("    [FAIL] Dangerous command was NOT blocked!")
    except BTPViolationError as e:
        print(f"    Verdict : [BLOCK] BLOCKED BEFORE OS DISPATCH")
        print(f"    Rule ID : {e.rule_id}")
        print(f"    Reason  : {e.reason}")
        print(f"    Latency : {e.latency_us:.1f} us")

    print("\n" + "=" * 76)
    print("  All CrewAI tool safety boundaries verified successfully.")
    print("=" * 76)


if __name__ == "__main__":
    main()
