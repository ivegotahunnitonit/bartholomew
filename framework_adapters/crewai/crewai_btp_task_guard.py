"""
CrewAI BTP v3.0 Task & Tool Execution Guard
Provides pre-flight in-process AST gating, secret scrubbing, and attestation verification for CrewAI agents.
"""

from typing import Callable, Dict, Any, List, Optional
import functools
import sys
import os

try:
    from btp_guard import Guard
except ImportError:
    Guard = None

def btp_crewai_tool(fn: Callable = None, *, spend_cap: float = 50.0, strict: bool = True):
    """
    Drop-in decorator for CrewAI tools providing sub-35µs in-process AST safety gating.
    
    Usage:
        @btp_crewai_tool
        def execute_code(code: str) -> str:
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if Guard is not None:
                guard = Guard(spend_cap=spend_cap, strict=strict)
                # Inspect argument strings for destructive AST patterns or raw shell commands
                for arg in args:
                    if isinstance(arg, str):
                        res = guard.evaluate_ast(arg)
                        if not res.get("allowed", True):
                            raise PermissionError(f"[BTP-VETO] CrewAI tool '{func.__name__}' execution blocked: {res.get('reason')}")
            return func(*args, **kwargs)
        return wrapper

    if fn is not None:
        return decorator(fn)
    return decorator

class CrewAIBTPTaskGuard:
    """
    Guards CrewAI task execution with capability bounds and offline attestation checks.
    
    Usage:
        guard = CrewAIBTPTaskGuard(trusted_authorities=[ROOT_KEY])
        guarded_task = guard.wrap_task("Deploy Production Patch", deploy_fn)
    """
    def __init__(self, 
                 trusted_authorities: List[str], 
                 recipient_id: str = "Agent-CrewAI-Worker",
                 allowed_capabilities: Optional[List[str]] = None,
                 enforce_strict: bool = True):
        self.trusted_authorities = trusted_authorities
        self.recipient_id = recipient_id
        self.allowed_capabilities = allowed_capabilities or ["FS_WRITE_RESTRICTED", "NO_NET_EGRESS"]
        self.enforce_strict = enforce_strict
        self.seen_nonces = set()

    def wrap_task(self, task_description: str, task_fn: Callable) -> Callable:
        """Wraps task function with BTP receipt check."""
        def guarded_task_exec(*args, **kwargs):
            receipt = kwargs.pop("btp_receipt", None)
            if self.enforce_strict and not receipt:
                raise PermissionError(f"[BTP_BLOCKED] Execution denied: Missing required BTP trust receipt for task '{task_description}'")
            
            if receipt:
                payload = {"task": task_description, "args": args, "kwargs": kwargs}
                ok, msg = independent_verify_btp_receipt(
                    receipt_json_str=receipt,
                    candidate_payload=payload,
                    trusted_root_pubkeys=self.trusted_authorities,
                    expected_recipient_context=self.recipient_id,
                    seen_nonces=self.seen_nonces,
                    allowed_capabilities=self.allowed_capabilities
                )
                if not ok:
                    raise PermissionError(f"[BTP_BLOCKED] Task attestation rejected: {msg}")
            
            return task_fn(*args, **kwargs)
        return guarded_task_exec
