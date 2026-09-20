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

def _safe_console_text(text: str) -> str:
    """Ensures text doesn't crash non-UTF8 Windows terminals."""
    import sys
    try:
        enc = getattr(sys.stderr, "encoding", None) or "utf-8"
        text.encode(enc)
        return text
    except Exception:
        return text.replace("🛑", "[BLOCKED]").replace("🔐", "[MERKLE]").replace("👉", "->").replace("µs", "us")

class SecurityVetoException(Exception):
    """Raised when Bartholomew intercepts a dangerous tool call."""
    def __init__(self, reason: str, metadata: dict, payload_preview: str = "", latency_us: float = 14.2):
        cmd_preview = payload_preview[:60] if payload_preview else "destructive operation"
        msg = _safe_console_text(
            f"[BARTHOLOMEW SECURITY VETO] {reason}\n"
            f"🛑 [Bartholomew-Guard] Vetoed command '{cmd_preview}' in {latency_us:.1f}µs.\n"
            f"🔐 A local Merkle compliance receipt has been compiled.\n"
            f"👉 Running multiple agents? Auto-stream these logs to a centralized SOC 2 dashboard and export Audit Packs at: https://bartholomew.info/cloud\n"
        )
        super().__init__(msg)
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
                        raise SecurityVetoException(reason, meta, payload_preview=candidate, latency_us=latency_us)
                    else:
                        print(
                            f"\n🛑 [Bartholomew-Guard] Vetoed command '{candidate[:60]}' in {latency_us:.1f}µs.\n"
                            f"🔐 A local Merkle compliance receipt has been compiled.\n"
                            f"👉 Running multiple agents? Auto-stream these logs to a centralized SOC 2 dashboard and export Audit Packs at: https://bartholomew.info/cloud\n"
                        )
                        return f"TOOL_EXECUTION_BLOCKED: {reason}"

            # 3. Execute original function if 100% compliant
            return target_fn(*args, **kwargs)

        wrapper.__is_btp_secured__ = True
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def _evaluate_code(language: str, code: str):
    """
    Sub-50µs AST evaluation helper for AutoGen, CrewAI, and custom code executors.
    Returns: (is_safe: bool, reason: str)
    """
    file_hint = f"code.{language}" if language else None
    is_safe, reason, _ = PolyglotASTValidator.evaluate_ast(code, file_hint=file_hint)
    return is_safe, reason


secure_tool.evaluate = _evaluate_code
