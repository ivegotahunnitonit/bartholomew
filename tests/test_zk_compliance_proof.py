"""
Tests for BTP v3.0.0 — Zero-Knowledge Compliance Proof Engine
==============================================================
7 tests covering proof generation, verification, privacy guarantees,
batch proving, receipt export schema, and offline operation.
"""

import json
import pytest

from src.zk_compliance_proof_engine import (
    ZKComplianceEngine,
    ZKComplianceProof,
    ZKProofWitness,
    PolicyCircuit,
    ZKStepProof,
    _P,
    _Q,
    _G,
    _H,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_TOOL_CALLS = [
    "read_file('/etc/hosts')",
    "list_directory('/home/agent')",
    "http_get('https://api.example.com/data')",
    "write_file('/tmp/output.txt', 'results')",
    "run_shell('echo hello')",
]


@pytest.fixture
def engine() -> ZKComplianceEngine:
    return ZKComplianceEngine()


@pytest.fixture
def sample_proof(engine: ZKComplianceEngine) -> ZKComplianceProof:
    return engine.prove_session(
        session_id="test-session-001",
        tool_calls=SAMPLE_TOOL_CALLS,
    )


# ---------------------------------------------------------------------------
# Test 1: Proof generation for a valid session
# ---------------------------------------------------------------------------

def test_proof_generation_valid_session(engine: ZKComplianceEngine) -> None:
    """A proof is generated and has the correct structure."""
    proof = engine.prove_session(
        session_id="gen-test-001",
        tool_calls=SAMPLE_TOOL_CALLS,
    )

    assert isinstance(proof, ZKComplianceProof)
    assert proof.session_id == "gen-test-001"
    assert proof.num_tool_calls == len(SAMPLE_TOOL_CALLS)
    assert len(proof.step_proofs) == len(SAMPLE_TOOL_CALLS)
    assert proof.protocol_version == "BTP/zk-SNARK/3.0.0"
    assert proof.policy_id == "BTP-STANDARD-3.0.0"
    assert proof.proof_id != ""
    assert proof.aggregate_commitment > 0
    assert proof.aggregate_challenge > 0
    assert proof.aggregate_response > 0

    # Each step proof has required fields
    for idx, step in enumerate(proof.step_proofs):
        assert step.step_index == idx
        assert step.commitment > 0
        assert step.challenge > 0
        assert step.response > 0
        assert step.constraint_id.startswith("BTP-C")


# ---------------------------------------------------------------------------
# Test 2: Proof verification passes for a correctly generated proof
# ---------------------------------------------------------------------------

def test_proof_verification_passes(sample_proof: ZKComplianceProof) -> None:
    """A freshly generated proof verifies correctly."""
    result = sample_proof.verify()
    assert result is True
    assert sample_proof.proof_valid is True


# ---------------------------------------------------------------------------
# Test 3: Tampered proof fails verification
# ---------------------------------------------------------------------------

def test_tampered_proof_fails(sample_proof: ZKComplianceProof) -> None:
    """Mutating the aggregate response causes verification to fail."""
    # Tamper: flip the last bit of the response
    original_response = sample_proof.aggregate_response
    sample_proof.aggregate_response = original_response ^ 0xDEADBEEF

    result = sample_proof.verify()
    assert result is False
    assert sample_proof.proof_valid is False

    # Restore and confirm it passes again (mutation is reversible)
    sample_proof.aggregate_response = original_response
    assert sample_proof.verify() is True


# ---------------------------------------------------------------------------
# Test 4: Privacy — witness content is absent from proof bytes
# ---------------------------------------------------------------------------

def test_privacy_witness_not_in_proof(engine: ZKComplianceEngine) -> None:
    """The actual tool call strings must not appear in the proof receipt."""
    sensitive_calls = [
        "db_query('SELECT * FROM users WHERE token=SECRET123')",
        "api_call('Authorization: Bearer sk-prod-abc123def456')",
        "shell_run('cat /etc/shadow')",
    ]

    proof = engine.prove_session(
        session_id="privacy-test-001",
        tool_calls=sensitive_calls,
    )

    receipt_json = proof.export_json()

    # None of the sensitive strings should appear in the proof output
    for call in sensitive_calls:
        assert call not in receipt_json, (
            f"Privacy violation: '{call}' found in proof receipt"
        )

    # Specific sensitive tokens must not appear
    for token in ["SECRET123", "sk-prod-abc123def456", "/etc/shadow", "SELECT * FROM"]:
        assert token not in receipt_json, (
            f"Privacy violation: token '{token}' found in proof receipt"
        )


# ---------------------------------------------------------------------------
# Test 5: Batch session proof
# ---------------------------------------------------------------------------

def test_batch_session_proof(engine: ZKComplianceEngine) -> None:
    """Prove 10 tool calls across 3 sessions in a single batch call."""
    sessions = {
        "session-A": ["tool_call_1()", "tool_call_2()", "tool_call_3()"],
        "session-B": ["tool_call_4()", "tool_call_5()", "tool_call_6()", "tool_call_7()"],
        "session-C": ["tool_call_8()", "tool_call_9()", "tool_call_10()"],
    }

    results = engine.batch_prove(sessions)

    assert len(results) == 3
    total_calls = 0

    for session_id, proof in results.items():
        assert isinstance(proof, ZKComplianceProof)
        assert proof.session_id == session_id
        assert proof.proof_valid is True
        assert proof.verify() is True
        total_calls += proof.num_tool_calls

    assert total_calls == 10


# ---------------------------------------------------------------------------
# Test 6: Compliance receipt export has correct schema
# ---------------------------------------------------------------------------

def test_compliance_receipt_export(sample_proof: ZKComplianceProof) -> None:
    """Exported receipt JSON has the expected schema fields."""
    receipt_json = sample_proof.export_json()
    receipt = json.loads(receipt_json)

    assert "btp_proof_receipt" in receipt
    payload = receipt["btp_proof_receipt"]

    required_fields = [
        "proof_id",
        "protocol",
        "session_id",
        "policy_id",
        "generated_at_unix",
        "num_tool_calls_covered",
        "proof_valid",
        "aggregate_commitment_hex",
        "aggregate_witness_commit_hex",
        "aggregate_challenge_hex",
        "aggregate_response_hex",
        "step_count",
        "step_proofs",
        "privacy_notice",
    ]

    for field in required_fields:
        assert field in payload, f"Missing required field: {field}"

    assert payload["num_tool_calls_covered"] == len(SAMPLE_TOOL_CALLS)
    assert payload["step_count"] == len(SAMPLE_TOOL_CALLS)
    assert payload["proof_valid"] is True
    assert "BTP/zk-SNARK/3.0.0" in payload["protocol"]
    assert "zero plaintext" in payload["privacy_notice"]

    # Hex-encoded values are valid hex
    for hex_field in [
        "aggregate_commitment_hex",
        "aggregate_witness_commit_hex",
        "aggregate_challenge_hex",
        "aggregate_response_hex",
    ]:
        hex_val = payload[hex_field]
        assert hex_val.startswith("0x"), f"{hex_field} should start with 0x"
        int(hex_val, 16)  # Should not raise

    # Step proofs have correct structure
    assert len(payload["step_proofs"]) == len(SAMPLE_TOOL_CALLS)
    for step in payload["step_proofs"]:
        assert "step_index" in step
        assert "commitment_hex" in step
        assert "challenge_hex" in step
        assert "response_hex" in step
        assert "constraint_id" in step


# ---------------------------------------------------------------------------
# Test 7: Offline verification — no network calls required
# ---------------------------------------------------------------------------

def test_offline_verification(engine: ZKComplianceEngine, monkeypatch: pytest.MonkeyPatch) -> None:
    """Proof generation and verification work with all network access blocked."""
    import socket

    # Block all socket operations to prove offline capability
    def raise_no_network(*args, **kwargs):
        raise RuntimeError("Network access is BLOCKED — this test verifies offline operation")

    monkeypatch.setattr(socket, "socket", raise_no_network)
    monkeypatch.setattr(socket, "getaddrinfo", raise_no_network)

    # Generate and verify without any network access
    proof = engine.prove_session(
        session_id="offline-test-001",
        tool_calls=["run_local_analysis()", "write_output('/tmp/result.json')"],
    )

    assert proof.verify() is True
    assert proof.num_tool_calls == 2

    # Export receipt also works offline
    receipt_json = proof.export_json()
    receipt = json.loads(receipt_json)
    assert receipt["btp_proof_receipt"]["proof_valid"] is True
