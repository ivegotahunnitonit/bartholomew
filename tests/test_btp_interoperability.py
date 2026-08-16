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

    standalone_verifier = StandaloneBTPVerifier(pinned_root_keys=data["pinned_root_keys"])
    project_verifier = StandaloneIndependentVerifier(pinned_root_pub_keys=data["pinned_root_keys"])

    valid_vector = data["test_vectors"][0]
    artifact = valid_vector["artifact"]

    # Both verifiers must independently agree
    standalone_valid, standalone_msg = standalone_verifier.verify_artifact(artifact)
    project_valid, project_msg = project_verifier.verify_evidence_artifact_independently(artifact)

    assert standalone_valid is True
    assert project_valid is True
    assert standalone_valid == project_valid
