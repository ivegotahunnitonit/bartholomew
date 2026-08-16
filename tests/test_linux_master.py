"""
Unit tests for Bartholomew BTP Linux Resource Execution Adapter (LinuxExecutionAdapter).
"""

import pytest
from bartholomew_eval.linux_adapter import LinuxExecutionAdapter


def test_linux_adapter_authority_boundary_check():
    adapter = LinuxExecutionAdapter()
    
    # Authorized command within permitted paths
    res_valid = adapter.evaluate_execution(
        command="cat /var/log/app.log",
        agent_did="did:bth:agent_auditor",
        possessed_capabilities=["posix.execute"],
        allowed_paths=["/var/log"]
    )
    assert res_valid["is_authorized"] is True
    assert res_valid["decision"] == "ALLOW"
    assert res_valid["denial_reason"] is None

    # Path boundary escape attempt
    res_escape = adapter.evaluate_execution(
        command="cat /etc/passwd",
        agent_did="did:bth:agent_restricted",
        possessed_capabilities=["posix.execute"],
        allowed_paths=["/tmp"]
    )
    assert res_escape["is_authorized"] is False
    assert res_escape["decision"] == "DENY"
    assert "Target path boundary escape" in res_escape["denial_reason"]


def test_linux_adapter_missing_capability():
    adapter = LinuxExecutionAdapter()
    res = adapter.evaluate_execution(
        command="echo 'test'",
        agent_did="did:bth:agent_no_exec",
        possessed_capabilities=["posix.read"]
    )
    assert res["is_authorized"] is False
    assert "lacks required capability" in res["denial_reason"]


def test_linux_adapter_cis_benchmark_evidence():
    adapter = LinuxExecutionAdapter()
    cis = adapter.evaluate_cis_benchmark("Ubuntu 24.04 LTS Level 1 Server")
    
    assert cis["controls_evaluated"] == 67
    assert cis["passed_controls"] == 58
    assert cis["failed_controls"] == 6
    assert cis["not_applicable_controls"] == 3
    assert len(cis["key_controls"]) > 0


def test_financial_fee_leakage_protection():
    adapter = LinuxExecutionAdapter()
    
    # Safe fee (1% fee)
    safe_res = adapter.evaluate_financial_protection(transaction_amount_usd=10.00, fee_usd=0.10, payment_method="paypal")
    assert safe_res["is_authorized"] is True
    assert safe_res["fee_protection_status"] == "FEE_PROTECTED"

    # Excessive fee leakage (15% gas fee)
    leak_res = adapter.evaluate_financial_protection(transaction_amount_usd=10.00, fee_usd=1.50, payment_method="crypto")
    assert leak_res["is_authorized"] is False
    assert leak_res["fee_protection_status"] == "BLOCKED_FEE_LEAKAGE"

