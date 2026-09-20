"""
Bartholomew Guard for LangChain & LangGraph (BTP v1.0.0)
=========================================================
First-class CallbackHandler and Tool Decorator providing sub-35µs AST gating,
spend caps, and cryptographic execution receipts for LangChain and LangGraph swarms.

Usage:
    from btp_guard.integrations.langchain import BtpCallbackHandler, BtpToolGuard

    # 1. As a global agent / graph callback:
    agent = create_react_agent(model, tools, callbacks=[BtpCallbackHandler(spend_cap=25.0)])

    # 2. Or wrap individual tools:
    @BtpToolGuard(spend_cap=10.0)
    def execute_sql(query: str): ...
"""

import functools
from typing import Any, Dict, Optional
from ..authorization_gate import AuthorizationGate


class BtpCallbackHandler:
    """LangChain & LangGraph Callback Handler for pre-flight tool execution inspection."""

    def __init__(
        self,
        spend_cap: float = 100.0,
        strict: bool = True,
        agent_id: str = "langchain-agent",
    ):
        self.spend_cap = float(spend_cap)
        self.agent_id = str(agent_id)
        self.current_spend = 0.0
        self.gate = AuthorizationGate(policy={
            "max_spend_usd": self.spend_cap,
            "strict": strict,
            "allow_destructive": False,
        })

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        """Pre-flight check executed immediately before a LangChain tool runs."""
        tool_name = serialized.get("name", "langchain_tool") if isinstance(serialized, dict) else "langchain_tool"
        
        # Check spend estimate
        estimated_cost = float(kwargs.get("cost_usd", 0.0) or 0.0)
        
        action = {
            "agent_id": self.agent_id,
            "action_type": tool_name,
            "payload": {
                "command": str(input_str),
                "query": str(input_str),
                "amount_usd": self.current_spend + estimated_cost,
            }
        }
        res = self.gate.evaluate(action)

        if res.get("verdict") == "DENY":
            rule_id = res.get("rule_id", "BTP-AST-001")
            reason = res.get("reason", "Action blocked by security policy")
            raise PermissionError(f"[{rule_id}] LangChain tool '{tool_name}' BLOCKED: {reason}")

        self.current_spend += estimated_cost
        return res


def BtpToolGuard(spend_cap: float = 50.0, strict: bool = True):
    """Decorator to protect LangChain tool functions with sub-35µs AST safety gating."""
    gate = AuthorizationGate(policy={
        "max_spend_usd": float(spend_cap),
        "strict": strict,
        "allow_destructive": False,
    })

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            payload_str = " ".join(str(a) for a in args) + " " + " ".join(f"{k}={v}" for k, v in kwargs.items())
            action = {
                "agent_id": "guarded-tool",
                "action_type": fn.__name__,
                "payload": {
                    "command": payload_str,
                    "query": payload_str,
                    "amount_usd": float(kwargs.get("amount_usd", 0.0) or 0.0),
                }
            }
            res = gate.evaluate(action)
            if res.get("verdict") == "DENY":
                rule = res.get("rule_id", "BTP-AST-001")
                reason = res.get("reason", "Security policy violation")
                raise PermissionError(f"[{rule}] Function '{fn.__name__}' BLOCKED by Bartholomew: {reason}")

            return fn(*args, **kwargs)
        return wrapper
    return decorator
