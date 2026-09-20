"""
Bartholomew Production Deployment Gate (BTP-Gate)
Acts as the mandatory cryptographic checkpoint in CI/CD and cloud pipelines.
Refuses deployment if code or autonomous agent action lacks an authentic,
un-tampered Bartholomew RFC 8785 Ed25519 Attestation Receipt.
"""

import sys
import os
import json
import hashlib
from typing import Dict, Any, Tuple

# Ensure src is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.trust_protocol import TrustVerifier, canonical_json_bytes

class ProductionDeployGate:
    """
    Mandatory Production Enforcement Gate.
    Ensures no autonomous agent can push code to production without a verified Bartholomew seal.
    """
    def __init__(self, trusted_authority_pubkey: str):
        self.trusted_authority_pubkey = trusted_authority_pubkey

    def verify_pipeline_deployment(self, 
                                   attestation_receipt_file: str, 
                                   candidate_payload: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Evaluates the deployment candidate:
        1. Checks for existence of attestation receipt file.
        2. Validates Ed25519 signature against root authority public key.
        3. Validates that payload hash matches the exact code artifact.
        4. Validates verdict == 'ALLOW'.
        """
        if not os.path.exists(attestation_receipt_file):
            return False, "DEPLOYMENT REFUSED: Missing required Bartholomew Attestation Receipt (RFC 8785 Ed25519)"

        try:
            with open(attestation_receipt_file, "r", encoding="utf-8") as f:
                packet = json.load(f)
                
            authorized, reason = TrustVerifier.verify_and_authorize(
                attestation_packet=packet,
                expected_payload=candidate_payload,
                trusted_authority_pubkey=self.trusted_authority_pubkey
            )
            
            if not authorized:
                return False, f"DEPLOYMENT REFUSED: {reason}"
                
            return True, "DEPLOYMENT AUTHORIZED: Valid Bartholomew Attestation Receipt Verified (Exit Code 0)"

        except Exception as e:
            return False, f"DEPLOYMENT REFUSED: Cryptographic Gate Error ({str(e)})"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python deploy_gate.py <receipt_file.json> <pubkey_hex>")
        sys.exit(1)
        
    receipt_file = sys.argv[1]
    pubkey = sys.argv[2]
    
    gate = ProductionDeployGate(trusted_authority_pubkey=pubkey)
    # Dummy payload check for CLI
    ok, msg = gate.verify_pipeline_deployment(receipt_file, {})
    print(msg)
    sys.exit(0 if ok else 1)
