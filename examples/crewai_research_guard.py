"""
Bartholomew + CrewAI Multi-Agent Swarm Guard Example
====================================================
Wraps CrewAI custom tool executions with Bartholomew's
Law of Diminishing Marginal Utility (LDMU) and spend bounds.
"""

import os
import sys

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from src.marginal_utility_engine import evaluate_marginal_utility
from src.trust_protocol import BartholomewTrustAuthority

authority = BartholomewTrustAuthority()


def crewai_guarded_tool_executor(agent_name: str, tool_name: str, payload: dict) -> dict:
    """Intersects CrewAI tool calls before invoking external APIs."""
    # 1. Marginal Utility / Loop Fatigue Check
    verdict, mu, reason, latency_us = evaluate_marginal_utility(
        agent_id=agent_name,
        action_type=tool_name,
        payload=payload
    )

    if verdict in ("CO_SIGN_REQUIRED", "DENY"):
        return {
            "status": "BLOCKED",
            "reason": reason,
            "marginal_utility": mu,
            "latency_us": latency_us
        }

    # 2. Hard Invariant AST / Destructive Filter
    receipt = authority.evaluate_intent(
        agent_id=agent_name,
        action_type=tool_name,
        payload=payload
    )

    return {
        "status": receipt["attestation"]["verdict"],
        "reason": receipt["attestation"].get("reason", "Approved"),
        "signature": receipt.get("signature"),
        "marginal_utility": mu,
        "latency_us": latency_us
    }


if __name__ == "__main__":
    print("--- CrewAI Tool Call 1 (Fresh Action) ---")
    res1 = crewai_guarded_tool_executor("researcher_agent", "web_search", {"query": "Latest AI trends 2026"})
    print(f"Status: {res1['status']} | MU: {res1['marginal_utility']}")

    print("\n--- CrewAI Runaway Loop Simulation (5 Rapid Identical Searches) ---")
    for attempt in range(2, 8):
        res = crewai_guarded_tool_executor("researcher_agent", "web_search", {"query": "Latest AI trends 2026"})
        print(f"Attempt #{attempt}: Status: {res['status']} | MU: {res['marginal_utility']}")
