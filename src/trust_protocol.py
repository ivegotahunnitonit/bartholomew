"""
Bartholomew Autonomous Trust Protocol (BTP-Core v2.2 Frozen)
Standardized on RFC 8785 Canonical JSON (JCS) and FIPS 186-5 Ed25519.
"""

import json
import time
import hashlib
import os
import secrets
from typing import Dict, Any, Tuple, Optional, List, Union, Set
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from src.rfc8785 import rfc8785_canonicalize

class BartholomewTrustAuthority:
    """
    Independent Verification & Evidence Generation Engine.
    "Trust isn't granted. Trust is demonstrated."
    """
    def __init__(self, ttl_seconds: int = 300):
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        self.public_key_hex = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        ).hex()
        self.ttl_seconds = ttl_seconds
        self.issued_nonces = set()

    def evaluate_intent(self, 
                        agent_id: str, 
                        action_type: str, 
                        payload: Dict[str, Any], 
                        target_recipient: str = "Agent-Universal-Recipient",
                        policy_id: str = "urn:btp:policy:owasp-agentic-v2026.1",
                        capability_scope: Optional[List[str]] = None,
                        sandbox_test_fn: Optional[callable] = None) -> Dict[str, Any]:
        """
        Generates a verifiable, time-bound, nonced cryptographic attestation (BTP/2.2).
        """
        start_time = time.perf_counter()
        now = time.time()
        nonce = secrets.token_hex(16)
        self.issued_nonces.add(nonce)

        dangerous_patterns = [
            "rm -rf", "drop table", "drop schema", "drop database", "truncate table",
            "aws_secret_access_key", "id_rsa", "/etc/shadow", "malicious", "system override",
            "sk-live", "eval(", "exec(", "<script>", "import os"
        ]
        
        raw_payload_str = json.dumps(payload).lower()
        blocked_reason = None
        
        for pattern in dangerous_patterns:
            if pattern in raw_payload_str:
                blocked_reason = f"Policy Violation: Trajectory contained forbidden pattern '{pattern}'"
                break
                
        # 2. Hermetic Pre-Flight Sandbox Execution
        sandbox_result = {"status": "SKIPPED", "tests_passed": 0, "tests_total": 0}
        if not blocked_reason and sandbox_test_fn:
            try:
                passed, total, details = sandbox_test_fn(payload)
                sandbox_result = {
                    "status": "PASSED" if passed == total else "FAILED",
                    "tests_passed": passed,
                    "tests_total": total,
                    "details": details
                }
                if passed < total:
                    blocked_reason = f"Pre-Flight Sandbox Gate Failed: {passed}/{total} tests passed."
            except Exception as e:
                blocked_reason = f"Sandbox Execution Crash: {str(e)}"
                sandbox_result = {"status": "CRASHED", "error": str(e)}

        eval_duration_us = (time.perf_counter() - start_time) * 1_000_000
        verdict = "DENY" if blocked_reason else "ALLOW"
        
        payload_bytes = rfc8785_canonicalize(payload)
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()
        policy_hash = hashlib.sha256(policy_id.encode('utf-8')).hexdigest()

        attestation_body = {
            "protocol_version": "BTP/2.2",
            "authority": "Bartholomew-Trust-Engine-v2.2",
            "authority_pubkey": self.public_key_hex,
            "nonce": nonce,
            "issued_at_unix": now,
            "expires_at_unix": now + self.ttl_seconds,
            "originating_agent": agent_id,
            "target_recipient": target_recipient,
            "action_type": action_type,
            "action_payload_hash": payload_hash,
            "policy_id": policy_id,
            "policy_hash": policy_hash,
            "capability_scope": capability_scope or ["FS_WRITE_RESTRICTED", "NO_NET_EGRESS", "AST_MAX_DELTA_5"],
            "verdict": verdict,
            "reason": blocked_reason or "All pre-flight checks and trajectory policies verified successfully.",
            "sandbox_receipt": sandbox_result,
            "evaluation_latency_us": round(eval_duration_us, 2)
        }

        canonical_bytes = rfc8785_canonicalize(attestation_body)
        signature = self.private_key.sign(canonical_bytes).hex()

        return {
            "attestation": attestation_body,
            "signature": signature
        }

class IndependentTrustVerifier:
    """
    100% Offline, Zero-Network Independent Verifier.
    """
    @staticmethod
    def verify_attestation(attestation_packet: Dict[str, Any], 
                           expected_payload: Dict[str, Any],
                           trusted_root_pubkey: str,
                           current_timestamp: Optional[float] = None,
                           seen_nonces: Optional[set] = None) -> Tuple[bool, str]:
        from standalone_btp_verifier import independent_verify_btp_receipt
        return independent_verify_btp_receipt(
            receipt_json_str=attestation_packet,
            candidate_payload=expected_payload,
            trusted_root_pubkeys=[trusted_root_pubkey],
            seen_nonces=seen_nonces,
            eval_timestamp=current_timestamp
        )
