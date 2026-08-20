"""
Bartholomew BTP v2.2 Official Model Context Protocol (MCP) Security Server
Enables Claude Desktop, Cursor, and any MCP client to evaluate, sign, 
and verify autonomous agent tool executions using pure RFC 8785 + Ed25519.
"""

import sys
import os
import json
import time
import hashlib
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.trust_protocol import BartholomewTrustAuthority
from standalone_btp_verifier import independent_verify_btp_receipt
from src.rfc8785 import rfc8785_canonicalize

class BartholomewMCPServer:
    """
    Standard JSON-RPC 2.0 stdio Model Context Protocol (MCP) Server.
    Provides cryptographic trust gating for Claude & LLM tool invocations.
    """
    def __init__(self, authority_instance: Optional[BartholomewTrustAuthority] = None):
        self.authority = authority_instance or BartholomewTrustAuthority(ttl_seconds=300)
        self.seen_nonces = set()

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Returns MCP tool definitions for Claude Desktop & Cursor."""
        return [
            {
                "name": "btp_evaluate_action",
                "description": "Evaluates an autonomous agent action in a pre-flight sandbox and returns an RFC 8785 Ed25519 cryptographic attestation receipt.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string", "description": "Originating agent identifier"},
                        "action_type": {"type": "string", "description": "Type of action (e.g., DEPLOY_PATCH, SQL_EXEC, BASH_CMD)"},
                        "payload": {"type": "object", "description": "Payload dictionary to evaluate and hash"},
                        "target_recipient": {"type": "string", "description": "Intended recipient execution context"},
                        "capability_scope": {"type": "array", "items": {"type": "string"}, "description": "Required capability permissions"}
                    },
                    "required": ["agent_id", "action_type", "payload"]
                }
            },
            {
                "name": "btp_verify_attestation",
                "description": "Verifies an incoming BTP action receipt 100% offline without cloud roundtrips.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "receipt": {"type": "object", "description": "The BTP attestation envelope to verify"},
                        "candidate_payload": {"type": "object", "description": "The candidate payload to match against attestation hash"},
                        "expected_recipient": {"type": "string", "description": "Expected target recipient identifier"},
                        "allowed_capabilities": {"type": "array", "items": {"type": "string"}, "description": "Allowed capabilities"}
                    },
                    "required": ["receipt", "candidate_payload"]
                }
            },
            {
                "name": "btp_get_trust_roots",
                "description": "Returns active recognized root public keys and registered security invariants.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    def handle_request(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """Handles MCP JSON-RPC requests."""
        method = req.get("method")
        params = req.get("params", {})
        req_id = req.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "mcp-server-bartholomew",
                        "version": "2.2.0"
                    }
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.get_tool_definitions()}
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})

            if tool_name == "btp_evaluate_action":
                receipt = self.authority.evaluate_intent(
                    agent_id=args.get("agent_id", "Claude-Agent"),
                    action_type=args.get("action_type", "TOOL_CALL"),
                    payload=args.get("payload", {}),
                    target_recipient=args.get("target_recipient", "Claude-Local-Worker"),
                    capability_scope=args.get("capability_scope")
                )
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(receipt, indent=2)}]
                    }
                }

            elif tool_name == "btp_verify_attestation":
                ok, msg = independent_verify_btp_receipt(
                    receipt_json_str=args.get("receipt", {}),
                    candidate_payload=args.get("candidate_payload", {}),
                    trusted_root_pubkeys=[self.authority.public_key_hex],
                    expected_recipient_context=args.get("expected_recipient"),
                    allowed_capabilities=args.get("allowed_capabilities"),
                    seen_nonces=self.seen_nonces
                )
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps({"valid": ok, "message": msg}, indent=2)}]
                    }
                }

            elif tool_name == "btp_get_trust_roots":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": json.dumps({
                                "protocol_version": "BTP/2.2",
                                "active_roots": [self.authority.public_key_hex],
                                "registered_invariants": [
                                    "BTP-SEC-001: Payload Tamper-Resistance",
                                    "BTP-SEC-002: Cross-Recipient Context Isolation",
                                    "BTP-SEC-003: Timestamp Validity Window",
                                    "BTP-SEC-004: Multi-Authority Root Pinning",
                                    "BTP-SEC-005: Capability Scope Containment",
                                    "BTP-SEC-006: Policy Provenance",
                                    "BTP-SEC-007: Replay Immunity",
                                    "BTP-SEC-008: 100% Offline Verifiability"
                                ]
                            }, indent=2)
                        }]
                    }
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
                }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method '{method}' not supported"}
        }

    def run_stdio(self):
        """Runs the MCP server over standard input/output (stdio)."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                resp = self.handle_request(req)
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error / Internal error: {str(e)}"}
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()

if __name__ == "__main__":
    server = BartholomewMCPServer()
    server.run_stdio()
