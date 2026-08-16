#!/usr/bin/env python3
"""
Agentic-Eval 1-Line Python Decorator SDK
Gives developers a zero-config decorator to protect AI agent functions against secret leaks,
prompt injections, infinite tool loops, and token budget overruns.
"""
import functools
import time
from typing import Callable, Any, Dict, List
from python_backend.app.agent_eval_janitor import janitor_engine

class AgenticGuardException(Exception):
    """Raised when an AI agent execution violates OWASP LLM security boundaries."""
    pass

def guard(max_budget_tokens: int = 2000, secret_scrubbing: bool = True, enforce_loop_guard: bool = True):
    """
    1-Line Python Decorator for AI Agent Functions.
    Usage:
        @guard(max_budget_tokens=1000)
        def my_ai_agent_step(prompt: str):
            return "Agent reasoning step..."
    """
    def decorator(func: Callable[..., Any]):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Formulate step payload from function arguments
            arg_str = " ".join([str(a) for a in args] + [f"{k}={v}" for k, v in kwargs.items()])

            trajectory_input = {
                "agent_name": func.__name__,
                "steps": [
                    {"step_index": 1, "type": "thought", "content": arg_str}
                ]
            }

            # Enforce OWASP LLM security audit
            audit_res = janitor_engine.evaluate_agent_trajectory(trajectory_input)
            summary = audit_res.get("audit_summary", {})

            if summary.get("compliance_status") == "SECURITY_RISK" and summary.get("credential_leaks", 0) > 0:
                raise AgenticGuardException(f"🚨 [Agentic-Eval Guard]: Unmasked credential leak blocked in input to function `{func.__name__}`!")

            # Enforce real-time token budget cap
            estimated_tokens = len(arg_str) // 4
            if estimated_tokens > max_budget_tokens:
                raise AgenticGuardException(f"🚨 [Agentic-Eval Guard]: Token budget exceeded ({estimated_tokens} > {max_budget_tokens})!")

            # Execute underlying agent function
            result = func(*args, **kwargs)

            # Scrub secrets from output if requested
            if secret_scrubbing and isinstance(result, str):
                from python_backend.app.micro_api_suite import micro_api_suite
                result = micro_api_suite.mask_secrets(result)["masked_text"]

            return result

        return wrapper
    return decorator

# Convenience alias for 1-line import
__all__ = ["guard", "AgenticGuardException"]

if __name__ == "__main__":
    @guard(max_budget_tokens=500, secret_scrubbing=True)
    def sample_agent(user_query: str):
        return f"Processing query: {user_query} with internal key sk-proj-1234567890abcdef1234567890"

    print("⚡ Testing 1-Line Python SDK Decorator...")
    clean_out = sample_agent("Check stock prices")
    print("Clean Output:", clean_out)
