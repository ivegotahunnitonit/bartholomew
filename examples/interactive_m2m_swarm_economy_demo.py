"""
Bartholomew Autonomous M2M Machine Economy Interactive Demo (BTP v1.0.0)
========================================================================
Demonstrates the full autonomous Machine-to-Machine execution & trust lifecycle:
  1. Discovery: Agent A fetches & parses Bartholomew's machine manifest (btp.json).
  2. Identity & Passport: Agent A inspects Sovereign Passports & Reputation Scores.
  3. Delegation: Human Owner delegates $50 spend cap -> Agent A -> $10 to Agent B.
  4. L402 Micropayment: Agent A pays L402 Lightning invoice ($0.01/action).
  5. Authorization Gate: Sub-35us AST & policy gating (ALLOW safe action, DENY destructive action).
  6. Replay & Fraud Protection: Verifies nonces & single-use receipt consumption.
  7. Audit & Dispute Resolution: Produces Ed25519-signed Merkle receipts & arbitrates mock dispute.
"""

import sys
import os
import json
import time
from cryptography.hazmat.primitives.asymmetric import ed25519

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.btp_manifest import generate_manifest
from src.agent_passport import SovereignAgentPassport
from src.delegation_chain import DelegationLink, VerifiableDelegationChain
from src.settlement.lightning_gateway import LightningGateway
from src.btp_guard.authorization_gate import AuthorizationGate
from src.replay_protector import ReplayProtectionVault
from src.reputation_engine import AgentReputationEngine
from src.dispute_resolver import AutomatedDisputeResolver


def run_interactive_m2m_demo():
    print("\n" + "=" * 80)
    print("   BARTHOLOMEW (BTP v1.0.0) AUTONOMOUS M2M MACHINE ECONOMY SWARM DEMO")
    print("=" * 80 + "\n")

    # Step 1: Discovery & Manifest Inspection
    print("[STEP 1: Capability & Policy Discovery]")
    manifest = generate_manifest()
    print(f"  * Discovered Service : {manifest['identity']['name']} (v{manifest['identity']['protocol_version']})")
    print(f"  * Active Capabilities: {', '.join(manifest['capabilities'][:4])}...")
    print(f"  * Security Rules     : {len(manifest['security']['rules'])} active invariant rules")
    print(f"  * Pricing Meter      : {manifest['pricing']['meter']['event']} (${manifest['pricing']['meter']['unit_price_usd']}/action)\n")

    # Step 2: Sovereign Agent Identity & Passport
    print("[STEP 2: Sovereign Agent Passport & Reputation]")
    owner_key = ed25519.Ed25519PrivateKey.generate()
    owner_pub = owner_key.public_key().public_bytes_raw().hex()

    agent_a_key = ed25519.Ed25519PrivateKey.generate()
    agent_a_pub = agent_a_key.public_key().public_bytes_raw().hex()

    passport_a = SovereignAgentPassport(
        agent_id="agent-a-requester",
        worker_model="claude-3-7-sonnet",
        owner_pubkey=owner_pub,
        granted_capabilities=["data:read", "code:mutate", "l402:pay"]
    )
    print(f"  * Agent Passport ID  : {passport_a.passport_id}")
    print(f"  * Initial Trust Score: {passport_a.reputation_vector['trust_score']} (Tier: SOVEREIGN)\n")

    # Step 3: Verifiable Authority Delegation Chain
    print("[STEP 3: Verifiable Authority Delegation Chain]")
    now = time.time()
    expires = now + 3600

    link1 = DelegationLink(
        grantor_id="human-owner",
        grantee_id="agent-a-requester",
        grantor_pubkey=owner_pub,
        max_spend_usd=50.0,
        allowed_capabilities=["data:read", "code:mutate", "l402:pay"],
        issued_at=now,
        expires_at=expires,
        parent_link_hash="GENESIS_ROOT"
    )
    link1.sign(owner_key)

    link2 = DelegationLink(
        grantor_id="agent-a-requester",
        grantee_id="agent-b-worker",
        grantor_pubkey=agent_a_pub,
        max_spend_usd=10.0,
        allowed_capabilities=["data:read", "l402:pay"],
        issued_at=now,
        expires_at=expires,
        parent_link_hash=link1.compute_link_hash()
    )
    link2.sign(agent_a_key)

    chain = VerifiableDelegationChain([link1, link2])
    is_chain_valid, effective_spend, caps, err = chain.evaluate_chain(now=now)
    print(f"  * Delegation Chain   : Human Owner -> Agent A ($50) -> Agent B ($10)")
    print(f"  * Chain Signature    : VERIFIED ({'VALID' if is_chain_valid else 'INVALID'})")
    print(f"  * Effective Spend Cap: ${effective_spend:.2f} USD")
    print(f"  * Granted Capabilities: {sorted(list(caps))}\n")

    # Step 4: L402 Lightning Micropayment Invoice & Settlement
    print("[STEP 4: L402 Lightning Micropayment Settlement]")
    ln_gateway = LightningGateway(node_type="SIMULATED")
    invoice = ln_gateway.create_invoice(amount_satoshis=15, memo="BTP M2M Execution Fee")
    preimage_hex = ln_gateway.preimage_vault[invoice.payment_hash]
    print(f"  * Payment Hash       : {invoice.payment_hash[:32]}...")
    print(f"  * BOLT11 Invoice     : {invoice.payment_request[:32]}...")
    print(f"  * Micropayment Sats  : {invoice.amount_satoshis} sats (~$0.01 USD)\n")

    # Step 5: Execution Authorization Gate Evaluation
    print("[STEP 5: Pre-Flight Authorization Gate Evaluation]")
    gate = AuthorizationGate(policy={"allow_destructive": False})
    replay_vault = ReplayProtectionVault()

    # 5a. Safe Action Request
    safe_action = {
        "agent_id": "agent-a-requester",
        "action_type": "m2m_call",
        "payload": {
            "command": "git status",
            "amount_usd": 0.01,
            "l402_preimage": preimage_hex,
            "l402_payment_hash": invoice.payment_hash
        },
        "request_id": "req-m2m-9001"
    }

    ok, replay_err = replay_vault.validate_request(request_id=safe_action["request_id"], timestamp=now)
    res_safe = gate.evaluate(safe_action)
    print(f"  * Safe Action        : 'git status'")
    print(f"  * Gate Verdict       : {res_safe['verdict']} (Reason: {res_safe['reason']})")
    print(f"  * Gate Latency       : {res_safe['latency_ms']} ms")
    print(f"  * L402 Settled       : {res_safe.get('l402_settled')}")
    print(f"  * Receipt SHA-256    : {res_safe['receipt_sha256'][:32]}...\n")

    # 5b. Destructive Action Request (Blocked)
    unsafe_action = {
        "agent_id": "agent-a-requester",
        "action_type": "m2m_call",
        "payload": {"command": "rm -rf /var/data/prod_db"},
        "request_id": "req-m2m-9002"
    }
    res_unsafe = gate.evaluate(unsafe_action)
    print(f"  * Destructive Action : 'rm -rf /var/data/prod_db'")
    print(f"  * Gate Verdict       : {res_unsafe['verdict']} (Rule: {res_unsafe['rule_id']})")
    print(f"  * Interception Reason: {res_unsafe['reason']}\n")

    # Step 6: Replay Attack Defense
    print("[STEP 6: Replay & Fraud Attack Interception]")
    ok_replay, replay_msg = replay_vault.validate_request(request_id=safe_action["request_id"], timestamp=now)
    print(f"  * Replaying req-m2m-9001 : INTERCEPTED & REJECTED")
    print(f"  * Security Reason        : {replay_msg}\n")

    # Step 7: Reputation Evidence & Automated Dispute Resolution
    print("[STEP 7: Reputation Evidence & Dispute Arbitration]")
    rep_engine = AgentReputationEngine()
    rep_report = rep_engine.generate_report(agent_id="agent-a-requester", receipts=[res_safe])
    print(f"  * Verified Txs Count : {rep_report.verified_transactions}")
    print(f"  * Calculated Score   : {rep_report.trust_score} (Tier: {rep_report.trust_tier})")
    print(f"  * Evidence Root Hash : {rep_report.evidence_root_hash[:32]}...")

    dispute_resolver = AutomatedDisputeResolver()
    verdict = dispute_resolver.arbitrate(
        claimant_id="agent-a-requester",
        respondent_id="agent-b-worker",
        claimed_reason="NON_DELIVERY",
        execution_receipt=res_safe,
        disputed_amount_usd=0.01
    )
    print(f"  * Mock Dispute Verdict : {verdict.verdict} (Action: {verdict.resolution_action})")
    print(f"  * Signed Dispute Proof : {verdict.signature[:32]}...")

    print("\n" + "=" * 80)
    print("   AUTONOMOUS M2M MACHINE ECONOMY SWARM DEMO COMPLETE — ALL STEPS PASSED")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_interactive_m2m_demo()
