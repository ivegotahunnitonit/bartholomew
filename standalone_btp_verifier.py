"""
BTP Standalone Independent Reference Verifier (Zero Bartholomew SDK Dependencies)
This 35-line reference implementation proves BTP is an open cryptographic protocol,
not a proprietary SDK. Any external agent framework (LangGraph, AutoGen, CrewAI, etc.)
can copy-paste this function to independently verify BTP receipts 100% offline.
"""

import json
import hashlib
import time
from typing import Dict, Any, Tuple, Optional
from cryptography.hazmat.primitives.asymmetric import ed25519

def canonical_json_bytes(obj: Any) -> bytes:
    """RFC 8785 Canonical JSON Serialization (JCS)"""
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')

def independent_verify_btp_receipt(receipt_json_str: str, 
                                  candidate_payload: Dict[str, Any], 
                                  trusted_root_pubkey_hex: str) -> Tuple[bool, str]:
    """
    Independently verifies a BTP trust receipt with ZERO network requests.
    """
    try:
        packet = json.loads(receipt_json_str) if isinstance(receipt_json_str, str) else receipt_json_str
        attestation = packet.get("attestation", {})
        signature_hex = packet.get("signature", "")

        # 1. Authority Pinning Check
        if attestation.get("authority_pubkey") != trusted_root_pubkey_hex:
            return False, "FORGERY_DETECTED: Authority public key does not match pinned root"

        # 2. Expiration Window Check (TTL)
        if time.time() > attestation.get("expires_at_unix", 0):
            return False, "EXPIRED_RECEIPT: Attestation token has expired"

        # 3. Payload Integrity Check (SHA-256 Hash Binding)
        expected_hash = hashlib.sha256(canonical_json_bytes(candidate_payload)).hexdigest()
        if attestation.get("action_payload_hash") != expected_hash:
            return False, "PAYLOAD_TAMPERED: Candidate payload does not match evaluated hash"

        # 4. Mathematical Ed25519 Signature Verification
        pubkey = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(trusted_root_pubkey_hex))
        pubkey.verify(bytes.fromhex(signature_hex), canonical_json_bytes(attestation))

        # 5. Verdict Authorization
        if attestation.get("verdict") != "ALLOW":
            return False, f"ACTION_DENIED_BY_POLICY: {attestation.get('reason')}"

        return True, "VERIFIED_VALID: Cryptographic proof demonstrated independently"

    except Exception as e:
        return False, f"VERIFICATION_FAILED: {str(e)}"
