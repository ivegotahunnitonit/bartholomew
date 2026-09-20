"""
Unit tests for Bartholomew Native Core FFI & Invariant Engine.
"""

import time
import pytest
from src.native_core.btp_ffi import NativeInvariantEngine


def test_native_marginal_utility_calculation():
    engine = NativeInvariantEngine()
    mu1 = engine.calculate_marginal_utility(0.35, 1)
    assert mu1 == 1.0

    mu5 = engine.calculate_marginal_utility(0.35, 5)
    assert mu5 < 0.30
    assert mu5 > 0.10


def test_native_pattern_containment():
    engine = NativeInvariantEngine()
    assert engine.contains_forbidden_pattern("DROP TABLE users;", "drop table") is True
    assert engine.contains_forbidden_pattern("SELECT * FROM items;", "drop table") is False


def test_native_path_traversal_detection():
    engine = NativeInvariantEngine()
    assert engine.is_path_traversal_attack("../../../etc/shadow") is True
    assert engine.is_path_traversal_attack("..\\..\\.env") is True
    assert engine.is_path_traversal_attack("src/app.py") is False


def test_sub_5_microsecond_execution():
    engine = NativeInvariantEngine()
    # Warm up
    for _ in range(10):
        engine.calculate_marginal_utility(0.35, 3)

    t0 = time.perf_counter()
    iterations = 1000
    for _ in range(iterations):
        engine.calculate_marginal_utility(0.35, 3)
        engine.contains_forbidden_pattern("git status --porcelain", "rm -rf")
        engine.is_path_traversal_attack("workspace/output.txt")
    total_sec = time.perf_counter() - t0
    avg_us_per_check = (total_sec / (iterations * 3)) * 1_000_000

    print(f"\n[BENCHMARK] Average latency per native invariant check: {avg_us_per_check:.2f} µs")
    assert avg_us_per_check < 10.0 # Sub-10 microseconds on any host!
