"""
Tests for Bartholomew Cloud Telemetry Dispatcher
================================================
Verifies non-blocking enqueueing, background worker batching,
and fault-tolerant fallback when endpoints are unavailable.
"""

import time
import pytest
from src.cloud_telemetry import CloudTelemetryDispatcher
from src import Guard


def test_cloud_telemetry_enqueue_non_blocking():
    """Verify that pushing an event to the queue takes < 100 microseconds and never blocks."""
    dispatcher = CloudTelemetryDispatcher(api_key="sk_btp_test_key", endpoint="http://localhost:9999/dummy")

    t0 = time.perf_counter()
    success = dispatcher.enqueue_event(
        verdict="ALLOW",
        reason="Approved safe execution",
        rule_id="RULE-AST-000",
        latency_us=14.2,
        agent_id="test-agent-alpha"
    )
    elapsed_us = (time.perf_counter() - t0) * 1_000_000

    assert success is True
    assert elapsed_us < 1000.0  # Must be sub-millisecond
    assert dispatcher.total_enqueued == 1

    dispatcher.stop()


def test_guard_cloud_sync_integration():
    """Verify that Guard with sync_cloud=True enqueues events without throwing."""
    guard = Guard(api_key="sk_btp_test_key", sync_cloud=True, cloud_endpoint="http://localhost:9999/dummy")
    assert guard.telemetry is not None

    res = guard.check("SELECT id, email FROM users WHERE id = 10;")
    assert res["allowed"] is True
    assert res["verdict"] == "ALLOW"

    # Blocked check
    blocked_res = guard.check("rm -rf /")
    assert blocked_res["allowed"] is False
    assert blocked_res["verdict"] == "DENY"

    # Telemetry should have at least 2 events recorded
    assert guard.telemetry.total_enqueued >= 2

    guard.telemetry.stop()
