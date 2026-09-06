"""
BTP Production Container Daemon & Prometheus Metrics Exporter (Milestone 3.4)
=============================================================================
Provides a production daemon service exposing:
1. /healthz: Liveness & readiness probes for Kubernetes.
2. /metrics: Prometheus-formatted telemetry (threat entropy, active quorum,
   ZK rollup throughput, and hardware enclave attestation counts).
3. /api/v1/anchor: Programmatic ZK-Rollup sealing and hardware anchoring.
"""

from __future__ import annotations

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from typing import Dict, Any, Optional

from src.ebpf_kernel_guard import DynamicThresholdRebalancer, KernelSyscallEvent
from src.zk_rollup_batcher import ZKRollupBatcher, EnclaveZKRollupAnchor
from src.zk_compliance_proof_engine import ZKComplianceEngine


class DaemonMetricsRegistry:
    """Thread-safe Prometheus metrics registry for BTP Guard."""

    def __init__(self):
        self._lock = threading.Lock()
        self.threat_entropy: float = 0.0
        self.active_quorum_k: int = 2
        self.active_quorum_n: int = 3
        self.zk_rollups_sealed_total: int = 0
        self.enclave_attestations_total: int = 0
        self.blocked_syscalls_total: int = 0
        self.total_tool_calls_audited: int = 0

    def update_threat_entropy(self, entropy: float, k: int, n: int):
        with self._lock:
            self.threat_entropy = round(entropy, 4)
            self.active_quorum_k = k
            self.active_quorum_n = n

    def record_sealed_rollup(self, tool_calls_count: int):
        with self._lock:
            self.zk_rollups_sealed_total += 1
            self.total_tool_calls_audited += tool_calls_count

    def record_enclave_attestation(self):
        with self._lock:
            self.enclave_attestations_total += 1

    def record_blocked_syscall(self):
        with self._lock:
            self.blocked_syscalls_total += 1

    def render_prometheus(self) -> str:
        with self._lock:
            lines = [
                "# HELP btp_threat_entropy_ratio Current monitored kernel threat entropy (0.0 to 1.0)",
                "# TYPE btp_threat_entropy_ratio gauge",
                f"btp_threat_entropy_ratio {self.threat_entropy}",
                "",
                "# HELP btp_active_quorum_k Current active required threshold signatures",
                "# TYPE btp_active_quorum_k gauge",
                f"btp_active_quorum_k {self.active_quorum_k}",
                "",
                "# HELP btp_active_quorum_n Current active total peer quorum size",
                "# TYPE btp_active_quorum_n gauge",
                f"btp_active_quorum_n {self.active_quorum_n}",
                "",
                "# HELP btp_zk_rollups_sealed_total Total recursive zero-knowledge rollup batches sealed",
                "# TYPE btp_zk_rollups_sealed_total counter",
                f"btp_zk_rollups_sealed_total {self.zk_rollups_sealed_total}",
                "",
                "# HELP btp_enclave_attestations_total Total confidential hardware enclave attestations verified",
                "# TYPE btp_enclave_attestations_total counter",
                f"btp_enclave_attestations_total {self.enclave_attestations_total}",
                "",
                "# HELP btp_blocked_syscalls_total Total blocked rogue agent syscalls",
                "# TYPE btp_blocked_syscalls_total counter",
                f"btp_blocked_syscalls_total {self.blocked_syscalls_total}",
                "",
                "# HELP btp_tool_calls_audited_total Total agent tool invocations audited across all batches",
                "# TYPE btp_tool_calls_audited_total counter",
                f"btp_tool_calls_audited_total {self.total_tool_calls_audited}",
                ""
            ]
            return "\n".join(lines)


GLOBAL_METRICS = DaemonMetricsRegistry()


class BTPDaemonHTTPHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for BTP Daemon."""

    def log_message(self, format: str, *args):
        # Suppress noisy standard request logging
        pass

    def do_GET(self):
        if self.path in ("/healthz", "/health"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            resp = {
                "status": "healthy",
                "service": "btp-daemon",
                "version": "3.5.0",
                "timestamp": time.time()
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        elif self.path in ("/metrics", "/metrics/"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.end_headers()
            self.wfile.write(GLOBAL_METRICS.render_prometheus().encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/v1/anchor":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
                sessions = data.get("sessions", [])

                zk_engine = ZKComplianceEngine()
                batcher = ZKRollupBatcher()

                for s in sessions:
                    s_id = s.get("session_id", f"sess-{time.time_ns()}")
                    calls = s.get("tool_calls", ["default_safe_tool_call"])
                    proof = zk_engine.prove_session(session_id=s_id, tool_calls=calls)
                    batcher.add_proof(proof)

                rollup = batcher.seal()
                GLOBAL_METRICS.record_sealed_rollup(rollup.total_tool_calls)

                anchor = EnclaveZKRollupAnchor.create_hardware_anchor(rollup)
                GLOBAL_METRICS.record_enclave_attestation()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(anchor).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


class BTPDaemon:
    """Manages the background daemon HTTP server."""

    def __init__(self, host: str = "127.0.0.1", port: int = 9090):
        self.host = host
        self.port = port
        self.server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def start(self):
        self.server = HTTPServer((self.host, self.port), BTPDaemonHTTPHandler)
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="BTP Container Daemon & Prometheus Metrics Exporter")
    parser.add_argument("--port", type=int, default=9090, help="Listen port (default 9090)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Listen host (default 0.0.0.0)")
    args = parser.parse_args()

    daemon = BTPDaemon(host=args.host, port=args.port)
    daemon.start()
    print(f"BTP Daemon active on http://{args.host}:{args.port}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        daemon.stop()
        print("BTP Daemon stopped.")
