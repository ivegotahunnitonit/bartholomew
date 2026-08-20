"""
Microsoft AutoGen BTP v2.2 Message Interceptor
Provides multi-agent conversation protection against confused-deputy tool attacks.
"""

from typing import Dict, Any, List, Optional
import sys
import os

try:
    from standalone_btp_verifier import independent_verify_btp_receipt
except ImportError:
    from btp_guard import independent_verify_btp_receipt

class AutoGenBTPInterceptor:
    """
    Intercepts and validates incoming AutoGen agent messages before tool execution.
    
    Usage:
        interceptor = AutoGenBTPInterceptor(trusted_authorities=[ROOT_KEY])
        safe_msg = interceptor.intercept_message(inbound_message)
    """
    def __init__(self, 
                 trusted_authorities: List[str], 
                 recipient_id: str = "Agent-AutoGen-Worker",
                 enforce_strict: bool = True):
        self.trusted_authorities = trusted_authorities
        self.recipient_id = recipient_id
        self.enforce_strict = enforce_strict
        self.seen_nonces = set()

    def intercept_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Validates incoming message envelope 100% offline."""
        if "btp_envelope" in message:
            envelope = message["btp_envelope"]
            payload = message.get("content", {})
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
