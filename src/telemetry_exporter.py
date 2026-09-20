"""
Bartholomew Prometheus & OpenTelemetry Metrics Exporter (v2.2.0)
===============================================================
Exports real-time sub-millisecond telemetry in standard Prometheus text format
for ingestion by Grafana, Datadog, Prometheus, and OpenTelemetry collectors.
"""

import time
import threading
from typing import Dict, Any, List
from http.server import HTTPServer, BaseHTTPRequestHandler

class BtpMetricsCollector:
    """Thread-safe Prometheus metrics collector for BTP decisions and latencies."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(BtpMetricsCollector, cls).__new__(cls)
                cls._instance._init_metrics()
            return cls._instance

    def _init_metrics(self):
        self.evaluations_allowed = 0
        self.evaluations_denied = 0
        self.total_latency_us = 0.0
        self.latency_samples = []
        self.violations_by_type: Dict[str, int] = {}
        self.start_time = time.time()

    def record_decision(self, verdict: str, latency_us: float, violation_reason: str = "") -> None:
        with self._lock:
            if verdict == "ALLOW":
                self.evaluations_allowed += 1
            else:
                self.evaluations_denied += 1
                if violation_reason:
                    key = violation_reason.split(":")[0].strip()
                    self.violations_by_type[key] = self.violations_by_type.get(key, 0) + 1

            self.total_latency_us += latency_us
            self.latency_samples.append(latency_us)
            if len(self.latency_samples) > 10000:
                self.latency_samples.pop(0)

    def generate_prometheus_metrics(self) -> str:
        with self._lock:
            total_evals = self.evaluations_allowed + self.evaluations_denied
            avg_latency = (self.total_latency_us / total_evals) if total_evals > 0 else 0.0
            uptime_seconds = int(time.time() - self.start_time)

            lines = [
                "# HELP btp_evaluations_total Total number of agent actions evaluated by BTP",
                "# TYPE btp_evaluations_total counter",
                f'btp_evaluations_total{{verdict="ALLOW"}} {self.evaluations_allowed}',
                f'btp_evaluations_total{{verdict="DENY"}} {self.evaluations_denied}',
                "",
                "# HELP btp_evaluation_latency_microseconds_average Average pre-flight decision latency in microseconds",
                "# TYPE btp_evaluation_latency_microseconds_average gauge",
                f"btp_evaluation_latency_microseconds_average {avg_latency:.2f}",
                "",
                "# HELP btp_guard_uptime_seconds Uptime of the Bartholomew Trust Authority in seconds",
                "# TYPE btp_guard_uptime_seconds counter",
                f"btp_guard_uptime_seconds {uptime_seconds}",
                "",
                "# HELP btp_violations_total Total security invariant violations intercepted",
                "# TYPE btp_violations_total counter"
            ]

            for v_type, count in self.violations_by_type.items():
                sanitized_type = v_type.replace('"', '\\"').replace("\n", "")
                lines.append(f'btp_violations_total{{type="{sanitized_type}"}} {count}')

            return "\n".join(lines) + "\n"

class BtpMetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/metrics", "/"]:
            collector = BtpMetricsCollector()
            body = collector.generate_prometheus_metrics().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress standard HTTP request log spam
        pass

def start_metrics_server(port: int = 9100) -> HTTPServer:
    """Starts Prometheus metrics exporter HTTP daemon."""
    server = HTTPServer(("0.0.0.0", port), BtpMetricsHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
