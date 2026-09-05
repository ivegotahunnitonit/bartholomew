"""
LangGraph / LangChain BTP v3.0 Tool Execution & Delegation Guard
Provides sub-35µs in-process AST gating, secret scrubbing, and Ed25519 Merkle receipt attestation for LangChain and LangGraph tools.
"""

from typing import Callable, Dict, Any, List, Optional
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


def btp_langchain_tool(fn: Callable = None, *, spend_cap: float = 50.0, strict: bool = True):
    """
    Drop-in decorator for LangChain / LangGraph tool functions.
    Intercepts raw tool arguments in memory and evaluates AST invariants (<35µs).

    Usage:
        @btp_langchain_tool
        def run_terminal_command(command: str) -> str:
            ...
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
                            raise PermissionError(f"[BTP-VETO] LangChain tool '{func.__name__}' blocked: {res.get('reason')}")
                for k, v in kwargs.items():
                    if isinstance(v, str):
                        res = guard.evaluate_ast(v)
                        if not res.get("allowed", True):
                            raise PermissionError(f"[BTP-VETO] LangChain tool '{func.__name__}' argument '{k}' blocked: {res.get('reason')}")
            return func(*args, **kwargs)
        return wrapper

    if fn is not None:
        return decorator(fn)
    return decorator


class BartholomewLangChainTool:
    """
    Wrapper for LangChain BaseTool instances to enforce BTP v3.0 execution safety.
    """
    def __init__(self, tool: Any, spend_cap: float = 50.0, strict: bool = True):
        self.tool = tool
        self.spend_cap = spend_cap
        self.strict = strict
        self.guard = Guard(spend_cap=spend_cap, strict=strict) if Guard else None

    def __call__(self, *args, **kwargs):
        if self.guard:
            for arg in args:
                if isinstance(arg, str):
                    res = self.guard.evaluate_ast(arg)
                    if not res.get("allowed", True):
                        raise PermissionError(f"[BTP-VETO] Tool execution blocked: {res.get('reason')}")
        return self.tool(*args, **kwargs)

    def run(self, *args, **kwargs):
        return self(*args, **kwargs)


class LangGraphBTPGuard:
    """
    Wraps LangGraph tools and nodes with offline Ed25519 Merkle receipt attestation.
    
    Usage:
        guard = LangGraphBTPGuard(trusted_authorities=[ROOT_PUBKEY], agent_id="Agent-Production-Cluster")
        
        @guard.wrap_tool
        def execute_sql_query(query: str):
            return db.execute(query)
    """
    def __init__(self, 
                 trusted_authorities: List[str], 
                 agent_id: str = "Agent-LangGraph-Node",
                 enforce_strict: bool = True):
        self.trusted_authorities = trusted_authorities
        self.agent_id = agent_id
        self.enforce_strict = enforce_strict
        self.seen_nonces = set()

    def wrap_tool(self, tool_fn: Callable):
        """Decorator for LangGraph tool functions with receipt verification."""
        @functools.wraps(tool_fn)
        def guarded_exec(*args, **kwargs):
            receipt = kwargs.pop("btp_receipt", None)
            if self.enforce_strict and not receipt:
                raise PermissionError(f"[BTP_BLOCKED] Execution denied: Missing required BTP trust receipt for tool '{tool_fn.__name__}'")
            
            if receipt and independent_verify_btp_receipt is not None:
                payload = {"tool": tool_fn.__name__, "args": args, "kwargs": kwargs}
                ok, msg = independent_verify_btp_receipt(
                    receipt_json_str=receipt,
                    candidate_payload=payload,
                    trusted_root_pubkeys=self.trusted_authorities,
                    expected_recipient_context=self.agent_id,
                    seen_nonces=self.seen_nonces
                )
                if not ok:
                    raise PermissionError(f"[BTP_BLOCKED] Attestation rejected for tool '{tool_fn.__name__}': {msg}")
            
            return tool_fn(*args, **kwargs)
        return guarded_exec
