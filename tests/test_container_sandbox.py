"""
Unit tests for Bartholomew Container Sandbox & Isolation Engine
==============================================================
"""

import os
import tempfile
import pytest
from src.container_sandbox import ContainerSandboxEngine


def test_container_sandbox_initialization():
    engine = ContainerSandboxEngine(
        base_image="alpine:latest",
        memory_limit="256m",
        cpu_limit=0.5,
        network_enabled=False,
        timeout_seconds=5
    )
    assert engine.memory_limit == "256m"
    assert engine.cpu_limit == "0.5"
    assert engine.network_enabled is False
    assert engine.timeout_seconds == 5


def test_container_sandbox_permitted_command_execution():
    engine = ContainerSandboxEngine(timeout_seconds=5)
    with tempfile.TemporaryDirectory() as tmpdir:
        # Permitted command: git status
        code, stdout, stderr, mode = engine.run_isolated_command(
            command="git status",
            workspace_dir=tmpdir
        )
        assert "ISOLATED" in mode or "FALLBACK" in mode
        assert code in (0, 128)  # 128 is git returncode outside git repo


def test_container_sandbox_blocks_destructive_commands_in_fallback():
    # Force fallback mode to test invariant safety
    engine = ContainerSandboxEngine(timeout_seconds=5)
    engine._docker_available = False  # Simulate offline Docker daemon

    with tempfile.TemporaryDirectory() as tmpdir:
        code, stdout, stderr, mode = engine.run_isolated_command(
            command="rm -rf / --no-preserve-root",
            workspace_dir=tmpdir
        )
        assert code == 126
        assert "Blocked" in stderr
        assert mode == "HERMETIC_FALLBACK_BLOCKED"


def test_container_sandbox_blocks_subshell_and_eval_flags():
    engine = ContainerSandboxEngine(timeout_seconds=5)
    engine._docker_available = False

    with tempfile.TemporaryDirectory() as tmpdir:
        # Command with eval flag -c is blocked
        code, stdout, stderr, mode = engine.run_isolated_command(
            command="python -c \"import os; os.system('echo exploit')\"",
            workspace_dir=tmpdir
        )
        assert code == 126
        assert "Forbidden flag" in stderr or "Blocked" in stderr
