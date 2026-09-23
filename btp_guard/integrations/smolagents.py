"""
Bartholomew Guard for Hugging Face Smolagents (BTP v5.4.1)
==========================================================
Deterministic AST execution firewall for Smolagents CodeAgent and ToolCallingAgent.

Usage:
    from btp_guard.integrations.smolagents import BtpSmolagentsGuard

    guard = BtpSmolagentsGuard()
    guard.validate_code("import os; os.system('rm -rf /')")  # Raises PermissionError
"""

from typing import Any, Callable, Dict, Optional
from ..authorization_gate import AuthorizationGate


class BtpSmolagentsGuard:
    """AST Execution gate for Hugging Face Smolagents."""

    def __init__(
        self,
        strict: bool = True,
        agent_id: str = "smolagents-code-agent",
    ):
        self.agent_id = str(agent_id)
        self.gate = AuthorizationGate(policy={
            "strict": strict,
            "allow_destructive": False,
        })

    def validate_code(self, code_str: str) -> bool:
        """Validates proposed Python code before execution in smolagents CodeAgent."""
        from src.polyglot_ast_validator import PolyglotASTValidator

        is_safe, reason, _ = PolyglotASTValidator.validate_code(code_str, language="python")
        if not is_safe:
            raise PermissionError(f"[BTP-SMOLAGENTS-VETO]: Unsafe code execution blocked: {reason}")

        action = {
            "agent_id": self.agent_id,
            "action_type": "CODE_EXECUTION",
            "payload": {"command": code_str}
        }
        res = self.gate.evaluate(action)
        if res.get("verdict") == "DENY":
            raise PermissionError(f"[BTP-SMOLAGENTS-VETO]: Code execution blocked by policy: {res.get('reason')}")

        return True

    def wrap_tool(self, tool_fn: Callable[..., Any]) -> Callable[..., Any]:
        """Protects a tool callable used in Smolagents ToolCallingAgent."""
        t_name = getattr(tool_fn, "__name__", "smolagents_tool")

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cmd_str = " ".join(str(a) for a in args) + " " + " ".join(f"{k}={v}" for k, v in kwargs.items())
            action = {
                "agent_id": self.agent_id,
                "action_type": t_name,
                "payload": {"command": cmd_str}
            }
            res = self.gate.evaluate(action)
            if res.get("verdict") == "DENY":
                raise PermissionError(f"[BTP-SMOLAGENTS-VETO]: Tool '{t_name}' blocked: {res.get('reason')}")
            return tool_fn(*args, **kwargs)

        return wrapper
