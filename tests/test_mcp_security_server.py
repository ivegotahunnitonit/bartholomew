"""
Test Suite for Bartholomew MCP Security Server (JSON-RPC Protocol)
"""

import sys
import os
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp_server.server import BartholomewMCPServer

def test_mcp_server_protocol():
    print("=" * 80)
    print("  TESTING BARTHOLOMEW MODEL CONTEXT PROTOCOL (MCP) SERVER")
    print("=" * 80)

    server = BartholomewMCPServer()

    # 1. Test Initialize
    init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    init_resp = server.handle_request(init_req)
    assert init_resp["result"]["serverInfo"]["name"] == "mcp-server-bartholomew"
    print("[1] MCP Initialize Handshake: SUCCESS")

    # 2. Test Tools List
    tools_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    tools_resp = server.handle_request(tools_req)
    tool_names = [t["name"] for t in tools_resp["result"]["tools"]]
    print(f"[2] MCP Tools Registered: {tool_names}")
    assert "btp_evaluate_action" in tool_names
    assert "btp_verify_attestation" in tool_names

    # 3. Test Evaluate Action Tool Call
    eval_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "btp_evaluate_action",
            "arguments": {
                "agent_id": "Claude-Desktop-01",
                "action_type": "EXEC_SQL",
                "payload": {"query": "SELECT * FROM users;"},
                "target_recipient": "Postgres-Worker-01"
            }
        }
    }
    eval_resp = server.handle_request(eval_req)
    receipt_text = eval_resp["result"]["content"][0]["text"]
    receipt = json.loads(receipt_text)
    assert receipt["attestation"]["verdict"] == "ALLOW"
    print(f"[3] Tool Call 'btp_evaluate_action': SUCCESS (Verdict: {receipt['attestation']['verdict']})")

    # 4. Test Verify Attestation Tool Call
    verify_req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "btp_verify_attestation",
            "arguments": {
                "receipt": receipt,
                "candidate_payload": {"query": "SELECT * FROM users;"},
                "expected_recipient": "Postgres-Worker-01"
            }
        }
    }
    verify_resp = server.handle_request(verify_req)
    verify_result = json.loads(verify_resp["result"]["content"][0]["text"])
    assert verify_result["valid"] is True
    print(f"[4] Tool Call 'btp_verify_attestation': SUCCESS (Valid: {verify_result['valid']})")

    print("\n" + "=" * 80)
    print("  MCP SERVER TEST SUITE: 100% PASSING")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = test_mcp_server_protocol()
    sys.exit(0 if success else 1)
