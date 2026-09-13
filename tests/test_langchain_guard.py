"""
Test Suite: Native LangChain & CrewAI Guardrail Callback Plugin
==============================================================
Tests:
  1. LangChain `on_tool_start` execution with safe input.
  2. LangChain `on_tool_start` blocking forbidden system commands (e.g. rm -rf).
  3. CrewAI agent action spend limit interception ($7,500 over $500 limit).
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath("."))
from src.langchain_guard import BTPCallbackHandler
from src.client_wrapper import BTPViolationError

class MockAgentAction:
    def __init__(self, tool: str, tool_input: dict):
        self.tool = tool
        self.tool_input = tool_input

def test_langchain_guard():
    print("=" * 80)
    print("TESTING NATIVE LANGCHAIN & CREWAI BTP CALLBACK GUARD")
    print("=" * 80 + "\n")

    guard = BTPCallbackHandler(max_spend_usd=500.0)

    # 1. Safe Tool Invocation
    res1 = guard.on_tool_start(
        serialized={"name": "SEARCH_VECTOR_DB"},
        input_str='{"query": "quantum computing algorithms"}'
    )
    print(f"[TEST 1: LangChain Safe Tool Call]")
    print(f"  * Verdict    : {res1['verdict']}")
    print(f"  * Latency    : {res1['latency_us']:.2f} µs")
    print(f"  * Ed25519 Sig: {res1['receipt']['signature'][:24]}...")
    assert res1["verdict"] == "ALLOW"

    # 2. Dangerous Command Interception (rm -rf /)
    print(f"\n[TEST 2: LangChain Dangerous Command (rm -rf)]")
    try:
        guard.on_tool_start(
            serialized={"name": "TERMINAL_EXEC"},
            input_str='{"command": "rm -rf /var/lib/data"}'
        )
        assert False, "Should have raised BTPViolationError"
    except BTPViolationError as e:
        print(f"  * Intercepted Cleanly : {e}")
        print(f"  * Latency Recorded    : {e.latency_us:.2f} µs")
        assert "TERMINAL_EXEC" in str(e)

    # 3. CrewAI Action Spend Limit Check ($7,500 Transfer)
    print(f"\n[TEST 3: CrewAI Action Spend Limit Violation]")
    crew_action = MockAgentAction("PAYOUT_DISPATCH", {"amount_usd": 7500.00, "recipient": "0xabc"})
    try:
        guard.on_agent_action(crew_action)
        assert False, "Should have raised BTPViolationError on spend limit"
    except BTPViolationError as e:
        print(f"  * Intercepted Cleanly : {e}")
        assert "PAYOUT_DISPATCH" in str(e)
        assert "Spend Limit Exceeded" in str(e)

    print("\n" + "=" * 80)
    print("ALL LANGCHAIN & CREWAI GUARD TESTS PASSED 100% CLEAN!")
    print("=" * 80)

if __name__ == "__main__":
    test_langchain_guard()
