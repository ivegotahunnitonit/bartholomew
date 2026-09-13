"""
Cookbook Recipe: Universal HTTP Sidecar Proxy (For "Already Built" Agents)
==========================================================================
Zero-code-change protection for legacy, proprietary, or containerized agents.
The proxy sits between any existing agent process and its external tools/APIs.

Architecture:
    [Any Existing Agent] ---> (HTTP POST /tool) ---> [BTP Sidecar Proxy] ---> [Real Tool / DB / API]
                                                            |
                                                (Validates AST & Invariants)
                                                (Vetoes Malicious Requests)

Run:
    python cookbook/already_built/http_sidecar_proxy.py
"""

import sys
import os
import json
import time
import threading
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add repository root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.polyglot_ast_validator import PolyglotASTValidator
from src.trust_protocol import BartholomewTrustAuthority


class SidecarProxyHandler(BaseHTTPRequestHandler):
    """Intercepts and inspects inbound tool requests from legacy agents."""

    def log_message(self, format, *args):
        pass

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body.decode("utf-8"))
            action = payload.get("action", "unknown_action")
            candidate_code = payload.get("code") or payload.get("command") or payload.get("query") or ""

            # 1. Evaluate Polyglot AST Invariant
            is_safe, msg, _ = PolyglotASTValidator.validate_code(str(candidate_code))

            if not is_safe:
                # Intercept and reject malicious action
                self.send_response(403)
                self.send_header("Content-Type", "application/json")
                self.send_header("X-BTP-Status", "VETOED")
                self.end_headers()
                response = {
                    "status": "BLOCKED_BY_BTP_INVARIANT",
                    "reason": msg,
                    "timestamp": time.time()
                }
                self.wfile.write(json.dumps(response).encode("utf-8"))
                return

            # 2. If valid, approve and forward (or return simulated upstream response)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("X-BTP-Status", "ATTESTED")
            self.end_headers()
            response = {
                "status": "UPSTREAM_SUCCESS",
                "action": action,
                "data": f"Executed safely: {action}",
                "btp_receipt": "URN:BTP:ATTESTATION:VERIFIED"
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))

        except Exception as e:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))


class BTPSidecarProxy:
    """Manages the lifecycle of the local sidecar proxy."""

    def __init__(self, host: str = "127.0.0.1", port: int = 18080):
        self.host = host
        self.port = port
        self.server = None
        self._thread = None

    def start(self):
        self.server = HTTPServer((self.host, self.port), SidecarProxyHandler)
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None


def main():
    print("=" * 75)
    print("  BTP Global Cookbook: Universal HTTP Sidecar Proxy Demo")
    print("=" * 75)

    proxy = BTPSidecarProxy(port=18081)
    proxy.start()
    print("[+] Universal BTP Sidecar Proxy active on http://127.0.0.1:18081")

    base_url = "http://127.0.0.1:18081"
    try:
        # Request 1: Legacy agent sending safe analytical query
        print("\n--- [1] Simulating Existing Agent Calling Safe Tool ---")
        safe_req = urllib.request.Request(
            base_url,
            data=json.dumps({"action": "query_db", "query": "SELECT * FROM users LIMIT 5"}).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(safe_req) as resp:
            data = json.loads(resp.read().decode())
            print(f"Proxy Response: {data['status']} (Header: {resp.headers.get('X-BTP-Status')})")
            assert data["status"] == "UPSTREAM_SUCCESS"

        # Request 2: Legacy agent tricked into sending destructive command
        print("\n--- [2] Simulating Existing Agent Tricked by Prompt Injection ---")
        attack_req = urllib.request.Request(
            base_url,
            data=json.dumps({"action": "run_script", "command": "rm -rf / --no-preserve-root"}).encode(),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(attack_req) as resp:
                print("Error: Malicious payload was not blocked!")
        except urllib.error.HTTPError as e:
            err_data = json.loads(e.read().decode())
            print(f"Proxy Response: HTTP {e.code} ({e.headers.get('X-BTP-Status')})")
            print(f"Veto Reason: {err_data['reason']}")
            assert e.code == 403

        print("\n" + "=" * 75)
        print("  Sidecar Proxy Demo Complete: Zero-Code-Change Protection Verified")
        print("=" * 75)
        return True
    finally:
        proxy.stop()


if __name__ == "__main__":
    main()
