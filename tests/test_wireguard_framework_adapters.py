"""
Test Suite for BTP v5.4.6 WireGuard Framework Adapters
======================================================
Validates that CrewAI, Universal Models (OpenAI, Claude, Gemini, AutoGen, Grok)
seamlessly integrate with the live Bartholomew public Cloud Run M2M gateway
via WireGuard, correctly approving safe operations and vetoing destructive operations.
"""

import os
import pytest
from btp_guard import WireGuard
from src.framework_adapters.crewai.crewai_btp_task_guard import btp_crewai_tool, BTPViolationError
from src.framework_adapters.universal.universal_model_guard import UniversalBTPModelGuard, ModelProvider


def test_crewai_wireguard_safe_and_veto():
    """Validates CrewAI tool execution with WireGuard cloud transport."""
    # 1. Safe Tool
    @btp_crewai_tool(use_wire=True)
    def query_tool(statement: str) -> str:
        return f"EXECUTED: {statement}"

    safe_res = query_tool("SELECT id, name FROM datasets LIMIT 5;")
    assert "EXECUTED: SELECT" in safe_res

    # 2. Destructive Tool
    @btp_crewai_tool(use_wire=True)
    def delete_tool(statement: str) -> str:
        return f"EXECUTED: {statement}"

    with pytest.raises(BTPViolationError) as exc_info:
        delete_tool("DROP TABLE production_core_secrets CASCADE;")

    assert "BTP Wire Gateway" in exc_info.value.reason or "BTP-AST-001" in exc_info.value.reason


def test_universal_model_guard_wireguard_openai():
    """Validates OpenAI-compatible function calling with WireGuard cloud transport."""
    guard = UniversalBTPModelGuard(use_wire=True)

    # Safe call
    tool_call = {
        "name": "calculate_hash",
        "arguments": {"input": "sample_data_stream"}
    }
    rec = guard.intercept_and_verify(tool_call, provider=ModelProvider.OPENAI)
    assert rec["status"] == "APPROVED"

    # Destructive call
    bad_tool_call = {
        "name": "wipe_database",
        "arguments": {"query": "DROP DATABASE production;"}
    }
    with pytest.raises(PermissionError):
        guard.intercept_and_verify(bad_tool_call, provider=ModelProvider.OPENAI)


def test_universal_model_guard_wireguard_claude():
    """Validates Anthropic Claude tool use format with WireGuard cloud transport."""
    guard = UniversalBTPModelGuard(use_wire=True)

    # Safe call
    claude_call = {
        "content": [
            {"type": "thinking", "thinking": "Analyzing request"},
            {"type": "tool_use", "name": "read_file", "input": {"path": "src/main.py"}}
        ]
    }
    rec = guard.intercept_and_verify(claude_call, provider=ModelProvider.ANTHROPIC)
    assert rec["status"] == "APPROVED"


def test_universal_model_guard_wireguard_gemini():
    """Validates Google Gemini function call format with WireGuard cloud transport."""
    guard = UniversalBTPModelGuard(use_wire=True)

    # Safe call
    gemini_call = {
        "function_call": {
            "name": "list_buckets",
            "args": {"prefix": "acn-data"}
        }
    }
    rec = guard.intercept_and_verify(gemini_call, provider=ModelProvider.GEMINI)
    assert rec["status"] == "APPROVED"
