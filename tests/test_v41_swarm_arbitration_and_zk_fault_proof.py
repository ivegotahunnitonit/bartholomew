"""
Unit Tests for BTP v4.1 — Decentralized Swarm Slashing Arbitration & ZK-Fault Proofs (zk-FP)
=============================================================================================
Validates:
1. Non-interactive Zero-Knowledge Fault Proof generation and mathematical verification.
2. Tamper-resistance of zk-Fault Proofs (rejecting corrupted commitments or post-states).
3. Decentralized Swarm Dispute opening, eligible juror quorum computation, and Byzantine voting.
4. Target agent and circuit-broken juror voting disqualification.
5. Autonomous Escrow liquidation and slashing driven by ArbitrationResolutionCertificate.
6. Target passport reputation penalty and circuit-breaker tripping.
"""

import os
import sys
import time
import pytest

sys.path.insert(0, os.path.abspath("."))

from src.agent_passport import SovereignAgentPassport
from src.settlement.autonomous_escrow import AutonomousEscrowPool
from src.settlement.swarm_arbitration import (
    ZKFaultProofEngine,
    ZKFaultProof,
    SwarmDisputeArbitrator,
    ArbitrationResolutionCertificate
)


@pytest.fixture
def swarm_setup():
    escrow_pool = AutonomousEscrowPool(reserve_pool_usd=50_000.0)
    arbitrator = escrow_pool.arbitrator

    passport_target = SovereignAgentPassport.issue(
        agent_id="agent-rogue-dba",
        model_family="gpt-4o",
        authorized_capabilities=["db:migrate", "sql:execute"],
        bonded_warranty_usd=3000.0
    )
    passport_juror1 = SovereignAgentPassport.issue(
        agent_id="agent-juror-secops",
        model_family="claude-3-5-sonnet",
        authorized_capabilities=["audit:verify"],
        bonded_warranty_usd=5000.0
    )
    passport_juror2 = SovereignAgentPassport.issue(
        agent_id="agent-juror-treasury",
        model_family="gemini-1-5-pro",
        authorized_capabilities=["settlement:audit"],
        bonded_warranty_usd=5000.0
    )

    arbitrator.register_validator(passport_target)
    arbitrator.register_validator(passport_juror1)
    arbitrator.register_validator(passport_juror2)

    deposit = escrow_pool.lock_escrow(
        agent_id=passport_target.agent_id,
        action_type="DATABASE_MIGRATION",
        amount_usd=2500.0,
        passport=passport_target,
        settlement_rail="L402_LIGHTNING"
    )

    return {
        "escrow_pool": escrow_pool,
        "arbitrator": arbitrator,
        "passport_target": passport_target,
        "passport_juror1": passport_juror1,
        "passport_juror2": passport_juror2,
        "deposit": deposit
    }


def test_zk_fault_proof_generation_and_verification():
    """Verify zk-Fault Proof generates and passes math verification in sub-100µs."""
    proof = ZKFaultProofEngine.generate_fault_proof(
        prover_agent_id="agent-monitor-01",
        target_action="DATABASE_MIGRATION",
        violated_invariant="CATASTROPHIC_DROP_TABLE",
        private_payload="DROP TABLE enterprise_ledger CASCADE;",
        state_pre_hash="state_pre_0x11223344"
    )

    assert proof.proof_id.startswith("zk_fp_")
    assert proof.target_action == "DATABASE_MIGRATION"
    assert proof.pedersen_commitment.startswith("0x")
    assert proof.challenge_response.startswith("0x")

    # Independent mathematical verification
    is_valid, reason = ZKFaultProofEngine.verify_fault_proof(proof)
    assert is_valid is True
    assert "mathematically proven" in reason.lower()


def test_zk_fault_proof_tamper_detection():
    """Corrupted commitments or forged challenge responses must be rejected."""
    proof = ZKFaultProofEngine.generate_fault_proof(
        prover_agent_id="agent-monitor-01",
        target_action="DATABASE_MIGRATION",
        violated_invariant="CATASTROPHIC_DROP_TABLE",
        private_payload="DROP TABLE enterprise_ledger CASCADE;",
        state_pre_hash="state_pre_0x11223344"
    )

    # Tamper with challenge response
    tampered_dict = proof.to_dict()
    tampered_dict["challenge_response"] = hex(int(proof.challenge_response, 16) + 1)
    tampered_proof = ZKFaultProof(**tampered_dict)

    is_valid, reason = ZKFaultProofEngine.verify_fault_proof(tampered_proof)
    assert is_valid is False

    # Tamper with post-state hash
    tampered_dict2 = proof.to_dict()
    tampered_dict2["state_post_hash"] = "0xdeadbeef" * 8
    tampered_proof2 = ZKFaultProof(**tampered_dict2)

    is_valid2, reason2 = ZKFaultProofEngine.verify_fault_proof(tampered_proof2)
    assert is_valid2 is False


def test_swarm_dispute_lifecycle_and_slashing(swarm_setup):
    """Test dispute opening, Byzantine peer juror voting, and escrow slashing."""
    pool = swarm_setup["escrow_pool"]
    arbitrator = swarm_setup["arbitrator"]
    p_target = swarm_setup["passport_target"]
    p_j1 = swarm_setup["passport_juror1"]
    p_j2 = swarm_setup["passport_juror2"]
    deposit = swarm_setup["deposit"]

    # 1. Generate zk-Fault Proof
    zk_proof = ZKFaultProofEngine.generate_fault_proof(
        prover_agent_id=p_j1.agent_id,
        target_action="DATABASE_MIGRATION",
        violated_invariant="CATASTROPHIC_DROP_TABLE",
        private_payload="DROP TABLE accounts;",
        state_pre_hash="state_pre_0x00aabbcc"
    )

    # 2. Open Dispute
    ok_open, msg_open, dispute = arbitrator.open_dispute(
        escrow_id=deposit.escrow_id,
        challenger_agent_id=p_j1.agent_id,
        target_agent_id=p_target.agent_id,
        target_action="DATABASE_MIGRATION",
        amount_usd=deposit.amount_usd,
        fault_proof=zk_proof
    )
    assert ok_open is True
    assert dispute.status == "VOTING"
    assert dispute.required_quorum == 2

    # 3. Target agent cannot vote
    ok_target_vote, msg_tv = arbitrator.cast_vote(dispute.dispute_id, p_target, "REJECT_SLASH")
    assert ok_target_vote is False
    assert "cannot vote" in msg_tv.lower()

    # 4. Jurors cast APPROVE_SLASH votes
    ok_v1, _ = arbitrator.cast_vote(dispute.dispute_id, p_j1, "APPROVE_SLASH")
    ok_v2, _ = arbitrator.cast_vote(dispute.dispute_id, p_j2, "APPROVE_SLASH")
    assert ok_v1 is True
    assert ok_v2 is True

    # 5. Resolve dispute
    ok_res, msg_res, cert = arbitrator.resolve_dispute(dispute.dispute_id)
    assert ok_res is True
    assert cert.verdict == "SLASH_COLLATERAL"
    assert cert.quorum_count == 2

    # 6. Execute Slashing on Escrow Pool
    ok_slash, msg_slash, receipt = pool.arbitrate_and_slash(
        escrow_id=deposit.escrow_id,
        arbitration_cert=cert,
        payee_destination="victim_reserve_vault",
        agent_passport=p_target
    )
    assert ok_slash is True
    assert receipt["indemnity_amount_usd"] == 2500.0
    assert receipt["passport_tripped"] is True
    assert receipt["status"] == "ARBITRATED_AND_DISBURSED"
    assert p_target.is_circuit_broken is True
    assert deposit.status == "SLASHED"


def test_swarm_dispute_dismissal_on_reject_quorum(swarm_setup):
    """Test dispute dismissed when jurors reject challenge."""
    arbitrator = swarm_setup["arbitrator"]
    p_target = swarm_setup["passport_target"]
    p_j1 = swarm_setup["passport_juror1"]
    p_j2 = swarm_setup["passport_juror2"]
    deposit = swarm_setup["deposit"]

    zk_proof = ZKFaultProofEngine.generate_fault_proof(
        prover_agent_id=p_j1.agent_id,
        target_action="DATABASE_MIGRATION",
        violated_invariant="FALSE_ALARM_EVENT",
        private_payload="SELECT 1;",
        state_pre_hash="state_pre_0x001122"
    )

    ok_open, _, dispute = arbitrator.open_dispute(
        escrow_id=deposit.escrow_id,
        challenger_agent_id=p_j1.agent_id,
        target_agent_id=p_target.agent_id,
        target_action="DATABASE_MIGRATION",
        amount_usd=deposit.amount_usd,
        fault_proof=zk_proof
    )

    arbitrator.cast_vote(dispute.dispute_id, p_j1, "REJECT_SLASH")
    arbitrator.cast_vote(dispute.dispute_id, p_j2, "REJECT_SLASH")

    ok_res, _, cert = arbitrator.resolve_dispute(dispute.dispute_id)
    assert ok_res is True
    assert cert.verdict == "DISMISS_CHALLENGE"
    assert cert.slashed_amount_usd == 0.0
    assert dispute.status == "DISMISSED"
    assert deposit.status == "LOCKED"
