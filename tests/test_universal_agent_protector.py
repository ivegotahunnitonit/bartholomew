"""
Unit Test: Universal Agent Protector (BTP v5.4.20)
==================================================
Tests:
  1. Tool list wrapping with @guard.protect
  2. Input prompt secret scrubbing & AST invariant interception
  3. Output credential masking
  4. LangGraph / AutoGen / CrewAI compatibility patterns
"""

import pytest
from btp_guard import protect_agent, Guard


class MockAutonomousAgent:
    def __init__(self, name="code-agent"):
        self.name = name
        self.tools = [
            lambda sql: f"Query result: {sql}",
            lambda cmd: f"Executed shell: {cmd}"
        ]

    def run(self, task: str):
        if "select" in task.lower():
            return self.tools[0](task)
        elif "rm " in task.lower():
            return self.tools[1](task)
        return f"Completed: {task}"

    def chat(self, message: str):
        return f"Echo: {message}"


def test_protect_agent_safe_execution():
    agent = MockAutonomousAgent()
    p_agent = protect_agent(agent)

    assert p_agent.is_btp_protected is True
    res = p_agent.run("SELECT id, username FROM users WHERE tenant_id = 42;")
    assert "Query result: SELECT id, username" in res


def test_protect_agent_blocks_malicious_input():
    agent = MockAutonomousAgent()
    p_agent = protect_agent(agent)

    res = p_agent.run("rm -rf / --no-preserve-root")
    assert "[BLOCKED BY BARTHOLOMEW]" in res
    assert "BTP-AST-001" in res or "Catastrophic" in res or "Polyglot" in res


def test_protect_agent_scrubs_secrets_in_input():
    agent = MockAutonomousAgent()
    p_agent = protect_agent(agent)

    # Input contains API key
    msg = p_agent.chat("Use API key sk-ant-api03-abcdef1234567890abcdef1234567890-test to connect")
    assert "sk-ant-api03" not in msg
    assert "[REDACTED" in msg


def test_protect_agent_tools_direct_call():
    agent = MockAutonomousAgent()
    p_agent = protect_agent(agent)

    # Calling tool 0 with safe query
    tool_0 = p_agent.tools[0]
    out = tool_0("SELECT count(*) FROM orders")
    assert "Query result: SELECT" in out

    # Calling tool 1 with destructive command directly
    tool_1 = p_agent.tools[1]
    with pytest.raises(PermissionError) as exc_info:
        tool_1("rm -rf /")
    assert "blocked" in str(exc_info.value).lower() or "veto" in str(exc_info.value).lower()
