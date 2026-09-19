import pytest
from fastapi.testclient import TestClient
from src.gateway_server import app

client = TestClient(app)

def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "grok" in data["supported_bots"]
    assert "muse" in data["supported_bots"]
    assert "meta_ai" in data["supported_bots"]

def test_manifest_discovery():
    response = client.get("/.well-known/btp.json")
    assert response.status_code == 200
    manifest = response.json()
    assert "identity" in manifest
    assert manifest["identity"]["name"] == "Bartholomew Trust Protocol"

def test_ai_plugin_manifest():
    response = client.get("/.well-known/ai-plugin.json")
    assert response.status_code == 200
    data = response.json()
    assert data["name_for_model"] == "bartholomew_guard"

def test_grok_bot_destructive_command_blocked():
    payload = {
        "bot_type": "grok",
        "action": "execute_command",
        "tool": "bash",
        "arguments": {"command": "rm -rf /var/data"},
        "agent_id": "grok-bot-test"
    }
    response = client.post("/v1/eval", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["allowed"] is False
    assert res["verdict"] == "DENY"
    assert "Catastrophic shell pattern" in res["reason"]
    assert res["latency_us"] < 25000  # Sub-25ms even under cold-start overhead

def test_muse_sql_mutation_blocked():
    payload = {
        "bot_type": "muse",
        "action": "run_sql",
        "tool": "database",
        "arguments": {"query": "DROP TABLE users;"},
        "agent_id": "muse-workflow-01"
    }
    response = client.post("/v1/eval", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["allowed"] is False
    assert res["verdict"] == "DENY"

def test_meta_ai_safe_action_allowed_with_attestation():
    payload = {
        "bot_type": "meta_ai",
        "action": "search_docs",
        "tool": "search",
        "arguments": {"query": "Bartholomew architecture"},
        "agent_id": "meta-llama-agent"
    }
    response = client.post("/v1/eval", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["allowed"] is True
    assert res["verdict"] == "ALLOW"
    assert "receipt" in res
    assert "signature" in res["receipt"]

def test_secret_leak_auto_scrubbed():
    payload = {
        "bot_type": "grok",
        "action": "api_call",
        "arguments": {"api_key": "sk-proj-1234567890123456789012345678901234567890", "url": "https://api.example.com"},
        "agent_id": "grok-bot"
    }
    response = client.post("/v1/eval", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["secret_scrubbed"] is True
    assert "sk-proj-" not in res["sanitized_arguments"]["api_key"]

def test_webhook_receiver():
    payload = {
        "event": "tool_execution",
        "bot": "muse",
        "tool": "bash",
        "payload": {"command": "echo safe"},
        "agent_id": "muse-worker"
    }
    response = client.post("/v1/webhooks/bot", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["allowed"] is True
