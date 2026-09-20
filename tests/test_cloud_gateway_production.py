"""
Integration and Smoke Test Suite for Bartholomew Cloud Gateway
==============================================================
Validates zero-install cloud endpoints, manifest discovery, AST gating,
secret scrubbing, and Ed25519 receipt verification for production readiness.
"""

import pytest
from fastapi.testclient import TestClient
from src.gateway_server import app, authority
from src.trust_protocol import IndependentTrustVerifier


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_gateway_health_check(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "BTP" in data["protocol"]
    assert data["rules_active"] > 0
    assert "authority_public_key" in data
    assert len(data["authority_public_key"]) == 64


def test_gateway_landing_page_html(client):
    response = client.get("/", headers={"accept": "text/html,application/xhtml+xml"})
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Bartholomew" in response.text
    assert "BTP" in response.text


def test_manifest_discovery_endpoint(client):
    response = client.get("/.well-known/btp.json")
    assert response.status_code == 200
    data = response.json()
    assert data["manifest_version"] in ["1.0.0", "5.4.0"]
    assert data["identity"]["name"] == "Bartholomew Trust Protocol"
    assert "transaction_authorization" in data["capabilities"]


def test_ai_plugin_manifest(client):
    response = client.get("/.well-known/ai-plugin.json")
    assert response.status_code == 200
    data = response.json()
    assert data["name_for_model"] == "bartholomew_guard"
    assert data["api"]["type"] == "openapi"


def test_trust_root_endpoint(client):
    response = client.get("/v1/trust-root")
    assert response.status_code == 200
    data = response.json()
    assert data["authority_pubkey"] == authority.public_key_hex
    assert data["active_rules_count"] > 0


def test_eval_benign_action_allowed(client):
    payload = {
        "bot_type": "grok",
        "action": "system_status",
        "tool": "bash",
        "arguments": {"command": "uptime -p"}
    }
    response = client.post("/v1/eval", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is True
    assert data["verdict"] == "ALLOW"
    assert "receipt" in data
    assert "signature" in data["receipt"]
    assert len(data["receipt"]["signature"]) == 128


def test_eval_destructive_command_blocked(client):
    payload = {
        "bot_type": "meta_ai",
        "tool": "bash",
        "arguments": {"command": "rm -rf / --no-preserve-root"}
    }
    response = client.post("/v1/eval", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is False
    assert data["verdict"] == "DENY"
    assert "Catastrophic shell pattern detected" in data["reason"] or "BTP-AST" in data["reason"]


def test_eval_secret_scrubbing(client):
    payload = {
        "bot_type": "muse",
        "tool": "api_fetch",
        "arguments": {
            "endpoint": "https://api.internal.com",
            "token": "sk-live-1234567890abcdef1234567890abcdef"
        }
    }
    response = client.post("/v1/eval", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["secret_scrubbed"] is True
    # Verify token is redacted in returned sanitized arguments
    assert "sk-live" not in data["sanitized_arguments"]["token"]
    assert "[REDACTED" in data["sanitized_arguments"]["token"]


def test_verify_receipt_validates_successfully(client):
    # First, generate a valid evaluation
    eval_resp = client.post("/v1/eval", json={
        "bot_type": "universal",
        "tool": "query",
        "arguments": {"query": "SELECT count(*) FROM orders;"}
    })
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    receipt = eval_data["receipt"]
    sanitized_args = eval_data["sanitized_arguments"]

    # Verify receipt against the verify endpoint
    verify_resp = client.post("/v1/verify", json={
        "attestation_receipt": receipt,
        "candidate_payload": sanitized_args,
        "trusted_root_pubkey": authority.public_key_hex
    })
    assert verify_resp.status_code == 200
    verify_data = verify_resp.json()
    assert verify_data["valid"] is True
