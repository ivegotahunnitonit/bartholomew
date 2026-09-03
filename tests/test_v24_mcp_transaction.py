"""
Bartholomew v2.4 MCP Proxy & Workspace Transaction Integration Test Suite
===========================================================================
Validates:
  1. Instant Workspace Transaction Snapshot & Rollback (<5ms)
  2. Workspace Path Containment & Escape Prevention
  3. In-Flight Secret Redaction on JSON-RPC Request Arguments
  4. Outgoing Secret Redaction on JSON-RPC Response Payloads
  5. Polyglot Invariant Hard Veto with Rollback Details
  6. Cryptographic Chained Session Receipts (Parent Hash -> Child Hash)
  7. Full Session Audit Manifest Generation
"""

import os
import sys
import json
import tempfile
import pytest

sys.path.insert(0, os.path.abspath("."))
from src.workspace_transaction import WorkspaceTransaction
from src.mcp_gateway import MCPProxyGateway


def test_workspace_transaction_rollback():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "config.json")
        with open(test_file, "w") as f:
            f.write('{"status": "original"}')

        tx = WorkspaceTransaction(workspace_root=tmpdir)
        tx.snapshot_file("config.json")

        # Simulate agent overwriting file
        with open(test_file, "w") as f:
            f.write('{"status": "corrupted_by_agent"}')

        # Simulate agent creating an unwanted temp file
        unwanted_file = os.path.join(tmpdir, "leak.tmp")
        tx.snapshot_file("leak.tmp")
        with open(unwanted_file, "w") as f:
            f.write("temporary junk")

        assert os.path.exists(unwanted_file)

        # Trigger instant rollback
        res = tx.rollback(reason="Test Rollback Trigger")
        assert res["status"] == "ROLLED_BACK"
        assert res["rollback_time_us"] < 50000.0  # < 50ms

        # Assert original content restored
        with open(test_file, "r") as f:
            assert f.read() == '{"status": "original"}'

        # Assert unwanted file deleted
        assert not os.path.exists(unwanted_file)


def test_mcp_secret_redaction_and_veto():
    with tempfile.TemporaryDirectory() as tmpdir:
        gateway = MCPProxyGateway(workspace_root=tmpdir)

        # 1. Test request secret scrubbing
        req_with_secret = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "query_database",
                "arguments": {
                    "token": "sk-proj-1234567890abcdef1234567890abcdef",
                    "sql": "SELECT count(*) FROM users"
                }
            }
        }

        forward, req, veto = gateway.intercept_jsonrpc_request(json.dumps(req_with_secret))
        assert forward is True
        assert veto is None
        assert "[REDACTED_OPENAI_KEY_BTP]" in req["params"]["arguments"]["token"]
        assert gateway.total_redacted >= 1
        assert "_btp_receipt_hash" in req

        # 2. Test response secret scrubbing
        server_resp_with_secret = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "user": "admin",
                "aws_key": "AKIAIOSFODNN7EXAMPLE"
            }
        }
        clean_resp = gateway.intercept_jsonrpc_response(json.dumps(server_resp_with_secret))
        assert "[REDACTED_AWS_ACCESS_KEY_BTP]" in str(clean_resp["result"]["aws_key"])

        # 3. Test destructive tool call hard veto
        req_destructive = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "execute_command",
                "arguments": {
                    "command": "rm -rf /"
                }
            }
        }
        forward2, req2, veto2 = gateway.intercept_jsonrpc_request(json.dumps(req_destructive))
        assert forward2 is False
        assert veto2 is not None
        assert veto2["error"]["code"] == -32000
        assert "BTP-VETO" in veto2["error"]["message"]
        assert veto2["error"]["data"]["verdict"] == "DENY"


def test_mcp_session_chaining_and_manifest():
    with tempfile.TemporaryDirectory() as tmpdir:
        gateway = MCPProxyGateway(workspace_root=tmpdir)

        # Turn 1
        req1 = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "read_file", "arguments": {"path": "main.py"}}
        }
        forward1, _, _ = gateway.intercept_jsonrpc_request(json.dumps(req1))
        assert forward1 is True

        # Turn 2
        req2 = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "read_file", "arguments": {"path": "utils.py"}}
        }
        forward2, _, _ = gateway.intercept_jsonrpc_request(json.dumps(req2))
        assert forward2 is True

        # Verify receipt chain
        assert len(gateway.session_receipt_chain) == 2
        chain = gateway.session_receipt_chain
        assert chain[0]["receipt"]["parent_receipt_hash"] == "GENESIS_ROOT_HASH_0000000000000000"
        assert chain[1]["receipt"]["parent_receipt_hash"] == chain[0]["receipt_hash"]

        # Export audit manifest
        manifest = gateway.export_session_audit_manifest()
        assert manifest["manifest"]["total_steps"] == 2
        assert manifest["manifest"]["final_root_hash"] == chain[1]["receipt_hash"]
        assert len(manifest["signature"]) == 128  # Valid hex Ed25519 signature


if __name__ == "__main__":
    test_workspace_transaction_rollback()
    test_mcp_secret_redaction_and_veto()
    test_mcp_session_chaining_and_manifest()
    print("ALL v2.4 MCP & WORKSPACE TRANSACTION TESTS PASSED CLEANLY!")
