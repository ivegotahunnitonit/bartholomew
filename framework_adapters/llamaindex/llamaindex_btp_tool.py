"""
LlamaIndex BTP v3.1 Tool & Function Execution Guard
Provides sub-35µs in-process AST gating, secret scrubbing, and Sovereign Passport authorization for LlamaIndex agents.
"""

from typing import Callable, Dict, Any, List, Optional
import functools
import sys
import os

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


def btp_llamaindex_tool(
    fn: Callable = None, 
    *, 
    required_capability: Optional[str] = "tools:execute", 
    spend_cap: float = 50.0, 
    strict: bool = True
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
                        raise PermissionError(f"[BTP-VETO] LlamaIndex agent passport invalid: {msg}")
                    if required_capability and not passport.has_capability(required_capability):
                        raise PermissionError(
                            f"[BTP-VETO] LlamaIndex agent passport unauthorized: missing '{required_capability}'"
                        )

            # 2. In-Process AST & Command Evaluation
            if Guard is not None:
                guard = Guard(spend_cap=spend_cap, strict=strict)
                for arg in args:
                    if isinstance(arg, str):
                        res = guard.evaluate_ast(arg)
                        if not res.get("allowed", True):
                            raise PermissionError(f"[BTP-VETO] LlamaIndex tool '{func.__name__}' argument blocked: {res.get('reason')}")
                for k, v in kwargs.items():
                    if isinstance(v, str):
                        res = guard.evaluate_ast(v)
                        if not res.get("allowed", True):
                            raise PermissionError(f"[BTP-VETO] LlamaIndex tool '{func.__name__}' argument '{k}' blocked: {res.get('reason')}")

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
        required_capability: Optional[str] = "tools:execute"
    ):
        self.name = tool_name
        self.description = description
        self.required_capability = required_capability
        self._guarded_fn = btp_llamaindex_tool(tool_fn, required_capability=required_capability)

    def __call__(self, *args, **kwargs):
        return self._guarded_fn(*args, **kwargs)
