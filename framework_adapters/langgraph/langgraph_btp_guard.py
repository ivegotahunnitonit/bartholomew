"""
LangGraph / LangChain BTP v2.2 Tool Delegation Guard
Provides 1-line cryptographic execution protection for LangGraph agent tools.
"""

from typing import Callable, Dict, Any, List, Optional
import sys
import os

try:
    from standalone_btp_verifier import independent_verify_btp_receipt
except ImportError:
    from btp_guard import independent_verify_btp_receipt

class LangGraphBTPGuard:
    """
    Wraps LangGraph tools with offline Ed25519 attestation verification.
    
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
        """Decorator for LangGraph / LangChain tool functions."""
        def guarded_exec(*args, **kwargs):
            receipt = kwargs.pop("btp_receipt", None)
            if self.enforce_strict and not receipt:
                raise PermissionError(f"[BTP_BLOCKED] Execution denied: Missing required BTP trust receipt for tool '{tool_fn.__name__}'")
            
            if receipt:
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
