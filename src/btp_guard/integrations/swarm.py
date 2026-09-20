"""
Bartholomew Guard for OpenAI Swarm & Agents SDK (BTP v5.4.1)
============================================================
Enforces deterministic tool limits, pre-flight safety gates, and cross-agent handoff invariants.

Usage:
    from btp_guard.integrations.swarm import BtpSwarmGuard

    guard = BtpSwarmGuard(spend_cap=25.0)
    protected_tool = guard.protect_tool(my_tool_function)
"""

from typing import Any, Callable, Dict, Optional
from ..authorization_gate import AuthorizationGate
from ..errors import AuthorizationError


class BtpSwarmGuard:
    """Wrapper and guard for OpenAI Swarm tool dispatch and handoffs."""

    def __init__(
        self,
        spend_cap: float = 50.0,
        strict: bool = True,
        agent_id: str = "openai-swarm-agent",
    ):
        self.spend_cap = float(spend_cap)
        self.agent_id = str(agent_id)
        self.gate = AuthorizationGate(policy={
            "max_spend_usd": self.spend_cap,
            "strict": strict,
            "allow_destructive": False,
        })

    def protect_tool(self, tool_fn: Callable[..., Any], tool_name: Optional[str] = None) -> Callable[..., Any]:
        """Wraps an individual Swarm tool with pre-flight AST and policy verification."""
        t_name = tool_name or getattr(tool_fn, "__name__", "swarm_tool")

        def wrapped(*args: Any, **kwargs: Any) -> Any:
            cmd_str = " ".join(str(a) for a in args) + " " + " ".join(f"{k}={v}" for k, v in kwargs.items())
            action = {
                "agent_id": self.agent_id,
                "action_type": t_name,
                "payload": {
                    "command": cmd_str,
                    "amount_usd": kwargs.get("amount_usd", 0.0),
                }
            }
            res = self.gate.evaluate(action)
            if res.get("verdict") == "DENY":
                raise PermissionError(f"[BTP-SWARM-VETO]: Tool '{t_name}' blocked: {res.get('reason', 'Policy violation')}")
            return tool_fn(*args, **kwargs)

        return wrapped

    def validate_handoff(self, from_agent: str, to_agent: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Validates swarm handoff between agents."""
        action = {
            "agent_id": from_agent,
            "action_type": "SWARM_HANDOFF",
            "payload": {
                "from_agent": from_agent,
                "to_agent": to_agent,
                "context": context or {}
            }
        }
        res = self.gate.evaluate(action)
        if res.get("verdict") == "DENY":
            raise PermissionError(f"[BTP-SWARM-HANDOFF-VETO]: Handoff from '{from_agent}' to '{to_agent}' denied.")
        return True
