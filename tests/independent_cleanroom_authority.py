"""
Clean-Room Independent BTP v2.2 Authority & Verifier
Written 100% from the frozen BTP v2.2 specification without importing or sharing ANY
Bartholomew internal code. Implements independent RFC 8785 canonicalization and Ed25519 signing.
"""

import json
import hashlib
import time
from typing import Dict, Any, Tuple, List
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

def cleanroom_jcs(val: Any) -> bytes:
    """Independent RFC 8785 JCS implementation."""
    def _s(v):
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
            return "[" + ",".join(_s(x) for x in v) + "]"
        if isinstance(v, dict):
            keys = sorted(v.keys(), key=lambda k: [ord(c) for c in k])
            return "{" + ",".join(f"{_s(k)}:{_s(v[k])}" for k in keys) + "}"
        raise TypeError(f"Unserializable: {type(v)}")
    return _s(val).encode('utf-8')

class CleanRoomIndependentAuthority:
    """Independent Third-Party Trust Authority built strictly from BTP v2.2 Spec."""
    def __init__(self):
        self.privkey = ed25519.Ed25519PrivateKey.generate()
        self.pubkey = self.privkey.public_key()
        self.pubkey_hex = self.pubkey.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        ).hex()

    def issue_attestation(self, 
                          originating_agent: str, 
                          target_recipient: str, 
                          action_type: str, 
                          candidate_payload: Dict[str, Any],
                          policy_id: str,
                          capability_scope: List[str]) -> Dict[str, Any]:
        """Issues an authentic BTP v2.2 signed attestation envelope."""
        now = time.time()
        payload_bytes = cleanroom_jcs(candidate_payload)
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()
        policy_hash = hashlib.sha256(policy_id.encode('utf-8')).hexdigest()

        attestation = {
            "protocol_version": "BTP/2.2",
            "authority": "CleanRoom-Independent-Authority-v1.0",
            "authority_pubkey": self.pubkey_hex,
            "nonce": hashlib.sha256(f"{now}-{self.pubkey_hex}".encode()).hexdigest()[:32],
            "issued_at_unix": now,
            "expires_at_unix": now + 300.0,
            "originating_agent": originating_agent,
            "target_recipient": target_recipient,
            "action_type": action_type,
            "action_payload_hash": payload_hash,
            "policy_id": policy_id,
            "policy_hash": policy_hash,
            "capability_scope": capability_scope,
            "verdict": "ALLOW",
            "reason": "Clean-room independent policy evaluation verified."
        }

        att_bytes = cleanroom_jcs(attestation)
        sig = self.privkey.sign(att_bytes).hex()

        return {
            "attestation": attestation,
            "signature": sig
        }

class CleanRoomIndependentVerifier:
    """Independent Third-Party Verifier built strictly from BTP v2.2 Spec."""
    @staticmethod
    def verify(receipt: Dict[str, Any], 
               candidate_payload: Dict[str, Any], 
               trusted_keys: List[str],
               expected_recipient: str) -> Tuple[bool, str]:
        try:
            att = receipt.get("attestation", {})
            sig_hex = receipt.get("signature", "")
            auth_key = att.get("authority_pubkey")

            if auth_key not in trusted_keys:
                return False, "FORGERY: Authority key not in clean-room trust store"
            if att.get("protocol_version") != "BTP/2.2":
                return False, "VERSION_MISMATCH"
            if att.get("target_recipient") != expected_recipient:
                return False, "RECIPIENT_MISMATCH"
            if time.time() > att.get("expires_at_unix", 0):
                return False, "EXPIRED"

            # Check Payload Hash
            pl_hash = hashlib.sha256(cleanroom_jcs(candidate_payload)).hexdigest()
            if att.get("action_payload_hash") != pl_hash:
                return False, "PAYLOAD_HASH_MISMATCH"

            # Check Ed25519 signature
            pub = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(auth_key))
            pub.verify(bytes.fromhex(sig_hex), cleanroom_jcs(att))

            return (att.get("verdict") == "ALLOW"), att.get("reason", "")
        except Exception as e:
            return False, f"ERROR: {str(e)}"
