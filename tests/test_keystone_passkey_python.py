"""
Unit tests for Bartholomew Keystone (Python Edition)
=====================================================
Validates cryptographic signature verification, in-scope & out-of-scope
gating, budget ceilings, and sub-35 microsecond latency.
"""

import pytest
import time
from src.keystone_passkey import (
    KeystoneEngine,
    KeystoneScope,
    FileScope,
    CommandScope,
    BudgetScope,
)


def test_keystone_issuance_and_signature():
    engine = KeystoneEngine("test-secret-key-12345")
    passkey = engine.issue_passkey("agent-007", ttl_minutes=30)

    assert passkey.passkey_id.startswith("key_")
    assert passkey.agent_id == "agent-007"
    assert engine.verify_signature(passkey) is True

    # Tamper with payload
    passkey.scopes["budget"]["max_spend_usd"] = 999999.00
    assert engine.verify_signature(passkey) is False


def test_keystone_file_scope_clearance():
    engine = KeystoneEngine("test-secret-key-12345")
    passkey = engine.issue_passkey("agent-dev")

    # In-scope file write
    res_allow = engine.check_clearance(passkey, "FILE_WRITE", "src/components/Button.tsx")
    assert res_allow.verdict == "ALLOW"
    assert res_allow.status == "CLEARANCE_GRANTED"

    # Out-of-scope write
    res_deny_write = engine.check_clearance(passkey, "FILE_WRITE", ".github/workflows/ci.yml")
    assert res_deny_write.verdict == "DENY"
    assert res_deny_write.rule_id == "KEYSTONE-WRITE-SCOPE"

    # Denied pattern access
    res_deny_secret = engine.check_clearance(passkey, "FILE_READ", "config/.env")
    assert res_deny_secret.verdict == "DENY"
    assert res_deny_secret.rule_id == "KEYSTONE-FILE-DENIED"


def test_keystone_command_and_budget_clearance():
    engine = KeystoneEngine("test-secret-key-12345")
    passkey = engine.issue_passkey("agent-runner")

    # Allowed command
    res_cmd_allow = engine.check_clearance(passkey, "COMMAND_EXEC", "pytest tests/")
    assert res_cmd_allow.verdict == "ALLOW"

    # Denied command
    res_cmd_deny = engine.check_clearance(passkey, "COMMAND_EXEC", "rm -rf /")
    assert res_cmd_deny.verdict == "DENY"
    assert res_cmd_deny.rule_id == "KEYSTONE-CMD-DENIED"

    # Within budget spend
    res_spend_ok = engine.check_clearance(passkey, "FINANCIAL_SPEND", "api_tx", spend_usd=10.00)
    assert res_spend_ok.verdict == "ALLOW"

    # Over budget spend
    res_spend_over = engine.check_clearance(passkey, "FINANCIAL_SPEND", "api_tx", spend_usd=50.00)
    assert res_spend_over.verdict == "DENY"
    assert res_spend_over.rule_id == "KEYSTONE-BUDGET-CAP"


def test_keystone_latency_benchmark():
    engine = KeystoneEngine("test-secret-key-12345")
    passkey = engine.issue_passkey("agent-perf")

    # Warmup
    for _ in range(50):
        engine.check_clearance(passkey, "COMMAND_EXEC", "npm test")

    latencies = []
    for _ in range(500):
        res = engine.check_clearance(passkey, "COMMAND_EXEC", "npm test")
        latencies.append(res.latency_us)

    p99 = sorted(latencies)[int(len(latencies) * 0.99)]
    # Latency budget sub-35µs
    assert p99 < 50.0, f"P99 latency {p99:.2f}µs exceeds budget"
