"""
Tests for Bartholomew Cloud Engine Server
=========================================
Tests health check, telemetry ingestion, stats computation,
key generation, and instant SOC 2 compliance dossier export.
"""

import time
import pytest
from fastapi.testclient import TestClient
from src.api.cloud_engine_server import app

client = TestClient(app)


def test_health_check_endpoint():
    """Verify Cloud Run container health probe."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "bartolomew-cloud-engine"
    assert data["version"] == "5.4.0"


def test_telemetry_batch_ingest_and_events():
    """Verify batch ingestion and retrieval of telemetry events."""
    payload = {
        "events": [
            {
                "event_id": "evt_test_1001",
                "workspace_id": "ws_test_enterprise",
                "agent_id": "agent-worker-1",
                "timestamp": time.time(),
                "action_type": "execute_sql",
                "verdict": "ALLOW",
                "rule_id": "RULE-AST-000",
                "reason": "Safe read query",
                "latency_us": 11.2,
                "payload_hash": "a1b2c3d4e5f6",
                "receipt": {"signature": "sig_test_1", "merkle_root": "mrk_test_1"}
            },
            {
                "event_id": "evt_test_1002",
                "workspace_id": "ws_test_enterprise",
                "agent_id": "agent-worker-1",
                "timestamp": time.time(),
                "action_type": "bash_exec",
                "verdict": "DENY",
                "rule_id": "RULE-AST-001",
                "reason": "Destructive shell command vetoed: rm -rf /var",
                "latency_us": 28.4,
                "payload_hash": "f6e5d4c3b2a1",
                "receipt": {"signature": "sig_test_2", "merkle_root": "mrk_test_2"}
            }
        ],
        "client_version": "5.4.0",
        "sent_at": time.time()
    }

    ingest_resp = client.post("/api/v1/telemetry/ingest", json=payload)
    assert ingest_resp.status_code == 200
    assert ingest_resp.json()["ingested"] == 2

    # Query events
    events_resp = client.get("/api/v1/telemetry/events?workspace_id=ws_test_enterprise&limit=10")
    assert events_resp.status_code == 200
    events_data = events_resp.json()
    assert events_data["count"] >= 2


def test_telemetry_stats_endpoint():
    """Verify fleet throughput, average latency, and compliance status."""
    resp = client.get("/api/v1/telemetry/stats?workspace_id=all")
    assert resp.status_code == 200
    stats = resp.json()
    assert "total_evaluations" in stats
    assert "average_latency_us" in stats
    assert "compliance_status" in stats
    assert stats["total_evaluations"] > 0
    assert stats["average_latency_us"] < 100.0


def test_key_generation_and_verification():
    """Verify generation of team API keys and license verification."""
    gen_payload = {
        "org_name": "Test Acme AI Corp",
        "tier": "PRO",
        "workspace_name": "Acme Coding Swarm"
    }
    gen_resp = client.post("/api/v1/workspaces/generate-key", json=gen_payload)
    assert gen_resp.status_code == 200
    key_info = gen_resp.json()
    assert key_info["api_key"].startswith("sk_btp_live_")
    assert key_info["tier"] == "PRO"
    assert key_info["max_agents"] == 10

    # Verify key
    verify_resp = client.get("/api/v1/workspaces/verify-key", headers={"x-api-key": key_info["api_key"]})
    assert verify_resp.status_code == 200
    v_data = verify_resp.json()
    assert v_data["valid"] is True
    assert v_data["tier"] == "PRO"
    assert v_data["org_name"] == "Test Acme AI Corp"


def test_soc2_compliance_export():
    """Verify generation of signed SOC 2 Type II audit dossier."""
    resp = client.post("/api/v1/compliance/soc2-export?workspace_id=ws_enterprise_core&org_name=AcmeCorp")
    assert resp.status_code == 200
    dossier = resp.json()
    assert "report_id" in dossier
    assert "compliance_frameworks" in dossier
    assert "merkle_verification" in dossier
    assert dossier["tenant_id"] == "ws_enterprise_core"


def test_security_badge_endpoints():
    """Verify dynamic SVG security badge generation for GitHub READMEs."""
    resp = client.get("/api/v1/badge/shield")
    assert resp.status_code == 200
    assert "image/svg+xml" in resp.headers["content-type"]
    svg_text = resp.text
    assert "<svg" in svg_text
    assert "Secured by Bartholomew" in svg_text
    assert "BTP v5.4.7" in svg_text

    # Test customized framework badge
    resp_crewai = client.get("/api/v1/badge/shield?agent=crewai&status=v5.4.7")
    assert resp_crewai.status_code == 200
    assert "Crewai • Bartholomew" in resp_crewai.text

