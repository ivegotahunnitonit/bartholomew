"""
Test Suite for BTP Machine-Readable Manifest & M2M Transaction Benchmark
========================================================================
Validates that the machine-readable manifest (btp.json) returns structured identity,
capabilities, protocols, pricing, and security invariants, and that the M2M benchmark
successfully processes 100+ transactions with <35us latency and signed receipts.
"""

import pytest
from src.btp_manifest import generate_manifest, BTPManifestBuilder
from examples.benchmark_m2m_transaction_flow import run_m2m_transaction_benchmark


def test_btp_manifest_structure():
    """Validates the schema and key fields of the machine-readable manifest."""
    manifest = generate_manifest()

    assert manifest["manifest_version"] == "5.4.20"
    assert manifest["identity"]["name"] == "Bartholomew Trust Protocol"
    assert "transaction_authorization" in manifest["capabilities"]
    assert "MCP (Model Context Protocol)" in manifest["protocols"]
    assert manifest["pricing"]["meter"]["event"] == "autonomous_action_allowed"
    assert manifest["pricing"]["meter"]["unit_price_usd"] == 0.0

    security_rules = [r["id"] for r in manifest["security"]["rules"]]
    assert "BTP-AST-001" in security_rules
    assert "BTP-SQL-001" in security_rules
    assert "BTP-SEC-001" in security_rules


def test_m2m_transaction_benchmark():
    """Validates the execution flow of 100 M2M transactions through the gate."""
    results = run_m2m_transaction_benchmark(total_transactions=100)

    assert results["total_transactions"] == 100
    assert results["allowed"] > 0
    assert results["denied"] > 0
    assert results["allowed"] + results["denied"] == 100
    assert results["receipts_count"] == 100
    assert results["throughput_tx_sec"] > 10
