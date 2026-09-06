"""
BTP v5.3 Cross-Tenant Autonomous Agent Marketplace & SLA Escrows Test Suite.
Tests machine-to-machine agent hiring, conditional two-sided micro-escrows,
zero-knowledge task completion proofs (zk-TCP), and trustless settlement.
"""

import pytest
import os
import time
import tempfile
from src.marketplace.sla_contract import (
    AgentMarketplaceEngine,
    SLAContract,
    SLAContractStatus,
    ZKTaskCompletionProof,
    MarketplaceListing
)
from src.settlement.autonomous_escrow import AutonomousEscrowPool


@pytest.fixture
def temp_engine():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    engine = AgentMarketplaceEngine(store_path=path)
    yield engine
    if os.path.exists(path):
        os.remove(path)


def test_marketplace_listing_and_filtering(temp_engine):
    specialists = temp_engine.list_specialists()
    assert len(specialists) >= 3
    
    # Filter by capability
    audit_specialists = temp_engine.list_specialists(capability="solidity_verify")
    assert len(audit_specialists) == 1
    assert audit_specialists[0].agent_id == "agent-code-auditor-99"
    assert audit_specialists[0].reputation_score >= 0.95

    clinical_specialists = temp_engine.list_specialists(capability="hipaa_compliance")
    assert len(clinical_specialists) == 1
    assert clinical_specialists[0].agent_id == "agent-risk-oracle-01"


def test_sla_contract_creation_and_locking(temp_engine):
    contract = temp_engine.create_contract(
        client_tenant_id="ten_acme_corp_dev",
        client_org_id="acme-corp",
        client_agent_id="acme-crawler-01",
        provider_agent_id="agent-code-auditor-99",
        required_capability="ast_gate:audit",
        budget_usd=150.0,
        provider_bond_usd=30.0,
        settlement_rail="L402_LIGHTNING"
    )
    assert contract.contract_id.startswith("SLA-")
    assert contract.status == SLAContractStatus.PROPOSED
    assert contract.payment_budget_usd == 150.0
    assert contract.provider_bond_usd == 30.0

    # Lock two-sided escrow
    pool = AutonomousEscrowPool()
    c_dep, p_dep = pool.lock_sla_escrow(contract)
    assert c_dep.escrow_id.startswith("ESCROW-")
    assert p_dep.escrow_id.startswith("ESCROW-")
    assert c_dep.amount_usd == 150.0
    assert p_dep.amount_usd == 30.0

    locked = temp_engine.lock_contract(contract.contract_id, c_dep.escrow_id, p_dep.escrow_id)
    assert locked.status == SLAContractStatus.LOCKED
    assert locked.client_escrow_id == c_dep.escrow_id
    assert locked.provider_escrow_id == p_dep.escrow_id


def test_zktcp_proof_verification_valid():
    proof = ZKTaskCompletionProof.create_proof(
        contract_id="SLA-TEST-001",
        provider_agent_id="agent-code-auditor-99",
        provider_tenant_id="ten_bartholomew_core_dev",
        input_data={"target": "smart_contract.sol", "rule": "ast_invariant"},
        output_data={"status": "CLEAN", "violations_found": 0},
        tool_actions=["ast_walk", "pattern_match"]
    )
    assert proof.proof_id.startswith("zktcp_")
    assert proof.verified is True
    assert proof.pedersen_commitment.startswith("0x")
    assert proof.fiat_shamir_response.startswith("0x")
    assert len(proof.execution_trace_root) == 64

    # Verify directly
    assert proof.verify(expected_contract_id="SLA-TEST-001") is True
    # Fails if contract_id mismatch
    assert proof.verify(expected_contract_id="SLA-WRONG-999") is False


def test_zktcp_proof_rejection_on_tampering():
    proof = ZKTaskCompletionProof.create_proof(
        contract_id="SLA-TEST-TAMPER",
        provider_agent_id="agent-code-auditor-99",
        provider_tenant_id="ten_bartholomew_core_dev",
        input_data={"job": 1},
        output_data={"result": "ok"},
        tool_actions=["run"]
    )
    assert proof.verify("SLA-TEST-TAMPER") is True

    # Tamper with pedersen commitment
    proof.pedersen_commitment = "0xdeadbeefbadf00d"
    assert proof.verify("SLA-TEST-TAMPER") is False


def test_sla_fulfillment_and_clean_settlement(temp_engine):
    pool = AutonomousEscrowPool()

    contract = temp_engine.create_contract(
        client_tenant_id="ten_novartis_health_prod",
        client_org_id="novartis-health",
        client_agent_id="agent-risk-oracle-01",
        provider_agent_id="agent-code-auditor-99",
        required_capability="solidity_verify",
        budget_usd=200.0,
        provider_bond_usd=40.0
    )
    c_dep, p_dep = pool.lock_sla_escrow(contract)
    temp_engine.lock_contract(contract.contract_id, c_dep.escrow_id, p_dep.escrow_id)

    # Provider generates valid zk-TCP proof
    proof = ZKTaskCompletionProof.create_proof(
        contract_id=contract.contract_id,
        provider_agent_id=contract.provider_agent_id,
        provider_tenant_id=contract.provider_tenant_id,
        input_data={"contract_code": "pragma solidity ^0.8.0; contract C {}"},
        output_data={"security_score": 100, "exploits": []},
        tool_actions=["ast_verify", "formal_check"]
    )

    # Fulfill contract in engine
    ok, msg, updated = temp_engine.fulfill_contract(contract.contract_id, proof)
    assert ok is True
    assert updated.status == SLAContractStatus.SETTLED

    # Settle in escrow pool
    s_ok, s_msg, receipt = pool.settle_sla_completion(
        contract=updated,
        completion_proof=proof,
        provider_payee_destination="0xProviderVaultAddress777"
    )
    assert s_ok is True
    assert receipt["status"] == "SLA_SETTLED_CLEAN"
    assert receipt["amount_disbursed_usd"] == 200.0
    assert receipt["bond_returned_usd"] == 40.0

    # Verify escrow deposit statuses
    assert pool.active_escrows[c_dep.escrow_id].status == "SETTLED"
    assert pool.active_escrows[p_dep.escrow_id].status == "RELEASED"


def test_sla_unverified_proof_rejection(temp_engine):
    pool = AutonomousEscrowPool()
    contract = temp_engine.create_contract(
        client_tenant_id="ten_client",
        client_org_id="client-org",
        client_agent_id="agent-c",
        provider_agent_id="agent-code-auditor-99",
        required_capability="solidity_verify",
        budget_usd=100.0,
        provider_bond_usd=20.0
    )
    temp_engine.lock_contract(contract.contract_id, "ESCROW-1", "ESCROW-2")

    fake_proof = ZKTaskCompletionProof(
        proof_id="zktcp_fake",
        contract_id=contract.contract_id,
        provider_agent_id="agent-imposter",
        provider_tenant_id="ten_imposter",
        input_state_hash="0x1",
        output_state_hash="0x2",
        tool_actions_executed=["fake"],
        pedersen_commitment="0x4",
        fiat_shamir_response="0x5",
        timestamp=time.time(),
        verified=False  # Invalid
    )

    ok, msg, _ = temp_engine.fulfill_contract(contract.contract_id, fake_proof)
    assert ok is False
    assert "failed" in msg.lower()

    s_ok, s_msg, _ = pool.settle_sla_completion(contract, fake_proof, "0xVault")
    assert s_ok is False
    assert "aborted" in s_msg


def test_cli_marketplace_flow(capsys):
    import argparse
    from cli import cmd_marketplace_list, cmd_marketplace_contract_create, cmd_marketplace_contract_fulfill

    # 1. Test listing
    args_list = argparse.Namespace(capability=None)
    cmd_marketplace_list(args_list)
    captured = capsys.readouterr()
    assert "BTP v5.3 CROSS-TENANT AGENT MARKETPLACE" in captured.out
    assert "Novartis Clinical Data Mesh Verifier" in captured.out
    assert "Bartholomew Autonomous Code Security Auditor" in captured.out

    # 2. Test listing with filter
    args_filter = argparse.Namespace(capability="clinical_data")
    cmd_marketplace_list(args_filter)
    captured = capsys.readouterr()
    assert "Novartis" in captured.out
    assert "Bartholomew Autonomous Code Security Auditor" not in captured.out

    # 3. Test contract creation
    args_create = argparse.Namespace(
        client_tenant="ten_pytest_client",
        client_org="pytest-org",
        client_agent="test-client-agent",
        provider_agent="agent-code-auditor-99",
        capability="ast_gate:audit",
        budget=125.0,
        bond=25.0,
        rail="L402_LIGHTNING"
    )
    cmd_marketplace_contract_create(args_create)
    captured = capsys.readouterr()
    assert "CROSS-TENANT SLA CONTRACT CREATED & ESCROWS LOCKED" in captured.out
    assert "$125.00 USD" in captured.out
    assert "$25.00 USD" in captured.out
    
    # Extract contract ID
    import re
    m = re.search(r"Contract ID\s+:\s+(SLA-[A-F0-9]+)", captured.out)
    assert m is not None
    contract_id = m.group(1)

    # 4. Test fulfillment
    args_fulfill = argparse.Namespace(contract_id=contract_id)
    cmd_marketplace_contract_fulfill(args_fulfill)
    captured = capsys.readouterr()
    assert "BTP v5.3 SLA CONTRACT FULFILLED & SETTLED" in captured.out
    assert "SLA_SETTLED_CLEAN" in captured.out

