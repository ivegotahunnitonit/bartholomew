"""
LangChain & LangGraph BTP v3.0 Integration Example
==================================================
Demonstrates how to protect LangChain / LangGraph tools with sub-35µs
in-process AST validation, secret scrubbing, and spend limits.
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))
from framework_adapters.langgraph.langgraph_btp_guard import btp_langchain_tool, BartholomewLangChainTool

# Example 1: Decorate any function directly
@btp_langchain_tool(spend_cap=50.0, strict=True)
def execute_database_query(sql_query: str) -> str:
    """Executes database queries with in-process AST gating."""
    return f"EXECUTED SAFELY ON DB: {sql_query}"

@btp_langchain_tool(spend_cap=25.0, strict=True)
def execute_shell_task(command: str) -> str:
    """Executes system commands with sub-35µs catastrophic pattern detection."""
    return f"COMMAND EXECUTED SAFELY: {command}"

if __name__ == "__main__":
    print("=" * 60)
    print("LANGCHAIN & LANGGRAPH BTP v3.0 INTEGRATION DEMO")
    print("=" * 60)

    # 1. Safe Query
    print("\n[1] Testing Safe Database Tool Call:")
    res = execute_database_query("SELECT id, name FROM accounts LIMIT 5;")
    print("    Result:", res)

    # 2. Destructive SQL Query
    print("\n[2] Testing Destructive Tool Call (DROP TABLE):")
    try:
        execute_database_query("DROP TABLE accounts;")
    except PermissionError as e:
        print("    [BLOCKED IN-PROCESS]:", e)

    # 3. Destructive Shell Command
    print("\n[3] Testing Destructive Shell Command (rm -rf /):")
    try:
        execute_shell_task("rm -rf /")
    except PermissionError as e:
        print("    [BLOCKED IN-PROCESS]:", e)

    print("\n" + "=" * 60)
    print("LANGCHAIN BTP v3.0 INTEGRATION DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)
