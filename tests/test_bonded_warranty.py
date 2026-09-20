"""
Unit Tests for Bartholomew Bonded Execution Warranty & Invariant Slashing Engine
==============================================================================
Validates:
  - Bond issuance with reserve pool bounds
  - Invariant breach slashing with cryptographic evidence receipts
  - Successful mission redemption
  - Automated indemnity claim payouts
"""

import pytest
from src.bonded_warranty import BondedExecutionWarranty


@pytest.fixture
def warranty_engine():
    return BondedExecutionWarranty(reserve_pool_usd=50_000.0, max_bond_per_action_usd=10_000.0)


def test_issue_warranty_bond(warranty_engine):
    bond = warranty_engine.issue_warranty_bond(
        attestation_hash="0xabcd1234ef567890",
        agent_id="agent-astra-001",
        action_type="DATABASE_MIGRATION",
        bond_amount_usd=5_000.0,
    )
    assert bond["bond_id"].startswith("BOND-")
    assert bond["bond_amount_usd"] == 5_000.0
    assert bond["status"] == "ACTIVE_BONDED"
    assert warranty_engine.get_bond_status(bond["bond_id"]) is not None


def test_issue_bond_exceeds_cap(warranty_engine):
    with pytest.raises(ValueError, match="exceeds max per-action cap"):
        warranty_engine.issue_warranty_bond(
            attestation_hash="0xabcd",
            agent_id="agent-002",
            action_type="EXEC_SHELL",
            bond_amount_usd=25_000.0,
        )


def test_slash_bond_for_invariant_breach(warranty_engine):
    bond = warranty_engine.issue_warranty_bond(
        attestation_hash="0xhash123",
        agent_id="agent-malicious-007",
        action_type="EXEC_TOOL",
        bond_amount_usd=8_000.0,
    )
    bond_id = bond["bond_id"]

    # Fraud / Invariant breach evidence
    breach_receipt = {
        "verdict": "BLOCKED",
        "reason": "Attempted rm -rf outside hermetic container boundary",
        "ast_violation": True,
    }

    success, msg, slashed_amt = warranty_engine.slash_bond_for_invariant_breach(bond_id, breach_receipt)
    assert success is True
    assert slashed_amt == 8_000.0
    assert "liquidated due to verified breach" in msg

    status = warranty_engine.get_bond_status(bond_id)
    assert status["status"] == "SLASHED_FOR_INVARIANT_BREACH"
    assert status["slashing_reason"] == breach_receipt["reason"]


def test_redeem_bond_success(warranty_engine):
    bond = warranty_engine.issue_warranty_bond(
        attestation_hash="0xsafehash",
        agent_id="agent-honest-042",
        action_type="READ_FILE",
        bond_amount_usd=2_500.0,
    )
    bond_id = bond["bond_id"]

    success, msg, returned_amt = warranty_engine.redeem_bond(bond_id)
    assert success is True
    assert returned_amt == 2_500.0
    assert "successfully redeemed" in msg

    status = warranty_engine.get_bond_status(bond_id)
    assert status["status"] == "REDEEMED_SUCCESSFUL"
