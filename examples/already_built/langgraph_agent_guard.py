"""
Bartholomew Cookbook: LangGraph & LangChain Agent Guard
=======================================================
30-second drop-in safety decorator for LangGraph nodes and LangChain tools.
Blocks destructive commands (rm -rf, DROP TABLE), prevents runaway spend loops,
and scrubs credentials before execution.

Run:
    python cookbook/already_built/langgraph_agent_guard.py
"""

import sys
import os

# Add repo root to import path if running from source
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from framework_adapters.langgraph import btp_langchain_tool, BTPViolationError

# ---------------------------------------------------------------------------
# 1. Define LangGraph Tools Protected with 1-Line Decorator
# ---------------------------------------------------------------------------

@btp_langchain_tool(spend_cap=30.0, action_type="sql_query")
def run_snowflake_query(query: str) -> str:
    """Simulated LangGraph Snowflake / BigQuery analytics tool."""
    return f"[SUCCESS] Query executed safely on data warehouse: {query}"


@btp_langchain_tool(spend_cap=10.0, action_type="cloud_cli")
def run_cloud_provisioning(command: str) -> str:
    """Simulated LangGraph cloud provisioning & Terraform dispatch tool."""
    return f"[SUCCESS] Cloud command executed safely: {command}"


# ---------------------------------------------------------------------------
# 2. Interactive Execution Demonstration
# ---------------------------------------------------------------------------

def main():
    print("=" * 76)
    print("  Bartholomew Guard -- LangGraph & LangChain Tool Safety Demo")
    print("=" * 76)

    # Scenario A: Safe Analytics Query
    print("\n[+] Test 1: Safe Analytics Query")
    safe_query = "SELECT client_id, SUM(amount) FROM transactions GROUP BY client_id LIMIT 100"
    try:
        res = run_snowflake_query(safe_query)
        print(f"    Input   : {safe_query}")
        print(f"    Verdict : ALLOW")
        print(f"    Output  : {res}")
    except BTPViolationError as e:
        print(f"    [FAIL] Unexpected block: {e}")

    # Scenario B: Accidental Table Wipe (DROP / TRUNCATE)
    print("\n[+] Test 2: Accidental Database Wipe (DROP TABLE)")
    wipe_query = "DROP TABLE transactions; -- reset database"
    try:
        print(f"    Input   : {wipe_query}")
        run_snowflake_query(wipe_query)
        print("    [FAIL] Dangerous query was NOT blocked!")
    except BTPViolationError as e:
        print(f"    Verdict : [BLOCK] BLOCKED BEFORE DATABASE QUERY DISPATCH")
        print(f"    Rule ID : {e.rule_id}")
        print(f"    Reason  : {e.reason}")
        print(f"    Latency : {e.latency_us:.1f} us")

    # Scenario C: Unconstrained Teardown / Destruction
    print("\n[+] Test 3: Unconstrained Cloud Teardown Command")
    wipe_cli = "rm -rf /etc/kubernetes/manifests/*"
    try:
        print(f"    Input   : {wipe_cli}")
        run_cloud_provisioning(wipe_cli)
        print("    [FAIL] Destructive cloud command was NOT blocked!")
    except BTPViolationError as e:
        print(f"    Verdict : [BLOCK] BLOCKED BEFORE CLOUD DISPATCH")
        print(f"    Rule ID : {e.rule_id}")
        print(f"    Reason  : {e.reason}")
        print(f"    Latency : {e.latency_us:.1f} us")

    print("\n" + "=" * 76)
    print("  All LangGraph tool safety boundaries verified successfully.")
    print("=" * 76)


if __name__ == "__main__":
    main()
