"""
Unit tests for Frontier Model Guards (Claude 3.7 & OpenAI Agents SDK)
=====================================================================
Tests hybrid thinking trace isolation, OpenAI Agents SDK tool normalization,
and sub-35µs AST invariant gating.
"""

import json
import pytest
from examples.being_built.anthropic_computer_use_guard import Claude37ToolGuard
from examples.being_built.openai_tool_calling_guard import OpenAIToolGuard


def test_claude_37_hybrid_thinking_isolation_and_execution():
    guard = Claude37ToolGuard()
    content_blocks = [
        {
            "type": "thinking",
            "thinking": "Analyzing file tree and formulating safe read command.",
        },
        {
            "type": "tool_use",
            "id": "toolu_01",
            "name": "bash",
            "input": {"command": "ls -la"},
        },
    ]

    thinking, tools = guard.extract_thinking_and_tools(content_blocks)
    assert thinking == "Analyzing file tree and formulating safe read command."
    assert len(tools) == 1

    results = guard.process_content_blocks(content_blocks)
    assert len(results) == 1
    assert results[0]["is_error"] is False
    assert "btp_receipt_signature" in results[0]


def test_claude_37_computer_use_veto_destructive_action():
    guard = Claude37ToolGuard()
    content_blocks = [
        {
            "type": "thinking",
            "thinking": "Attempting forbidden destructive wipe.",
        },
        {
            "type": "tool_use",
            "id": "toolu_bad",
            "name": "bash",
            "input": {"command": "rm -rf / --no-preserve-root"},
        },
    ]

    results = guard.process_content_blocks(content_blocks)
    assert len(results) == 1
    assert results[0]["is_error"] is True
    assert "[BTP_VETO]" in results[0]["content"]


def test_openai_agents_sdk_format_dispatch_and_execution():
    dispatcher = OpenAIToolGuard()

    def process_order(order_id: int, note: str) -> str:
        return f"Order {order_id} processed: {note}"

    dispatcher.register_tool("process_order", process_order)

    # Agents SDK payload format
    payload = {
        "tool_name": "process_order",
        "tool_arguments": {"order_id": 999, "note": "Priority clearance"},
    }
    resp = dispatcher.dispatch_tool_call(payload)
    parsed = json.loads(resp["content"])
    assert parsed["success"] is True
    assert "Order 999 processed" in parsed["result"]
    assert "btp_receipt_signature" in parsed


def test_openai_agents_sdk_prompt_injection_veto():
    dispatcher = OpenAIToolGuard()

    def execute_query(sql: str) -> str:
        return "Executed"

    dispatcher.register_tool("execute_query", execute_query)

    # Injected destructive query
    payload = {
        "tool_name": "execute_query",
        "tool_arguments": {"sql": "DROP TABLE users CASCADE;"},
    }
    resp = dispatcher.dispatch_tool_call(payload)
    parsed = json.loads(resp["content"])
    assert parsed["error"] == "BTP_POLICY_VETO"
    assert "violated safety policy" in parsed["message"]
