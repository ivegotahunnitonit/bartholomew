"""
Test Suite: Bartholomew Live Public Agent Gateway Server
========================================================
Tests:
  1. `GET /healthz` and vital status inspection.
  2. `GET /v1/trust-root` public key retrieval.
  3. `POST /v1/evaluate` for safe actions (ALLOW) and dangerous actions (DENY).
  4. `POST /v1/verify` independent offline attestation verification.
  5. `GET /metrics` Prometheus text formatting.
"""

import sys
import os
import json
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("."))
from src.gateway_server import app

client = TestClient(app)

def test_gateway_server_endpoints():
    print("=" * 80)
    print("TESTING BARTHOLOMEW LIVE PUBLIC AGENT GATEWAY (M2M NODE)")
    print("=" * 80 + "\n")

    # 1. Test Healthz
    r1 = client.get("/healthz")
    print(f"[TEST 1: Health & Node Vitals]")
    print(f"  * Status Code : {r1.status_code}")
    print(f"  * Protocol    : {r1.json()['protocol']}")
    print(f"  * Public Key  : {r1.json()['authority_public_key'][:32]}...")
    assert r1.status_code == 200
    assert r1.json()["status"] == "HEALTHY"

    # 2. Test Trust Root
    r2 = client.get("/v1/trust-root")
    print(f"\n[TEST 2: Trust Root Endpoint]")
    print(f"  * Policy ID   : {r2.json()['policy_id']}")
    print(f"  * Active Rules: {r2.json()['active_rules_count']}")
    assert r2.status_code == 200
    assert "authority_pubkey" in r2.json()

    # 3. Test Evaluate (Safe Payload)
    safe_payload = {"command": "git status", "amount_usd": 49.0}
    r3 = client.post("/v1/evaluate", json={
        "agent_id": "test_agent_01",
        "action_type": "EXECUTE_COMMAND",
        "payload": safe_payload
    })
    print(f"\n[TEST 3: Evaluate Safe Action (ALLOW)]")
    print(f"  * Verdict     : {r3.json()['verdict']}")
    print(f"  * Latency     : {r3.json()['total_latency_us']} µs")
    print(f"  * Ed25519 Sig : {r3.json()['receipt']['signature'][:32]}...")
    assert r3.status_code == 200
    assert r3.json()["verdict"] == "ALLOW"
    receipt = r3.json()["receipt"]

    # 4. Test Evaluate (Destructive SQL Payload - DENY)
    r4 = client.post("/v1/evaluate", json={
        "agent_id": "test_agent_01",
        "action_type": "EXECUTE_SQL",
        "payload": {"query": "DROP TABLE users;"}
    })
    print(f"\n[TEST 4: Evaluate Destructive Action (DENY)]")
    print(f"  * Verdict     : {r4.json()['verdict']}")
    print(f"  * Reason      : {r4.json()['reason']}")
    assert r4.status_code == 200
    assert r4.json()["verdict"] == "DENY"

    # 5. Test Independent Verify Endpoint
    r5 = client.post("/v1/verify", json={
        "attestation_receipt": receipt,
        "candidate_payload": safe_payload
    })
    print(f"\n[TEST 5: Independent Offline Verification]")
    print(f"  * Is Valid    : {r5.json()['is_valid']}")
    print(f"  * Message     : {r5.json()['verification_message']}")
    assert r5.status_code == 200
    assert r5.json()["is_valid"] is True

    # 6. Test Prometheus Metrics
    r6 = client.get("/metrics")
    print(f"\n[TEST 6: Prometheus Metrics Output]")
    print(f"  * Body Sample : {r6.text.strip().splitlines()[0]}")
    assert r6.status_code == 200
    assert "btp_evaluations_total" in r6.text

    print("\n" + "=" * 80)
    print("ALL GATEWAY SERVER ENDPOINTS PASSED 100% CLEAN!")
    print("=" * 80)

if __name__ == "__main__":
    test_gateway_server_endpoints()
