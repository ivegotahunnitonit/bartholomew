#!/usr/bin/env python3
"""
Autonomous Agent-to-Agent (A2A) Game-Theoretic Verification Benchmark
========================================================================
Executes a 1,000-cycle simulation benchmarking Nash Equilibrium payoff dynamics,
prover collateral bonding, challenger audit red-teaming, and exploit suppression.
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.game_theoretic_engine import GameTheoreticStakeEngine, AgentToAgentGameSimulator
from bartholomew_eval.agent_protocol import (
    CryptographicIdentityCredential,
    CapabilityNegotiationRequest,
    VendorNeutralProtocolGateway,
    StandaloneIndependentVerifier
)

def run_a2a_game_theoretic_benchmark():
    print("=" * 110)
    print("BARTHOLOMEW: AUTONOMOUS AGENT-TO-AGENT (A2A) GAME-THEORETIC VERIFICATION BENCHMARK")
    print("=" * 110)
    print("Execution Mode: 100% Autonomous Agent-to-Agent (Zero Human In The Loop)\n")

    sim = AgentToAgentGameSimulator()

    print(">>> [PHASE 1: Executing 1,000 Autonomous A2A Interaction Rounds...]")
    benchmark_results = sim.run_multi_round_simulation(
        num_rounds=1000,
        prover_did="did:bth:prover_enclave_alpha",
        challenger_did="did:bth:red_team_auditor_beta"
    )

    print("\n" + "=" * 110)
    print("EXECUTIVE A2A GAME-THEORETIC BENCHMARK RESULTS")
    print("=" * 110)
    print(f"- Total Autonomous A2A Rounds Executed  : {benchmark_results['total_rounds']:,}")
    print(f"- Caught & Slashed Adversarial Attempts  : {benchmark_results['caught_defects']:,}")
    print(f"- Leaked Un-audited Exploits             : {benchmark_results['leaked_exploits']:,}")
    print(f"- Exploit Suppression Success Rate      : {benchmark_results['exploit_prevention_rate_pct']:.2f}%")
    print(f"- Net Prover Economic Payout             : ${benchmark_results['total_prover_net_usd']:,.2f}")
    print(f"- Net Challenger Bounty Payout           : ${benchmark_results['total_challenger_net_usd']:,.2f}")
    print(f"- Benchmark Elapsed Duration             : {benchmark_results['elapsed_ms']:.2f} ms")
    print(f"- Autonomous Execution Throughput        : {benchmark_results['throughput_cycles_per_sec']:,.1f} cycles/sec")
    print("=" * 110)

    print("\n>>> [PHASE 2: Verifying Standalone Offline 3-Org Cryptographic Proof Compatibility...]")
    gateway = VendorNeutralProtocolGateway()
    org_c_verifier = StandaloneIndependentVerifier(
        pinned_root_pub_keys={"did:bth:org_a_root": "pubkey_org_a_ed25519_key_101"}
    )

    cred = CryptographicIdentityCredential(
        agent_did="did:bth:org_a_agent_autonomous",
        issuer_did="did:bth:org_a_root",
        issuer_pub_key="pubkey_org_a_ed25519_key_101",
        possessed_capabilities=["financial.settlement"],
        constraint_manifest=["max_cost_1000"]
    )

    req = CapabilityNegotiationRequest(
        request_id="req_a2a_bench_001",
        nonce=f"nonce_a2a_{int(time.time())}",
        timestamp_epoch=time.time(),
        credential=cred,
        intent_requested_capability="financial.settlement",
        action_payload={"amount": 450.00},
        context_conditions={"environment": "production"},
        target_system="Settlement_Gateway",
        bonded_collateral_usd=529.41,
        challenger_address="did:bth:auditor_red_team"
    )

    res = gateway.verify_request(req)
    verified_ok, msg = org_c_verifier.verify_evidence_artifact_independently(res["evidence_artifact"])

    print(f"    - Protocol Gateway Decision          : {res['decision']}")
    print(f"    - Bonded Collateral Recorded         : ${res['evidence_artifact']['bonded_collateral_usd']:.2f}")
    print(f"    - Cryptographic Evidence Proof      : {res['evidence_artifact']['ed25519_proof']}")
    print(f"    - Standalone Independent Verifier   : {'PASSED (100% Offline)' if verified_ok else 'FAILED'}")
    print(f"    - Verifier Output Message            : '{msg}'")
    print("=" * 110 + "\n")

    return benchmark_results

if __name__ == "__main__":
    run_a2a_game_theoretic_benchmark()
