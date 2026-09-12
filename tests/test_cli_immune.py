"""
BTP v5.4.6 CLI Auto-Immunity Suite
==================================
Tests CLI subcommands:
  - python cli.py immune run
  - python cli.py immune status
  - python cli.py immune rules
"""

import subprocess
import sys
import json
import pytest


def test_cli_immune_help():
    result = subprocess.run(
        [sys.executable, "cli.py", "immune", "--help"],
        capture_output=True,
        text=True,
        check=True
    )
    assert "run" in result.stdout
    assert "status" in result.stdout
    assert "rules" in result.stdout


def test_cli_immune_status():
    result = subprocess.run(
        [sys.executable, "cli.py", "immune", "status"],
        capture_output=True,
        text=True,
        check=True
    )
    assert "BTP v5.4.6 AUTO-IMMUNITY ENGINE TELEMETRY" in result.stdout
    assert "Active Immune Invariants" in result.stdout
    assert "SUB-35 MICROSECONDS" in result.stdout


def test_cli_immune_rules():
    result = subprocess.run(
        [sys.executable, "cli.py", "immune", "rules"],
        capture_output=True,
        text=True,
        check=True
    )
    assert "BTP v5.4.6 IMMUNE HEURISTIC PATTERN MATRIX" in result.stdout
    assert "RULE_IMMUNE_BASE64_SUBSHELL" in result.stdout
    assert "RULE_IMMUNE_QUOTED_OBFUSCATION" in result.stdout


def test_cli_immune_run():
    result = subprocess.run(
        [sys.executable, "cli.py", "immune", "run", "--iterations", "10", "--seed", "123"],
        capture_output=True,
        text=True,
        check=True
    )
    assert "BTP v5.4.6 AUTO-IMMUNITY ENGINE -- CONTINUOUS ADVERSARIAL RED-TEAMING" in result.stdout
    assert "Mutations Fuzzed  : 10" in result.stdout
    assert "False Positive %  : 0.0%" in result.stdout
