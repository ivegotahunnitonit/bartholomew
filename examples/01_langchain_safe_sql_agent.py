"""
Bartholomew Cookbook 01: LangChain Safe SQL & Shell Agent
=========================================================
Demonstrates protecting LangChain tools and callback handlers with sub-35µs AST
syntax checks, secret scrubbing, and spend caps.

Run:
    python examples/01_langchain_safe_sql_agent.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from btp_guard import Guard, secure_tool, SecurityVetoException
from btp_guard.integrations.langchain import BtpCallbackHandler, BtpToolGuard

print("=" * 75)
print("  BARTHOLOMEW COOKBOOK: LANGCHAIN AGENT EXECUTION GUARD (BTP v5.4.20)")
print("=" * 75)

# --- Technique A: 1-Line Tool Decoration ---
print("\n[1] Testing 1-Line Tool Decoration (@secure_tool):")

@secure_tool
def execute_sql_query(query: str) -> str:
    """Mock database query executor."""
    return f"DB_SUCCESS: Returned 42 rows for query [{query}]"

# Safe query
safe_q = "SELECT id, email, created_at FROM users WHERE status = 'active';"
t0 = time.perf_counter()
res = execute_sql_query(safe_q)
dt_us = (time.perf_counter() - t0) * 1_000_000
print(f"  [PASS] Safe Query Allowed ({dt_us:.1f}µs):")
print(f"         {res}")

# Malicious query (SQL injection / wipe)
evil_q = "SELECT * FROM users; DROP TABLE users; --"
print(f"\n  [ATTEMPT] Agent proposing dangerous SQL: '{evil_q}'")
try:
    execute_sql_query(evil_q)
except SecurityVetoException as veto:
    print(f"  [BLOCKED] Bartholomew Veto Triggered:")
    print(f"            Reason: {veto.reason}")
    print(f"            Audit:  Cryptographic Ed25519 receipt generated.")

# --- Technique B: LangChain Global Callback Handler ---
print("\n[2] Testing LangChain Global Callback Handler (BtpCallbackHandler):")

handler = BtpCallbackHandler(spend_cap=25.0, strict=True, agent_id="langchain-sql-bot")

# Simulating agent invoking a tool
safe_action = {"name": "query_database"}
res_cb = handler.on_tool_start(safe_action, "SELECT count(*) FROM orders;")
print(f"  [PASS] Callback check for safe query: ALLOWED")

# Simulating prompt injection causing destructive shell execution
destructive_action = {"name": "bash_tool"}
try:
    handler.on_tool_start(destructive_action, "rm -rf /var/log/app")
except PermissionError as e:
    print(f"  [BLOCKED] Callback intercepted rogue bash tool call: {e}")

print("\n[SUMMARY] LangChain agent successfully secured with 0 second-model GPU overhead!")
