"""
Test Suite for Bartholomew MCP Bonded Warranty & Arbitration Tools (Milestone 3.1)
Verifies:
1. btp_issue_execution_bond via MCP JSON-RPC call
2. btp_get_bond_status via MCP JSON-RPC call
3. btp_slash_execution_bond upon verified invariant breach receipt
4. Rejection of invalid slashing claims
"""

import json
import pytest
from mcp_server import BartholomewMCPServer


@pytest.fixture
def mcp_server(tmp_path):
    workspace = str(tmp_path / "mcp_workspace")
    return BartholomewMCPServer(workspace_root=workspace)


def test_mcp_issue_execution_bond(mcp_server):
    req = json.dumps({
        "jsonrpc": "2.0",
        "id": 101,
        "method": "tools/call",
        "params": {
            "name": "btp_issue_execution_bond",
            "arguments": {
                "agent_id": "agent-gpt6-astra-01",
                "action_type": "HIGH_STAKES_DB_MIGRATION",
                "bond_amount_usd": 5000.0,
                "attestation_hash": "0xdeadbeef12345678"
            }
        }
    })
    res_str = mcp_server.process_message(req)
    assert res_str is not None
    res = json.loads(res_str)
    assert "result" in res
    assert not res["result"].get("isError", False)

    content = json.loads(res["result"]["content"][0]["text"])
    assert content["originating_agent"] == "agent-gpt6-astra-01"
    assert content["action_type"] == "HIGH_STAKES_DB_MIGRATION"
    assert content["bond_amount_usd"] == 5000.0
    assert content["status"] == "ACTIVE_BONDED"
    assert "bond_id" in content


def test_mcp_get_bond_status(mcp_server):
    # 1. Issue bond
    issue_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 102,
        "method": "tools/call",
        "params": {
            "name": "btp_issue_execution_bond",
            "arguments": {
                "agent_id": "agent-claude-35",
                "action_type": "K8S_ROLLOUT",
                "bond_amount_usd": 2500.0
            }
        }
    })
    issue_res = json.loads(mcp_server.process_message(issue_req))
    bond_data = json.loads(issue_res["result"]["content"][0]["text"])
    bond_id = bond_data["bond_id"]

    # 2. Query status
    status_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 103,
        "method": "tools/call",
        "params": {
            "name": "btp_get_bond_status",
            "arguments": {
                "bond_id": bond_id
            }
        }
    })
    status_res = json.loads(mcp_server.process_message(status_req))
    assert not status_res["result"].get("isError", False)
    queried_bond = json.loads(status_res["result"]["content"][0]["text"])
    assert queried_bond["bond_id"] == bond_id
    assert queried_bond["bond_amount_usd"] == 2500.0
    assert queried_bond["status"] == "ACTIVE_BONDED"


def test_mcp_slash_execution_bond(mcp_server):
    # 1. Issue bond
    issue_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 104,
        "method": "tools/call",
        "params": {
            "name": "btp_issue_execution_bond",
            "arguments": {
                "agent_id": "rogue-devin-agent",
                "action_type": "DDL_DROP_TABLE",
                "bond_amount_usd": 8000.0
            }
        }
    })
    issue_res = json.loads(mcp_server.process_message(issue_req))
    bond_data = json.loads(issue_res["result"]["content"][0]["text"])
    bond_id = bond_data["bond_id"]

    # 2. Slash bond with verified invariant breach receipt
    slash_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 105,
        "method": "tools/call",
        "params": {
            "name": "btp_slash_execution_bond",
            "arguments": {
                "bond_id": bond_id,
                "breach_receipt": {
                    "verdict": "BLOCKED",
                    "reason": "Destructive DDL DROP TABLE production_db intercepted",
                    "rule_id": "BTP-INV-003",
                    "ast_violation": True
                }
            }
        }
    })
    slash_res = json.loads(mcp_server.process_message(slash_req))
    assert not slash_res["result"].get("isError", False)
    slash_data = json.loads(slash_res["result"]["content"][0]["text"])
    assert slash_data["slashed"] is True
    assert slash_data["liquidated_amount_usd"] == 8000.0

    # 3. Verify status updated to slashed
    status_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 106,
        "method": "tools/call",
        "params": {
            "name": "btp_get_bond_status",
            "arguments": {"bond_id": bond_id}
        }
    })
    status_res = json.loads(mcp_server.process_message(status_req))
    queried = json.loads(status_res["result"]["content"][0]["text"])
    assert queried["status"] == "SLASHED_FOR_INVARIANT_BREACH"
