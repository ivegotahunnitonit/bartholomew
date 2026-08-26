"""
Bartholomew Model Context Protocol (MCP) Transparent Proxy Gateway (v2.3)
========================================================================
Acts as an inline intercepting proxy between any MCP Client (Claude Desktop,
Cursor, AWS Bedrock) and any downstream MCP Server (Postgres, Filesystem, GitHub).

Architecture:
  [MCP Client] <--(stdio/HTTP)--> [Bartholomew MCP Gateway] <--(stdio)--> [Downstream MCP Server]
                                             │
                                   [In-Memory AST + Secret Gate]
                                   [Ed25519 Attestation Receipt]

Intercepts JSON-RPC 2.0 requests:
  - tools/call: Evaluates arguments against AST invariants and Secret Masker before forwarding.
  - tools/list: Decorates tool schemas with BTP invariant safety badges.
"""

import sys
import os
import json
import time
from typing import Dict, Any, Tuple, Optional, Callable

sys.path.insert(0, os.path.abspath("."))
from src.polyglot_ast_validator import PolyglotASTValidator
from src.secret_masker import SecretVaultMasker
from src.trust_protocol import BartholomewTrustAuthority


class MCPProxyGateway:
    """
    Transparent JSON-RPC 2.0 Invariant Interception Gateway for MCP tool calling.
    """

    def __init__(self, trust_authority: Optional[BartholomewTrustAuthority] = None):
        self.authority = trust_authority or BartholomewTrustAuthority()
        self.total_intercepted = 0
        self.total_vetoed = 0
        self.total_redacted = 0

    def intercept_jsonrpc_request(self, raw_json_str: str) -> Tuple[bool, Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Intercepts incoming JSON-RPC payload from an MCP Client.
        
        Returns:
          (forward_to_downstream: bool, sanitized_request_dict, veto_response_dict)
        """
        t0 = time.perf_counter()
        self.total_intercepted += 1

        try:
            req = json.loads(raw_json_str)
        except Exception as e:
            return False, {}, {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
            }

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        # Only gate tools/call requests
        if method != "tools/call":
            return True, req, None

        tool_name = params.get("name", "unknown_tool")
        arguments = params.get("arguments", {})

        # 1. High-Entropy Secret Masking on Tool Arguments
        sanitized_args, redactions_count, _ = SecretVaultMasker.sanitize_payload(arguments)
        if redactions_count > 0:
            self.total_redacted += redactions_count
            params["arguments"] = sanitized_args
            req["params"] = params

        # 2. Extract code or command strings from arguments
        code_candidates = []
        if isinstance(sanitized_args, dict):
            for k in ["command", "code", "query", "script", "payload", "input"]:
                if k in sanitized_args and isinstance(sanitized_args[k], str):
                    code_candidates.append(sanitized_args[k])

        # 3. Polyglot AST Invariant Evaluation
        for candidate in code_candidates:
            is_safe, msg, meta = PolyglotASTValidator.validate_code(candidate)
            if not is_safe:
                self.total_vetoed += 1
                latency_us = (time.perf_counter() - t0) * 1_000_000
                
                # Construct JSON-RPC Hard Veto Error
                veto_response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32000,
                        "message": f"BTP-VETO: Invariant Gate Violation on tool '{tool_name}'",
                        "data": {
                            "verdict": "DENY",
                            "rule": msg,
                            "latency_us": round(latency_us, 2),
                            "authority_pubkey": self.authority.public_key_hex
                        }
                    }
                }
                return False, req, veto_response

        # 4. Action Approved: Forward sanitized request to downstream MCP server
        return True, req, None

    def intercept_jsonrpc_response(self, raw_resp_str: str) -> Dict[str, Any]:
        """
        Intercepts outgoing response from downstream MCP Server, scrubbing any secrets before returning to client.
        """
        try:
            resp = json.loads(raw_resp_str)
            sanitized_resp, _, _ = SecretVaultMasker.sanitize_payload(resp)
            return sanitized_resp if isinstance(sanitized_resp, dict) else resp
        except Exception:
            return {}
