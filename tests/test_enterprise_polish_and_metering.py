"""
Tests for BTP Enterprise Polish & Developer Experience:
- Project Init Wizard (Framework detection, policy scaffolding, scoped tenant keys)
- Multi-Tenant Metered Usage Engine & Cryptographically Signed Invoices
"""

import os
import json
import yaml
import tempfile
import argparse
import pytest

from src.init_wizard import detect_framework, scaffold_project
from src.billing.metering_engine import (
    TenantUsageMeter,
    TenantUsageRecord,
    MeteredInvoiceGenerator,
    BASE_PRO_SUBSCRIPTION_USD,
    AST_SCAN_UNIT_USD,
    THREAT_BLOCKED_UNIT_USD,
    ESCROW_FEE_RATIO,
    WEBHOOK_UNIT_USD
)
from cli import cmd_init, cmd_billing_usage, cmd_billing_invoice


def test_framework_detection_and_scaffolding():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock requirements.txt containing crewai
        req_path = os.path.join(temp_dir, "requirements.txt")
        with open(req_path, "w", encoding="utf-8") as f:
            f.write("crewai>=0.28.0\nlangchain-core\n")

        detected = detect_framework(temp_dir)
        assert detected == "crewai"

        # Scaffold project
        res = scaffold_project(
            target_dir=temp_dir,
            org="acme-health",
            project="clinical-crawler",
            env="dev"
        )
        assert res["status"] == "SUCCESS"
        assert res["framework"] == "crewai"
        assert res["tenant_id"].startswith("ten_")
        assert res["api_key"].startswith("btp_dev_")
        assert "BTPCrewAITaskGuard" in res["snippet"]

        # Verify files created on disk
        btp_dir = os.path.join(temp_dir, ".btp")
        assert os.path.isdir(btp_dir)
        
        # Policy
        with open(os.path.join(btp_dir, "policy.yaml"), "r", encoding="utf-8") as f:
            policy = yaml.safe_load(f)
            assert policy["ast_gating"]["enabled"] is True
            assert len(policy["invariants"]) >= 3

        # Tenant
        with open(os.path.join(btp_dir, "tenant.json"), "r", encoding="utf-8") as f:
            tenant = json.load(f)
            assert tenant["org_id"] == "acme-health"
            assert tenant["project_id"] == "clinical-crawler"

        # Passport
        with open(os.path.join(btp_dir, "passport.json"), "r", encoding="utf-8") as f:
            passport = json.load(f)
            assert passport["status"] == "ACTIVE"


def test_usage_meter_and_persistence():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        ledger_path = f.name

    try:
        meter = TenantUsageMeter(ledger_path=ledger_path)
        tenant_id = "ten_test_enterprise_01"

        # Record various activities
        meter.record_ast_scan(tenant_id, count=2500)
        meter.record_threat_blocked(tenant_id, count=12)
        meter.record_escrow_settlement(tenant_id, volume_usd=5000.0)
        meter.record_webhook_dispatch(tenant_id, count=50)

        rec = meter.records[tenant_id]
        assert rec.ast_scans == 2500
        assert rec.threats_blocked == 12
        assert rec.escrow_volume_usd == 5000.0
        assert rec.webhooks_dispatched == 50

        # Reload in a new instance to verify persistence
        meter_reloaded = TenantUsageMeter(ledger_path=ledger_path)
        rec2 = meter_reloaded.records[tenant_id]
        assert rec2.ast_scans == 2500
        assert rec2.escrow_volume_usd == 5000.0
    finally:
        if os.path.exists(ledger_path):
            os.remove(ledger_path)


def test_metered_invoice_generation_math_and_signatures():
    usage = TenantUsageRecord(
        tenant_id="ten_finance_corp_prod",
        org_id="finance-corp",
        project_id="risk-mesh",
        ast_scans=10000,           # 10,000 * 0.0001 = $1.00
        threats_blocked=100,       # 100 * 0.001 = $0.10
        escrow_volume_usd=20000.0, # 20,000 * 0.005 = $100.00
        webhooks_dispatched=500,   # 500 * 0.002 = $1.00
    )

    inv = MeteredInvoiceGenerator.generate_invoice(
        usage=usage,
        settlement_rail="L402_LIGHTNING",
        include_base_subscription=True
    )

    expected_total = 49.00 + 1.00 + 0.10 + 100.00 + 1.00  # $151.10
    assert inv.base_subscription_usd == 49.00
    assert inv.ast_scans_cost_usd == 1.00
    assert inv.threats_blocked_cost_usd == 0.10
    assert inv.escrow_fees_usd == 100.00
    assert inv.webhooks_cost_usd == 1.00
    assert inv.total_due_usd == expected_total
    assert inv.settlement_rail == "L402_LIGHTNING"
    assert inv.signature.startswith("btp_sig_")
    assert len(inv.signature) > 16


def test_cli_init_and_billing_execution(capsys):
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. Test CLI init
        args_init = argparse.Namespace(
            dir=temp_dir,
            framework="langgraph",
            org="test-ai-labs",
            project="graph-agent",
            env="staging"
        )
        cmd_init(args_init)
        out_init = capsys.readouterr().out
        assert "BTP ENTERPRISE DEVELOPER ONBOARDING: PROJECT INITIALIZED" in out_init
        assert "LANGGRAPH" in out_init
        assert "BTPLangGraphGuard" in out_init

        # 2. Test CLI billing usage & invoice
        args_usage = argparse.Namespace(tenant="ten_novartis_health_prod")
        cmd_billing_usage(args_usage)
        out_usage = capsys.readouterr().out
        assert "BTP METERED USAGE STATEMENT" in out_usage

        args_invoice = argparse.Namespace(tenant="ten_novartis_health_prod", rail="STRIPE_METERED")
        cmd_billing_invoice(args_invoice)
        out_invoice = capsys.readouterr().out
        assert "BTP ITEMIZED INVOICE:" in out_invoice
        assert "TOTAL AMOUNT DUE" in out_invoice
