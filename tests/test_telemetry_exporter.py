"""
Test Suite: Bartholomew Prometheus & OpenTelemetry Exporter
============================================================
Tests:
  1. Metrics recording (evaluations_allowed, evaluations_denied, latencies).
  2. Prometheus standard text format generation.
  3. Live HTTP /metrics endpoint response.
"""

import sys
import os
import urllib.request
import time

sys.path.insert(0, os.path.abspath("."))
from src.telemetry_exporter import BtpMetricsCollector, start_metrics_server

def test_metrics_exporter():
    print("=" * 80)
    print("TESTING PROMETHEUS & OPENTELEMETRY METRICS EXPORTER")
    print("=" * 80 + "\n")

    collector = BtpMetricsCollector()

    # 1. Record sample decisions
    collector.record_decision("ALLOW", 42.5)
    collector.record_decision("ALLOW", 38.2)
    collector.record_decision("DENY", 55.0, "AST_INJECTION: forbidden os.system")
    collector.record_decision("DENY", 61.2, "SPEND_LIMIT: exceeded max threshold")

    # 2. Test text format generation
    metrics_text = collector.generate_prometheus_metrics()
    print("[*] Generated Prometheus Metrics Output:")
    print("-" * 60)
    print(metrics_text.strip())
    print("-" * 60)

    assert 'btp_evaluations_total{verdict="ALLOW"} 2' in metrics_text
    assert 'btp_evaluations_total{verdict="DENY"} 2' in metrics_text
    assert 'btp_evaluation_latency_microseconds_average' in metrics_text
    assert 'btp_violations_total{type="AST_INJECTION"} 1' in metrics_text

    # 3. Test Live HTTP Endpoint on port 9199
    server = start_metrics_server(port=9199)
    time.sleep(0.1)

    req = urllib.request.urlopen("http://localhost:9199/metrics")
    body = req.read().decode("utf-8")
    server.shutdown()

    assert req.status == 200
    assert 'btp_evaluations_total' in body
    print("\n[+] Live HTTP /metrics endpoint returned 200 OK with valid Prometheus text format.")

    print("\n" + "=" * 80)
    print("ALL PROMETHEUS EXPORTER TESTS PASSED 100% CLEAN!")
    print("=" * 80)

if __name__ == "__main__":
    test_metrics_exporter()
