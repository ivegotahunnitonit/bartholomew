import pytest
import time
import json
import threading
import urllib.request
from daemon.approval_queue import ApprovalQueue
from daemon.daemon_server import BartholomewDaemon


def test_approval_queue():
    queue = ApprovalQueue()
    approval = queue.submit_for_approval(
        agent_id="test-agent",
        action_type="WIRE_TRANSFER",
        payload={"amount_usd": 1500.00},
        reason="Spend cap exceeded",
        timeout_seconds=5.0
    )
    assert approval.status == "PENDING"
    assert len(queue.list_active()) == 1

    # Decide approve
    decided = queue.decide(approval.request_id, approve=True, operator_name="Admin")
    assert decided.status == "APPROVED"
    assert decided.decided_by == "Admin"
    assert len(queue.list_active()) == 0


def test_daemon_evaluate_endpoints():
    # Spin up daemon on test port 8999
    daemon = BartholomewDaemon(host="127.0.0.1", port=8999, policy_file="policies/default_security_policy.yaml")
    server = daemon.start_server()
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.1)

    try:
        # 1. Test status endpoint
        req = urllib.request.Request("http://127.0.0.1:8999/v1/status")
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            status_data = json.loads(resp.read().decode())
            assert status_data["status"] == "ACTIVE"
            assert "public_key" in status_data

        # 2. Test evaluate blocked intent (SQL DROP)
        eval_payload = {
            "agent_id": "claude-subagent-01",
            "action_type": "EXECUTE_TOOL",
            "payload": {"code": "DROP TABLE accounts;"}
        }
        req = urllib.request.Request(
            "http://127.0.0.1:8999/v1/evaluate",
            data=json.dumps(eval_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            eval_res = json.loads(resp.read().decode())
            assert eval_res["allowed"] is False
            assert eval_res["latency_us"] > 0
            assert "signature" in eval_res

        # 3. Test evaluate allowed intent
        eval_clean = {
            "agent_id": "cursor-worker",
            "action_type": "EXECUTE_TOOL",
            "payload": {"command": "git status"}
        }
        req = urllib.request.Request(
            "http://127.0.0.1:8999/v1/evaluate",
            data=json.dumps(eval_clean).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            eval_clean_res = json.loads(resp.read().decode())
            assert eval_clean_res["allowed"] is True

        # 4. Test evaluate high-stakes spend requiring human co-signing
        eval_high_stakes = {
            "agent_id": "finance-bot",
            "action_type": "TRANSFER",
            "payload": {"amount_usd": 2500.00}
        }
        req = urllib.request.Request(
            "http://127.0.0.1:8999/v1/evaluate",
            data=json.dumps(eval_high_stakes).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            res_high = json.loads(resp.read().decode())
            assert res_high["verdict"] == "PENDING_APPROVAL"
            req_id = res_high["request_id"]

        # 5. List approvals
        req = urllib.request.Request("http://127.0.0.1:8999/v1/approvals")
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            approvals_data = json.loads(resp.read().decode())
            assert len(approvals_data["approvals"]) == 1

        # 6. Approve from desktop operator portal
        req = urllib.request.Request(
            f"http://127.0.0.1:8999/v1/approvals/{req_id}/decide",
            data=json.dumps({"approve": True, "operator": "Test Operator"}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            decide_res = json.loads(resp.read().decode())
            assert decide_res["status"] == "APPROVED"
    finally:
        server.shutdown()
        server.server_close()
