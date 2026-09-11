"""
Test Suite for BTP v5.4 Autonomous M2M Wire Daemon & Utility Barter Clearinghouse.
Validates machine discovery, sub-35us AST verification, secret scrubbing, and mutual barter.
"""

import sys
import os
import time
import json
import urllib.request
import urllib.error

workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from src.daemon.m2m_wire_daemon import M2MWireDaemon, GLOBAL_M2M_LEDGER


def run_m2m_wire_daemon_suite():
    port = 18443
    daemon = M2MWireDaemon(host="127.0.0.1", port=port)
    daemon.start(blocking=False)
    time.sleep(0.5)  # Allow socket to bind

    base_url = f"http://127.0.0.1:{port}"
    print(f"[*] Testing M2M Wire Daemon on {base_url}...")

    try:
        # 1. Test Healthz
        req = urllib.request.Request(f"{base_url}/healthz")
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode())
            assert data["status"] == "HEALTHY"
            print("  [+] GET /healthz: PASS")

        # 2. Test Autonomous Discovery (.well-known)
        req = urllib.request.Request(f"{base_url}/.well-known/agent-protocol.json")
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            discovery = json.loads(resp.read().decode())
            assert discovery["protocol"] == "BTP/5.4"
            assert discovery["agent_id"] == "bartholomew-sentinel-core"
            assert "ast_gate:audit" in discovery["capabilities"]
            assert discovery["barter_unit"] == "AWU (Attested Work Unit)"
            assert discovery["latency_sla_us"] == 35.0
            print("  [+] GET /.well-known/agent-protocol.json: PASS")

        # 3. Test Safe Tool Verification via M2M wire
        safe_payload = {
            "agent_id": "agent-analytics-01",
            "tool_name": "database_reader",
            "arguments": {
                "query": "SELECT id, email, created_at FROM accounts WHERE active = 1 LIMIT 25;",
                "api_key": "sk-live-secret-entropy-test-12345"
            }
        }
        req = urllib.request.Request(
            f"{base_url}/v1/m2m/verify",
            data=json.dumps(safe_payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "X-Agent-ID": "agent-analytics-01"}
        )
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            res = json.loads(resp.read().decode())
            assert res["status"] == "APPROVED"
            assert res["tool_name"] == "database_reader"
            assert res["proof_id"].startswith("zktcp_")
            assert "fiat_shamir_response" in res
            # Secret must be masked in sanitized arguments
            assert "sk-live" not in res["sanitized_arguments"]["api_key"]
            assert "[REDACTED_" in res["sanitized_arguments"]["api_key"]
            print(f"  [+] POST /v1/m2m/verify (Safe Query + Secret Masking): PASS ({res['latency_us']}us)")

        # 4. Test Malicious Tool Verification (VETO)
        malicious_payload = {
            "agent_id": "rogue-worker-99",
            "tool_name": "database_writer",
            "arguments": {
                "statement": "DROP TABLE accounts CASCADE;"
            }
        }
        req = urllib.request.Request(
            f"{base_url}/v1/m2m/verify",
            data=json.dumps(malicious_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            res = json.loads(resp.read().decode())
            assert res["status"] == "VETOED"
            assert "table" in res["violation"].lower()
            assert "Bartholomew's Counsel" in res["counsel"]
            print(f"  [+] POST /v1/m2m/verify (Malicious AST Veto): PASS ({res['latency_us']}us)")

        # 5. Test Mutual Barter Exchange
        barter_payload = {
            "agent_id": "agent-analytics-01",
            "task_type": "inference_chunk",
            "work_units": 3.5
        }
        req = urllib.request.Request(
            f"{base_url}/v1/m2m/barter",
            data=json.dumps(barter_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            res = json.loads(resp.read().decode())
            assert res["status"] == "BARTER_SETTLED"
            assert res["work_units_credited"] == 3.5
            print("  [+] POST /v1/m2m/barter: PASS")

        # 6. Test Ledger Merkle Root
        req = urllib.request.Request(f"{base_url}/v1/m2m/ledger")
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            ledger = json.loads(resp.read().decode())
            assert ledger["verified_calls_count"] >= 1
            assert ledger["vetoed_calls_count"] >= 1
            assert ledger["total_surplus_awu"] >= 4.5
            assert ledger["merkle_root"].startswith("0x")
            assert len(ledger["merkle_root"]) == 66
            print(f"  [+] GET /v1/m2m/ledger: PASS (Merkle: {ledger['merkle_root'][:18]}...)")

        print("[+] All M2M Wire Daemon integration tests passed successfully!")

    finally:
        daemon.stop()
        print("[*] M2M Wire Daemon stopped.")


if __name__ == "__main__":
    run_m2m_wire_daemon_suite()
