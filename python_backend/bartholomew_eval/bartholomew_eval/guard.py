"""
bartholomew_eval.guard
======================
1-Line Python Decorator for AI Agent Trajectory Security & OWASP LLM Boundary Protection.
"""

from __future__ import annotations

import functools
from typing import Any, Callable, Dict, Optional, TypeVar, Union

from .engine import BartholomewEngine

F = TypeVar("F", bound=Callable[..., Any])


class GuardViolation(Exception):
    """Raised when an AI agent execution violates OWASP LLM security boundaries or token caps."""

    def __init__(self, message: str, audit_summary: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.audit_summary = audit_summary or {}


def guard(
    max_budget_tokens: int = 2000,
    secret_scrubbing: bool = True,
    enforce_loop_guard: bool = True,
    self_healing: bool = True,
    agent_name: Optional[str] = None,
    engine: Optional[BartholomewEngine] = None,
) -> Callable[[F], F]:
    """
    1-Line Python Decorator for AI Agent Functions with Self-Healing Recovery.

    Usage:
        from bartholomew_eval import guard

        @guard(max_budget_tokens=1000, self_healing=True)
        def my_agent_step(query: str) -> str:
            return agent.run(query)
    """
    auditor = engine or BartholomewEngine()

    def decorator(func: F) -> F:
        target_name = agent_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            arg_strs = [str(a) for a in args] + [f"{k}={v}" for k, v in kwargs.items()]
            payload_str = " ".join(arg_strs)

            trajectory_input = {
                "agent_name": target_name,
                "steps": [{"step_index": 1, "type": "thought", "content": payload_str}],
            }

            audit_res = auditor.evaluate_trajectory(trajectory_input, agent_name=target_name)
            summary = audit_res.get("audit_summary", {})

            if summary.get("compliance_status") == "SECURITY_RISK" and summary.get("credential_leaks", 0) > 0:
                raise GuardViolation(
                    f"[Bartholomew Guard]: Credential leak blocked in function `{target_name}`!",
                    audit_summary=summary,
                )

            if summary.get("prompt_injections", 0) > 0:
                raise GuardViolation(
                    f"[Bartholomew Guard]: Prompt injection attempt blocked in function `{target_name}`!",
                    audit_summary=summary,
                )

            estimated_tokens = max(1, len(payload_str) // 4)
            if estimated_tokens > max_budget_tokens:
                raise GuardViolation(
                    f"🚨 [Bartholomew Guard]: Token budget cap exceeded ({estimated_tokens} > {max_budget_tokens})!",
                    audit_summary=summary,
                )

            try:
                result = func(*args, **kwargs)
            except Exception as ex:
                if self_healing:
                    healing_log = auditor.self_healing.heal_execution_failure(target_name, args, kwargs, ex)
                    result = healing_log["fallback_response"]
                else:
                    raise ex

            if secret_scrubbing and isinstance(result, str):
                result, _ = auditor.scrub_secrets(result)

            return result

        return wrapper  # type: ignore[return-value]

    return decorator
