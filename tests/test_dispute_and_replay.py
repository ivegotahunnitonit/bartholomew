"""
Test Suite for BTP Automated Dispute Resolution & Replay Protection Engine
=============================================================================
Validates:
  1. Automated M2M dispute arbitration decisions based on receipt evidence.
  2. Ed25519 signature verification on dispute verdicts.
  3. Nonce deduplication and replay attack prevention.
  4. Timestamp clock skew enforcement.
  5. Single-use cryptographic receipt consumption.
"""

import time
import pytest
from src.dispute_resolver import AutomatedDisputeResolver, DisputeVerdict
from src.replay_protector import ReplayProtectionVault


def test_dispute_resolution_denied_receipt_claimant_wins():
    """Validates that a claimant wins refund if execution receipt showed DENY or rule violation."""
    resolver = AutomatedDisputeResolver()
    receipt = {
        "verdict": "DENY",
        "rule_id": "BTP-SQL-001",
        "receipt_sha256": "abcdef1234567890",
        "policy_version": "1.0.0"
    }

    verdict = resolver.arbitrate(
        claimant_id="agent-a",
        respondent_id="agent-b",
        claimed_reason="INVARIANT_BREACH",
        execution_receipt=receipt,
        disputed_amount_usd=50.0
    )

    assert verdict.verdict == "CLAIMANT_WINS"
    assert verdict.resolution_action == "REFUND_CLAIMANT"
    assert verdict.refund_amount_usd == 50.0
    assert verdict.rule_violated == "BTP-SQL-001"
    assert verdict.verify_signature(resolver.public_key_hex) is True


def test_dispute_resolution_allowed_receipt_respondent_wins():
    """Validates that respondent wins if execution receipt showed ALLOW with valid proof."""
    resolver = AutomatedDisputeResolver()
    receipt = {
        "verdict": "ALLOW",
        "rule_id": None,
        "receipt_sha256": "1234567890abcdef",
        "policy_version": "1.0.0"
    }

    verdict = resolver.arbitrate(
        claimant_id="agent-a",
        respondent_id="agent-b",
        claimed_reason="NON_DELIVERY",
        execution_receipt=receipt,
        disputed_amount_usd=50.0
    )

    assert verdict.verdict == "RESPONDENT_WINS"
    assert verdict.resolution_action == "MAINTAIN_ESCROW"
    assert verdict.refund_amount_usd == 0.0
    assert verdict.verify_signature(resolver.public_key_hex) is True


def test_replay_protection_nonce_deduplication():
    """Validates replay protection against duplicate nonces/request IDs."""
    vault = ReplayProtectionVault(max_clock_skew_seconds=300.0)
    now = time.time()

    # First request: valid
    ok, err = vault.validate_request(request_id="tx-1001", nonce="nonce-001", timestamp=now)
    assert ok is True
    assert err is None

    # Replayed request: rejected
    ok2, err2 = vault.validate_request(request_id="tx-1001", nonce="nonce-001", timestamp=now)
    assert ok2 is False
    assert "Replay Violation" in err2


def test_replay_protection_timestamp_skew():
    """Validates replay protection against out-of-window timestamp skew."""
    vault = ReplayProtectionVault(max_clock_skew_seconds=300.0)
    now = time.time()

    # Request with 600s skew (exceeds 300s max)
    ok, err = vault.validate_request(request_id="tx-1002", timestamp=now - 600.0, now=now)
    assert ok is False
    assert "timestamp skew" in err


def test_single_use_receipt_consumption():
    """Validates that cryptographic receipts can only be consumed once."""
    vault = ReplayProtectionVault()
    receipt_hash = "f" * 64

    # First consumption: allowed
    ok1, err1 = vault.validate_and_consume_receipt(receipt_hash)
    assert ok1 is True
    assert err1 is None

    # Duplicate consumption attempt: rejected
    ok2, err2 = vault.validate_and_consume_receipt(receipt_hash)
    assert ok2 is False
    assert "Fraud Violation" in err2
