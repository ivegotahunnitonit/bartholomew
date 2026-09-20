"""
Bartholomew + LangGraph Invariant Security Gate Example
======================================================
Demonstrates how to attach Bartholomew's sub-50 µs invariant validator
to any LangGraph StateGraph transition node.
"""

from typing import Dict, Any, TypedDict
import os
import sys

# Ensure repo root in sys.path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from src.trust_protocol import BartholomewTrustAuthority


class AgentState(TypedDict):
    task: str
    proposed_action: str
    payload: Dict[str, Any]
    is_safe: bool
    verdict_receipt: Dict[str, Any]


# 1. Initialize sovereign authority
authority = BartholomewTrustAuthority()


def btp_security_guard_node(state: AgentState) -> AgentState:
    """
    LangGraph Guard Node: Runs pre-execution AST & spend validation in <35 µs.
    """
    receipt = authority.evaluate_intent(
        agent_id="langgraph-worker-01",
        action_type=state["proposed_action"],
        payload=state["payload"]
    )
    
    verdict = receipt["attestation"]["verdict"]
    return {
        **state,
        "is_safe": (verdict == "ALLOW"),
        "verdict_receipt": receipt
    }


def execution_node(state: AgentState) -> AgentState:
    """LangGraph Action Node: Only executes if Bartholomew approved."""
    if not state["is_safe"]:
        print(f"[BLOCKED BY BTP] Dangerous action halted: {state['verdict_receipt']['attestation'].get('reason')}")
        return state
    
    print(f"[EXECUTING ACTION] Signed by Ed25519 Seal: {state['verdict_receipt']['signature'][:16]}...")
    return state


if __name__ == "__main__":
    print("--- 1. Testing Safe LangGraph Action ---")
    safe_state: AgentState = {
        "task": "Query user metrics",
        "proposed_action": "POSTGRES_QUERY",
        "payload": {"query": "SELECT count(*) FROM users WHERE status='active';"},
        "is_safe": False,
        "verdict_receipt": {}
    }
    guarded_safe = btp_security_guard_node(safe_state)
    execution_node(guarded_safe)

    print("\n--- 2. Testing Malicious LangGraph Action ---")
    bad_state: AgentState = {
        "task": "Clean database",
        "proposed_action": "POSTGRES_QUERY",
        "payload": {"query": "DROP TABLE users CASCADE;"},
        "is_safe": False,
        "verdict_receipt": {}
    }
    guarded_bad = btp_security_guard_node(bad_state)
    execution_node(guarded_bad)
