"""
Unit & Integration Tests for BTP Milestone 5.1: Real-Time Incident Webhooks & SecOps Alerts
========================================================================================
Validates HMAC-SHA256 signing, multi-platform formatting (Slack, Discord, PagerDuty),
multi-tenant isolation, severity filtering, and end-to-end guard/escrow emission.
"""

import os
import json
import time
import tempfile
import pytest

from src.alerting.webhook_dispatcher import (
    AlertSeverity,
    WebhookPlatform,
    IncidentEventType,
    IncidentEvent,
    WebhookSubscription,
    WebhookFormatter,
    WebhookSignatureEngine,
    WebhookDispatcher,
)
from framework_adapters.universal.universal_model_guard import UniversalBTPModelGuard, ModelProvider
from src.agent_passport import SovereignAgentPassport
from src.settlement.autonomous_escrow import AutonomousEscrowPool
from src.settlement.swarm_arbitration import (
    SwarmDisputeArbitrator,
    ArbitrationResolutionCertificate,
    ZKFaultProofEngine,
)


@pytest.fixture
def temp_store():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_hmac_signature_generation_and_verification():
    secret = "btp_wh_super_secret_signing_key_42"
    payload = json.dumps({"event": "threat.ast_veto", "agent": "agent-007"}).encode("utf-8")

    # 1. Fresh valid signature
    sig_header = WebhookSignatureEngine.sign_payload(payload, secret)
    assert sig_header.startswith("t=")
    assert ",v1=" in sig_header
    assert WebhookSignatureEngine.verify_signature(payload, sig_header, secret) is True

    # 2. Secret mismatch fails
    assert WebhookSignatureEngine.verify_signature(payload, sig_header, "wrong_secret") is False

    # 3. Tampered payload fails
    tampered = json.dumps({"event": "threat.ast_veto", "agent": "agent-008"}).encode("utf-8")
    assert WebhookSignatureEngine.verify_signature(tampered, sig_header, secret) is False

    # 4. Expired timestamp (> 300s) fails
    old_ts = int(time.time()) - 400
    expired_sig = WebhookSignatureEngine.sign_payload(payload, secret, timestamp=old_ts)
    assert WebhookSignatureEngine.verify_signature(payload, expired_sig, secret, max_age_seconds=300) is False


def test_webhook_formatters():
    event = IncidentEvent(
        event_id="evt_test_format_01",
        tenant_id="ten_acme_corp_prod",
        org_id="acme-corp",
        project_id="risk-swarm",
        environment="prod",
        event_type=IncidentEventType.AST_VETO,
        severity=AlertSeverity.CRITICAL,
        title="Unauthorized Shell Command",
        description="Agent attempted 'rm -rf /' in production environment.",
        agent_id="agent-risk-42",
        tool_name="bash_executor",
        target_payload='{"cmd": "rm -rf /"}',
        slashed_amount_usd=250.0,
        metadata={"quarantined": True}
    )

    # 1. Slack Block Kit
    slack_payload = WebhookFormatter.format_slack(event)
    assert "attachments" in slack_payload
    blocks = slack_payload["attachments"][0]["blocks"]
    assert any("Unauthorized Shell Command" in b.get("text", {}).get("text", "") for b in blocks)
    assert slack_payload["attachments"][0]["color"] == "#7b0000"

    # 2. Discord Embed
    discord_payload = WebhookFormatter.format_discord(event)
    assert "embeds" in discord_payload
    embed = discord_payload["embeds"][0]
    assert "Unauthorized Shell Command" in embed["title"]
    assert embed["color"] == 8060928
    assert any(f["name"] == "Slashed Collateral" for f in embed["fields"])

    # 3. PagerDuty Events v2
    pd_payload = WebhookFormatter.format_pagerduty(event, routing_key="pd-route-key-123")
    assert pd_payload["event_action"] == "trigger"
    assert pd_payload["payload"]["severity"] == "critical"
    assert "risk-42" in pd_payload["dedup_key"]

    # 4. Generic SIEM
    generic_payload = WebhookFormatter.format_generic(event)
    assert generic_payload["version"] == "5.1.0"
    assert generic_payload["event"]["event_id"] == "evt_test_format_01"


def test_dispatcher_tenant_isolation_and_severity_filtering(temp_store):
    dispatched_calls = []

    def mock_http_post(url, data, headers):
        dispatched_calls.append({"url": url, "data": json.loads(data.decode("utf-8")), "headers": headers})
        return 200, "OK"

    dispatcher = WebhookDispatcher(store_path=temp_store, sync_mode=True, http_post_fn=mock_http_post)

    # Sub 1: Tenant A, Min Severity HIGH
    dispatcher.register_subscription(
        tenant_id="ten_aaa",
        platform=WebhookPlatform.SLACK,
        target_url="https://hooks.slack.com/ten_aaa",
        min_severity=AlertSeverity.HIGH
    )
    # Sub 2: Tenant B, Min Severity LOW
    dispatcher.register_subscription(
        tenant_id="ten_bbb",
        platform=WebhookPlatform.DISCORD,
        target_url="https://discord.com/api/ten_bbb",
        min_severity=AlertSeverity.LOW
    )
    # Sub 3: Universal (*), Min Severity CRITICAL
    dispatcher.register_subscription(
        tenant_id="*",
        platform=WebhookPlatform.GENERIC,
        target_url="https://siem.enterprise.corp/events",
        min_severity=AlertSeverity.CRITICAL
    )

    # Event 1: Tenant A, LOW severity -> Should trigger 0 subscriptions (Sub 1 requires HIGH, Sub 2 is Tenant B, Sub 3 is CRITICAL)
    event_low_a = IncidentEvent(
        event_id="evt_1",
        tenant_id="ten_aaa",
        org_id="org_a",
        project_id="p1",
        environment="dev",
        event_type=IncidentEventType.AST_VETO,
        severity=AlertSeverity.LOW,
        title="Minor Notice",
        description="Harmless query",
        agent_id="agent-a1"
    )
    res1 = dispatcher.emit_incident(event_low_a)
    assert len(res1) == 0
    assert len(dispatched_calls) == 0

    # Event 2: Tenant A, HIGH severity -> Should trigger Sub 1 only
    event_high_a = IncidentEvent(
        event_id="evt_2",
        tenant_id="ten_aaa",
        org_id="org_a",
        project_id="p1",
        environment="dev",
        event_type=IncidentEventType.AST_VETO,
        severity=AlertSeverity.HIGH,
        title="High Invariant Warning",
        description="Dangerous command dropped",
        agent_id="agent-a1"
    )
    res2 = dispatcher.emit_incident(event_high_a)
    assert len(res2) == 1
    assert res2[0]["target_url"] == "https://hooks.slack.com/ten_aaa"
    assert len(dispatched_calls) == 1
    assert "X-BTP-Signature" in dispatched_calls[0]["headers"]

    # Event 3: Tenant B, CRITICAL severity -> Should trigger Sub 2 (Tenant B) AND Sub 3 (Universal *)
    event_crit_b = IncidentEvent(
        event_id="evt_3",
        tenant_id="ten_bbb",
        org_id="org_b",
        project_id="p2",
        environment="prod",
        event_type=IncidentEventType.ESCROW_SLASHED,
        severity=AlertSeverity.CRITICAL,
        title="Escrow Slashed",
        description="Malicious action penalized",
        agent_id="agent-b1"
    )
    res3 = dispatcher.emit_incident(event_crit_b)
    assert len(res3) == 2
    urls = [r["target_url"] for r in res3]
    assert "https://discord.com/api/ten_bbb" in urls
    assert "https://siem.enterprise.corp/events" in urls
    assert len(dispatched_calls) == 3


def test_universal_guard_emits_webhook_on_veto(temp_store):
    dispatched = []

    def mock_post(url, data, headers):
        dispatched.append({"url": url, "payload": json.loads(data.decode("utf-8")), "headers": headers})
        return 200, "OK"

    dispatcher = WebhookDispatcher(store_path=temp_store, sync_mode=True, http_post_fn=mock_post)

    # Register subscription for our specific tenant
    guard = UniversalBTPModelGuard(
        org_id="bartholomew-core",
        project_id="antigravity-dev",
        environment="dev",
        strict=False,  # Non-strict returns VETOED dict instead of raising
        webhook_dispatcher=dispatcher
    )

    dispatcher.register_subscription(
        tenant_id=guard.tenant_id,
        platform=WebhookPlatform.GENERIC,
        target_url="https://secops.bartholomew.network/alerts",
        min_severity=AlertSeverity.HIGH
    )

    # Safe call: Should not trigger alert
    res_safe = guard.intercept_and_verify(
        {"name": "read_file", "arguments": {"path": "README.md"}},
        provider=ModelProvider.OPENAI
    )
    assert res_safe["status"] == "APPROVED"
    assert len(dispatched) == 0

    # Malicious call: Should veto and trigger webhook alert
    res_bad = guard.intercept_and_verify(
        {"name": "shell_exec", "arguments": {"command": "rm -rf /var/log"}},
        provider=ModelProvider.OPENAI
    )
    assert res_bad["status"] == "VETOED"
    assert len(dispatched) == 1
    call = dispatched[0]
    assert call["url"] == "https://secops.bartholomew.network/alerts"
    assert call["headers"]["X-BTP-Event-Type"] == IncidentEventType.AST_VETO.value
    assert call["payload"]["event"]["tenant_id"] == guard.tenant_id
    assert "rm -rf" in call["payload"]["event"]["target_payload"]


def test_escrow_slashing_emits_webhook(temp_store):
    dispatched = []

    def mock_post(url, data, headers):
        dispatched.append({"url": url, "payload": json.loads(data.decode("utf-8")), "headers": headers})
        return 200, "OK"

    dispatcher = WebhookDispatcher(store_path=temp_store, sync_mode=True, http_post_fn=mock_post)

    passport = SovereignAgentPassport.issue(
        agent_id="agent-slashed-worker-01",
        model_family="gpt-4o",
        org_id="test-org",
        project_id="settlement-test",
        environment="dev"
    )

    pool = AutonomousEscrowPool(webhook_dispatcher=dispatcher)

    # Register webhook for this tenant
    dispatcher.register_subscription(
        tenant_id=passport.tenant_id,
        platform=WebhookPlatform.SLACK,
        target_url="https://hooks.slack.com/services/escrow-alert",
        min_severity=AlertSeverity.HIGH
    )

    # Lock collateral
    deposit = pool.lock_escrow(
        agent_id=passport.agent_id,
        action_type="HIGH_RISK_TRADE",
        amount_usd=500.0,
        passport=passport
    )

    # Swarm dispute arbitration verdict
    cert = ArbitrationResolutionCertificate(
        certificate_id="CERT-ARB-TEST-01",
        dispute_id="DISPUTE-01",
        escrow_id=deposit.escrow_id,
        target_agent_id=passport.agent_id,
        verdict="SLASH_COLLATERAL",
        slashed_amount_usd=500.0,
        quorum_count=3,
        participating_passports=["p1", "p2", "p3"],
        certificate_hash="0xabcdef",
        timestamp=time.time(),
        aggregate_signatures=["sig1", "sig2", "sig3"]
    )

    ok, msg, receipt = pool.arbitrate_and_slash(
        escrow_id=deposit.escrow_id,
        arbitration_cert=cert,
        payee_destination="victim_vault_0x123",
        agent_passport=passport
    )
    assert ok is True

    # Check that webhook was dispatched
    assert len(dispatched) == 1
    assert dispatched[0]["url"] == "https://hooks.slack.com/services/escrow-alert"
    assert dispatched[0]["headers"]["X-BTP-Event-Type"] == IncidentEventType.ESCROW_SLASHED.value
    assert "attachments" in dispatched[0]["payload"]
