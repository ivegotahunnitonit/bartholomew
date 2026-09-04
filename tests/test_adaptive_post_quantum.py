"""
Tests for BTP v2.9.0 — Adaptive State Machine & Post-Quantum Hybrid Migration
==============================================================================
Validates:
  1. Pre-computation nonce pools for sub-millisecond Round 1 dispatch.
  2. FaFROST adaptive signer dropout recovery mid-session.
  3. Post-quantum WOTS+ hash-based keygen, signing, and verification.
  4. Quantum signature forgery and tampered payload rejection.
  5. Dual-layer Hybrid Threshold Signature envelope verification.
"""

import hashlib
import json
import pytest

from src.frost_threshold_engine import frost_keygen
from src.adaptive_post_quantum_engine import (
    AdaptiveSwarmSigner,
    AdaptiveStateCoordinator,
    CeremonyState,
    PostQuantumEngine,
    create_hybrid_threshold_envelope,
)


def test_precomputed_nonce_pool():
    """Signer pre-computes nonces and retrieves them instantly."""
    keygens = frost_keygen(n=4, t=2)
    signer = AdaptiveSwarmSigner(keygens[0], pool_size=5)
    assert len(signer.nonce_pool) == 5

    nid, commitment = signer.get_precomputed_commitment()
    assert nid is not None
    assert commitment.signer_index == 1
    assert commitment.D > 0
    assert commitment.E > 0
    assert len(signer.nonce_pool) == 4


def test_adaptive_state_machine_dropout_recovery():
    """If a signer drops out during Round 2, the coordinator recovers using an alternate signer."""
    keygens = frost_keygen(n=5, t=2)  # 3-of-5 threshold
    signers = [AdaptiveSwarmSigner(kg, pool_size=5) for kg in keygens]
    coordinator = AdaptiveStateCoordinator(
        group_pubkey=keygens[0].group_pubkey,
        threshold=2,
        total_participants=5,
    )

    message = b"AUTONOMOUS_SWARM_CRITICAL_PAYLOAD_V29"

    # Initial Round 1 signers: 1, 2, 3
    initial_signers = [signers[0], signers[1], signers[2]]
    commitments = [s.get_precomputed_commitment()[1] for s in initial_signers]
    state = coordinator.register_commitments(commitments)
    assert state == CeremonyState.ROUND1_COMMITTED

    # Simulate signer 2 dropping out / network disconnect
    dropped_index = 2
    # Alternate replacement signer 4 joins
    replacement_signer = signers[3]
    ok, msg = coordinator.handle_signer_dropout(dropped_index, replacement_signer)
    assert ok is True
    assert coordinator.state == CeremonyState.ADAPTIVE_REBALANCED
    assert 2 not in coordinator.commitments
    assert 4 in coordinator.commitments

    # Round 2 partial signing across active set: 1, 3, 4
    active_set = [signers[0], signers[2], signers[3]]
    active_commits = [coordinator.commitments[s.index] for s in active_set]

    partial_sigs = [s.round2_sign(message, active_commits) for s in active_set]
    sig = coordinator.finalize_signature(message, partial_sigs)

    assert sig.verify() is True
    assert sig.signing_indices == [1, 3, 4]
    assert coordinator.state == CeremonyState.AGGREGATED


def test_post_quantum_wots_signing_and_verification():
    """Test quantum-resistant hash-based WOTS+ signature scheme."""
    payload = b"QUANTUM_SAFE_AUDIT_TRANSACTION"
    keypair = PostQuantumEngine.keygen()
    assert keypair.public_key_hex is not None
    assert len(keypair.public_key_hex) == 64

    # Sign
    sig_hex = PostQuantumEngine.sign(payload, keypair)
    assert sig_hex is not None
    assert len(bytes.fromhex(sig_hex)) == 64 * 32

    # Verify
    is_valid = PostQuantumEngine.verify_wots_signature(payload, sig_hex, keypair.public_key_hex)
    assert is_valid is True

    # Tampered payload fails
    tampered_payload = b"TAMPERED_TRANSACTION"
    assert PostQuantumEngine.verify_wots_signature(tampered_payload, sig_hex, keypair.public_key_hex) is False

    # Tampered signature fails
    tampered_sig = ("00" * 32) + sig_hex[64:]
    assert PostQuantumEngine.verify_wots_signature(payload, tampered_sig, keypair.public_key_hex) is False


def test_hybrid_threshold_envelope_dual_verification():
    """Test full hybrid envelope: classical FROST + post-quantum WOTS+."""
    keygens = frost_keygen(n=4, t=2)
    signers = [AdaptiveSwarmSigner(kg) for kg in keygens]
    coordinator = AdaptiveStateCoordinator(keygens[0].group_pubkey, threshold=2, total_participants=4)

    payload = b'{"action":"DEPLOY_ENCLAVE","pqc":"enabled"}'

    # Classical 3-of-4 FROST
    active_signers = signers[:3]
    commits = [s.get_precomputed_commitment()[1] for s in active_signers]
    coordinator.register_commitments(commits)
    partial_sigs = [s.round2_sign(payload, commits) for s in active_signers]
    frost_sig = coordinator.finalize_signature(payload, partial_sigs)
    assert frost_sig.verify() is True

    # Post-Quantum keypair
    pq_keypair = PostQuantumEngine.keygen()

    # Construct dual-layer hybrid envelope
    hybrid_envelope = create_hybrid_threshold_envelope(
        frost_sig=frost_sig,
        payload=payload,
        pq_keypair=pq_keypair,
    )

    # Verify both layers pass
    assert hybrid_envelope.verify(payload) is True

    # Tampering payload fails hybrid envelope
    assert hybrid_envelope.verify(b"FORGED_PAYLOAD") is False

    dict_repr = hybrid_envelope.to_dict()
    assert dict_repr["hybrid_valid"] is True
    assert dict_repr["quantum_security_bits"] == 128
