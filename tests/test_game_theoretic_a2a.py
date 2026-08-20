"""
Unit Tests for Autonomous Agent-to-Agent (A2A) Game-Theoretic Verification Engine
"""

import pytest
import sys
import os
import time

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.game_theoretic_engine import GameTheoreticStakeEngine, AgentToAgentGameSimulator
from bartholomew_eval.agent_protocol import (
    CryptographicIdentityCredential,
    CapabilityNegotiationRequest,
    VendorNeutralProtocolGateway,
    StandaloneIndependentVerifier
)

def test_nash_equilibrium_payoff_evaluation():
    engine = GameTheoreticStakeEngine(alpha_bounty_ratio=0.85)

    # Calculate required bond for $100 target asset at 10% posterior threat prob
    bond = engine.calculate_required_bond(
        potential_exploit_value_usd=100.0,
        posterior_threat_prob=0.10,
        agent_did="did:bth:agent_test_1"
    )

    assert bond >= 117.65  # 100 / 0.85 * (1 + 0.2)

    # Case 1: Honest Prover, Pass Challenger
    payoff_pass = engine.evaluate_payoff_matrix(
        prover_action="HONEST",
        challenger_action="PASS",
        prover_bond_usd=bond,
        challenger_stake_usd=10.0,
        execution_reward_usd=5.0,
        potential_exploit_usd=100.0
    )

    assert payoff_pass["outcome"] == "NASH_OPTIMAL_PASS"
    assert payoff_pass["payoff_prover_usd"] == 5.0
    assert payoff_pass["payoff_challenger_usd"] == 0.0
    assert payoff_pass["is_nash_equilibrium"] is True

    # Case 2: Adversarial Prover caught by Challenger Audit
    payoff_slash = engine.evaluate_payoff_matrix(
        prover_action="ADVERSARIAL",
        challenger_action="AUDIT",
        prover_bond_usd=bond,
        challenger_stake_usd=10.0,
        execution_reward_usd=5.0,
        potential_exploit_usd=100.0
    )

    assert payoff_slash["outcome"] == "DEFECT_CAUGHT_AND_SLASHED"
    assert payoff_slash["payoff_prover_usd"] == -bond
    assert payoff_slash["payoff_challenger_usd"] > 10.0  # Earned bounty bonus


def test_grim_trigger_reputation_tracking():
    engine = GameTheoreticStakeEngine(default_discount_factor=0.95)
    agent_did = "did:bth:rogue_agent_99"

    # Clean game
    engine.record_agent_game_outcome(agent_did, "NASH_OPTIMAL_PASS")
    assert engine.agent_history[agent_did]["defects"] == 0
    assert engine.agent_history[agent_did]["grim_triggered"] is False

    # Defect game
    engine.record_agent_game_outcome(agent_did, "DEFECT_CAUGHT_AND_SLASHED")
    assert engine.agent_history[agent_did]["defects"] == 1
    assert engine.agent_history[agent_did]["grim_triggered"] is True
    assert engine.agent_history[agent_did]["discount_factor"] < 0.95  # Penalty applied


def test_a2a_protocol_request_with_bonded_collateral():
    gateway = VendorNeutralProtocolGateway()
    org_c_verifier = StandaloneIndependentVerifier(
        pinned_root_pub_keys={"did:bth:org_a_root": "pubkey_org_a_ed25519_key_101"}
    )

    cred = CryptographicIdentityCredential(
        agent_did="did:bth:org_a_agent_bonded",
        issuer_did="did:bth:org_a_root",
        issuer_pub_key="pubkey_org_a_ed25519_key_101",
        possessed_capabilities=["database.write"],
        constraint_manifest=[]
    )

    req = CapabilityNegotiationRequest(
        request_id="req_bonded_001",
        nonce=f"nonce_bonded_{int(time.time())}",
        timestamp_epoch=time.time(),
        credential=cred,
        intent_requested_capability="database.write",
        action_payload={"table": "financial_records"},
        context_conditions={},
        target_system="Prod_DB",
        bonded_collateral_usd=250.00,
        challenger_address="did:bth:auditor_red_team"
    )

    res = gateway.verify_request(req)
    assert res["decision"] == "ALLOW"
    artifact = res["evidence_artifact"]
    assert artifact["bonded_collateral_usd"] == 250.00
    assert artifact["challenger_address"] == "did:bth:auditor_red_team"

    # Verify offline with Org C Standalone Verifier
    verified_ok, msg = org_c_verifier.verify_evidence_artifact_independently(artifact)
    assert verified_ok is True


def test_a2a_multi_round_simulator():
    sim = AgentToAgentGameSimulator()
    benchmark_res = sim.run_multi_round_simulation(num_rounds=25)

    assert benchmark_res["total_rounds"] == 25
    assert benchmark_res["exploit_prevention_rate_pct"] > 50.0
    assert benchmark_res["throughput_cycles_per_sec"] > 100.0
