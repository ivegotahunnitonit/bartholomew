"""
Unit tests for Bartholomew MCP (Model Context Protocol) Guard Server.
Verifies JSON-RPC 2.0 stdio handshake, tool listing, and runtime execution gating.
"""

import os
import json
import pytest
from src.mcp_server import BartholomewMCPServer


@pytest.fixture
def mcp_server(tmp_path):
    workspace = str(tmp_path / "mcp_workspace")
    os.makedirs(workspace, exist_ok=True)
    return BartholomewMCPServer(workspace_root=workspace)


def test_mcp_initialize(mcp_server):
    init_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "Claude-Desktop", "version": "1.0"}
        }
    })
    res_str = mcp_server.process_message(init_req)
    assert res_str is not None
    res = json.loads(res_str)
    assert res["id"] == 1
    assert res["result"]["serverInfo"]["name"] == "bartholomew-guard"
    assert res["result"]["protocolVersion"] == "2024-11-05"


def test_mcp_tools_list(mcp_server):
    list_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    })
    res_str = mcp_server.process_message(list_req)
    assert res_str is not None
    res = json.loads(res_str)
    tools = res["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "btp_execute_command" in tool_names
    assert "btp_write_file" in tool_names
    assert "btp_read_file" in tool_names
    assert "btp_evaluate_intent" in tool_names
    assert "btp_get_security_status" in tool_names


def test_mcp_btp_get_manifest(mcp_server):
    manifest_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 99,
        "method": "tools/call",
        "params": {
            "name": "btp_get_manifest",
            "arguments": {}
        }
    })
    res_str = mcp_server.process_message(manifest_req)
    assert res_str is not None
    res = json.loads(res_str)
    assert res["id"] == 99
    content_text = res["result"]["content"][0]["text"]
    assert "Bartholomew Trust Protocol" in content_text
    assert "autonomous_action_allowed" in content_text


def test_mcp_execute_command_allowed(mcp_server):
    exec_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "btp_execute_command",
            "arguments": {
                "command": "python -c \"print('BTP_MCP_OK')\""
            }
        }
    })
    res_str = mcp_server.process_message(exec_req)
    res = json.loads(res_str)
    assert res["result"]["isError"] is False
    content_text = res["result"]["content"][0]["text"]
    assert "BTP_MCP_OK" in content_text
    assert "BTP SEAL: VERIFIED & EXECUTED" in content_text


def test_mcp_execute_command_blocked(mcp_server):
    exec_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "btp_execute_command",
            "arguments": {
                "command": "rm -rf /"
            }
        }
    })
    res_str = mcp_server.process_message(exec_req)
    res = json.loads(res_str)
    assert res["result"]["isError"] is True
    content_text = res["result"]["content"][0]["text"]
    assert "BARTHOLOMEW INTERCEPTION: BLOCKED" in content_text


def test_mcp_file_write_and_read(mcp_server):
    # 1. Write file inside workspace
    write_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "btp_write_file",
            "arguments": {
                "path": "app/config.json",
                "content": "{\"status\":\"ok\"}"
            }
        }
    })
    write_res = json.loads(mcp_server.process_message(write_req))
    assert write_res["result"]["isError"] is False
    assert "BTP ATTESTATION SEALED" in write_res["result"]["content"][0]["text"]

    # 2. Read file back
    read_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "btp_read_file",
            "arguments": {
                "path": "app/config.json"
            }
        }
    })
    read_res = json.loads(mcp_server.process_message(read_req))
    assert read_res["result"]["isError"] is False
    assert "{\"status\":\"ok\"}" in read_res["result"]["content"][0]["text"]


def test_mcp_path_traversal_blocked(mcp_server):
    # Try reading outside workspace
    read_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "btp_read_file",
            "arguments": {
                "path": "../../../Windows/System32/config/SAM"
            }
        }
    })
    read_res = json.loads(mcp_server.process_message(read_req))
    assert read_res["result"]["isError"] is True
    assert "BARTHOLOMEW INTERCEPTION" in read_res["result"]["content"][0]["text"]


def test_mcp_request_threshold_signature(mcp_server):
    req = json.dumps({
        "jsonrpc": "2.0",
        "id": 8,
        "method": "tools/call",
        "params": {
            "name": "btp_request_threshold_signature",
            "arguments": {
                "action_intent": "Execute database migration v2.8"
            }
        }
    })
    res = json.loads(mcp_server.process_message(req))
    assert res["result"]["isError"] is False
    data = json.loads(res["result"]["content"][0]["text"])
    assert data["status"] == "ATTESTED_AND_CO_SIGNED"
    assert data["quorum"] == "2-of-3 Swarm Consensus"
    assert "signature" in data


def test_mcp_verify_safety_proof(mcp_server):
    from src.zk_compliance_proof_engine import ZKComplianceEngine
    engine = ZKComplianceEngine()
    proof = engine.prove_session("mcp-test-session", ["read_config()", "verify_sandbox()"])
    receipt = proof.to_receipt()

    req = json.dumps({
        "jsonrpc": "2.0",
        "id": 9,
        "method": "tools/call",
        "params": {
            "name": "btp_verify_safety_proof",
            "arguments": {
                "receipt": receipt
            }
        }
    })
    res = json.loads(mcp_server.process_message(req))
    assert res["result"]["isError"] is False
    data = json.loads(res["result"]["content"][0]["text"])
    assert data["verified"] is True
    assert data["plaintext_leaked_bytes"] == 0
    assert data["status"] == "PASS (COMPLIANCE VERIFIED)"


def test_mcp_get_security_status(mcp_server):
    req = json.dumps({
        "jsonrpc": "2.0",
        "id": 10,
        "method": "tools/call",
        "params": {
            "name": "btp_get_security_status",
            "arguments": {}
        }
    })
    res = json.loads(mcp_server.process_message(req))
    assert res["result"]["isError"] is False
    data = json.loads(res["result"]["content"][0]["text"])
    assert data["status"] == "ACTIVE"
    assert data["protocol"] == "BTP v2.8.0"
    assert "RFC 9591" in data["threshold_quorum"]



def test_mcp_keystone_passkey_lifecycle(mcp_server):
    # 1. Issue passkey
    issue_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 11,
        "method": "tools/call",
        "params": {
            "name": "btp_issue_keystone_passkey",
            "arguments": {
                "agent_id": "test-agent-mcp-01",
                "ttl_minutes": 120
            }
        }
    })
    res = json.loads(mcp_server.process_message(issue_req))
    assert res["result"]["isError"] is False
    passkey = json.loads(res["result"]["content"][0]["text"])
    assert passkey["agent_id"] == "test-agent-mcp-01"
    assert passkey["passkey_id"].startswith("key_")
    assert len(passkey["signature"]) == 64

    # 2. Verify safe action (in-scope file read)
    verify_req_safe = json.dumps({
        "jsonrpc": "2.0",
        "id": 12,
        "method": "tools/call",
        "params": {
            "name": "btp_verify_keystone_clearance",
            "arguments": {
                "passkey": passkey,
                "action_type": "FILE_READ",
                "target": "src/main.py"
            }
        }
    })
    res_safe = json.loads(mcp_server.process_message(verify_req_safe))
    assert res_safe["result"]["isError"] is False
    verdict_safe = json.loads(res_safe["result"]["content"][0]["text"])
    assert verdict_safe["verdict"] == "ALLOW"
    assert verdict_safe["status"] == "CLEARANCE_GRANTED"

    # 3. Intercept unsafe action (forbidden secret read)
    verify_req_unsafe = json.dumps({
        "jsonrpc": "2.0",
        "id": 13,
        "method": "tools/call",
        "params": {
            "name": "btp_verify_keystone_clearance",
            "arguments": {
                "passkey": passkey,
                "action_type": "FILE_READ",
                "target": ".env"
            }
        }
    })
    res_unsafe = json.loads(mcp_server.process_message(verify_req_unsafe))
    assert res_unsafe["result"]["isError"] is True
    verdict_unsafe = json.loads(res_unsafe["result"]["content"][0]["text"])
    assert verdict_unsafe["verdict"] == "DENY"

    # 4. Revoke passkey
    revoke_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 14,
        "method": "tools/call",
        "params": {
            "name": "btp_revoke_keystone_passkey",
            "arguments": {
                "passkey_id": passkey["passkey_id"]
            }
        }
    })
    res_revoke = json.loads(mcp_server.process_message(revoke_req))
    assert res_revoke["result"]["isError"] is False
    revoke_data = json.loads(res_revoke["result"]["content"][0]["text"])
    assert revoke_data["revoked"] is True

    # 5. Verify revoked passkey is immediately denied
    verify_req_revoked = json.dumps({
        "jsonrpc": "2.0",
        "id": 15,
        "method": "tools/call",
        "params": {
            "name": "btp_verify_keystone_clearance",
            "arguments": {
                "passkey": passkey,
                "action_type": "FILE_READ",
                "target": "src/main.py"
            }
        }
    })
    res_revoked = json.loads(mcp_server.process_message(verify_req_revoked))
    assert res_revoked["result"]["isError"] is True
    revoked_verdict = json.loads(res_revoked["result"]["content"][0]["text"])
    assert revoked_verdict["status"] == "PASSKEY_REVOKED"
