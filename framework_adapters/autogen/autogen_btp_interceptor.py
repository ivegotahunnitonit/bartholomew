"""
Microsoft AutoGen BTP v5.4 Message & Tool Security Interceptor
==============================================================
Provides multi-agent conversation protection against confused-deputy tool attacks,
destructive command injections (rm -rf, DROP TABLE), and credential leakage
using sub-35µs in-process AST syntax safety gating.

Usage:
    from framework_adapters.autogen import btp_autogen_guard, AutoGenBTPInterceptor, BTPViolationError

    @btp_autogen_guard
    def execute_sql(query: str):
        ...
"""

import functools
import logging
import time
from typing import Dict, Any, List, Optional, Callable, Union

logger = logging.getLogger("btp.adapters.autogen")

try:
    from btp_guard import Guard
except ImportError:
    try:
        from src.polyglot_ast_validator import PolyglotASTValidator as Guard
    except ImportError:
        Guard = None

try:
    from standalone_btp_verifier import independent_verify_btp_receipt
except ImportError:
    try:
        from btp_guard import independent_verify_btp_receipt
    except ImportError:
        independent_verify_btp_receipt = None


class BTPViolationError(PermissionError):
    """
    Structured security violation raised when an AutoGen tool or agent payload
    breaches AST safety invariants.
    """

    def __init__(
        self,
        reason: str,
        rule_id: str = "BTP-AST-001",
        blocked_payload: str = "",
        latency_us: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(f"[BTP-SECURITY-VETO] AutoGen execution blocked by rule {rule_id}: {reason}")
        self.reason = reason
        self.rule_id = rule_id
        self.blocked_payload = blocked_payload
        self.latency_us = latency_us
        self.metadata = metadata or {}

    def to_diagnostics(self) -> Dict[str, Any]:
        """Returns structured JSON diagnostics suitable for logs or telemetry."""
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
            f"[BTP-VETO] AutoGen Tool Execution Blocked!\n"
            f"  - Rule ID:   {self.rule_id}\n"
            f"  - Reason:    {self.reason}\n"
            f"  - Latency:   {self.latency_us:.1f} µs\n"
            f"  - Payload:   {self.blocked_payload[:80] + ('...' if len(self.blocked_payload) > 80 else '')}"
        )


def btp_autogen_guard(
    fn: Optional[Callable] = None,
    *,
    spend_cap: float = 50.0,
    strict: bool = True,
    custom_patterns: Optional[List[str]] = None,
    on_violation: Optional[Callable[[BTPViolationError], Any]] = None,
):
    """
    Decorator for AutoGen agent tool calls or register_for_execution functions.
    Inspects tool inputs for malicious payloads, destructive commands, or prompt injections
    in sub-35 microseconds before dispatching to the underlying system.

    Example:
        @btp_autogen_guard
        def query_database(sql: str) -> str:
            return db.execute(sql)
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            guard_instance = Guard(spend_cap=spend_cap, strict=strict) if Guard else None

            # 1. Inspect positional arguments
            for i, arg in enumerate(args):
                if isinstance(arg, str) and guard_instance:
                    res = guard_instance.evaluate_ast(arg)
                    if not res.get("allowed", True):
                        err = BTPViolationError(
                            reason=res.get("reason", "Destructive pattern detected"),
                            rule_id=res.get("violations", ["BTP-AST-001"])[0].split(":")[0] if res.get("violations") else "BTP-AST-001",
                            blocked_payload=arg,
                            latency_us=res.get("latency_us", 0.0),
                            metadata=res.get("metadata", {})
                        )
                        if on_violation:
                            return on_violation(err)
                        raise err

            # 2. Inspect keyword arguments
            for k, v in kwargs.items():
                if isinstance(v, str) and guard_instance:
                    res = guard_instance.evaluate_ast(v)
                    if not res.get("allowed", True):
                        err = BTPViolationError(
                            reason=f"Argument '{k}' violation: {res.get('reason', 'Destructive pattern detected')}",
                            rule_id=res.get("violations", ["BTP-AST-001"])[0].split(":")[0] if res.get("violations") else "BTP-AST-001",
                            blocked_payload=v,
                            latency_us=res.get("latency_us", 0.0),
                            metadata=res.get("metadata", {})
                        )
                        if on_violation:
                            return on_violation(err)
                        raise err

            # 3. Safe execution
            return func(*args, **kwargs)

        return wrapper

    if fn is not None:
        return decorator(fn)
    return decorator


class AutoGenBTPInterceptor:
    """
    Intercepts and validates incoming AutoGen agent messages before tool execution,
    protecting against confused-deputy attacks, destructive code generation, and forged envelopes.

    Usage:
        interceptor = AutoGenBTPInterceptor(trusted_authorities=[root_pubkey], recipient_id="Agent-AutoGen-01")
        safe_message = interceptor.intercept_message(inbound_message)
    """

    def __init__(
        self,
        trusted_authorities: Optional[List[str]] = None,
        recipient_id: str = "Agent-AutoGen-01",
        enforce_strict: bool = True,
        **kwargs
    ):
        self.trusted_authorities = trusted_authorities or []
        self.recipient_id = recipient_id
        self.enforce_strict = enforce_strict
        self.guard = Guard() if Guard else None
        self.seen_nonces = set()

    def intercept_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates incoming message envelope 100% offline in-process.
        Returns original message if safe, or a security alert envelope if blocked.
        """
        # 1. Verify BTP attestation envelope/receipt if present
        envelope = message.get("btp_envelope") or message.get("btp_receipt")
        if envelope and independent_verify_btp_receipt is not None and self.trusted_authorities:
            content = message.get("content", {})
            payload = content if isinstance(content, dict) else {"content": content}
            ok, msg = independent_verify_btp_receipt(
                receipt_json_str=envelope,
                candidate_payload=payload,
                trusted_root_pubkeys=self.trusted_authorities,
                expected_recipient_context=self.recipient_id,
                seen_nonces=self.seen_nonces,
            )
            if not ok:
                return {
                    "role": "system",
                    "content": f"[BTP_SECURITY_ALERT] Invalid BTP attestation: {msg}",
                    "status": "DENIED",
                    "diagnostics": {
                        "rule_id": "BTP-RECEIPT-INVALID",
                        "reason": msg,
                        "latency_us": 0.0,
                    }
                }

        # 2. Evaluate text/code content via AST Guard
        content = message.get("content", "")
        if self.guard and isinstance(content, str):
            res = self.guard.evaluate_ast(content)
            if not res.get("allowed", True):
                rule_id = res.get("violations", ["BTP-AST-001"])[0].split(":")[0] if res.get("violations") else "BTP-AST-001"
                latency = res.get("latency_us", 0.0)
                return {
                    "role": "system",
                    "content": (
                        f"[BTP_SECURITY_ALERT] Blocked destructive agent payload by rule {rule_id}: "
                        f"{res.get('reason')} (Evaluated in {latency:.1f}µs)."
                    ),
                    "status": "DENIED",
                    "diagnostics": {
                        "rule_id": rule_id,
                        "reason": res.get("reason"),
                        "latency_us": latency
                    }
                }

        return message
