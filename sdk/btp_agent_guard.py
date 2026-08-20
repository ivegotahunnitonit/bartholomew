"""
BTP Agent Guard (Universal Framework Middleware for Autonomous Systems)
Enables 1-line cryptographic trust validation for:
- LangChain / LangGraph
- Microsoft AutoGen
- CrewAI
- LlamaIndex
"""

import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Callable, Union, Set
from src.rfc8785 import rfc8785_canonicalize
from standalone_btp_verifier import independent_verify_btp_receipt
from src.trust_protocol import BartholomewTrustAuthority

class BTPGuard:
    """
    Universal 1-Line Cryptographic Guard for Agent Frameworks.
    
    Usage:
        guard = BTPGuard(trusted_authorities=[ROOT_KEY], agent_id="Agent-Production-Worker")
        
        # 1. LangGraph / LangChain Tool Wrapper
        @guard.wrap_tool
        def execute_migration(sql_query: str):
            ...
            
        # 2. AutoGen Message Interceptor
        safe_msg = guard.intercept_autogen_message(incoming_packet)
    """
    def __init__(self, 
                 trusted_authorities: List[str], 
                 agent_id: str = "Agent-Universal-Node",
                 authority_instance: Optional[BartholomewTrustAuthority] = None,
                 allowed_capabilities: Optional[List[str]] = None,
                 enforce_strict: bool = True):
        self.trusted_authorities = trusted_authorities
        self.agent_id = agent_id
        self.authority = authority_instance
        self.allowed_capabilities = allowed_capabilities
        self.enforce_strict = enforce_strict
        self.seen_nonces: Set[str] = set()

    def verify_action(self, 
                      receipt_or_packet: Union[str, Dict[str, Any]], 
                      candidate_payload: Dict[str, Any],
                      required_policy_hash: Optional[str] = None) -> Tuple[bool, str]:
        """Verifies an incoming action packet 100% offline."""
        return independent_verify_btp_receipt(
            receipt_json_str=receipt_or_packet,
            candidate_payload=candidate_payload,
            trusted_root_pubkeys=self.trusted_authorities,
            expected_recipient_context=self.agent_id,
            seen_nonces=self.seen_nonces,
            required_policy_hash=required_policy_hash,
            allowed_capabilities=self.allowed_capabilities
        )

    def issue_action_attestation(self, 
                                 target_recipient: str, 
                                 action_type: str, 
                                 payload: Dict[str, Any],
                                 capability_scope: Optional[List[str]] = None) -> Dict[str, Any]:
        """Signs and attaches a verifiable BTP attestation to an outbound payload."""
        if not self.authority:
            raise RuntimeError("BTPGuard requires an initialized authority_instance to issue attestations.")
        return self.authority.evaluate_intent(
            agent_id=self.agent_id,
            action_type=action_type,
            payload=payload,
            target_recipient=target_recipient,
            capability_scope=capability_scope
        )

    # -------------------------------------------------------------------------
    # Framework Adapter: LangChain / LangGraph Tool Wrapper
    # -------------------------------------------------------------------------
    def wrap_tool(self, func: Callable):
        """Decorator for LangChain / LangGraph Tool execution."""
        def wrapped(*args, **kwargs):
            # Inspect kwargs for btp_receipt
            receipt = kwargs.pop("btp_receipt", None)
            if self.enforce_strict and not receipt:
                raise PermissionError(f"[BTP_BLOCKED] Execution denied: Missing required BTP trust receipt for '{func.__name__}'")
            
            payload = {"func": func.__name__, "args": args, "kwargs": kwargs}
            if receipt:
                ok, msg = self.verify_action(receipt, payload)
                if not ok:
                    raise PermissionError(f"[BTP_BLOCKED] Attestation rejected for '{func.__name__}': {msg}")
            return func(*args, **kwargs)
        return wrapped

    # -------------------------------------------------------------------------
    # Framework Adapter: Microsoft AutoGen Message Interceptor
    # -------------------------------------------------------------------------
    def intercept_autogen_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Validates incoming AutoGen agent messages before tool/code dispatch."""
        if "btp_envelope" in message:
            envelope = message["btp_envelope"]
            payload = message.get("content", {})
            ok, msg = self.verify_action(envelope, payload)
            if not ok:
                return {
                    "role": "system",
                    "content": f"[BTP_SECURITY_ALERT] Inbound message attestation failed: {msg}. Message halted.",
                    "status": "DENIED"
                }
        elif self.enforce_strict and message.get("action_type") in ["EXEC_COMMAND", "DEPLOY_PATCH", "SQL_EXEC"]:
            return {
                "role": "system",
                "content": "[BTP_SECURITY_ALERT] Unattested high-privilege action rejected.",
                "status": "DENIED"
            }
        return message

    # -------------------------------------------------------------------------
    # Framework Adapter: CrewAI Task Middleware
    # -------------------------------------------------------------------------
    def wrap_crewai_task(self, task_description: str, task_fn: Callable) -> Callable:
        """Wraps a CrewAI task execution with pre-flight BTP policy checks."""
        def guarded_task_exec(*args, **kwargs):
            payload = {"task": task_description, "args": args, "kwargs": kwargs}
            if self.authority:
                receipt = self.authority.evaluate_intent(
                    agent_id=self.agent_id,
                    action_type="CREW_TASK",
                    payload=payload
                )
                if receipt["attestation"]["verdict"] != "ALLOW":
                    raise RuntimeError(f"[BTP_CREW_DENIED] Task blocked: {receipt['attestation']['reason']}")
            return task_fn(*args, **kwargs)
        return guarded_task_exec
