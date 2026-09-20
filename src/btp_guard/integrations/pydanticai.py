"""
Bartholomew Guard for PydanticAI (BTP v5.4.1)
=============================================
Type-safe runtime guard for PydanticAI agents, dependency injection, and tool functions.

Usage:
    from btp_guard.integrations.pydanticai import BtpPydanticAIGuard

    guard = BtpPydanticAIGuard(spend_cap=100.0)
    @guard.tool
    def search_database(query: str):
        ...
"""

from typing import Any, Callable, Dict, Optional
from ..authorization_gate import AuthorizationGate


class BtpPydanticAIGuard:
    """Type-safe guard for PydanticAI agent tools."""

    def __init__(
        self,
        spend_cap: float = 100.0,
        strict: bool = True,
        agent_id: str = "pydanticai-agent",
    ):
        self.spend_cap = float(spend_cap)
        self.agent_id = str(agent_id)
        self.gate = AuthorizationGate(policy={
            "max_spend_usd": self.spend_cap,
            "strict": strict,
            "allow_destructive": False,
        })

    def tool(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator for PydanticAI tool functions."""
        tool_name = getattr(fn, "__name__", "pydanticai_tool")

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            call_dict = {}
            for k, v in kwargs.items():
                if hasattr(v, "model_dump"):
                    call_dict[k] = v.model_dump()
                elif hasattr(v, "dict"):
                    call_dict[k] = v.dict()
                else:
                    call_dict[k] = str(v)

            cmd_str = " ".join(str(a) for a in args) + " " + " ".join(f"{k}={v}" for k, v in call_dict.items())
            action = {
                "agent_id": self.agent_id,
                "action_type": tool_name,
                "payload": {
                    "command": cmd_str,
                    "amount_usd": kwargs.get("amount_usd", 0.0),
                    **call_dict
                }
            }
            res = self.gate.evaluate(action)
            if res.get("verdict") == "DENY":
                raise PermissionError(f"[BTP-PYDANTIC-VETO]: Tool '{tool_name}' blocked: {res.get('reason', 'Policy violation')}")

            return fn(*args, **kwargs)

        return wrapper
