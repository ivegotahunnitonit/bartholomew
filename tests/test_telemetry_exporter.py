"""
Test Suite: Bartholomew Multi-SIEM & OpenTelemetry Exporter
============================================================
Tests:
  1. Prometheus metrics recording & HTTP /metrics endpoint.
  2. OpenTelemetry (OTel) OTLP ResourceSpans v1.26.0 export.
  3. Datadog Logs & APM JSON ingest formatting.
  4. Splunk HTTP Event Collector (HEC) JSON batch formatting.
"""

import sys
import os
import urllib.request
import time
import json

sys.path.insert(0, os.path.abspath("."))
from src.telemetry_exporter import BtpMetricsCollector, BtpTelemetryExporter, start_metrics_server


def test_metrics_exporter():
    print("=" * 80)
    print("TESTING MULTI-SIEM & OPENTELEMETRY METRICS EXPORTER")
    print("=" * 80 + "\n")

    collector = BtpMetricsCollector()

    # 1. Record sample decisions
    collector.record_decision("ALLOW", 42.5)
    collector.record_decision("ALLOW", 38.2)
    collector.record_decision("DENY", 55.0, "AST_INJECTION: forbidden os.system")
    collector.record_decision("DENY", 61.2, "SPEND_LIMIT: exceeded max threshold")

    # 2. Test Prometheus text format generation
    metrics_text = collector.generate_prometheus_metrics()
    assert 'btp_evaluations_total{verdict="ALLOW"}' in metrics_text
    assert 'btp_evaluations_total{verdict="DENY"}' in metrics_text
    assert 'btp_evaluation_latency_microseconds_average' in metrics_text
    print("[+] Prometheus text metrics verified.")

    # 3. Test Live HTTP Endpoint on port 9199
    server = start_metrics_server(port=9199)
    time.sleep(0.1)
    req = urllib.request.urlopen("http://localhost:9199/metrics")
    body = req.read().decode("utf-8")
    server.shutdown()
    assert req.status == 200
    assert 'btp_evaluations_total' in body
    print("[+] Live HTTP /metrics endpoint verified.")

    # 4. Test OpenTelemetry (OTel) export
    receipts = [
        {
            "agent_id": "test-agent-1",
            "target_tool": "postgres_query",
            "verdict": "ALLOW",
            "reason": "OK",
            "rule_id": "BTP-INV-000",
            "latency_us": 12.4,
            "receipt_sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        },
        {
            "agent_id": "test-agent-2",
            "target_tool": "bash_exec",
            "verdict": "DENY",
            "reason": "rm -rf / blocked",
            "rule_id": "BTP-AST-001",
            "latency_us": 4.1,
            "receipt_sha256": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        }
    ]

    otel_data = BtpTelemetryExporter.to_opentelemetry(receipts)
    assert "resourceSpans" in otel_data
    spans = otel_data["resourceSpans"][0]["scopeSpans"][0]["spans"]
    assert len(spans) == 2
    assert spans[0]["status"]["code"] == 1
    assert spans[1]["status"]["code"] == 2
    print("[+] OpenTelemetry (OTel) ResourceSpans specification verified.")

    # 5. Test Datadog export
    dd_logs = BtpTelemetryExporter.to_datadog(receipts)
    assert len(dd_logs) == 2
    assert dd_logs[0]["status"] == "info"
    assert dd_logs[1]["status"] == "error"
    print("[+] Datadog Logs & APM payload verified.")

    # 6. Test Splunk HEC export
    splunk_events = BtpTelemetryExporter.to_splunk_hec(receipts)
    assert len(splunk_events) == 2
    assert splunk_events[0]["sourcetype"] == "btp:agent:audit"
    print("[+] Splunk HEC batch payload verified.")

    print("\n" + "=" * 80)
    print("ALL TELEMETRY & SIEM EXPORTER TESTS PASSED 100% CLEAN!")
    print("=" * 80)


if __name__ == "__main__":
    test_metrics_exporter()
