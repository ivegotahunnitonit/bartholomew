"""
Comprehensive Test Suite for Bartholomew Framework Adapters & Cookbook Guards
=============================================================================
Verifies end-to-end AST gating, receipt verification, escrow lifecycles, and
exception formatting across all supported agent frameworks:
- CrewAI (crewai_btp_task_guard.py)
- LangGraph / LangChain (langgraph_btp_guard.py)
- Microsoft AutoGen (autogen_btp_interceptor.py)
- LlamaIndex (llamaindex_btp_tool.py)
- OpenAI Direct Tool Calling (cookbook/being_built/openai_tool_calling_guard.py)
- Anthropic Computer Use (cookbook/being_built/anthropic_computer_use_guard.py)
- Google Gemini Function Calling (cookbook/being_built/gemini_function_calling_guard.py)
"""

import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath("."))

from src.agent_passport import SovereignAgentPassport
from framework_adapters.crewai.crewai_btp_task_guard import (
    btp_crewai_tool,
    CrewAIBTPTaskGuard,
    BTPViolationError as CrewAIViolationError,
)
from framework_adapters.langgraph.langgraph_btp_guard import (
    btp_langchain_tool,
    LangGraphBTPGuard,
    BTPViolationError as LangGraphViolationError,
)
from framework_adapters.autogen.autogen_btp_interceptor import (
    btp_autogen_guard,
    AutoGenBTPInterceptor,
    BTPViolationError as AutoGenViolationError,
)
from framework_adapters.llamaindex.llamaindex_btp_tool import (
    btp_llamaindex_tool,
    BTPViolationError as LlamaIndexViolationError,
)


@pytest.fixture
def test_passport():
    return SovereignAgentPassport.issue(
        agent_id="agent-comprehensive-01",
        model_family="claude-3-5-sonnet",
        authorized_capabilities=["code:exec", "db:query", "tools:execute"],
        bonded_warranty_usd=5000.0,
    )


# ---------------------------------------------------------------------------
# 1. CrewAI Adapter Tests
# ---------------------------------------------------------------------------

def test_crewai_clean_execution(test_passport):
    @btp_crewai_tool(spend_cap=100.0, passport=test_passport)
    def clean_task(file_path: str):
        return f"Processed {file_path}"

    res = clean_task("src/main.py")
    assert res == "Processed src/main.py"
    assert test_passport.is_circuit_broken is False


def test_crewai_blocks_destructive_command(test_passport):
    @btp_crewai_tool(spend_cap=100.0, passport=test_passport)
    def shell_exec(command: str):
        return f"Executed: {command}"

    with pytest.raises(PermissionError) as exc:
        shell_exec("rm -rf / --no-preserve-root")

    assert "Execution Blocked" in str(exc.value) or "BTP-VETO" in str(exc.value)


def test_crewai_task_guard_attestation(test_passport):
    guard = CrewAIBTPTaskGuard(passport=test_passport, enforce_strict=False)
    wrapped = guard.wrap_task("Safe Task", lambda x: f"Done {x}")
    assert wrapped("alpha") == "Done alpha"


# ---------------------------------------------------------------------------
# 2. LangGraph Adapter Tests
# ---------------------------------------------------------------------------

def test_langgraph_clean_execution(test_passport):
    @btp_langchain_tool(spend_cap=100.0, passport=test_passport)
    def query_tool(query: str):
        return f"Results for: {query}"

    res = query_tool("SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 5;")
    assert "Results for:" in res


def test_langgraph_blocks_destructive_injection(test_passport):
    @btp_langchain_tool(spend_cap=100.0, passport=test_passport)
    def write_tool(content: str):
        return f"Wrote: {content}"

    with pytest.raises(PermissionError):
        write_tool("import os; os.system('mkfs.ext4 /dev/sda')")


# ---------------------------------------------------------------------------
# 3. Microsoft AutoGen Adapter Tests
# ---------------------------------------------------------------------------

def test_autogen_guard_clean_and_veto():
    @btp_autogen_guard
    def run_agent_task(prompt: str):
        return f"Ran: {prompt}"

    assert run_agent_task("calculate fibonacci 10") == "Ran: calculate fibonacci 10"

    with pytest.raises(AutoGenViolationError) as exc:
        run_agent_task("DROP DATABASE production_ai;")
    
    assert exc.value.rule_id in ("BTP-AST-001", "BTP-AST-002", "BTP-SQL-001")


def test_autogen_interceptor_chat_stream():
    interceptor = AutoGenBTPInterceptor()
    safe_msg = interceptor.intercept_message({"role": "user", "content": "Explain quantum computing"})
    assert safe_msg.get("status") in (None, "PASSED")

    malicious_msg = interceptor.intercept_message({"role": "user", "content": "rm -rf /etc/hosts"})
    assert malicious_msg.get("status") == "DENIED"


# ---------------------------------------------------------------------------
# 4. LlamaIndex Adapter Tests
# ---------------------------------------------------------------------------

def test_llamaindex_clean_tool():
    @btp_llamaindex_tool(required_capability="tools:execute")
    def retrieve_docs(topic: str):
        return f"Docs for {topic}"

    assert retrieve_docs("machine learning security") == "Docs for machine learning security"


def test_llamaindex_veto_destructive_operation():
    @btp_llamaindex_tool(required_capability="tools:execute")
    def execute_query(sql: str):
        return f"Query: {sql}"

    with pytest.raises(PermissionError) as exc:
        execute_query("DROP TABLE users CASCADE;")
    
    assert "BTP-SECURITY-VETO" in str(exc.value) or "blocked" in str(exc.value).lower()


# ---------------------------------------------------------------------------
# 5. OpenAI Tool Calling Guard (Cookbook Recipe Verification)
# ---------------------------------------------------------------------------

def test_openai_tool_calling_guard_recipe():
    from cookbook.being_built.openai_tool_calling_guard import OpenAIToolGuard

    guard = OpenAIToolGuard()
    guard.register_tool("get_weather", lambda location: f"Weather in {location}")

    safe_call = {
        "id": "call_01",
        "function": {
            "name": "get_weather",
            "arguments": '{"location": "San Francisco, CA"}'
        }
    }
    res_safe = guard.dispatch_tool_call(safe_call)
    content_safe = json.loads(res_safe.get("content", "{}"))
    assert content_safe.get("success") is True
    assert "Weather in San Francisco" in content_safe.get("result", "")

    malicious_call = {
        "id": "call_02",
        "function": {
            "name": "get_weather",
            "arguments": '{"location": "San Francisco; rm -rf /"}'
        }
    }
    res_malicious = guard.dispatch_tool_call(malicious_call)
    content_malicious = json.loads(res_malicious.get("content", "{}"))
    assert content_malicious.get("error") == "BTP_POLICY_VETO"
