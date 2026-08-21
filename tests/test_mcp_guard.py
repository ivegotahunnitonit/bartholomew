"""
Unit tests for Bartholomew MCP (Model Context Protocol) Guard Server.
Verifies JSON-RPC 2.0 stdio handshake, tool listing, and runtime execution gating.
"""

import os
import json
import pytest
from mcp_server import BartholomewMCPServer


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
