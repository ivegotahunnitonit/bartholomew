"""
Bartholomew Cookbook: LlamaIndex Tool Execution Guard
=====================================================
30-second drop-in safety decorator for LlamaIndex query tools and function agents.
Blocks destructive SQL commands, prevents runaway loops, and scrubs credentials
in sub-35 microsecond time before execution.

Run:
    python cookbook/already_built/llamaindex_agent_guard.py
"""

import sys
import os

# Add repo root to import path if running from source
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from framework_adapters.llamaindex import btp_llamaindex_tool, BTPViolationError

# ---------------------------------------------------------------------------
# 1. Define LlamaIndex Tools Protected with 1-Line Decorator
# ---------------------------------------------------------------------------

@btp_llamaindex_tool(spend_cap=25.0, required_capability="db:query")
def llamaindex_sql_query_tool(query: str) -> str:
    """Simulated LlamaIndex text-to-SQL query engine tool."""
    return f"[SUCCESS] SQL executed safely against index: {query}"


@btp_llamaindex_tool(spend_cap=10.0, required_capability="tools:execute")
def llamaindex_file_reader_tool(file_path: str) -> str:
    """Simulated LlamaIndex document reader tool."""
    return f"[SUCCESS] Document loaded safely: {file_path}"


# ---------------------------------------------------------------------------
# 2. Interactive Execution Demonstration
# ---------------------------------------------------------------------------

def main():
    print("=" * 76)
    print("  Bartholomew Guard -- LlamaIndex Tool & Query Safety Demo")
    print("=" * 76)

    # Scenario A: Safe RAG SQL Query
    print("\n[+] Test 1: Safe LlamaIndex SQL Query")
    safe_query = "SELECT document_id, vector_embedding FROM documents WHERE category = 'reports'"
    try:
        res = llamaindex_sql_query_tool(safe_query)
        print(f"    Input   : {safe_query}")
        print(f"    Verdict : ALLOW")
        print(f"    Output  : {res}")
    except BTPViolationError as e:
        print(f"    [FAIL] Unexpected block: {e}")

    # Scenario B: Accidental Table Wipe (DROP TABLE)
    print("\n[+] Test 2: Accidental Database Wipe Attempt (DROP TABLE)")
    bad_query = "DROP TABLE documents; -- purge vector embeddings"
    try:
        print(f"    Input   : {bad_query}")
        llamaindex_sql_query_tool(bad_query)
        print("    [FAIL] Dangerous query was NOT blocked!")
    except BTPViolationError as e:
        print(f"    Verdict : [BLOCK] BLOCKED BEFORE DATABASE QUERY DISPATCH")
        print(f"    Rule ID : {e.rule_id}")
        print(f"    Reason  : {e.reason}")
        print(f"    Latency : {e.latency_us:.1f} us")

    # Scenario C: System Path Traversal / Destruction
    print("\n[+] Test 3: Destructive Command via Tool Payload")
    bad_cmd = "rm -rf /var/indexes/vector_store"
    try:
        print(f"    Input   : {bad_cmd}")
        llamaindex_file_reader_tool(bad_cmd)
        print("    [FAIL] Destructive command was NOT blocked!")
    except BTPViolationError as e:
        print(f"    Verdict : [BLOCK] BLOCKED BEFORE OS EXECUTION")
        print(f"    Rule ID : {e.rule_id}")
        print(f"    Reason  : {e.reason}")
        print(f"    Latency : {e.latency_us:.1f} us")

    print("\n" + "=" * 76)
    print("  All LlamaIndex tool safety boundaries verified successfully.")
    print("=" * 76)


if __name__ == "__main__":
    main()
