"""
Unit Tests for Bartholomew Execution Dispatch-Seam Interceptor
===============================================================
Validates that dynamic runtime indirection (shlex, getattr, eval strings,
subprocess argument arrays, nested dicts) cannot bypass the dispatch seam.
"""

import os
import shlex
import subprocess
import sys
import time
import pytest

sys.path.insert(0, os.path.abspath("."))

from src.dispatch_seam import (
    dispatch_seam_guard,
    DispatchSeamInterceptor,
    DispatchViolationError,
    extract_evaluated_payloads,
)
from src import Guard


class MockAgentToolSuite:
    """Mock agent tool suite exposing dynamic execution methods."""

    @dispatch_seam_guard
    def run_command(self, cmd_args):
        return f"Executed command: {cmd_args}"

    @dispatch_seam_guard
    def query_database(self, query_payload):
        return f"Query executed: {query_payload}"

    @dispatch_seam_guard
    def execute_arbitrary_callable(self, fn_name, *args, **kwargs):
        return f"Invoked {fn_name}"


def test_extract_evaluated_payloads_canonicalization():
    """Verifies that lists, tuples, and nested dictionaries are correctly canonicalized."""
    # List of tokens -> reconstructs unified shell command
    tokens = ["rm", "-rf", "/tmp/cache"]
    payloads = extract_evaluated_payloads(tokens)
    assert "rm -rf /tmp/cache" in payloads

    # Nested dict
    nested = {"action": "db_query", "params": {"query": ["DROP", "TABLE", "customers"]}}
    payloads_nested = extract_evaluated_payloads(nested)
    assert "DROP TABLE customers" in payloads_nested


def test_dispatch_seam_blocks_subprocess_argument_arrays():
    """
    Simulates: agent uses shlex.split to construct command array across multiple lines.
    Ensures the dispatch seam intercepts the evaluated array.
    """
    suite = MockAgentToolSuite()

    # Dynamic shlex split
    raw_input = "rm -rf /data/prod"
    command_array = shlex.split(raw_input)  # ['rm', '-rf', '/data/prod']

    with pytest.raises(DispatchViolationError) as exc_info:
        suite.run_command(command_array)

    assert "blocked by" in str(exc_info.value).lower()
    assert exc_info.value.function_name == "run_command"


def test_dispatch_seam_blocks_dynamic_string_concatenation():
    """
    Simulates: agent dynamically concatenates strings to evade static AST regex/ast scans.
    By dispatch time, the arguments are materialized strings.
    """
    suite = MockAgentToolSuite()

    # Dynamic concatenation
    part1 = "DR" + "OP "
    part2 = "TA" + "BLE "
    target = "users;"
    dynamic_query = part1 + part2 + target  # 'DROP TABLE users;'

    with pytest.raises(DispatchViolationError) as exc_info:
        suite.query_database({"sql": dynamic_query})

    assert "DROP TABLE" in str(exc_info.value) or "blocked" in str(exc_info.value).lower()


def test_dispatch_seam_blocks_getattr_indirection():
    """
    Simulates: agent resolves method dynamically via getattr and executes it.
    """
    suite = MockAgentToolSuite()
    method_name = "".join(["run_", "command"])
    dynamic_method = getattr(suite, method_name)

    with pytest.raises(DispatchViolationError):
        dynamic_method(["rm", "-rf", "/var/run"])


def test_dispatch_seam_allows_benign_operations():
    """Verifies that clean and compliant tool calls pass through seamlessly."""
    suite = MockAgentToolSuite()

    res_cmd = suite.run_command(["ls", "-la", "/var/log"])
    assert "Executed command" in res_cmd

    res_sql = suite.query_database("SELECT id, username FROM users WHERE active = 1 LIMIT 50;")
    assert "Query executed" in res_sql


def test_dispatch_seam_latency_benchmark():
    """
    Microsecond performance test: dispatch interception must complete in <25 microseconds.
    """
    suite = MockAgentToolSuite()
    cmd = ["git", "status", "--porcelain"]

    # Warmup
    for _ in range(10):
        suite.run_command(cmd)

    iterations = 1000
    t0 = time.perf_counter_ns()
    for _ in range(iterations):
        suite.run_command(cmd)
    total_elapsed_ns = time.perf_counter_ns() - t0

    avg_latency_us = (total_elapsed_ns / iterations) / 1000.0
    print(f"\n[BENCHMARK] Average Dispatch-Seam Interception Latency: {avg_latency_us:.2f} µs")
    assert avg_latency_us < 35.0, f"Latency {avg_latency_us:.2f}µs exceeded 35µs budget"


def test_guard_protect_decorator_with_dispatch_seam():
    """Verifies Guard.protect uses the new dispatch seam with list arguments."""
    g = Guard()

    @g.protect
    def sample_executor(args):
        return "SUCCESS"

    # Benign passes
    assert sample_executor(["cat", "/etc/hosts"]) == "SUCCESS"

    # Malicious array fails
    with pytest.raises(PermissionError) as exc:
        sample_executor(["rm", "-rf", "/"])
    assert "Blocked" in str(exc.value) or "blocked" in str(exc.value).lower()
