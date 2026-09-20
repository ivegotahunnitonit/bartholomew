"""
Unit tests for Bartholomew Enterprise Fleet Telemetry & OpenTelemetry Exporter.
"""

import pytest
from src.fleet_telemetry import FleetTelemetryAggregator


def test_fleet_registration_and_ingestion():
    aggregator = FleetTelemetryAggregator()
    aggregator.register_node("node-01", "dev-laptop-macbook", "a35ab4eb80dd3c4c33659b314e659168c7ca30e3a53b58046f85f350173ed18f")

    receipt = {
        "attestation": {
            "agent_id": "claude-dev-01",
            "action_type": "EXEC_COMMAND",
            "verdict": "ALLOW",
            "nonce": "test-nonce-123"
        },
        "signature": "mock_sig_123456789"
    }

    assert aggregator.ingest_receipt(receipt, node_id="node-01") is True
    assert aggregator.node_registry["node-01"]["receipt_count"] == 1


def test_otlp_json_export_structure():
    aggregator = FleetTelemetryAggregator()
    aggregator.ingest_receipt({
        "attestation": {
            "agent_id": "cursor-agent",
            "action_type": "WRITE_FILE",
            "verdict": "ALLOW",
            "nonce": "nonce-456"
        },
        "signature": "sig_allow_789"
    })
    aggregator.ingest_receipt({
        "attestation": {
            "agent_id": "malicious-agent",
            "action_type": "DROP_TABLE",
            "verdict": "DENY",
            "nonce": "nonce-999"
        },
        "signature": "sig_deny_999"
    })

    otlp = aggregator.export_otlp_json(limit=10)
    assert "resourceLogs" in otlp
    logs = otlp["resourceLogs"][0]["scopeLogs"][0]["logRecords"]
    assert len(logs) == 2

    # Check ALLOW record
    assert logs[0]["severityText"] == "INFO"
    assert logs[0]["severityNumber"] == 9

    # Check DENY record
    assert logs[1]["severityText"] == "ERROR"
    assert logs[1]["severityNumber"] == 17

    summary = aggregator.get_fleet_health_summary()
    assert summary["verdict_distribution"]["ALLOW"] == 1
    assert summary["verdict_distribution"]["DENY"] == 1
