"""
LangGraph + BTP Guard: Secure Financial Analyst Workflow
========================================================
Demonstrates wrapping state-graph node tools with LangGraphBTPGuard
to enforce strict schema validation and prevent unauthorized data exfiltration.

Run:
    python examples/langgraph_financial_analyst/run_workflow.py
"""

import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from framework_adapters.langgraph.langgraph_btp_guard import LangGraphBTPGuard
from src.trust_protocol import BartholomewTrustAuthority


def main():
    print("=" * 70)
    print("  LangGraph + BTP Guard: Financial Workflow Protection")
    print("=" * 70)

    auth = BartholomewTrustAuthority(ttl_seconds=300)
    root_pubkey = auth.public_key_hex
    print(f"[+] Initialized Trust Authority (Root: {root_pubkey[:16]}...)")

    guard = LangGraphBTPGuard(
        trusted_authorities=[root_pubkey],
        agent_id="Financial-Analyst-Node-01"
    )

    # Define sensitive analytical tool
    @guard.wrap_tool
    def query_quarterly_ledger(account_id: str, limit: int = 10) -> str:
        return f"[LEDGER-DATA] 200 OK: 10 transactions fetched for account {account_id}"

    # 1. Authorized Query
    print("\n--- [1] Executing Authorized Financial Query ---")
    query_payload = {
        "tool": "query_quarterly_ledger",
        "args": ("ACC-CORP-9881",),
        "kwargs": {"limit": 10}
    }
    receipt = auth.evaluate_intent(
        "Supervisor-Graph-Node",
        "LEDGER_QUERY",
        query_payload,
        target_recipient="Financial-Analyst-Node-01"
    )
    result = query_quarterly_ledger("ACC-CORP-9881", limit=10, btp_receipt=receipt)
    print(f"Outcome: {result}")

    # 2. Unattested or Forged Node Invocation
    print("\n--- [2] Intercepting Forged Tool Call ---")
    try:
        # Calling without valid cryptographic receipt
        query_quarterly_ledger("ACC-CORP-9881", limit=10, btp_receipt="FORGED_INVALID_RECEIPT")
        print("Error: Forged invocation was not blocked!")
    except Exception as e:
        print(f"Outcome: Correctly blocked by LangGraphBTPGuard ({type(e).__name__})")

    print("\n" + "=" * 70)
    print("  LangGraph Workflow Demo Complete: Financial Nodes Guarded")
    print("=" * 70)
    return True


if __name__ == "__main__":
    main()
