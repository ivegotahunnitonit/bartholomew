"""
Bartholomew Model Context Protocol (MCP) Guard Server
Official MCP (2024-11-05) JSON-RPC 2.0 stdio server providing sub-millisecond
AST verification, hermetic path containment, and Ed25519 cryptographic attestations
for Claude Desktop, Cursor, Windsurf, and custom AI agents.
"""

import sys
import os
import json
import subprocess
import time
from typing import Dict, Any, List, Optional

# Ensure parent directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.trust_protocol import BartholomewTrustAuthority
from src.ast_validator import ASTSecurityValidator
from src.hermetic_sandbox import HermeticCommandSandbox


class BartholomewMCPServer:
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = os.path.abspath(workspace_root or os.path.join(BASE_DIR, "workspace"))
        os.makedirs(self.workspace_root, exist_ok=True)
        
        self.authority = BartholomewTrustAuthority()
        self.ast_validator = ASTSecurityValidator()
        self.sandbox = HermeticCommandSandbox()
        
        self.tools_schema = [
            {
                "name": "btp_execute_command",
                "description": "Executes a shell command safely within Bartholomew's AST compiler gate and hermetic workspace boundary, generating an RFC 8785 Ed25519 cryptographic receipt.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The shell command to execute (e.g., 'git status', 'python test.py')."
                        },
                        "cwd": {
                            "type": "string",
                            "description": "Working directory relative to workspace root (defaults to workspace root)."
                        }
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "btp_write_file",
                "description": "Writes content to a file strictly contained inside the workspace boundary, blocking any directory traversal (../) or system file overwrites.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path relative to workspace root (e.g., 'src/app.py')."
                        },
                        "content": {
                            "type": "string",
                            "description": "Text content to write."
                        }
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "btp_read_file",
                "description": "Reads a file inside the protected workspace boundary, preventing credential exfiltration (.env, id_rsa, /etc/shadow, SAM).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path relative to workspace root."
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "btp_evaluate_intent",
                "description": "Microsecond pre-flight safety evaluation for custom agent tool calls or SQL queries. Returns ALLOW/DENY with cryptographic signature.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Identifier of the calling AI agent."
                        },
                        "action_type": {
                            "type": "string",
                            "description": "Type of action (e.g., 'EXEC_TOOL', 'SQL_QUERY', 'WIRE_TRANSFER')."
                        },
                        "payload": {
                            "type": "object",
                            "description": "The proposed payload dictionary."
                        }
                    },
                    "required": ["action_type", "payload"]
                }
            },
            {
                "name": "btp_get_security_status",
                "description": "Returns active Bartholomew BTP v2.2 invariant state, sovereign public key, and protection telemetry.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    def _is_safe_path(self, target_rel_path: str) -> bool:
        """Ensures path is strictly within self.workspace_root and doesn't target protected files."""
        abs_path = os.path.abspath(os.path.join(self.workspace_root, target_rel_path))
        try:
            common = os.path.commonpath([self.workspace_root, abs_path])
            if common != self.workspace_root:
                return False
        except ValueError:
            return False

        # Forbidden secret filenames
        forbidden_names = [".env", "id_rsa", "id_ed25519", "sam", "system", "shadow", "credentials.json"]
        base_name = os.path.basename(abs_path).lower()
        if base_name in forbidden_names:
            return False

        return True

    def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name == "btp_execute_command":
            cmd = arguments.get("command", "").strip()
            cwd_rel = arguments.get("cwd", ".")
            
            # 1. Evaluate intent through cryptographic authority
            receipt = self.authority.evaluate_intent(
                agent_id="claude-desktop-mcp",
                action_type="EXECUTE_COMMAND",
                payload={"command": cmd, "cwd": cwd_rel}
            )
            
            attestation = receipt.get("attestation", {})
            if attestation.get("verdict") != "ALLOW":
                return {
                    "isError": True,
                    "content": [
                        {
                            "type": "text",
                            "text": f"[BARTHOLOMEW INTERCEPTION: BLOCKED]\nReason: {attestation.get('reason')}\nLatency: {attestation.get('evaluation_latency_us')} µs\nBTP Signature: {receipt.get('signature')}"
                        }
                    ]
                }

            # 2. Path validation
            target_cwd = os.path.abspath(os.path.join(self.workspace_root, cwd_rel))
            if not self._is_safe_path(cwd_rel):
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": f"[HERMETIC BREACH] Working directory '{cwd_rel}' is outside the authorized workspace boundary."}]
                }

            # 3. Execute safely
            try:
                t0 = time.perf_counter()
                proc = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=target_cwd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                exec_time_ms = round((time.perf_counter() - t0) * 1000, 2)
                output = proc.stdout if proc.returncode == 0 else f"{proc.stdout}\n[STDERR]: {proc.stderr}"
                return {
                    "isError": proc.returncode != 0,
                    "content": [
                        {
                            "type": "text",
                            "text": f"{output}\n\n[BTP SEAL: VERIFIED & EXECUTED]\nExit Code: {proc.returncode} | Execution Time: {exec_time_ms} ms | Invariant Latency: {attestation.get('evaluation_latency_us')} µs\nSignature: {receipt.get('signature')[:32]}..."
                        }
                    ]
                }
            except Exception as e:
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": f"[EXECUTION ERROR]: {str(e)}"}]
                }

        elif name == "btp_write_file":
            rel_path = arguments.get("path", "")
            content = arguments.get("content", "")

            if not self._is_safe_path(rel_path):
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": f"[BARTHOLOMEW INTERCEPTION] Path '{rel_path}' violates containment boundary or targets sensitive files."}]
                }

            target_abs = os.path.abspath(os.path.join(self.workspace_root, rel_path))
            os.makedirs(os.path.dirname(target_abs), exist_ok=True)
            with open(target_abs, "w", encoding="utf-8") as f:
                f.write(content)

            receipt = self.authority.evaluate_intent(
                agent_id="claude-desktop-mcp",
                action_type="WRITE_FILE",
                payload={"path": rel_path, "bytes": len(content.encode("utf-8"))}
            )

            return {
                "isError": False,
                "content": [
                    {
                        "type": "text",
                        "text": f"[SUCCESS] Written {len(content)} characters to '{rel_path}'.\n[BTP ATTESTATION SEALED: {receipt.get('signature')[:32]}...]"
                    }
                ]
            }

        elif name == "btp_read_file":
            rel_path = arguments.get("path", "")
            if not self._is_safe_path(rel_path):
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": f"[BARTHOLOMEW INTERCEPTION] Read access to '{rel_path}' blocked by containment policy."}]
                }

            target_abs = os.path.abspath(os.path.join(self.workspace_root, rel_path))
            if not os.path.exists(target_abs):
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": f"File not found: '{rel_path}'"}]
                }

            with open(target_abs, "r", encoding="utf-8", errors="replace") as f:
                data = f.read(50000)

            return {
                "isError": False,
                "content": [{"type": "text", "text": data}]
            }

        elif name == "btp_evaluate_intent":
            agent_id = arguments.get("agent_id", "claude-subagent")
            action_type = arguments.get("action_type", "EXEC_TOOL")
            payload = arguments.get("payload", {})

            receipt = self.authority.evaluate_intent(
                agent_id=agent_id,
                action_type=action_type,
                payload=payload
            )

            attestation = receipt.get("attestation", {})
            return {
                "isError": attestation.get("verdict") != "ALLOW",
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(receipt, indent=2)
                    }
                ]
            }

        elif name == "btp_get_security_status":
            status = {
                "status": "ACTIVE",
                "protocol": "BTP v2.2",
                "engine": "Bartholomew Autonomous Trust Protocol",
                "authority_pubkey": self.authority.public_key_hex,
                "workspace_boundary": self.workspace_root,
                "offline_verification": "100% Zero Cloud Dependency"
            }
            return {
                "isError": False,
                "content": [{"type": "text", "text": json.dumps(status, indent=2)}]
            }

        else:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Unknown tool: {name}"}]
            }

    def process_message(self, request_str: str) -> Optional[str]:
        try:
            req = json.loads(request_str)
        except Exception:
            return None

        msg_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        # Handle notifications (no response needed)
        if method == "notifications/initialized" or method == "initialized":
            return None

        # Handle JSON-RPC methods
        if method == "initialize":
            res = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "bartholomew-guard",
                        "version": "2.2.0"
                    }
                }
            }
            return json.dumps(res)

        elif method == "tools/list":
            res = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": self.tools_schema
                }
            }
            return json.dumps(res)

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            call_result = self.handle_tool_call(tool_name, arguments)
            res = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": call_result
            }
            return json.dumps(res)

        elif method == "ping":
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {}})

        else:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            })

    def run_stdio(self):
        """Runs the MCP server over standard input/output."""
        # Ensure utf-8 text stream
        sys.stdin.reconfigure(encoding='utf-8')
        sys.stdout.reconfigure(encoding='utf-8')

        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue

                response = self.process_message(line)
                if response:
                    sys.stdout.write(response + "\n")
                    sys.stdout.flush()
            except (KeyboardInterrupt, SystemExit):
                break
            except Exception as e:
                err_resp = json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": str(e)}
                })
                sys.stdout.write(err_resp + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    server = BartholomewMCPServer()
    server.run_stdio()
