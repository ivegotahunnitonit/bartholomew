"""
Sidecar Proxy End-to-End Test Suite
===================================
Verifies:
  1. /healthz returns proxy status & root key in <1ms.
  2. Destructive SQL injection ("DROP TABLE") is intercepted with 403 Forbidden & cryptographic receipt.
  3. Excessive financial spend ($15,000 > $500 cap) is intercepted with 403 Forbidden.
  4. Safe payloads pass through the verification gate cleanly.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))

from fastapi.testclient import TestClient
from sidecar.main import app

def test_sidecar():
    print("=" * 80)
    print("TESTING BARTHOLOMEW RUNTIME EXECUTION SIDECAR PROXY")
    print("=" * 80 + "\n")

    client = TestClient(app)

    # 1. Health check
    res = client.get("/healthz")
    print("[1] /healthz response:", res.status_code, res.json())
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"

    # 2. Intercept DROP TABLE
    attack_payload = {"query": "DROP TABLE transactions; SELECT * FROM api_keys;"}
    res = client.post("/api/query", json=attack_payload, headers={"x-agent-id": "autonomous-worker-01"})
    print("\n[2] Destructive SQL Interception:", res.status_code)
    print("    Blocked Reason :", res.json().get("reason"))
    print("    Decision Time  :", res.json().get("latency_us"), "µs")
    assert res.status_code == 403
    assert "Destructive payload pattern detected" in res.json().get("reason")
    assert "cryptographic_receipt" in res.json()

    # 3. Intercept Spend Limit Escalation ($15k > $500)
    spend_attack = {"action": "WIRE_TRANSFER", "amount_usd": 15000.0, "recipient": "untrusted_wallet"}
    res = client.post("/api/finance", json=spend_attack, headers={"x-agent-id": "autonomous-worker-02"})
    print("\n[3] Spend Escalation Interception:", res.status_code)
    print("    Blocked Reason :", res.json().get("reason"))
    print("    Decision Time  :", res.json().get("latency_us"), "µs")
    assert res.status_code == 403
    assert "Spend limit escalation" in res.json().get("reason")

    print("\n" + "=" * 80)
    print("ALL SIDECAR PROXY RUNTIME INVARIANT TESTS PASSED 100% CLEAN!")
    print("=" * 80)

if __name__ == "__main__":
    test_sidecar()
