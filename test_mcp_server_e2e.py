"""
MCP Server End-to-End JSON-RPC Protocol Test
============================================
Tests the Bartholomew Model Context Protocol (MCP) server:
  - initialize
  - tools/list
  - tools/call (btp_evaluate_action)
  - tools/call (btp_verify_attestation)
  - tools/call (btp_get_trust_roots)
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))
from mcp_server.server import BartholomewMCPServer

def test_mcp_protocol():
    print("=" * 80)
    print("TESTING BARTHOLOMEW MCP (MODEL CONTEXT PROTOCOL) SERVER")
    print("=" * 80)

    server = BartholomewMCPServer()

    # 1. Initialize
    init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    init_resp = server.handle_request(init_req)
    print("[1] initialize response:", init_resp["result"]["serverInfo"])
    assert init_resp["result"]["serverInfo"]["name"] == "mcp-server-bartholomew"

    # 2. List tools
    list_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    list_resp = server.handle_request(list_req)
    tool_names = [t["name"] for t in list_resp["result"]["tools"]]
    print("[2] tools/list tools found:", tool_names)
    assert "btp_evaluate_action" in tool_names
    assert "btp_verify_attestation" in tool_names
    assert "btp_get_trust_roots" in tool_names

    # 3. Call btp_evaluate_action
    eval_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "btp_evaluate_action",
            "arguments": {
                "agent_id": "claude-desktop-agent-01",
                "action_type": "DATABASE_MUTATION",
                "payload": {"query": "UPDATE accounts SET verified=true WHERE id=123", "max_cost": 5.0},
                "target_recipient": "postgres-prod-enclave",
                "capability_scope": ["db.write", "posix.read"]
            }
        }
    }
    eval_resp = server.handle_request(eval_req)
    receipt_text = eval_resp["result"]["content"][0]["text"]
    receipt_json = json.loads(receipt_text)
    attestation = receipt_json.get("attestation", {})
    print("[3] btp_evaluate_action verdict:", attestation.get("verdict"), "| Action:", attestation.get("action_type"))
    assert "signature" in receipt_json
    assert attestation.get("verdict") == "ALLOW"

    # 4. Call btp_verify_attestation
    verify_req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "btp_verify_attestation",
            "arguments": {
                "receipt": receipt_json,
                "candidate_payload": {"query": "UPDATE accounts SET verified=true WHERE id=123", "max_cost": 5.0},
                "expected_recipient": "postgres-prod-enclave"
            }
        }
    }
    verify_resp = server.handle_request(verify_req)
    verify_result = json.loads(verify_resp["result"]["content"][0]["text"])
    print("[4] btp_verify_attestation status:", verify_result["valid"], "| Message:", verify_result["message"])
    assert verify_result["valid"] is True

    # 5. Call btp_get_trust_roots
    roots_req = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "btp_get_trust_roots",
            "arguments": {}
        }
    }
    roots_resp = server.handle_request(roots_req)
    roots_result = json.loads(roots_resp["result"]["content"][0]["text"])
    print("[5] btp_get_trust_roots active roots:", len(roots_result["active_roots"]))
    assert len(roots_result["registered_invariants"]) >= 2

    print("\n" + "=" * 80)
    print("ALL 5 MCP JSON-RPC 2.0 PROTOCOL TESTS PASSED 100% CLEAN!")
    print("=" * 80)

if __name__ == "__main__":
    test_mcp_protocol()
