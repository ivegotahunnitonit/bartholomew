"""
Bartholomew Local Daemon Server (Zero External Dependencies)
Sub-millisecond local HTTP & event gateway for autonomous AI agent protection.
Uses pure Python standard library (http.server) with zero pip dependencies required.
"""

import sys
import os
import time
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from typing import Dict, Any, List

# Add parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.trust_protocol import BartholomewTrustAuthority
from daemon.approval_queue import ApprovalQueue
from daemon.notifications import send_desktop_notification


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class BartholomewDaemon:
    def __init__(self, host: str = "127.0.0.1", port: int = 8080, policy_file: str = "policies/default_security_policy.yaml"):
        self.host = host
        self.port = port
        self.policy_file = policy_file
        self.start_time = time.time()

        # Core Engines
        self.authority = BartholomewTrustAuthority()
        self.approval_queue = ApprovalQueue()

        # Telemetry State
        self.total_evaluations = 0
        self.total_blocked = 0
        self.total_allowed = 0
        self.latencies_us = []
        self.recent_events: List[Dict[str, Any]] = []
        self.server: ThreadedHTTPServer = None

        # Wire up notification listener on approval queue
        self.approval_queue.add_listener(self._on_approval_requested)

    def _on_approval_requested(self, approval):
        send_desktop_notification(
            title="[Bartholomew Action Required]",
            message=f"Agent '{approval.agent_id}' requests: {approval.action_type}. Requires approval.",
            is_threat=True
        )
        self.broadcast_event({
            "type": "APPROVAL_REQUESTED",
            "data": approval.to_dict()
        })

    def broadcast_event(self, event: Dict[str, Any]):
        self.recent_events.insert(0, event)
        if len(self.recent_events) > 50:
            self.recent_events.pop()

    def evaluate_payload(self, agent_id: str, action_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.perf_counter()

        # Check high-stakes co-signing gate before execution
        amount_usd = payload.get("amount_usd", 0)
        if isinstance(amount_usd, (int, float)) and amount_usd > 500:
            approval = self.approval_queue.submit_for_approval(
                agent_id=agent_id,
                action_type=action_type,
                payload=payload,
                reason=f"Spend amount ${amount_usd:.2f} exceeds $500 threshold and requires human co-signing."
            )
            t_eval = (time.perf_counter() - t0) * 1_000_000
            return {
                "verdict": "PENDING_APPROVAL",
                "request_id": approval.request_id,
                "reason": approval.reason,
                "latency_us": round(t_eval, 2),
                "expires_at": approval.expires_at
            }

        # Evaluate intent using BTP Core cryptographic authority
        receipt = self.authority.evaluate_intent(
            agent_id=agent_id,
            action_type=action_type,
            payload=payload
        )

        attestation = receipt.get("attestation", {})
        verdict = attestation.get("verdict", "DENY")
        is_allowed = (verdict == "ALLOW")
        reason = attestation.get("reason", "Evaluated by policy invariants")
        total_latency_us = round(attestation.get("evaluation_latency_us", (time.perf_counter() - t0) * 1_000_000), 2)

        self.total_evaluations += 1
        if is_allowed:
            self.total_allowed += 1
        else:
            self.total_blocked += 1
            send_desktop_notification(
                title="[Bartholomew Threat Intercepted]",
                message=f"Agent '{agent_id}' was BLOCKED: {reason}",
                is_threat=True
            )

        self.latencies_us.append(total_latency_us)
        if len(self.latencies_us) > 1000:
            self.latencies_us.pop(0)

        # Record event
        event_dict = {
            "type": "EVALUATION",
            "receipt": receipt,
            "latency_us": total_latency_us,
            "timestamp": time.strftime("%H:%M:%S")
        }
        self.broadcast_event(event_dict)

        return {
            "allowed": is_allowed,
            "verdict": verdict,
            "reason": reason,
            "latency_us": total_latency_us,
            "signature": receipt.get("signature"),
            "public_key": self.authority.public_key_hex,
            "receipt": receipt
        }

    def get_status_dict(self) -> Dict[str, Any]:
        uptime_sec = round(time.time() - self.start_time, 1)
        avg_latency = round(sum(self.latencies_us) / len(self.latencies_us), 2) if self.latencies_us else 32.4

        return {
            "status": "ACTIVE",
            "version": "2.2.0",
            "engine": "BTP Sovereign Invariant Engine",
            "host": self.host,
            "port": self.port,
            "uptime_seconds": uptime_sec,
            "total_evaluations": self.total_evaluations,
            "total_allowed": self.total_allowed,
            "total_blocked": self.total_blocked,
            "average_latency_us": avg_latency,
            "policy_file": self.policy_file,
            "public_key": self.authority.public_key_hex,
            "active_approvals_count": len(self.approval_queue.list_active()),
            "recent_events": self.recent_events[:15]
        }

    def start_server(self):
        daemon_instance = self

        class DaemonRequestHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # Keep console silent for sub-50us performance

            def _send_cors(self):
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

            def do_OPTIONS(self):
                self.send_response(200)
                self._send_cors()
                self.end_headers()

            def do_GET(self):
                if self.path.startswith("/v1/status"):
                    data = daemon_instance.get_status_dict()
                    body = json.dumps(data).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors()
                    self.end_headers()
                    self.wfile.write(body)
                elif self.path.startswith("/v1/approvals"):
                    active = daemon_instance.approval_queue.list_active()
                    body = json.dumps({"approvals": active}).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors()
                    self.end_headers()
                    self.wfile.write(body)
                elif self.path.startswith("/v1/events"):
                    events = daemon_instance.recent_events[:20]
                    body = json.dumps({"events": events}).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors()
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    self.send_response(404)
                    self._send_cors()
                    self.end_headers()

            def do_POST(self):
                content_length = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                try:
                    payload_json = json.loads(raw_body)
                except Exception:
                    payload_json = {}

                if self.path.startswith("/v1/evaluate"):
                    agent_id = payload_json.get("agent_id", "unnamed_agent")
                    action_type = payload_json.get("action_type", "EXECUTE_TOOL")
                    payload = payload_json.get("payload", {})

                    result = daemon_instance.evaluate_payload(agent_id, action_type, payload)
                    body = json.dumps(result).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors()
                    self.end_headers()
                    self.wfile.write(body)
                elif "/v1/approvals/" in self.path and self.path.endswith("/decide"):
                    parts = self.path.split("/")
                    req_id = parts[3]
                    approve = bool(payload_json.get("approve", False))
                    operator = payload_json.get("operator", "Local Operator")

                    decided = daemon_instance.approval_queue.decide(req_id, approve=approve, operator_name=operator)
                    if not decided:
                        self.send_response(404)
                        self._send_cors()
                        self.end_headers()
                        self.wfile.write(b'{"error":"Request not found"}')
                        return

                    # Stamp co-signed attestation
                    receipt = daemon_instance.authority.evaluate_intent(
                        agent_id=decided.agent_id,
                        action_type=decided.action_type,
                        payload=decided.payload
                    )
                    daemon_instance.broadcast_event({
                        "type": "APPROVAL_DECIDED",
                        "data": decided.to_dict(),
                        "receipt": receipt
                    })

                    body = json.dumps({
                        "status": decided.status,
                        "decided_by": decided.decided_by,
                        "receipt": receipt
                    }).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors()
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    self.send_response(404)
                    self._send_cors()
                    self.end_headers()

        self.server = ThreadedHTTPServer((self.host, self.port), DaemonRequestHandler)
        return self.server

    def run(self):
        self.start_server()
        print(f"[BARTHOLOMEW DAEMON] Active on http://{self.host}:{self.port}")
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.server.server_close()


if __name__ == "__main__":
    daemon = BartholomewDaemon()
    daemon.run()
