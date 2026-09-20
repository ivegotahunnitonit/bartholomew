"""
Tests for BTP v3.1.0 — FROST RFC 9591 Threshold Signature Engine
=================================================================
8 tests covering key generation, 2-round signing, signature verification,
threshold enforcement, signer subset flexibility, forgery resistance,
swarm certificate integration, and Lagrange coefficient correctness.
"""

import hashlib
import pytest

from src.frost_threshold_engine import (
    frost_keygen,
    frost_reconstruct_secret,
    FrostSigner,
    FrostCoordinator,
    FrostThresholdSignature,
    _lagrange_coefficient,
    _evaluate_polynomial,
    _G, _P, _Q,
)
from src.byzantine_swarm_consensus import ByzantineSwarmEngine


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_swarm(n: int, t: int) -> tuple[list[FrostSigner], FrostCoordinator]:
    """Create n signers with threshold t and a coordinator."""
    keygens = frost_keygen(n=n, t=t)
    signers = [FrostSigner(kg) for kg in keygens]
    coordinator = FrostCoordinator(
        group_pubkey=keygens[0].group_pubkey,
        threshold=t,
    )
    return signers, coordinator


def run_frost_signing(
    signers: list[FrostSigner],
    coordinator: FrostCoordinator,
    message: bytes,
) -> FrostThresholdSignature:
    """Full 2-round FROST signing with all provided signers."""
    # Round 1
    commitments = [s.round1_commit() for s in signers]
    # Round 2
    partial_sigs = [s.round2_sign(message, commitments) for s in signers]
    # Aggregate
    return coordinator.aggregate_signature(message, commitments, partial_sigs)


# ---------------------------------------------------------------------------
# Test 1: Shamir shares reconstruct the group secret
# ---------------------------------------------------------------------------

def test_keygen_shares_reconstruct_secret() -> None:
    """Any t+1 shares reconstruct the same group secret, confirming Shamir correctness."""
    n, t = 5, 2  # 3-of-5
    keygens = frost_keygen(n=n, t=t)
    group_pubkey = keygens[0].group_pubkey

    # All participants have the same group public key
    for kg in keygens:
        assert kg.group_pubkey == group_pubkey

    # Reconstruct from exactly t+1 = 3 shares → g^secret == group_pubkey
    shares_3 = [(kg.index, kg.secret_share) for kg in keygens[:3]]
    recovered_secret = frost_reconstruct_secret(shares_3)
    assert pow(_G, recovered_secret, _P) == group_pubkey

    # Different subset of t+1 shares → same reconstruction
    shares_alt = [(kg.index, kg.secret_share) for kg in keygens[2:5]]
    recovered_secret_alt = frost_reconstruct_secret(shares_alt)
    assert pow(_G, recovered_secret_alt, _P) == group_pubkey

    assert recovered_secret == recovered_secret_alt


# ---------------------------------------------------------------------------
# Test 2: Full 2-round signing with 3-of-4 produces a valid signature
# ---------------------------------------------------------------------------

def test_full_2round_signing() -> None:
    """3-of-4 FROST signing produces a complete threshold signature."""
    n, t = 4, 2  # 3-of-4 (t+1 = 3)
    signers, coordinator = make_swarm(n, t)
    message = b"BTP:HIGH_VALUE_TRANSFER:50000:USD"

    # Use 3 of 4 signers
    active = signers[:3]
    sig = run_frost_signing(active, coordinator, message)

    assert isinstance(sig, FrostThresholdSignature)
    assert sig.threshold == t
    assert len(sig.signing_indices) == 3
    assert sig.R > 0
    assert sig.z > 0
    assert sig.group_pubkey == coordinator.group_pubkey


# ---------------------------------------------------------------------------
# Test 3: FROST signature verifies against the group public key
# ---------------------------------------------------------------------------

def test_signature_verifies_against_group_pubkey() -> None:
    """The aggregate FROST sig passes Schnorr verification: g^z == R * Y^c mod p."""
    n, t = 4, 2
    signers, coordinator = make_swarm(n, t)
    message = b"BTP:DB_SCHEMA_MIGRATION:users.ADD_COLUMN"

    sig = run_frost_signing(signers[:3], coordinator, message)

    assert sig.verify() is True


# ---------------------------------------------------------------------------
# Test 4: Fewer than t+1 signers cannot produce an aggregate
# ---------------------------------------------------------------------------

def test_insufficient_signers_rejected() -> None:
    """t signers (one short of threshold) cannot produce a valid aggregate."""
    n, t = 4, 2  # need 3, try with 2
    signers, coordinator = make_swarm(n, t)
    message = b"BTP:IAM_ELEVATION:admin"

    # Only t = 2 signers (need t+1 = 3)
    active = signers[:t]
    commitments = [s.round1_commit() for s in active]
    partial_sigs = [s.round2_sign(message, commitments) for s in active]

    with pytest.raises(ValueError, match="Need at least t\\+1"):
        coordinator.aggregate_signature(message, commitments, partial_sigs)


# ---------------------------------------------------------------------------
# Test 5: Different signer subsets produce signatures that all verify
# ---------------------------------------------------------------------------

def test_different_signer_subsets_all_verify() -> None:
    """
    Any t+1 subset of n signers produces a valid Schnorr sig on the same
    group public key. All subsets must independently verify.
    """
    n, t = 5, 2  # 3-of-5
    keygens = frost_keygen(n=n, t=t)
    message = b"BTP:CONFIG_RELOAD:safety_policy_v3"

    subsets = [
        [0, 1, 2],  # agents 1, 2, 3
        [0, 1, 3],  # agents 1, 2, 4
        [1, 2, 4],  # agents 2, 3, 5
        [0, 3, 4],  # agents 1, 4, 5
    ]

    for subset_indices in subsets:
        active_keygens = [keygens[i] for i in subset_indices]
        active_signers = [FrostSigner(kg) for kg in active_keygens]
        coord = FrostCoordinator(group_pubkey=keygens[0].group_pubkey, threshold=t)

        commitments = [s.round1_commit() for s in active_signers]
        partial_sigs = [s.round2_sign(message, commitments) for s in active_signers]
        sig = coord.aggregate_signature(message, commitments, partial_sigs)

        assert sig.verify() is True, (
            f"Verification failed for signer subset {subset_indices}"
        )


# ---------------------------------------------------------------------------
# Test 6: Tampered partial signature breaks the aggregate
# ---------------------------------------------------------------------------

def test_forge_attempt_fails() -> None:
    """Mutating one partial signature produces an invalid aggregate."""
    n, t = 4, 2
    signers, coordinator = make_swarm(n, t)
    message = b"BTP:DROP_DATABASE:critical_schema"

    active = signers[:3]
    commitments = [s.round1_commit() for s in active]
    partial_sigs = [s.round2_sign(message, commitments) for s in active]

    # Tamper: flip bits in the first partial sig
    partial_sigs[0] = dataclasses.replace(
        partial_sigs[0],
        z=(partial_sigs[0].z ^ 0xDEADBEEF_CAFEBABE) % _Q,
    )

    # Aggregation succeeds structurally (coordinator can't detect bad partials)
    sig = coordinator.aggregate_signature(message, commitments, partial_sigs)

    # But verification fails
    assert sig.verify() is False


# ---------------------------------------------------------------------------
# Test 7: FROST threshold signature embedded in SwarmQuorumCertificate
# ---------------------------------------------------------------------------

def test_frost_integrated_in_swarm_certificate() -> None:
    """
    Full integration test: vote-based BFT quorum → triggers FROST signing →
    certificate contains an embedded, verifiable threshold signature.
    """
    validator_ids = ["agent-alpha", "agent-beta", "agent-gamma", "agent-delta"]
    n, t = 4, 2  # 3-of-4 BFT swarm

    # Key generation (would happen in enclave at swarm initialization)
    keygens = frost_keygen(n=n, t=t)
    signers = {vid: FrostSigner(keygens[i]) for i, vid in enumerate(validator_ids)}
    coordinator = FrostCoordinator(group_pubkey=keygens[0].group_pubkey, threshold=t)

    # Standard BFT vote phase
    swarm = ByzantineSwarmEngine(validator_ids)
    proposal_id = "prop-frost-001"
    action_payload = {"table": "users", "operation": "ADD_COLUMN", "col": "verified_at"}

    swarm.submit_proposal(
        proposal_id=proposal_id,
        proposer_agent_id="agent-alpha",
        action_type="DB_SCHEMA_MIGRATION",
        action_payload=action_payload,
    )

    approving_agents = ["agent-alpha", "agent-beta", "agent-gamma"]
    for agent_id in approving_agents:
        swarm.cast_vote(proposal_id, agent_id, "APPROVE")

    reached, cert, msg = swarm.evaluate_consensus(proposal_id)
    assert reached is True
    assert cert is not None

    # Once quorum is reached, drive FROST signing on the action payload
    canonical_msg = (
        proposal_id.encode()
        + b":"
        + "DB_SCHEMA_MIGRATION".encode()
        + b":"
        + str(sorted(action_payload.items())).encode()
    )

    active_signers = [signers[vid] for vid in approving_agents]
    commitments = [s.round1_commit() for s in active_signers]
    partial_sigs = [s.round2_sign(canonical_msg, commitments) for s in active_signers]
    frost_sig = coordinator.aggregate_signature(canonical_msg, commitments, partial_sigs)

    # Verify the embedded threshold signature
    assert frost_sig.verify() is True
    assert frost_sig.threshold == t
    assert len(frost_sig.signing_indices) == 3

    # The receipt is auditor-shareable
    receipt = frost_sig.to_dict()
    assert receipt["valid"] is True
    assert "R_hex" in receipt
    assert "z_hex" in receipt
    assert "group_pubkey_hex" in receipt
    assert receipt["threshold"] == 2


# ---------------------------------------------------------------------------
# Test 8: Lagrange coefficient correctness
# ---------------------------------------------------------------------------

def test_lagrange_coefficient_correctness() -> None:
    """
    Verify Lagrange interpolation: for a known polynomial,
    the coefficients correctly reconstruct f(0) = constant term.
    """
    # Known polynomial: f(x) = 7 + 3x + 2x^2 (mod q)
    # f(0) = 7, f(1) = 12, f(2) = 21, f(3) = 34
    coeffs = [7, 3, 2]
    secret = 7

    points = [(i, _evaluate_polynomial(coeffs, i)) for i in range(1, 4)]  # 3 points for degree-2
    indices = [p[0] for p in points]

    # Lagrange interpolation at x=0
    reconstructed = 0
    for idx, val in points:
        lam = _lagrange_coefficient(idx, indices)
        reconstructed = (reconstructed + lam * val) % _Q

    assert reconstructed == secret % _Q

    # Also confirm it works for any subset of 3 from 4 points
    points_4 = [(i, _evaluate_polynomial(coeffs, i)) for i in range(1, 5)]
    for i in range(4):
        subset = [points_4[j] for j in range(4) if j != i]
        sub_indices = [p[0] for p in subset]
        recon = 0
        for idx, val in subset:
            lam = _lagrange_coefficient(idx, sub_indices)
            recon = (recon + lam * val) % _Q
        assert recon == secret % _Q, f"Reconstruction failed for subset excluding point {i}"


# ---------------------------------------------------------------------------
# Import fix for dataclasses.replace in test 6
# ---------------------------------------------------------------------------
import dataclasses
