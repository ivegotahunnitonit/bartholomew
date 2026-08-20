"""
Generator for Cross-Language RFC 8785 & Ed25519 BTP Test Vectors
Produces deterministic test vectors verified by both Python and Go implementations.
"""

import json
import hashlib
import os
import sys
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.rfc8785 import rfc8785_canonicalize

def generate_vectors():
    # Deterministic 32-byte Ed25519 private key seed
    seed = b"\x01" * 32
    privkey = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
    pubkey = privkey.public_key()
    pubkey_hex = pubkey.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    ).hex()

    test_payload = {
        "zeta": 100,
        "alpha": "Hello, 世界",
        "beta": [3.14, -0.0, True, None, "escaped: \" \\ \n \t"],
        "nested": {"z": 1, "a": 2}
    }

    canonical_payload_bytes = rfc8785_canonicalize(test_payload)
    payload_hash = hashlib.sha256(canonical_payload_bytes).hexdigest()

    attestation = {
        "protocol_version": "BTP/2.2",
        "authority": "Bartholomew-Trust-Engine-v2.2",
        "authority_pubkey": pubkey_hex,
        "nonce": "d8e8fca2dc6b4b9b9c9f0a1b2c3d4e5f",
        "issued_at_unix": 1755648000,
        "expires_at_unix": 1755648300,
        "originating_agent": "Agent-LangGraph-01",
        "target_recipient": "Agent-AutoGen-02",
        "action_type": "DEPLOY_PATCH",
        "action_payload_hash": payload_hash,
        "verdict": "ALLOW",
        "reason": "All pre-flight checks and trajectory policies verified successfully."
    }

    canonical_attestation_bytes = rfc8785_canonicalize(attestation)
    signature = privkey.sign(canonical_attestation_bytes).hex()

    test_vector_doc = {
        "test_vector_id": "BTP-TV-RFC8785-ED25519-001",
        "description": "Deterministic Cross-Language RFC 8785 Canonicalization & Ed25519 Verification Vector",
        "deterministic_seed_hex": seed.hex(),
        "trusted_root_pubkey_hex": pubkey_hex,
        "candidate_payload_raw": test_payload,
        "canonical_payload_utf8_hex": canonical_payload_bytes.hex(),
        "canonical_payload_sha256": payload_hash,
        "attestation_packet": {
            "attestation": attestation,
            "signature": signature
        },
        "canonical_attestation_utf8_hex": canonical_attestation_bytes.hex(),
        "expected_verification_result": True
    }

    with open("BTP_TEST_VECTORS.json", "w", encoding="utf-8") as f:
        json.dump(test_vector_doc, f, indent=2, ensure_ascii=False)
        
    print("[OK] Generated BTP_TEST_VECTORS.json with deterministic RFC 8785 vectors")

if __name__ == "__main__":
    generate_vectors()
