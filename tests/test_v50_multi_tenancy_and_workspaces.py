"""
Milestone 5.0 Tests: Multi-Tenant Enterprise Workspaces, Scoped API Keys & Cross-Tenant Isolation.
"""

import pytest
import os
from src.tenancy.workspace_manager import WorkspaceManager, WorkspaceTenant, EnvironmentType
from src.agent_passport import SovereignAgentPassport
from src.settlement.autonomous_escrow import AutonomousEscrowPool
from src.settlement.swarm_arbitration import SwarmDisputeArbitrator, ArbitrationResolutionCertificate
from framework_adapters.universal.universal_model_guard import UniversalBTPModelGuard, ModelProvider


def test_workspace_creation_and_api_keys(tmp_path):
    storage = str(tmp_path / "workspaces.json")
    wm = WorkspaceManager(storage_path=storage)

    tenant_dev = wm.create_tenant(org_id="acme-corp", project_id="payments-swarm", environment=EnvironmentType.DEVELOPMENT)
    assert tenant_dev.tenant_id.startswith("ten_")
    assert tenant_dev.org_id == "acme-corp"
    assert tenant_dev.project_id == "payments-swarm"
    assert tenant_dev.environment == "dev"

    # Test key generation
    test_key = wm.generate_scoped_api_key(org_id="acme-corp", project_id="payments-swarm", environment=EnvironmentType.DEVELOPMENT)
    assert test_key.startswith("btp_test_")
    key_ctx = wm.verify_api_key(test_key)
    assert key_ctx is not None
    assert key_ctx["tenant_id"] == tenant_dev.tenant_id

    # Prod key generation
    live_key = wm.generate_scoped_api_key(org_id="acme-corp", project_id="payments-swarm", environment=EnvironmentType.PRODUCTION)
    assert live_key.startswith("btp_live_")


def test_passport_tenant_cryptographic_isolation():
    # Tenant 1: Acme Finance
    pass_acme = SovereignAgentPassport.issue(
        agent_id="agent-worker-1",
        model_family="gpt-4o",
        org_id="acme-corp",
        project_id="finance",
        environment="prod"
    )

    # Tenant 2: Beta Health
    pass_beta = SovereignAgentPassport.issue(
        agent_id="agent-worker-1",  # Same agent name, different tenant
        model_family="gpt-4o",
        org_id="beta-health",
        project_id="clinical-mesh",
        environment="prod"
    )

    assert pass_acme.tenant_id != pass_beta.tenant_id
    assert pass_acme.passport_id != pass_beta.passport_id
    assert pass_acme.to_dict()["tenant_id"] == pass_acme.tenant_id
    assert pass_beta.to_dict()["tenant_id"] == pass_beta.tenant_id


def test_cross_tenant_escrow_firewall_rejection():
    pool = AutonomousEscrowPool()

    # Create Acme agent & deposit
    pass_acme = SovereignAgentPassport.issue(
        agent_id="agent-acme-treasury",
        model_family="claude-3-5-sonnet",
        org_id="acme-corp",
        project_id="treasury",
        environment="prod"
    )

    deposit = pool.lock_escrow(
        agent_id=pass_acme.agent_id,
        action_type="FINANCIAL_TRANSFER",
        amount_usd=500.0,
        passport=pass_acme
    )
    assert deposit.tenant_id == pass_acme.tenant_id

    # Dummy resolution certificate
    import time
    cert = ArbitrationResolutionCertificate(
        certificate_id="cert-mock-001",
        dispute_id="disp-001",
        escrow_id=deposit.escrow_id,
        target_agent_id=pass_acme.agent_id,
        verdict="SLASH_COLLATERAL",
        slashed_amount_usd=500.0,
        quorum_count=2,
        participating_passports=["pass-1", "pass-2"],
        certificate_hash="0x123456",
        timestamp=time.time(),
        aggregate_signatures=["sig1", "sig2"]
    )

    # Attempt to slash using a rogue passport from Beta Health (Tenant Mismatch)
    pass_beta = SovereignAgentPassport.issue(
        agent_id="agent-beta-juror",
        model_family="claude-3-5-sonnet",
        org_id="beta-health",
        project_id="clinical-mesh",
        environment="prod"
    )

    ok, msg, _ = pool.arbitrate_and_slash(
        escrow_id=deposit.escrow_id,
        arbitration_cert=cert,
        payee_destination="victim-vault",
        agent_passport=pass_beta
    )

    assert not ok
    assert "Cross-tenant slashing vetoed" in msg
    assert deposit.status == "LOCKED"  # Slashed was aborted by cross-tenant firewall!


def test_universal_guard_tenant_scoping():
    guard = UniversalBTPModelGuard(
        org_id="acme-corp",
        project_id="customer-support",
        environment="staging",
        escrow_collateral_usd=200.0,
        strict=False
    )
    assert guard.org_id == "acme-corp"
    assert guard.project_id == "customer-support"
    assert guard.environment == "staging"
    assert guard.tenant_id.startswith("ten_")

    # Safe call executes cleanly in tenant scope
    call = {"name": "lookup_user", "arguments": {"user_id": 101}}
    res = guard.intercept_and_verify(call, provider=ModelProvider.OPENAI)
    assert res["status"] == "APPROVED"
