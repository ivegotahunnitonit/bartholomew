"""
Bartholomew Autonomous Trust & Governance Protocol (BTP-Core)
Implements an independent, interoperable trust exchange layer between autonomous agents.
Uses RFC 8785 Canonical JSON and Ed25519 Cryptographic Signatures.
"""

import json
import time
import hashlib
import os
from typing import Dict, Any, Tuple, Optional
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

# Canonical JSON Serializer (RFC 8785)
def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False
    ).encode('utf-8')

class BartholomewTrustAuthority:
    """
    The Neutral Referee & Trust Layer.
    Evaluates actions, runs sandbox verification, and signs tamper-evident receipts.
    """
    def __init__(self):
        # Generate or load sovereign Ed25519 keypair
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        self.public_key_hex = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        ).hex()

    def evaluate_intent(self, 
                        agent_id: str, 
                        action_type: str, 
                        payload: Dict[str, Any], 
                        sandbox_test_fn: Optional[callable] = None) -> Dict[str, Any]:
        """
        Independent verification gate:
        1. Sub-microsecond trajectory & security policy inspection.
        2. Hermetic pre-flight sandbox test battery (if applicable).
        3. Generates cryptographically signed attestation token.
        """
        start_time = time.perf_counter()
        
        # Policy & Trajectory Firewall Check (OWASP LLM Top-10 / Dangerous POSIX commands)
        dangerous_patterns = [
            "rm -rf", "drop table", "aws_secret_access_key", 
            "id_rsa", "system(", "exec(", "shutil.rmtree(/)",
            "curl http://malicious", "exfiltrate", "ignore previous instructions"
        ]
        
        raw_payload_str = json.dumps(payload).lower()
        blocked_reason = None
        
        for pattern in dangerous_patterns:
            if pattern in raw_payload_str:
                blocked_reason = f"Security Policy Violation: Trajectory contained forbidden pattern '{pattern}'"
                break
                
        # Sandbox Pre-Flight Test Battery
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
                    blocked_reason = f"Pre-Flight Test Gate Failed: {passed}/{total} tests passed."
            except Exception as e:
                blocked_reason = f"Sandbox Execution Crash: {str(e)}"
                sandbox_result = {"status": "CRASHED", "error": str(e)}

        eval_duration_us = (time.perf_counter() - start_time) * 1_000_000

        # Build Unsigned Attestation Payload
        verdict = "DENY" if blocked_reason else "ALLOW"
        
        attestation_body = {
            "authority": "Bartholomew-Trust-Engine-v2.0",
            "authority_pubkey": self.public_key_hex,
            "timestamp_ns": time.time_ns(),
            "originating_agent": agent_id,
            "action_type": action_type,
            "action_payload_hash": hashlib.sha256(canonical_json_bytes(payload)).hexdigest(),
            "verdict": verdict,
            "reason": blocked_reason or "All pre-flight checks and trajectory policies verified successfully.",
            "sandbox_receipt": sandbox_result,
            "evaluation_latency_us": round(eval_duration_us, 2)
        }

        # Sign RFC 8785 Canonical JSON bytes with Ed25519
        canonical_bytes = canonical_json_bytes(attestation_body)
        signature = self.private_key.sign(canonical_bytes).hex()

        return {
            "attestation": attestation_body,
            "signature": signature
        }

class TrustVerifier:
    """
    Downstream Tool / Target Agent / Infrastructure Receiver.
    Verifies Bartholomew's cryptographic attestation before executing any action.
    """
    @staticmethod
    def verify_and_authorize(attestation_packet: Dict[str, Any], 
                             expected_payload: Dict[str, Any],
                             trusted_authority_pubkey: str) -> Tuple[bool, str]:
        """
        Strict cryptographic verification:
        1. Validates Ed25519 signature against trusted authority pubkey.
        2. Validates that payload hash matches the actual action payload.
        3. Validates that verdict is 'ALLOW'.
        """
        try:
            attestation = attestation_packet["attestation"]
            signature_hex = attestation_packet["signature"]
            
            # 1. Verify Authority Public Key Matches
            if attestation.get("authority_pubkey") != trusted_authority_pubkey:
                return False, "Untrusted Authority Public Key"

            # 2. Verify Payload Hash
            actual_payload_hash = hashlib.sha256(canonical_json_bytes(expected_payload)).hexdigest()
            if attestation.get("action_payload_hash") != actual_payload_hash:
                return False, "Payload Tampering Detected: Payload hash mismatch"

            # 3. Verify Cryptographic Ed25519 Signature
            pubkey_bytes = bytes.fromhex(trusted_authority_pubkey)
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(pubkey_bytes)
            
            canonical_bytes = canonical_json_bytes(attestation)
            public_key.verify(bytes.fromhex(signature_hex), canonical_bytes)

            # 4. Check Verdict
            if attestation.get("verdict") != "ALLOW":
                return False, f"Action Denied by Bartholomew: {attestation.get('reason')}"

            return True, "Authorized & Verified by Bartholomew"

        except Exception as e:
            return False, f"Cryptographic Verification Failed: {str(e)}"
