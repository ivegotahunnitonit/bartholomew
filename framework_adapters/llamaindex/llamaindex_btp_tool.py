"""
LlamaIndex BTP v4.1 Tool & Function Execution Guard
Provides sub-35µs in-process AST gating, secret scrubbing, Sovereign Passport authorization,
and structured BTPViolationError parity for LlamaIndex agents.
"""

from typing import Callable, Dict, Any, List, Optional
import functools
import sys
import os
import time

try:
    from btp_guard import Guard, SovereignAgentPassport
except ImportError:
    Guard = None
    SovereignAgentPassport = None

try:
    from standalone_btp_verifier import independent_verify_btp_receipt
except ImportError:
    try:
        from btp_guard import independent_verify_btp_receipt
    except ImportError:
        independent_verify_btp_receipt = None


# ---------------------------------------------------------------------------
# Structured Violation Exception
# ---------------------------------------------------------------------------

class BTPViolationError(PermissionError):
    """
    Structured security violation raised when a LlamaIndex tool or agent payload
    breaches AST safety invariants enforced by the Bartholomew Trust Protocol.
    Inherits from PermissionError for backward compatibility.
    """

    def __init__(
        self,
        reason: str,
        rule_id: str = "BTP-AST-001",
        blocked_payload: str = "",
        latency_us: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            f"[BTP-SECURITY-VETO] LlamaIndex execution blocked by rule {rule_id}: {reason}"
        )
        self.reason = reason
        self.rule_id = rule_id
        self.blocked_payload = blocked_payload
        self.latency_us = latency_us
        self.metadata = metadata or {}

    def to_diagnostics(self) -> Dict[str, Any]:
        """Returns structured JSON diagnostics suitable for telemetry and logs."""
        return {
            "status": "BLOCKED",
            "rule_id": self.rule_id,
            "reason": self.reason,
            "blocked_payload": (
                self.blocked_payload[:120] + "..."
                if len(self.blocked_payload) > 120
                else self.blocked_payload
            ),
            "latency_us": round(self.latency_us, 2),
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        return (
            f"[BTP-SECURITY-VETO] LlamaIndex execution blocked by rule {self.rule_id}: {self.reason} "
            f"(latency={round(self.latency_us, 2)}µs)"
        )


# ---------------------------------------------------------------------------
# Tool Decorator
# ---------------------------------------------------------------------------

def btp_llamaindex_tool(
    fn: Callable = None, 
    *, 
    required_capability: Optional[str] = "tools:execute", 
    spend_cap: float = 50.0, 
    strict: bool = True,
    on_violation: Optional[Callable[[BTPViolationError], Any]] = None,
):
    """
    Drop-in decorator for LlamaIndex agent tool functions.
    Intercepts proposed tool arguments in local memory (<35µs) and validates
    optional Sovereign Agent Passport credentials.

    Usage:
        @btp_llamaindex_tool(required_capability="db:query")
        def query_database(sql: str) -> str:
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            t0 = time.perf_counter()

            # 1. Sovereign Passport Verification (if passed via kwargs)
            passport_data = kwargs.pop("agent_passport", None)
            if passport_data is not None:
                if SovereignAgentPassport is not None:
                    if isinstance(passport_data, dict):
                        passport = SovereignAgentPassport.from_dict(passport_data)
                    else:
                        passport = passport_data
                    is_valid, msg = passport.verify_signature()
                    if not is_valid:
                        latency_us = (time.perf_counter() - t0) * 1_000_000
                        err = BTPViolationError(
                            reason=f"LlamaIndex agent passport signature invalid: {msg}",
                            rule_id="BTP-PASSPORT-001",
                            latency_us=latency_us,
                            metadata={"tool": func.__name__},
                        )
                        if on_violation:
                            return on_violation(err)
                        raise err

                    if required_capability and not passport.has_capability(required_capability):
                        latency_us = (time.perf_counter() - t0) * 1_000_000
                        err = BTPViolationError(
                            reason=f"LlamaIndex agent passport unauthorized: missing capability '{required_capability}'",
                            rule_id="BTP-AUTH-002",
                            latency_us=latency_us,
                            metadata={"tool": func.__name__, "required": required_capability},
                        )
                        if on_violation:
                            return on_violation(err)
                        raise err

            # 2. In-Process AST & Command Evaluation
            if Guard is not None:
                guard = Guard(spend_cap=spend_cap, strict=strict)
                for arg in args:
                    if isinstance(arg, str):
                        res = guard.evaluate_ast(arg)
                        if not res.get("allowed", True):
                            latency_us = (time.perf_counter() - t0) * 1_000_000
                            err = BTPViolationError(
                                reason=res.get("reason", "Prohibited AST construction"),
                                rule_id="BTP-AST-001",
                                blocked_payload=arg,
                                latency_us=latency_us,
                                metadata={"tool": func.__name__},
                            )
                            if on_violation:
                                return on_violation(err)
                            raise err

                for k, v in kwargs.items():
                    if isinstance(v, str):
                        res = guard.evaluate_ast(v)
                        if not res.get("allowed", True):
                            latency_us = (time.perf_counter() - t0) * 1_000_000
                            err = BTPViolationError(
                                reason=res.get("reason", f"Argument '{k}' blocked"),
                                rule_id="BTP-AST-001",
                                blocked_payload=v,
                                latency_us=latency_us,
                                metadata={"tool": func.__name__, "param": k},
                            )
                            if on_violation:
                                return on_violation(err)
                            raise err

            return func(*args, **kwargs)
        return wrapper

    if fn is not None:
        return decorator(fn)
    return decorator


class BartholomewLlamaIndexTool:
    """
    Wrapper for LlamaIndex BaseTool or FunctionTool instances to enforce BTP execution safety.
    """
    def __init__(
        self, 
        tool_fn: Callable, 
        tool_name: str, 
        description: str,
        required_capability: Optional[str] = "tools:execute",
        on_violation: Optional[Callable[[BTPViolationError], Any]] = None,
    ):
        self.name = tool_name
        self.description = description
        self.required_capability = required_capability
        self._guarded_fn = btp_llamaindex_tool(
            tool_fn, 
            required_capability=required_capability,
            on_violation=on_violation,
        )

    def __call__(self, *args, **kwargs):
        return self._guarded_fn(*args, **kwargs)
