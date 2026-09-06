"""
Tests for BTP v4.0 Autonomous Micro-Escrow, L402 Protocol, and EIP-712 Multi-Chain Settlement
==============================================================================================
"""

import pytest
import time
import hashlib
from src import Guard
from src.agent_passport import SovereignAgentPassport
from src.settlement.l402_protocol import L402ProtocolEngine, L402Challenge, L402Caveat
from src.settlement.evm_escrow import EVMEscrowGateway, EscrowSlashingClaim, EIP712Domain
from src.settlement.autonomous_escrow import AutonomousEscrowPool, EscrowDeposit


def test_l402_protocol_engine_challenge_and_preimage():
    engine = L402ProtocolEngine()
    challenge, preimage = engine.create_challenge(
        agent_id="agent-worker-01",
        action_type="DB_MUTATION",
        amount_satoshis=5000,
        ttl_seconds=3600
    )

    assert challenge.payment_hash is not None
    assert challenge.amount_satoshis == 5000
    assert challenge.invoice.startswith("lnbc5000u1p")
    header = challenge.to_header()
    assert 'L402 token="' in header
    assert 'invoice="' in header

    # 1. Verify Payment Preimage
    is_valid_preimage = engine.verify_preimage(challenge.payment_hash, preimage)
    assert is_valid_preimage is True

    # 2. Verify Macaroon Caveats
    valid_mac, msg, caveats = engine.verify_macaroon(
        macaroon_b64=challenge.macaroon_b64,
        expected_agent_id="agent-worker-01",
        expected_action="DB_MUTATION"
    )
    assert valid_mac is True
    assert caveats["agent_id"] == "agent-worker-01"
    assert caveats["max_satoshis"] == "5000"

    # 3. Verify HTTP Authorization Header
    auth_header = f"L402 {challenge.macaroon_b64}:{preimage}"
    auth_ok, auth_msg = engine.verify_authorization(
        auth_header,
        expected_agent_id="agent-worker-01",
        expected_action="DB_MUTATION"
    )
    assert auth_ok is True
    assert "Paid & Authorized" in auth_msg


def test_l402_tamper_and_expiration_rejection():
    engine = L402ProtocolEngine()
    challenge, preimage = engine.create_challenge(
        agent_id="agent-worker-02",
        action_type="HIGH_RISK_ACTION",
        amount_satoshis=1000,
        ttl_seconds=3600
    )

    # 1. Tampered preimage must fail
    fake_preimage = "00" * 32
    assert engine.verify_preimage(challenge.payment_hash, fake_preimage) is False

    # 2. Agent ID mismatch in caveat check must fail
    valid_mac, msg, _ = engine.verify_macaroon(
        challenge.macaroon_b64,
        expected_agent_id="malicious-impersonator"
    )
    assert valid_mac is False
    assert "agent_id" in msg

    # 3. Expired challenge must fail
    expired_challenge, exp_preimage = engine.create_challenge(
        agent_id="agent-worker-02",
        action_type="FAST_ACTION",
        ttl_seconds=-10  # already expired
    )
    exp_mac, exp_msg, _ = engine.verify_macaroon(expired_challenge.macaroon_b64)
    assert exp_mac is False
    assert "expired" in exp_msg.lower()


def test_evm_escrow_eip712_structured_signing():
    gateway = EVMEscrowGateway()
    claim = EscrowSlashingClaim(
        escrow_id="ESCROW-TEST-1234",
        agent_id="agent-worker-01",
        payee_address="0x1111222233334444555566667777888899990000",
        amount_usd=250.0,
        violated_invariant="INVARIANT_NO_DESTRUCTIVE_MUTATION",
        proof_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        nonce=1,
        deadline=int(time.time() + 3600)
    )

    sig_payload = gateway.sign_slashing_claim(claim)
    assert sig_payload["r"].startswith("0x")
    assert sig_payload["s"].startswith("0x")
    assert sig_payload["v"] == 27
    assert sig_payload["signer_address"].startswith("0x")

    # Verify signature
    valid, msg = gateway.verify_claim_signature(
        claim=claim,
        r_hex=sig_payload["r"],
        s_hex=sig_payload["s"],
        expected_signer=sig_payload["signer_address"]
    )
    assert valid is True
    assert "verified valid" in msg

    # Tampered claim must fail verification
    tampered_claim = EscrowSlashingClaim(
        escrow_id="ESCROW-TEST-1234",
        agent_id="agent-worker-01",
        payee_address="0x1111222233334444555566667777888899990000",
        amount_usd=9999.0,  # tampered amount
        violated_invariant="INVARIANT_NO_DESTRUCTIVE_MUTATION",
        proof_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        nonce=1,
        deadline=int(time.time() + 3600)
    )
    tampered_valid, _ = gateway.verify_claim_signature(
        claim=tampered_claim,
        r_hex=sig_payload["r"],
        s_hex=sig_payload["s"]
    )
    assert tampered_valid is False


def test_autonomous_escrow_l402_slashing_lifecycle():
    pool = AutonomousEscrowPool()
    passport = SovereignAgentPassport.issue(
        agent_id="autonomous-executor-01",
        model_family="claude-3-5-sonnet",
        authorized_capabilities=["fs:write", "trade:dispatch"]
    )

    deposit = pool.lock_escrow(
        agent_id=passport.agent_id,
        action_type="TRADE_DISPATCH",
        amount_usd=400.0,
        passport=passport,
        settlement_rail="L402_LIGHTNING"
    )

    assert deposit.l402_challenge is not None
    assert deposit.l402_preimage is not None
    assert deposit.status == "LOCKED"

    # Execute Slashing with regression proof
    proof = {
        "type": "BTP_REGRESSION_PROOF",
        "violated_invariant": "INVARIANT_MAX_DRAWDOWN",
        "proof_signature": "0xdeadbeef1234567890",
        "target_action": "TRADE_DISPATCH"
    }

    ok, msg, receipt = pool.claim_and_slash(
        escrow_id=deposit.escrow_id,
        regression_proof=proof,
        payee_destination="lnbc400u1p...claimant_invoice",
        agent_passport=passport
    )

    assert ok is True
    assert receipt["status"] == "DISBURSED_AND_SETTLED"
    assert receipt["l402_preimage_revealed"] == deposit.l402_preimage
    assert receipt["passport_tripped"] is True
    assert passport.circuit_breaker_tripped is True


def test_autonomous_escrow_evm_slashing_lifecycle():
    pool = AutonomousEscrowPool()
    deposit = pool.lock_escrow(
        agent_id="arbitrum-trader-01",
        action_type="DEFI_SWAP",
        amount_usd=750.0,
        settlement_rail="EVM_ARBITRUM"
    )

    proof = {
        "type": "BTP_REGRESSION_PROOF",
        "violated_invariant": "SLIPPAGE_LIMIT_EXCEEDED",
        "proof_signature": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "target_action": "DEFI_SWAP"
    }

    ok, msg, receipt = pool.claim_and_slash(
        escrow_id=deposit.escrow_id,
        regression_proof=proof,
        payee_destination="0x9999888877776666555544443333222211110000"
    )

    assert ok is True
    assert "evm_eip712_claim" in receipt
    evm_claim = receipt["evm_eip712_claim"]
    assert evm_claim["chain_id"] == 42161
    assert evm_claim["r"].startswith("0x")
    assert evm_claim["s"].startswith("0x")


def test_guard_escrow_collateral_decorator():
    guard = Guard(spend_cap=1000.0)
    pool = AutonomousEscrowPool()
    passport = SovereignAgentPassport.issue(
        agent_id="safe-worker-01",
        model_family="gpt-4o",
        authorized_capabilities=["db:query"]
    )

    # 1. Clean execution released
    @guard.escrow_collateral(amount_usd=150.0, action_type="READ_STATS", agent_id=passport.agent_id, passport=passport, pool=pool)
    def clean_tool(cmd: str):
        return f"Executed clean: {cmd}"

    result = clean_tool("SELECT count(*) FROM analytics;")
    assert "Executed clean" in result
    assert passport.circuit_breaker_tripped is False
    assert passport.verified_action_count == 1
    assert passport.total_settled_volume_usd == 150.0

    # 2. Destructive execution slashed and circuit breaker tripped
    @guard.escrow_collateral(amount_usd=200.0, action_type="DB_PURGE", agent_id=passport.agent_id, passport=passport, pool=pool)
    def dangerous_tool(cmd: str):
        return f"Run: {cmd}"

    with pytest.raises(PermissionError, match="Bartholomew Micro-Escrow Slashed"):
        dangerous_tool("DROP TABLE users CASCADE;")

    assert passport.circuit_breaker_tripped is True
    assert passport.violation_count == 1
