"""
Unit tests for Bartholomew Swarm Red-Team & Stress-Benchmark Suite
"""

import pytest
from src.swarm_stress_benchmark import SwarmStressBenchmark


def test_swarm_stress_benchmark_accuracy_and_latency():
    benchmark = SwarmStressBenchmark(runs=100)
    metrics = benchmark.run()

    assert metrics.total_operations == 100
    assert metrics.threats_intercepted == metrics.threats_injected
    assert metrics.false_positives == 0
    assert metrics.accuracy_pct == 100.0
    assert metrics.p50_latency_us < 35.0
    assert len(metrics.merkle_seal) == 64
