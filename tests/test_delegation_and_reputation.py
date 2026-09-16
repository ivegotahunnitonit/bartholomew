"""
Test Suite for BTP Verifiable Delegation Chains & Reputation Evidence Engine
=============================================================================
Validates:
  1. Cryptographically signed multi-agent delegation chains (Root -> Agent B -> Agent C).
  2. Non-escalation spend cap invariant enforcement.
  3. Non-escalation capability set subset invariant enforcement.
  4. Reputation report generation & Ed25519 evidence signature verification.
"""

import time
import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519

from src.delegation_chain import DelegationLink, VerifiableDelegationChain
from src.reputation_engine import AgentReputationEngine, ReputationReport


def test_valid_delegation_chain():
    """Validates a 3-step valid delegation chain with non-escalating spend and capabilities."""
    root_key = ed25519.Ed25519PrivateKey.generate()
    root_pub = root_key.public_key().public_bytes_raw().hex()

    agent_b_key = ed25519.Ed25519PrivateKey.generate()
    agent_b_pub = agent_b_key.public_key().public_bytes_raw().hex()

    now = time.time()
    expires = now + 3600

    # Step 1: Root Owner -> Agent B ($100 spend, ["data:read", "code:mutate", "l402:pay"])
    link1 = DelegationLink(
        grantor_id="human-owner",
        grantee_id="agent-b-orchestrator",
        grantor_pubkey=root_pub,
        max_spend_usd=100.0,
        allowed_capabilities=["data:read", "code:mutate", "l402:pay"],
        issued_at=now,
        expires_at=expires,
        parent_link_hash="GENESIS_ROOT"
    )
    link1.sign(root_key)

    # Step 2: Agent B -> Agent C ($25 spend, ["data:read", "l402:pay"])
    link2 = DelegationLink(
        grantor_id="agent-b-orchestrator",
        grantee_id="agent-c-worker",
        grantor_pubkey=agent_b_pub,
        max_spend_usd=25.0,
        allowed_capabilities=["data:read", "l402:pay"],
        issued_at=now,
        expires_at=expires,
        parent_link_hash=link1.compute_link_hash()
    )
    link2.sign(agent_b_key)

    chain = VerifiableDelegationChain([link1, link2])
    is_valid, effective_spend, caps, err = chain.evaluate_chain(now=now)

    assert is_valid is True
    assert err is None
    assert effective_spend == 25.0
    assert caps == {"data:read", "l402:pay"}


def test_delegation_chain_spend_escalation_breach():
    """Validates that grantee attempting to claim a higher spend cap than grantor is vetoed."""
    root_key = ed25519.Ed25519PrivateKey.generate()
    root_pub = root_key.public_key().public_bytes_raw().hex()

    agent_b_key = ed25519.Ed25519PrivateKey.generate()
    agent_b_pub = agent_b_key.public_key().public_bytes_raw().hex()

    now = time.time()
    expires = now + 3600

    link1 = DelegationLink(
        grantor_id="human-owner",
        grantee_id="agent-b",
        grantor_pubkey=root_pub,
        max_spend_usd=10.0,
        allowed_capabilities=["data:read"],
        issued_at=now,
        expires_at=expires,
        parent_link_hash="GENESIS_ROOT"
    )
    link1.sign(root_key)

    # Escalation: Agent C claims $50 cap when B only has $10
    link2 = DelegationLink(
        grantor_id="agent-b",
        grantee_id="agent-c",
        grantor_pubkey=agent_b_pub,
        max_spend_usd=50.0,
        allowed_capabilities=["data:read"],
        issued_at=now,
        expires_at=expires,
        parent_link_hash=link1.compute_link_hash()
    )
    link2.sign(agent_b_key)

    chain = VerifiableDelegationChain([link1, link2])
    is_valid, spend, caps, err = chain.evaluate_chain(now=now)

    assert is_valid is False
    assert "Delegation Escalation Breach" in err


def test_reputation_engine_evidence_generation():
    """Validates generation and signature verification of machine-readable reputation reports."""
    engine = AgentReputationEngine()
    agent_id = "agent-market-worker-01"

    receipts = [
        {"verdict": "ALLOW", "amount_usd": 0.01, "latency_us": 25.0, "receipt_sha256": "hash1"},
        {"verdict": "ALLOW", "amount_usd": 0.01, "latency_us": 30.0, "receipt_sha256": "hash2"},
        {"verdict": "ALLOW", "amount_usd": 0.01, "latency_us": 20.0, "receipt_sha256": "hash3"},
        {"verdict": "ALLOW", "amount_usd": 0.01, "latency_us": 15.0, "receipt_sha256": "hash4"},
        {"verdict": "ALLOW", "amount_usd": 0.01, "latency_us": 22.0, "receipt_sha256": "hash5"},
        {"verdict": "ALLOW", "amount_usd": 0.01, "latency_us": 28.0, "receipt_sha256": "hash6"},
        {"verdict": "ALLOW", "amount_usd": 0.01, "latency_us": 18.0, "receipt_sha256": "hash7"},
        {"verdict": "ALLOW", "amount_usd": 0.01, "latency_us": 26.0, "receipt_sha256": "hash8"},
        {"verdict": "ALLOW", "amount_usd": 0.01, "latency_us": 24.0, "receipt_sha256": "hash9"},
        {"verdict": "ALLOW", "amount_usd": 0.01, "latency_us": 21.0, "receipt_sha256": "hash10"},
    ]

    report = engine.generate_report(agent_id=agent_id, receipts=receipts)

    assert report.agent_id == agent_id
    assert report.verified_transactions == 10
    assert report.trust_tier == "SOVEREIGN"
    assert report.trust_score == 1.0
    assert report.verify_signature(engine.public_key_hex) is True
