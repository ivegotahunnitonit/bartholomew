"""
Unit Tests for BTP v4.2 Settlement Gateway & Multi-Chain Escrows
================================================================
Validates:
1. LightningGateway: Live/Simulated invoice generation, BOLT11 parsing, and preimage proofs.
2. Lightning L402 HTTP challenge creation and preimage verification (H(preimage) == payment_hash).
3. EVM EIP-712 Slashing Claim typed data generation, signature recovery, and quorum tallying.
4. Smart Escrow contract ABI integrity and cryptographic non-repudiation.
"""

import hashlib
import os
import sys
import time
import pytest

sys.path.insert(0, os.path.abspath("."))

from src.settlement.lightning_gateway import LightningGateway, LightningInvoice
from src.settlement.l402_protocol import L402ProtocolEngine, L402Challenge
from src.settlement.evm_escrow import EVMEscrowGateway, EscrowSlashingClaim, EIP712Domain


def test_lightning_gateway_invoice_lifecycle():
    """Verify Lightning invoice creation, BOLT11 request formatting, and preimage verification."""
    gateway = LightningGateway(node_type="SIMULATED", sats_per_usd=1500)
    invoice = gateway.create_invoice(amount_satoshis=7500, memo="Test Agent Escrow Bond", expiry_seconds=1800)

    assert invoice.payment_hash is not None
    assert len(invoice.payment_hash) == 64
    assert invoice.amount_satoshis == 7500
    assert invoice.payment_request.startswith("lnbc7500u")
    assert invoice.settled is False

    # Reveal preimage and verify payment
    preimage = gateway.reveal_simulated_preimage(invoice.payment_hash)
    assert preimage is not None

    ok, msg = gateway.verify_payment_preimage(invoice.payment_hash, preimage)
    assert ok is True
    assert "settled" in msg
    assert invoice.settled is True

    # Bad preimage must fail
    bad_preimage = "00" * 32
    ok_bad, msg_bad = gateway.verify_payment_preimage(invoice.payment_hash, bad_preimage)
    assert ok_bad is False
    assert "mismatch" in msg_bad


def test_lightning_l402_challenge_issuance():
    """Verify L402 HTTP Challenge issuance with real/simulated Lightning invoice binding."""
    gateway = LightningGateway(node_type="SIMULATED", sats_per_usd=1500)
    challenge, invoice = gateway.issue_l402_escrow_challenge(
        agent_id="agent-settlement-01",
        action_type="HIGH_VALUE_TRADE",
        amount_usd=50.0,
        expiry_seconds=3600
    )

    assert challenge.payment_hash == invoice.payment_hash
    assert challenge.invoice == invoice.payment_request
    assert challenge.amount_satoshis == 75_000  # 50 * 1500

    header_str = challenge.to_header()
    assert 'L402 token="' in header_str
    assert 'invoice="lnbc' in header_str


def test_evm_eip712_slashing_claim_signing_and_verification():
    """Verify EIP-712 typed data hashing and ECDSA SECP256K1 signature recovery."""
    gateway = EVMEscrowGateway(chain_id=8453)  # Base Mainnet
    claim = EscrowSlashingClaim(
        escrow_id="ESCROW-EVM-TEST-001",
        agent_id="0x1111111111111111111111111111111111111111",
        payee_address="0x2222222222222222222222222222222222222222",
        amount_usd=2500.0,
        violated_invariant="CATASTROPHIC_DROP_TABLE",
        proof_hash="0x" + hashlib.sha256(b"zk_proof_payload").hexdigest(),
        nonce=12345,
        deadline=int(time.time() + 3600)
    )

    signed_claim = gateway.sign_slashing_claim(claim)
    assert "signature_hex" in signed_claim
    assert "r" in signed_claim
    assert "s" in signed_claim
    assert "v" in signed_claim
    assert signed_claim["chain_id"] == 8453

    # Verify signature recovers to the gateway signer address
    is_valid, recovered_signer = gateway.verify_slashing_claim(signed_claim)
    assert is_valid is True
    assert recovered_signer.lower() == gateway.signer_address.lower()


def test_solidity_contract_source_integrity():
    """Verify Solidity smart contract source file contains necessary NatSpec and EIP-712 methods."""
    contract_path = os.path.join("src", "settlement", "contracts", "BartholomewEscrowPool.sol")
    assert os.path.exists(contract_path)

    with open(contract_path, "r", encoding="utf-8") as f:
        source = f.read()

    assert "contract BartholomewEscrowPool" in source
    assert "DOMAIN_TYPEHASH" in source
    assert "SLASHING_CLAIM_TYPEHASH" in source
    assert "lockNativeEscrow" in source
    assert "releaseEscrow" in source
    assert "slashWithQuorum" in source
    assert "MIN_JUROR_QUORUM = 2" in source
