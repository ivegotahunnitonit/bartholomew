import json
import os
from urllib import error

from src.btp_guard import Guard
from src.btp_guard.authorization_gate import AuthorizationGate
from src.btp_guard.stripe_bridge import StripeMeterBridge


def test_l402_settlement_verification(tmp_path):
    import secrets
    import hashlib

    gate = AuthorizationGate(policy={"allow_destructive": False})
    preimage_bytes = secrets.token_bytes(32)
    preimage_hex = preimage_bytes.hex()
    payment_hash = hashlib.sha256(preimage_bytes).hexdigest()

    # Valid settlement
    res_valid = gate.evaluate({
        "agent_id": "l402-agent",
        "action_type": "m2m_call",
        "payload": {
            "command": "git status",
            "l402_preimage": preimage_hex,
            "l402_payment_hash": payment_hash
        }
    })
    assert res_valid["verdict"] == "ALLOW"
    assert res_valid["l402_settled"] is True

    # Invalid settlement
    res_invalid = gate.evaluate({
        "agent_id": "l402-agent",
        "action_type": "m2m_call",
        "payload": {
            "command": "git status",
            "l402_preimage": secrets.token_bytes(32).hex(),
            "l402_payment_hash": payment_hash
        }
    })
    assert res_invalid["verdict"] == "DENY"
    assert "BTP-L402-001" in res_invalid["rule_id"]


def test_allowed_action_creates_billable_ledger_event(tmp_path):
    ledger_path = tmp_path / "ledger.db"
    gate = AuthorizationGate(policy={"allow_destructive": False}, ledger_path=str(ledger_path))
    result = gate.evaluate({
        "agent_id": "worker-ledger",
        "tenant_id": "tenant-123",
        "action_type": "tool_call",
        "payload": {"command": "echo hello"},
    })

    assert result["verdict"] == "ALLOW"
    assert os.path.exists(ledger_path)
    billable_rows = gate.ledger.list_events(limit=10)
    assert len(billable_rows) == 1
    assert billable_rows[0]["event_name"] == "btp.guard.action.allowed"
    assert billable_rows[0]["amount_usd"] > 0


def test_denied_action_does_not_create_billable_ledger_event(tmp_path):
    ledger_path = tmp_path / "ledger.db"
    gate = AuthorizationGate(policy={"allow_destructive": False}, ledger_path=str(ledger_path))
    result = gate.evaluate({
        "agent_id": "worker-deny",
        "tenant_id": "tenant-456",
        "action_type": "shell",
        "payload": {"command": "rm -rf /tmp/data"},
    })

    assert result["verdict"] == "DENY"
    assert gate.ledger.list_events(limit=10) == []


def test_stripe_meter_bridge_builds_usage_payload_from_ledger_event():
    bridge = StripeMeterBridge(api_key="sk_test_123", meter_name="autonomous_action_allowed")
    event = {
        "id": "evt_123",
        "event_name": "btp.guard.action.allowed",
        "tenant_id": "tenant-123",
        "agent_id": "worker-ledger",
        "action_type": "tool_call",
        "amount_usd": 0.01,
        "currency": "USD",
        "policy_version": "v5.4.12",
        "receipt_sha256": "abc123",
        "created_at": "2026-09-15T00:00:00+00:00",
    }

    payload = bridge.build_usage_payload(event)

    assert payload["event_name"] == "btp.guard.action.allowed"
    assert payload["quantity"] == 1
    assert payload["value"] == 0.01
    assert payload["customer_id"] == "tenant-123"
    assert payload["policy_version"] == "v5.4.12"


def test_stripe_meter_bridge_skips_when_no_api_key():
    bridge = StripeMeterBridge(api_key="", meter_name="autonomous_action_allowed")
    event = {"id": "evt_456", "event_name": "btp.guard.action.allowed", "tenant_id": "tenant-abc"}

    assert bridge.report_usage(event) is None


def test_stripe_meter_bridge_resolves_customer_mapping():
    bridge = StripeMeterBridge(
        api_key="sk_test_123",
        meter_name="autonomous_action_allowed",
        customer_map={"tenant-123": "cus_abc123"},
    )

    payload = bridge.build_usage_payload({
        "event_name": "btp.guard.action.allowed",
        "tenant_id": "tenant-123",
        "amount_usd": 0.01,
    })

    assert payload["customer_id"] == "cus_abc123"


def test_stripe_meter_bridge_posts_meter_event(monkeypatch):
    calls = {}

    class FakeResponse:
        status = 200

        def read(self):
            return b'{"status": "ok"}'

    def fake_urlopen(req):
        calls["method"] = req.get_method()
        calls["url"] = req.full_url
        calls["headers"] = req.headers
        calls["data"] = req.data.decode("utf-8")
        return FakeResponse()

    monkeypatch.setattr("src.btp_guard.stripe_bridge.urlopen", fake_urlopen)

    bridge = StripeMeterBridge(api_key="sk_test_123", meter_name="autonomous_action_allowed")
    event = {
        "id": "evt_789",
        "event_name": "btp.guard.action.allowed",
        "tenant_id": "tenant-123",
        "agent_id": "worker-ledger",
        "action_type": "tool_call",
        "amount_usd": 0.01,
        "currency": "USD",
        "policy_version": "v5.4.12",
        "receipt_sha256": "abc123",
        "created_at": "2026-09-15T00:00:00+00:00",
    }

    result = bridge.report_usage(event)

    assert result["status"] == "success"
    assert calls["method"] == "POST"
    assert "billing/meter_events" in calls["url"]
    assert "Bearer sk_test_123" in calls["headers"]["Authorization"]
    assert "event_name=autonomous_action_allowed" in calls["data"]
    assert "payload%5Bstripe_customer_id%5D=tenant-123" in calls["data"]
    assert "payload%5Bvalue%5D=1" in calls["data"]


def test_stripe_meter_bridge_exposes_http_error_details_on_failure(monkeypatch):
    def fake_urlopen(req):
        raise error.URLError("customer not found")

    monkeypatch.setattr("src.btp_guard.stripe_bridge.urlopen", fake_urlopen)

    bridge = StripeMeterBridge(api_key="sk_test_123", meter_name="autonomous_action_allowed")
    result = bridge.report_usage({
        "id": "evt_err",
        "event_name": "btp.guard.action.allowed",
        "tenant_id": "tenant-123",
        "amount_usd": 0.01,
    })

    assert result["status"] == "failed"
    assert "customer not found" in str(result["error"])


def test_validate_configuration_checks_account_meter_and_customer(monkeypatch):
    calls = []

    class FakeResponse:
        def __init__(self, payload):
            self.payload = payload

        def read(self):
            return json.dumps(self.payload).encode("utf-8")

        def close(self):
            pass

    def fake_urlopen(req):
        calls.append((req.full_url, req.get_method(), req.headers.get("Authorization")))
        url = req.full_url
        if url.endswith("/v1/account"):
            return FakeResponse({"id": "acct_live_123"})
        if "/v1/billing/meters" in url:
            return FakeResponse({"data": [{"id": "meters_001", "display_name": "autonomous_action_allowed"}]})
        if url.endswith("/v1/customers/cus_123"):
            return FakeResponse({"id": "cus_123", "email": "tenant@example.com"})
        raise AssertionError(f"Unexpected URL {url}")

    monkeypatch.setattr("src.btp_guard.stripe_bridge.urlopen", fake_urlopen)

    bridge = StripeMeterBridge(
        api_key="sk_test_123",
        meter_name="autonomous_action_allowed",
        customer_map={"tenant-demo": "cus_123"},
    )
    result = bridge.validate_configuration("tenant-demo")

    assert result["status"] == "ok"
    assert result["account_found"] is True
    assert result["meter_found"] is True
    assert result["customer_found"] is True


def test_safe_action_is_allowed():
    gate = AuthorizationGate()
    result = gate.evaluate(
        {
            "agent_id": "worker-1",
            "action_type": "shell",
            "payload": {"command": "ls -la /tmp"},
            "policy": {"allow_destructive": False},
        }
    )

    assert result["verdict"] == "ALLOW"
    assert result["rule_id"] is None
    assert result["reason"] == "No policy violations detected"
    assert "receipt_sha256" in result
    assert result["latency_ms"] >= 0


def test_destructive_shell_action_is_denied():
    gate = AuthorizationGate()
    result = gate.evaluate(
        {
            "agent_id": "worker-1",
            "action_type": "shell",
            "payload": {"command": "rm -rf /tmp/data"},
            "policy": {"allow_destructive": False},
        }
    )

    assert result["verdict"] == "DENY"
    assert result["rule_id"] == "BTP-SHELL-001"
    assert "Destructive shell pattern" in result["reason"]
    assert result["receipt_sha256"]


def test_secret_leak_is_denied():
    gate = AuthorizationGate()
    result = gate.evaluate(
        {
            "agent_id": "worker-1",
            "action_type": "tool_call",
            "payload": {"text": "Token: ghp_1234567890abcdef1234567890abcdef"},
            "policy": {"allow_destructive": False},
        }
    )

    assert result["verdict"] == "DENY"
    assert result["rule_id"] == "BTP-SECRET-001"
    assert "secret" in result["reason"].lower()


def test_max_spend_policy_is_enforced():
    gate = AuthorizationGate(policy={"max_spend_usd": 10.0})
    result = gate.evaluate(
        {
            "agent_id": "worker-2",
            "action_type": "payment",
            "payload": {"amount_usd": 25.0},
        }
    )

    assert result["verdict"] == "DENY"
    assert result["rule_id"] == "BTP-SPEND-001"
    assert "max_spend_usd" in result["reason"].lower()


def test_blocked_rule_policy_is_applied():
    gate = AuthorizationGate(policy={"blocked_rules": ["BTP-SECRET-001"]})
    result = gate.evaluate(
        {
            "agent_id": "worker-3",
            "action_type": "tool_call",
            "payload": {"text": "Token: ghp_1234567890abcdef1234567890abcdef"},
        }
    )

    assert result["verdict"] == "DENY"
    assert result["rule_id"] == "BTP-SECRET-001"
    assert "blocked by policy" in result["reason"].lower()


def test_action_policy_override_allows_destructive_command():
    gate = AuthorizationGate(policy={"allow_destructive": False})
    result = gate.evaluate(
        {
            "agent_id": "worker-4",
            "action_type": "shell",
            "payload": {"command": "rm -rf /tmp/data"},
            "policy": {"allow_destructive": True},
        }
    )

    assert result["verdict"] == "ALLOW"
    assert result["rule_id"] is None
    assert result["reason"] == "No policy violations detected"


def test_guard_public_api_checks_command_strings():
    guard = Guard(policy={"allow_destructive": False})
    result = guard.check("ls -la /tmp")

    assert result["verdict"] == "ALLOW"
    assert result["rule_id"] is None
    assert "receipt_sha256" in result


def test_guard_evaluate_alias_and_is_allowed_helper():
    guard = Guard(policy={"allow_destructive": False})
    result = guard.evaluate({
        "agent_id": "worker-5",
        "action_type": "shell",
        "payload": {"command": "echo hello"},
    })

    assert result["verdict"] == "ALLOW"
    assert guard.is_allowed("echo hello") is True
    assert guard.is_allowed("rm -rf /tmp/data") is False


def test_request_policy_version_is_propagated():
    gate = AuthorizationGate(policy={"allow_destructive": False})
    result = gate.evaluate({
        "agent_id": "worker-6",
        "action_type": "shell",
        "payload": {"command": "echo hello"},
        "policy": {"allow_destructive": False, "policy_version": "v5.5.0"},
    })

    assert result["policy_version"] == "v5.5.0"
    assert result["verdict"] == "ALLOW"


def test_request_level_policy_override_takes_precedence():
    gate = AuthorizationGate(policy={"allow_destructive": False})
    result = gate.evaluate({
        "agent_id": "worker-7",
        "action_type": "shell",
        "payload": {"command": "rm -rf /tmp/data"},
        "policy": {"allow_destructive": True, "policy_version": "v5.5.0"},
    })

    assert result["verdict"] == "ALLOW"
    assert result["policy_version"] == "v5.5.0"
