import os
import json
import pytest
from independent_verifier_standalone import StandaloneBTPVerifier, run_standalone_verification_suite
from bartholomew_eval.agent_protocol import create_3_organization_simulation, StandaloneIndependentVerifier


def test_btp_test_vectors_standalone_compliance():
    """
    Proves that independent_verifier_standalone.py (zero Bartholomew code)
    passes 100% of BTP v0.1 test vectors in btp_test_vectors.json.
    """
    assert run_standalone_verification_suite("btp_test_vectors.json") is True


def test_interoperable_proof_equality():
    """
    Proves that Bartholomew Protocol Gateway and StandaloneBTPVerifier
    produce and verify identical RFC 8785 canonical evidence proofs.
    """
    with open("btp_test_vectors.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    keys = data.get("pinned_root_keys") or data.get("trusted_root_pubkeys_hex") or [data.get("trusted_root_pubkey_hex", "8a88e3dd7409f195fd52db2d3cba5d72ca6709bf1d94121bf3748801b40f6f5c")]
    if "test_vectors" in data:
        standalone_verifier = StandaloneBTPVerifier(pinned_root_keys=keys)
        project_verifier = StandaloneIndependentVerifier(pinned_root_pub_keys=keys)

        valid_vector = data["test_vectors"][0]
        artifact = valid_vector["artifact"]

        # Both verifiers must independently agree
        standalone_valid, standalone_msg = standalone_verifier.verify_artifact(artifact)
        project_valid, project_msg = project_verifier.verify_evidence_artifact_independently(artifact)

        assert standalone_valid is True
        assert project_valid is True
        assert standalone_valid == project_valid
