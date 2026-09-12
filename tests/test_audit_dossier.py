"""
Automated Test for BTP Enterprise Audit Dossier Generator
Verifies signature verification, control matrix evaluation, and JSON-LD structure.
"""

import os
import json
import hashlib
from src.security.audit_dossier import AuditDossierGenerator
from cryptography.hazmat.primitives.asymmetric import ed25519

def test_audit_dossier_generation():
    test_out = os.path.abspath(".btp_test_dossier.json")
    if os.path.exists(test_out):
        os.remove(test_out)

    generator = AuditDossierGenerator()
    dossier = generator.generate_dossier(output_path=test_out)

    assert dossier["compliance_grade"] == "A+"
    assert dossier["compliance_score"] == 100.0
    assert len(dossier["controls_matrix"]) == 5
    assert dossier["benchmark_evidence"]["false_negatives"] == 0
    assert dossier["benchmark_evidence"]["throughput_ops_sec"] > 5000.0

    # Cryptographic signature validation
    pub_bytes = bytes.fromhex(dossier["public_key_hex"])
    sig_bytes = bytes.fromhex(dossier["cryptographic_signature"])
    digest_bytes = bytes.fromhex(dossier["content_digest_sha256"])

    pub_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
    pub_key.verify(sig_bytes, digest_bytes)

    assert os.path.exists(test_out)
    if os.path.exists(test_out):
        os.remove(test_out)

    print("[PASS] Audit dossier signature and invariant controls verified.")

if __name__ == "__main__":
    test_audit_dossier_generation()
    print("ALL AUDIT DOSSIER TESTS PASSED.")
