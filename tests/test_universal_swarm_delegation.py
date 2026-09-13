"""
Unit tests for Universal Swarm Delegation Recipe
=================================================
Verifies end-to-end execution of examples/future_swarms/universal_swarm_delegation.py
including RFC 8785 Ed25519 signing, A2A protocol validation, and capability gating.
"""

import subprocess
import sys
import pytest


def test_universal_swarm_delegation_recipe():
    result = subprocess.run(
        [sys.executable, "examples/future_swarms/universal_swarm_delegation.py"],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode == 0, f"Execution failed with stderr:\n{result.stderr}"
    assert "Universal Swarm Delegation (A2A Protocol)" in result.stdout
    assert "Protocol: BTP/A2A/3.1" in result.stdout
    assert "Verification Result: True" in result.stdout
    assert "Privilege escalation blocked" in result.stdout
