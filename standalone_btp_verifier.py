"""
BTP Standalone Independent Reference Verifier (Standards-Compliant RFC 8785 & FIPS 186-5)
Provides 100% offline, zero-network cryptographic verification for BTP receipts.
Does not depend on any proprietary Bartholomew SDK.
"""

import json
import hashlib
import time
from typing import Dict, Any, Tuple, Optional, Set
from cryptography.hazmat.primitives.asymmetric import ed25519

# Embedded RFC 8785 JSON Canonicalization Scheme (JCS)
def rfc8785_canonicalize(val: Any) -> bytes:
    def _ser(v):
        if v is None: return "null"
        if isinstance(v, bool): return "true" if v else "false"
        if isinstance(v, int): return str(v)
        if isinstance(v, float):
            if v == 0.0: return "0"
            return str(int(v)) if v.is_integer() else repr(v).replace("E", "e").replace("e+", "e")
        if isinstance(v, str):
            out = []
            for c in v:
                code = ord(c)
                if c == '"': out.append('\\"')
                elif c == '\\': out.append('\\\\')
                elif c == '\b': out.append('\\b')
                elif c == '\f': out.append('\\f')
                elif c == '\n': out.append('\\n')
                elif c == '\r': out.append('\\r')
                elif c == '\t': out.append('\\t')
                elif code < 0x20: out.append(f"\\u{code:04x}")
                else: out.append(c)
            return '"' + "".join(out) + '"'
        if isinstance(v, (list, tuple)):
            return "[" + ",".join(_ser(x) for x in v) + "]"
        if isinstance(v, dict):
            keys = sorted(v.keys(), key=lambda k: [ord(c) for c in k])
            return "{" + ",".join(f"{_ser(k)}:{_ser(v[k])}" for k in keys) + "}"
        raise TypeError(f"Unserializable type {type(v)}")
    return _ser(val).encode('utf-8')

def independent_verify_btp_receipt(receipt_json_str: str, 
                                  candidate_payload: Dict[str, Any], 
                                  trusted_root_pubkey_hex: str,
                                  expected_recipient_context: Optional[str] = None,
                                  seen_nonces: Optional[Set[str]] = None) -> Tuple[bool, str]:
    """
    Independently verifies a BTP trust receipt with ZERO network requests.
    Validates complete contextual binding:
    1. Authority Public Key match.
    2. Protocol Version compatibility.
    3. Target Recipient context binding.
    4. Expiration Window (TTL).
    5. Nonce uniqueness (Replay Attack Defense).
    6. RFC 8785 SHA-256 payload hash binding.
    7. Mathematical Ed25519 digital signature.
    8. Policy verdict authorization.
    """
    try:
        packet = json.loads(receipt_json_str) if isinstance(receipt_json_str, str) else receipt_json_str
        att = packet.get("attestation", {})
        signature_hex = packet.get("signature", "")

        # 1. Authority Pinning Check
        if att.get("authority_pubkey") != trusted_root_pubkey_hex:
            return False, "FORGERY_DETECTED: Authority public key does not match pinned root"

        # 2. Protocol Version Check
        if not att.get("protocol_version", "").startswith("BTP/"):
            return False, "PROTOCOL_MISMATCH: Unsupported or missing BTP protocol version"

        # 3. Recipient Context Binding Check (Cross-Context Replay Defense)
        if expected_recipient_context:
            receipt_recipient = att.get("target_recipient")
            if receipt_recipient and receipt_recipient != expected_recipient_context:
                return False, f"CONTEXT_MISMATCH: Receipt intended for '{receipt_recipient}', not '{expected_recipient_context}'"

        # 4. Expiration Window Check (TTL)
        now = time.time()
        expires_at = att.get("expires_at_unix", 0)
        if now > expires_at:
            return False, f"EXPIRED_RECEIPT: Attestation token expired {now - expires_at:.1f}s ago"

        # 5. Nonce Uniqueness Check (Replay Defense)
        nonce = att.get("nonce")
        if not nonce:
            return False, "INVALID_RECEIPT: Missing cryptographic nonce"
        if seen_nonces is not None:
            if nonce in seen_nonces:
                return False, f"REPLAY_ATTACK: Nonce '{nonce}' has already been processed"
            seen_nonces.add(nonce)

        # 6. RFC 8785 SHA-256 Payload Hash Binding Check
        expected_hash = hashlib.sha256(rfc8785_canonicalize(candidate_payload)).hexdigest()
        if att.get("action_payload_hash") != expected_hash:
            return False, "PAYLOAD_TAMPERED: Candidate payload does not match evaluated hash"

        # 7. Mathematical Ed25519 Signature Verification
        pubkey = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(trusted_root_pubkey_hex))
        canonical_att_bytes = rfc8785_canonicalize(att)
        pubkey.verify(bytes.fromhex(signature_hex), canonical_att_bytes)

        # 8. Verdict Authorization
        if att.get("verdict") != "ALLOW":
            return False, f"ACTION_DENIED_BY_POLICY: {att.get('reason')}"

        return True, "VERIFIED_VALID: Cryptographic proof demonstrated independently"

    except Exception as e:
        return False, f"VERIFICATION_FAILED: {str(e)}"
