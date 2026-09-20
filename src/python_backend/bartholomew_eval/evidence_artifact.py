import json
import time
import uuid
from typing import List, Dict, Any, Optional

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

class BartholomewEvidence:
    """
    Generates and verifies machine-readable JSON Evidence Artifacts for AI agents.
    Uses Ed25519 Public/Private key cryptography to allow independent verification.
    """
    
    def __init__(self, private_key_pem: Optional[bytes] = None, public_key_pem: Optional[bytes] = None):
        """
        Initialize with a private key (for issuing) or public key (for verifying).
        """
        self.private_key = None
        self.public_key = None
        
        if private_key_pem:
            self.private_key = serialization.load_pem_private_key(private_key_pem, password=None)
            self.public_key = self.private_key.public_key()
        elif public_key_pem:
            self.public_key = serialization.load_pem_public_key(public_key_pem)

    @classmethod
    def generate_keypair(cls) -> tuple[bytes, bytes]:
        """Generates a new Ed25519 keypair and returns (private_pem, public_pem)."""
        priv = ed25519.Ed25519PrivateKey.generate()
        pub = priv.public_key()
        
        priv_pem = priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        pub_pem = pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return priv_pem, pub_pem

    def generate(
        self,
        agent_id: str,
        agent_version: str,
        action: str,
        target: str,
        capabilities: List[str],
        decision: str,
        policy: str,
        checks: List[Dict[str, str]],
        validity_seconds: int = 3600
    ) -> Dict[str, Any]:
        """
        Produces a signed evidence artifact using Ed25519.
        """
        if not self.private_key:
            raise ValueError("Private key is required to generate evidence.")
            
        now = time.time()
        issued_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
        expires_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now + validity_seconds))
        
        payload = {
            "artifact_version": "1.0",
            "issuer": "bartholomew",
            "agent": {
                "id": agent_id,
                "version": agent_version
            },
            "request": {
                "action": action,
                "target": target,
                "capabilities": sorted(capabilities)
            },
            "evaluation": {
                "decision": decision,
                "policy": policy,
                "checks": sorted(checks, key=lambda x: x["name"])
            },
            "issued_at": issued_at,
            "expires_at": expires_at,
            "artifact_id": str(uuid.uuid4())
        }
        
        signature = self._sign_payload(payload)
        payload["signature"] = signature
        return payload

    def verify(self, artifact: Dict[str, Any], enforce_expiration: bool = True) -> bool:
        """
        Verifies the Ed25519 cryptographic signature and timestamp validity of an evidence artifact.
        """
        if not self.public_key:
            raise ValueError("Public key is required to verify evidence.")
            
        if "signature" not in artifact:
            return False
            
        provided_signature_hex = artifact["signature"]
        
        # 1. Verify Expiration if enforced
        if enforce_expiration and "expires_at" in artifact:
            try:
                expires_ts = time.mktime(time.strptime(artifact["expires_at"], "%Y-%m-%dT%H:%M:%SZ"))
                # Adjust for GMT/UTC time
                now_utc = time.mktime(time.gmtime())
                if now_utc > expires_ts:
                    return False
            except Exception:
                return False
        
        # 2. Cryptographic Signature Verification
        payload_to_verify = artifact.copy()
        del payload_to_verify["signature"]
        
        canonical_json = self._canonicalize(payload_to_verify)
        
        try:
            signature_bytes = bytes.fromhex(provided_signature_hex)
            self.public_key.verify(signature_bytes, canonical_json.encode("utf-8"))
            return True
        except Exception:
            return False
        
    def _canonicalize(self, payload: Dict[str, Any]) -> str:
        """Canonicalize the JSON for deterministic signing."""
        return json.dumps(payload, separators=(',', ':'), sort_keys=True)

    def _sign_payload(self, payload: Dict[str, Any]) -> str:
        """Computes Ed25519 signature for the JSON payload and returns hex string."""
        canonical_json = self._canonicalize(payload)
        signature = self.private_key.sign(canonical_json.encode("utf-8"))
        return signature.hex()
