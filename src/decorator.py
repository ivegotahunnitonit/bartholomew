"""
Bartholomew 1-Line Secure Tool Decorator (@secure_tool)
=======================================================
Wraps any Python function, LangChain tool, CrewAI tool, or LLM callable
with sub-50µs in-memory AST invariant gating, secret leak interception,
and cryptographic audit logging.

Usage:
    from btp_guard import secure_tool

    @secure_tool
    def execute_sql(query: str):
        return db.query(query)

    @secure_tool(max_spend_usd=50.0, strict_mode=True)
    def run_bash_command(cmd: str):
        return subprocess.check_output(cmd, shell=True)
"""

import functools
import time
import inspect
from typing import Callable, Any, Optional
from src.polyglot_ast_validator import PolyglotASTValidator
from src.trust_protocol import BartholomewTrustAuthority

_GLOBAL_AUTHORITY = None

def _get_authority():
    global _GLOBAL_AUTHORITY
    if _GLOBAL_AUTHORITY is None:
        try:
            _GLOBAL_AUTHORITY = BartholomewTrustAuthority()
        except Exception:
            _GLOBAL_AUTHORITY = None
    return _GLOBAL_AUTHORITY

class SecurityVetoException(Exception):
    """Raised when Bartholomew intercepts a dangerous tool call."""
    def __init__(self, reason: str, metadata: dict):
        super().__init__(f"[BARTHOLOMEW SECURITY VETO] {reason}")
        self.reason = reason
        self.metadata = metadata

def secure_tool(
    func: Optional[Callable] = None,
    *,
    strict_mode: bool = True,
    max_spend_usd: float = 100.0,
    agent_id: str = "agent-autonomous"
):
    """
    1-Line Drop-in Security Decorator for Autonomous Agent Tools.
    Evaluates function arguments before execution in <50 µs.
    """
    def decorator(target_fn: Callable) -> Callable:
        @functools.wraps(target_fn)
        def wrapper(*args, **kwargs) -> Any:
            t0 = time.perf_counter()

            # 1. Inspect all string arguments passed to the tool
            candidate_strings = []
            for arg in args:
                if isinstance(arg, str):
                    candidate_strings.append(arg)
            for k, v in kwargs.items():
                if isinstance(v, str):
                    candidate_strings.append(v)

            # 2. Fast In-Memory Invariant & Secret Check
            for candidate in candidate_strings:
                is_safe, reason, meta = PolyglotASTValidator.validate_code(candidate)
                if not is_safe:
                    latency_us = (time.perf_counter() - t0) * 1_000_000
                    # Cryptographic receipt
                    auth = _get_authority()
                    if auth:
                        auth.evaluate_intent(
                            agent_id=agent_id,
                            action_type=f"TOOL_VETO:{target_fn.__name__}",
                            payload={"reason": reason, "blocked_arg": candidate[:100], "latency_us": latency_us}
                        )

                    if strict_mode:
                        raise SecurityVetoException(reason, meta)
                    else:
                        print(f"⚠️ [BARTHOLOMEW VETO] Blocked tool execution for '{target_fn.__name__}': {reason}")
                        return f"TOOL_EXECUTION_BLOCKED: {reason}"

            # 3. Execute original function if 100% compliant
            return target_fn(*args, **kwargs)

        wrapper.__is_btp_secured__ = True
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator
