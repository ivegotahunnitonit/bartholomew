import argparse
import json
import sys
from typing import Dict, Any, Optional

from .evidence_artifact import BartholomewEvidence

class BartholomewVerifier:
    """
    Standalone Cryptographic Ed25519 Evidence Verifier with Replay Protection.
    Enables auditors to verify agent tool requests with zero external dependencies,
    without requiring the private signing key.
    """

    _seen_artifact_ids = set()

    @classmethod
    def verify(
        cls, 
        artifact: Dict[str, Any], 
        public_key_pem: bytes, 
        enforce_expiration: bool = True,
        prevent_replay: bool = False
    ) -> bool:
        """
        SDK Primitive to verify an evidence artifact.
        
        Usage:
            result = BartholomewVerifier.verify(artifact_dict, b"-----BEGIN PUBLIC KEY...")
        """
        if prevent_replay:
            artifact_id = artifact.get("artifact_id")
            if not artifact_id or artifact_id in cls._seen_artifact_ids:
                return False
                
        evidence_checker = BartholomewEvidence(public_key_pem=public_key_pem)
        is_valid = evidence_checker.verify(artifact, enforce_expiration=enforce_expiration)
        
        if is_valid and prevent_replay and artifact.get("artifact_id"):
            cls._seen_artifact_ids.add(artifact.get("artifact_id"))
            
        return is_valid

    @classmethod
    def reset_replay_cache(cls):
        """Clears the seen artifact_id cache for testing."""
        cls._seen_artifact_ids.clear()

def main(args: Optional[list[str]] = None) -> int:
    """CLI terminal runner for bartholomew-verify."""
    parser = argparse.ArgumentParser(description="Bartholomew Cryptographic Evidence Verifier")
    parser.add_argument("artifact", type=str, help="Path to the artifact JSON file.")
    parser.add_argument("--pubkey", type=str, required=True, help="Path to the Ed25519 Public Key PEM file.")
    
    parsed_args = parser.parse_args(args if args is not None else sys.argv[1:])
    
    try:
        with open(parsed_args.artifact, "r") as f:
            artifact_data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read artifact file: {e}")
        return 1
        
    try:
        with open(parsed_args.pubkey, "rb") as f:
            pubkey_pem = f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read public key file: {e}")
        return 1

    print("=== BARTHOLOMEW CRYPTOGRAPHIC EVIDENCE VERIFIER ===")
    print(f"Verifying Artifact ID : {artifact_data.get('artifact_id', 'UNKNOWN')}")
    print(f"Issued by             : {artifact_data.get('issuer', 'UNKNOWN')}")
    print(f"Agent ID              : {artifact_data.get('agent', {}).get('id', 'UNKNOWN')}")
    print("-" * 50)
    
    is_valid = BartholomewVerifier.verify(artifact_data, pubkey_pem)
    
    if is_valid:
        print("[VERIFICATION RESULT] : VALID (Independently Verifiable)")
        print(f"[SIGNATURE ALGORITHM] : Ed25519 Public-Key")
        print(f"[EVALUATION DECISION] : {artifact_data.get('evaluation', {}).get('decision', 'UNKNOWN').upper()}")
        return 0
    else:
        print("[VERIFICATION RESULT] : INVALID (Tampered or Forged Signature)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
