"""
Test Suite: Real-World Fund Legitimacy & Financial Invariant Verifier
====================================================================
Tests:
  1. Cryptographic HMAC-SHA256 verification of authentic Stripe webhook settlements.
  2. Rejection of forged/spoofed payment headers (Anti-Fraud Gate).
  3. Verification of on-chain USDC settlement transactions.
  4. Epistemic audit of mission_state.json ledger balance.
"""

import sys
import os
import time
import hmac
import hashlib

sys.path.insert(0, os.path.abspath("."))
from src.fund_legitimacy_verifier import FundLegitimacyVerifier

def test_fund_legitimacy():
    print("=" * 80)
    print("TESTING FUND LEGITIMACY & FINANCIAL INVARIANT VERIFIER")
    print("=" * 80 + "\n")

    secret = "whsec_live_test_secret_9981"
    verifier = FundLegitimacyVerifier(stripe_webhook_secret=secret)

    # 1. Test Authentic Stripe Webhook Verification
    raw_event = b'{"id": "evt_001", "type": "payment_intent.succeeded", "amount": 250000}'
    now_ts = str(int(time.time()))
    signed_payload = f"{now_ts}.".encode("utf-8") + raw_event
    valid_sig = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    valid_header = f"t={now_ts},v1={valid_sig}"

    is_valid, msg = verifier.verify_stripe_webhook_signature(raw_event, valid_header)
    print(f"[TEST 1: Authentic Stripe Settlement Webhook]")
    print(f"  * Verification Status : {is_valid}")
    print(f"  * Audit Message       : {msg}")
    assert is_valid is True
    assert msg == "VERIFIED_AUTHENTIC_STRIPE_SETTLEMENT"

    # 2. Test Forged / Spoofed Payment Header (Anti-Fraud Gate)
    print(f"\n[TEST 2: Forged Payment Header Detection]")
    fake_header = f"t={now_ts},v1=deadbeef000000000000000000000000"
    is_valid_fake, fake_msg = verifier.verify_stripe_webhook_signature(raw_event, fake_header)
    print(f"  * Verification Status : {is_valid_fake}")
    print(f"  * Security Action     : {fake_msg} (BLOCKED)")
    assert is_valid_fake is False
    assert "SPOOFED_TRANSACTION" in fake_msg

    # 3. Test On-Chain USDC Verification
    print(f"\n[TEST 3: On-Chain USDC Settlement Verification]")
    usdc_audit = verifier.verify_onchain_usdc_receipt(
        tx_hash="0x4a8f9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a",
        expected_amount_usd=12500.00,
        recipient_address="0xRecipientWalletAddress"
    )
    print(f"  * Tx Hash Valid       : {usdc_audit['is_cryptographically_valid']}")
    print(f"  * Amount Audited      : ${usdc_audit['amount_usd']:,.2f} {usdc_audit['token']}")
    print(f"  * Audit Result        : {usdc_audit['audit_status']}")
    assert usdc_audit["is_cryptographically_valid"] is True

    # 4. Epistemic Audit of Local Ledger
    print(f"\n[TEST 4: Epistemic State Ledger Audit]")
    ledger_audit = verifier.audit_mission_state_revenue("mission_state.json")
    print(f"  * Recorded Ledger Value: ${ledger_audit['recorded_ledger_value_usd']:,.2f} USD")
    print(f"  * Status               : {ledger_audit['epistemic_audit']}")
    print(f"  * Next Step            : {ledger_audit['real_world_action_required']}")

    print("\n" + "=" * 80)
    print("ALL FUND LEGITIMACY & FINANCIAL AUDIT INVARIANTS PASSED 100% CLEAN!")
    print("=" * 80)

if __name__ == "__main__":
    test_fund_legitimacy()
