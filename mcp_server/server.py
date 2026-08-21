"""
Bartholomew BTP v2.2 Official Model Context Protocol (MCP) Security Server
==========================================================================
Enforces mandatory in-line cryptographic gating for Claude Desktop tool calls:
  1. All write/command execution tools are registered behind MandatoryToolGate.
  2. Tools literally cannot execute if AST inspection or BTP attestation fails.
  3. Returns RFC 8785 Ed25519 tamper-proof receipts for every action.
"""

import sys
import os
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Callable

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.trust_protocol import BartholomewTrustAuthority
from standalone_btp_verifier import independent_verify_btp_receipt
from src.rfc8785 import rfc8785_canonicalize
from src.ast_validator import ASTSecurityValidator
from mcp_server.inline_tool_gate import MandatoryToolGate

class BartholomewMCPServer:
    """
    Standard JSON-RPC 2.0 stdio Model Context Protocol (MCP) Server.
    Provides mandatory in-line execution gating for Claude Desktop & Cursor.
    """
    def __init__(self, authority_instance: Optional[BartholomewTrustAuthority] = None):
        self.authority = authority_instance or BartholomewTrustAuthority(ttl_seconds=300)
        self.seen_nonces = set()
        self.gate = MandatoryToolGate(self.authority)
        self._register_default_underlying_tools()

    def _register_default_underlying_tools(self):
        """Registers actual system actions behind the mandatory gate."""
        def _safe_write_file(path: str, code: str) -> str:
            # Physical disk write only reachable when gate allows
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
            return f"File '{path}' written successfully ({len(code)} bytes)."

        def _safe_run_command(command: str) -> str:
            # Physical subprocess execution reachable ONLY when gate allows
            import subprocess
            res = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            output = res.stdout if res.returncode == 0 else f"Command error ({res.returncode}): {res.stderr}"
            return output.strip() or "[Command executed successfully with no output]"

        self.gate.register_tool("write_file", _safe_write_file)
        self.gate.register_tool("run_command", _safe_run_command)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Returns MCP tool definitions for Claude Desktop."""
        return [
            {
                "name": "execute_gated_file_write",
                "description": "Writes code to a file behind mandatory in-line AST security inspection and Ed25519 signing. Blocks eval, subprocess, and destructive calls before writing.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Target file path"},
                        "code": {"type": "string", "description": "Python source code content to write"}
                    },
                    "required": ["path", "code"]
                }
            },
            {
                "name": "execute_gated_command",
                "description": "Executes a system command behind mandatory spend cap and invariant gating.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "System command to execute"}
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "btp_evaluate_action",
                "description": "Evaluates an agent action against pre-flight policy rules and returns an RFC 8785 Ed25519 receipt.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string"},
                        "action_type": {"type": "string"},
                        "payload": {"type": "object"}
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
                        "receipt": {"type": "object"},
                        "candidate_payload": {"type": "object"}
                    },
                    "required": ["receipt", "candidate_payload"]
                }
            },
            {
                "name": "btp_get_trust_roots",
                "description": "Returns active Ed25519 root public keys and registered security invariants.",
                "inputSchema": {"type": "object", "properties": {}}
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

            # 1. GATED FILE WRITE: Physically routes through MandatoryToolGate
            if tool_name == "execute_gated_file_write":
                res = self.gate.execute_gated_tool(
                    agent_id="claude-desktop",
                    tool_name="write_file",
                    arguments={"path": args.get("path", ""), "code": args.get("code", "")}
                )
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(res, indent=2)}]
                    }
                }

            # 2. GATED COMMAND EXECUTION: Routes through MandatoryToolGate
            elif tool_name == "execute_gated_command":
                res = self.gate.execute_gated_tool(
                    agent_id="claude-desktop",
                    tool_name="run_command",
                    arguments={"command": args.get("command", "")}
                )
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(res, indent=2)}]
                    }
                }

            # 3. DIRECT EVALUATION
            elif tool_name == "btp_evaluate_action":
                receipt = self.authority.evaluate_intent(
                    agent_id=args.get("agent_id", "Claude-Agent"),
                    action_type=args.get("action_type", "TOOL_CALL"),
                    payload=args.get("payload", {})
                )
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(receipt, indent=2)}]
                    }
                }

            # 4. OFFLINE VERIFICATION
            elif tool_name == "btp_verify_attestation":
                ok, msg = independent_verify_btp_receipt(
                    receipt_json_str=args.get("receipt", {}),
                    candidate_payload=args.get("candidate_payload", {}),
                    trusted_root_pubkeys=[self.authority.public_key_hex],
                    seen_nonces=self.seen_nonces
                )
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps({"valid": ok, "message": msg}, indent=2)}]
                    }
                }

            # 5. TRUST ROOTS
            elif tool_name == "btp_get_trust_roots":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": json.dumps({
                                "protocol_version": "BTP/2.2",
                                "active_roots": [self.authority.public_key_hex]
                            }, indent=2)
                        }]
                    }
                }

        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

def run_stdio_server():
    server = BartholomewMCPServer()
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line.strip())
            resp = server.handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"Error: {str(e)}\n")

if __name__ == "__main__":
    run_stdio_server()
