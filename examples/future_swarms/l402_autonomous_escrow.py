"""
Cookbook Recipe: Autonomous Micro-Escrow & L402 Cross-Chain Slashing
=====================================================================
Demonstrates programmatic collateral locking and trustless automated slashing
when an autonomous agent violates safety invariants.

Run:
    python cookbook/future_swarms/l402_autonomous_escrow.py
"""

import sys
import os

# Add repository root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.settlement.autonomous_escrow import AutonomousEscrowPool
from src.agent_passport import SovereignAgentPassport
from cryptography.hazmat.primitives.asymmetric import ed25519


def main():
    print("=" * 75)
    print("  BTP Global Cookbook: Autonomous Micro-Escrow & Slashing Demo")
    print("=" * 75)

    pool = AutonomousEscrowPool(reserve_pool_usd=100_000.0)

    # 1. Authority and Agent Passport Setup
    owner_key = ed25519.Ed25519PrivateKey.generate()
    owner_pubkey_hex = owner_key.public_key().public_bytes_raw().hex()

    passport = SovereignAgentPassport(
        agent_id="Agent-Production-Worker-09",
        worker_model="Llama-3.3-70B",
        owner_pubkey=owner_pubkey_hex,
        granted_capabilities=["db:write", "api:pay"]
    )
    passport.sign(owner_key)

    # 2. Lock Micro-Escrow Before High-Risk Action
    print("\n--- [1] Locking Collateral Micro-Escrow for High-Risk Action ---")
    deposit = pool.lock_escrow(
        agent_id="Agent-Production-Worker-09",
        action_type="HIGH_VALUE_SETTLEMENT",
        amount_usd=2_500.0,
        passport=passport,
        settlement_rail="L402_LIGHTNING"
    )
    print(f"[+] Locked Escrow ID: {deposit.escrow_id}")
    print(f"[+] Collateral Amount: ${deposit.amount_usd} USD")
    print(f"[+] Status: {deposit.status} (Rail: {deposit.settlement_rail})")
    assert deposit.status == "LOCKED"

    # 3. Trigger Invariant Violation & Automated Slashing
    print("\n--- [2] Invariant Violation Occurs: Automated Proof-Based Slashing ---")
    regression_proof = {
        "type": "BTP_REGRESSION_PROOF",
        "proof_signature": "ed25519_observer_proof_signature_hex_1234",
        "target_action": "HIGH_VALUE_SETTLEMENT",
        "violated_invariant": "CATASTROPHIC_POLICY_ESCAPE: Unauthorized fund drain"
    }

    claimant_invoice = "lnbc2500000000satoshis_indemnity_payout_hash"
    ok, msg, receipt = pool.claim_and_slash(
        escrow_id=deposit.escrow_id,
        regression_proof=regression_proof,
        payee_destination=claimant_invoice,
        agent_passport=passport
    )

    print(f"Slashing Execution: {ok} ({msg})")
    print(f"Settlement Status: {receipt['status']}")
    print(f"Disbursed To: {receipt['payee_destination']}")
    print(f"Passport Tripped: {receipt['passport_tripped']}")

    assert ok is True
    assert passport.circuit_breaker_tripped is True
    assert receipt["status"] == "DISBURSED_AND_SETTLED"

    print("\n" + "=" * 75)
    print("  Autonomous Escrow Demo Complete: Zero Human Arbitration Required")
    print("=" * 75)
    return True


if __name__ == "__main__":
    main()
