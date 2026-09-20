"""
Tests for BTP v3.5 Recursive ZK-Rollups, Hardware Enclave Anchors,
Vectorized Crypto, and Milestone 3.2 Dynamic Invariant Engine.
"""

import pytest
import time
import copy
from src.zk_compliance_proof_engine import ZKComplianceEngine, ZKComplianceProof
from src.zk_rollup_batcher import ZKRollupBatch, ZKRollupBatcher, EnclaveZKRollupAnchor
from src.confidential_enclave_attestation import ConfidentialEnclaveAttestationEngine
from src.native_core.vectorized_crypto import VectorizedCrypto
from src.ebpf_kernel_guard import HotPluggableInvariantEngine, DynamicThresholdRebalancer, KernelSyscallEvent


def test_zk_rollup_batcher_aggregation_and_verification():
    engine = ZKComplianceEngine()
    batcher = ZKRollupBatcher(batch_id="urn:btp:zk-rollup:test-001")

    proofs = []
    # Generate 3 independent session compliance proofs
    for i in range(3):
        session_id = f"session-agent-{i+1}"
        tool_calls = [
            f"cat /workspace/docs_{i}.txt",
            f"grep pattern /workspace/log_{i}.txt"
        ]
        proof = engine.prove_session(session_id=session_id, tool_calls=tool_calls)
        proofs.append(proof)
        batcher.add_proof(proof)

    rollup = batcher.seal()

    assert rollup.session_count == 3
    assert rollup.total_tool_calls == 6
    assert rollup.sealed is True
    assert rollup.merkle_root is not None
    assert rollup.aggregate_commitment.startswith("0x")
    assert rollup.aggregate_response.startswith("0x")

    # Verify rollup with and without original proofs
    valid, msg = ZKRollupBatcher.verify_rollup(rollup)
    assert valid is True
    assert "Verified Clean" in msg

    valid_with_proofs, msg_proofs = ZKRollupBatcher.verify_rollup(rollup, original_proofs=proofs)
    assert valid_with_proofs is True
    assert "Verified Clean" in msg_proofs


def test_zk_rollup_batcher_empty_raises():
    batcher = ZKRollupBatcher()
    with pytest.raises(ValueError, match="Cannot seal empty ZKRollupBatch"):
        batcher.seal()


def test_zk_rollup_tampering_rejection():
    engine = ZKComplianceEngine()
    batcher = ZKRollupBatcher()

    proofs = []
    for i in range(2):
        proof = engine.prove_session(
            session_id=f"sess-{i}",
            tool_calls=[f"sanitize_input --id {i}"]
        )
        proofs.append(proof)
        batcher.add_proof(proof)

    rollup = batcher.seal()

    # 1. Tamper with Merkle leaf
    tampered_rollup = copy.deepcopy(rollup)
    tampered_rollup.leaf_proof_digests[0] = "0" * 64
    valid, err = ZKRollupBatcher.verify_rollup(tampered_rollup)
    assert valid is False
    assert "Merkle root mismatch" in err

    # 2. Tamper with Fiat-Shamir challenge
    tampered_rollup2 = copy.deepcopy(rollup)
    tampered_rollup2.batch_challenge = "f" * 64
    valid2, err2 = ZKRollupBatcher.verify_rollup(tampered_rollup2)
    assert valid2 is False
    assert "Batch challenge verification failed" in err2


def test_hardware_enclave_rollup_anchor():
    engine = ZKComplianceEngine()
    batcher = ZKRollupBatcher()

    for i in range(2):
        proof = engine.prove_session(
            session_id=f"enclave-sess-{i}",
            tool_calls=[f"query_db --id {i}"]
        )
        batcher.add_proof(proof)

    rollup = batcher.seal()
    enclave_engine = ConfidentialEnclaveAttestationEngine()

    anchor = EnclaveZKRollupAnchor.create_hardware_anchor(
        rollup=rollup,
        enclave_engine=enclave_engine,
        module_id="nitro-rollup-core-test"
    )

    assert anchor["status"] == "HARDWARE_ANCHORED_AND_ATTESTED"
    assert "hardware_enclave_attestation" in anchor
    assert anchor["merkle_root"] == rollup.merkle_root

    # Verify hardware anchor
    is_valid, msg = EnclaveZKRollupAnchor.verify_hardware_anchor(
        anchor_data=anchor,
        enclave_engine=enclave_engine
    )
    assert is_valid is True
    assert "Verified Clean" in msg

    # Tamper with PCR measurement
    tampered_anchor = copy.deepcopy(anchor)
    tampered_anchor["hardware_enclave_attestation"]["measurements"]["pcr0"] = "a" * 64
    is_valid_t, err_t = EnclaveZKRollupAnchor.verify_hardware_anchor(
        anchor_data=tampered_anchor,
        enclave_engine=enclave_engine
    )
    assert is_valid_t is False
    assert "PCR0 measurement tampered" in err_t


def test_vectorized_crypto_math_and_throughput():
    witnesses = [12345, 67890, 112233]
    blindings = [99999, 88888, 77777]

    # Vectorized commitments match serial commitments
    batch_commits = VectorizedCrypto.batch_pedersen_commit(witnesses, blindings, chunk_size=2)
    assert len(batch_commits) == 3

    from src.zk_compliance_proof_engine import _P, _G, _H
    for i in range(3):
        expected = (pow(_G, witnesses[i], _P) * pow(_H, blindings[i], _P)) % _P
        assert batch_commits[i] == expected

    # Batch homomorphic aggregation
    responses = [100, 200, 300]
    c_agg, s_agg = VectorizedCrypto.batch_homomorphic_aggregate(batch_commits, responses)
    expected_c_agg = (batch_commits[0] * batch_commits[1] * batch_commits[2]) % _P
    assert c_agg == expected_c_agg
    assert s_agg == 600

    # Fast Merkle root
    payloads = [b"leaf_1", b"leaf_2", b"leaf_3"]
    hashes = VectorizedCrypto.batch_merkle_leaves_hash(payloads)
    root = VectorizedCrypto.fast_merkle_root(hashes)
    assert len(root) == 32

    # Benchmark run
    bench = VectorizedCrypto.benchmark_throughput(num_samples=50)
    assert bench["num_samples"] == 50
    assert bench["serial_ops_per_sec"] > 0
    assert bench["batch_ops_per_sec"] > 0
    assert "merkle_root" in bench


def test_hot_pluggable_invariant_engine():
    engine = HotPluggableInvariantEngine()
    assert engine.generation == 1

    # Hot reload a new rule
    ok, msg, gen = engine.hot_reload_rules(
        new_blocked_binaries=["custom_malware_tool"],
        new_protected_paths=["/etc/custom_secret"],
        change_rationale="Live zero-day mitigation"
    )
    assert ok is True
    assert gen == 2
    assert engine.generation == 2
    assert "custom_malware_tool" in engine.active_policy.blocked_binaries

    # Rollback to generation 1
    rolled_back, rb_msg, rb_gen = engine.rollback()
    assert rolled_back is True
    assert rb_gen == 1
    assert engine.generation == 1
    assert "custom_malware_tool" not in engine.active_policy.blocked_binaries


def test_dynamic_threshold_rebalancer():
    rebalancer = DynamicThresholdRebalancer()
    assert (rebalancer.current_k, rebalancer.current_n) == (2, 3)

    # 1. Normal baseline events (all allowed)
    normal_events = [
        KernelSyscallEvent(
            pid=1001, uid=1000, syscall_nr=59, action="ALLOW", comm="python", target="script.py", timestamp_ns=time.time_ns()
        )
        for _ in range(20)
    ]
    entropy, k, n, status = rebalancer.evaluate_threat_entropy(normal_events)
    assert (k, n) == (2, 3)
    assert status == "NORMAL_BASELINE"

    # 2. Elevated threat: 20% blocked
    elevated_events = [
        KernelSyscallEvent(
            pid=1001, uid=1000, syscall_nr=59, action="BLOCK" if i % 5 == 0 else "ALLOW", comm="python", target="scan", timestamp_ns=time.time_ns()
        )
        for i in range(50)
    ]
    entropy_e, k_e, n_e, status_e = rebalancer.evaluate_threat_entropy(elevated_events)
    assert (k_e, n_e) == (3, 5)
    assert status_e == "ELEVATED_THREAT_REBALANCED"

    # 3. Critical threat: 50% blocked
    critical_events = [
        KernelSyscallEvent(
            pid=1001, uid=1000, syscall_nr=59, action="BLOCK" if i % 2 == 0 else "ALLOW", comm="python", target="exfil", timestamp_ns=time.time_ns()
        )
        for i in range(50)
    ]
    entropy_c, k_c, n_c, status_c = rebalancer.evaluate_threat_entropy(critical_events)
    assert (k_c, n_c) == (5, 7)
    assert status_c == "CRITICAL_ATTACK_ELEVATION"
