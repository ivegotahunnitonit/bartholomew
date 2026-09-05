"""
Microsoft AutoGen BTP v3.0 Message & Tool Interceptor
Provides multi-agent conversation protection against confused-deputy tool attacks,
AST syntax safety gating, and offline Merkle receipt attestation.
"""

from typing import Dict, Any, List, Optional, Callable
import functools
import sys
import os

try:
    from btp_guard import Guard
except ImportError:
    Guard = None

try:
    from standalone_btp_verifier import independent_verify_btp_receipt
except ImportError:
    try:
        from btp_guard import independent_verify_btp_receipt
    except ImportError:
        independent_verify_btp_receipt = None


def btp_autogen_guard(fn: Callable = None, *, spend_cap: float = 50.0, strict: bool = True):
    """
    Decorator for AutoGen agent tool calls or register_for_execution functions.
    Inspects tool inputs for malicious payload / command injection prior to dispatch.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if Guard is not None:
                guard = Guard(spend_cap=spend_cap, strict=strict)
                for arg in args:
                    if isinstance(arg, str):
                        res = guard.evaluate_ast(arg)
                        if not res.get("allowed", True):
                            raise PermissionError(f"[BTP-VETO] AutoGen tool '{func.__name__}' execution blocked: {res.get('reason')}")
                for k, v in kwargs.items():
                    if isinstance(v, str):
                        res = guard.evaluate_ast(v)
                        if not res.get("allowed", True):
                            raise PermissionError(f"[BTP-VETO] AutoGen tool '{func.__name__}' argument '{k}' blocked: {res.get('reason')}")
            return func(*args, **kwargs)
        return wrapper

    if fn is not None:
        return decorator(fn)
    return decorator


class AutoGenBTPInterceptor:
    """
    Intercepts and validates incoming AutoGen agent messages before tool execution.
    
    Usage:
        interceptor = AutoGenBTPInterceptor(trusted_authorities=[ROOT_KEY])
        safe_msg = interceptor.intercept_message(inbound_message)
    """
    def __init__(self, 
                 trusted_authorities: List[str] = None, 
                 recipient_id: str = "Agent-AutoGen-Worker",
                 enforce_strict: bool = True):
        self.trusted_authorities = trusted_authorities or []
        self.recipient_id = recipient_id
        self.enforce_strict = enforce_strict
        self.seen_nonces = set()
        self.guard = Guard() if Guard else None

    def intercept_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Validates incoming message envelope 100% offline."""
        content = message.get("content", "")
        
        # 1. AST Invariant Check on raw content if text command
        if self.guard and isinstance(content, str):
            res = self.guard.evaluate_ast(content)
            if not res.get("allowed", True):
                return {
                    "role": "system",
                    "content": f"[BTP_SECURITY_ALERT] Blocked destructive agent payload: {res.get('reason')}",
                    "status": "DENIED"
                }

        # 2. Offline cryptographic receipt verification if envelope present
        if "btp_envelope" in message:
            envelope = message["btp_envelope"]
            payload = message.get("content", {})
            if independent_verify_btp_receipt is not None and self.trusted_authorities:
                ok, msg = independent_verify_btp_receipt(
                    receipt_json_str=envelope,
                    candidate_payload=payload,
                    trusted_root_pubkeys=self.trusted_authorities,
                    expected_recipient_context=self.recipient_id,
                    seen_nonces=self.seen_nonces
                )
                if not ok:
                    return {
                        "role": "system",
                        "content": f"[BTP_SECURITY_ALERT] Inbound message attestation failed: {msg}. Execution halted.",
                        "status": "DENIED"
                    }
        elif self.enforce_strict and message.get("action_type") in ["EXEC_COMMAND", "DEPLOY_PATCH", "SQL_EXEC"]:
            return {
                "role": "system",
                "content": "[BTP_SECURITY_ALERT] Unattested high-privilege action rejected.",
                "status": "DENIED"
            }
        return message
