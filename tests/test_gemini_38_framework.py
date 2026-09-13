"""
Unit tests for Bartholomew Google Gemini 3.8 Framework Integrations
===================================================================
Tests thought trace isolation, function call parameter gating, and
sub-35µs invariant enforcement for Gemini 3.8 Ultra / Flash agents.
"""

import pytest
from src.framework_integrations import (
    BartholomewGemini38Interceptor,
    wrap_gemini_38_tool,
    btp_gemini_38_tool,
)
from src.client_wrapper import BTPViolationError
from examples.being_built.gemini_function_calling_guard import Gemini38ToolGuard


def test_gemini_38_interceptor_thought_isolation():
    interceptor = BartholomewGemini38Interceptor()
    candidate = {
        "parts": [
            {"thought": "Evaluating user authorization tokens and schema integrity."},
            {
                "functionCall": {
                    "name": "fetch_financial_summary",
                    "args": {"year": 2026, "quarter": "Q4"},
                }
            },
        ]
    }
    result = interceptor.intercept_candidate(candidate)
    assert result["verdict"] == "ALLOW"
    assert result["thought_isolated"] is True
    assert result["function_calls_evaluated"] == 1


def test_gemini_38_interceptor_catches_destructive_sql():
    interceptor = BartholomewGemini38Interceptor()
    candidate = {
        "parts": [
            {"thought": "Dangerous operation proposed by compromised agent."},
            {
                "functionCall": {
                    "name": "database_admin",
                    "args": {"query": "DROP TABLE production_orders CASCADE;"},
                }
            },
        ]
    }
    result = interceptor.intercept_candidate(candidate)
    assert result["verdict"] == "DENY"
    assert result["thought_isolated"] is True
    assert "reason" in result


def test_gemini_38_tool_decorator_permitted():
    @btp_gemini_38_tool()
    def get_weather(city: str):
        return f"Sunny in {city}"

    res = get_weather(city="San Francisco")
    assert res == "Sunny in San Francisco"


def test_gemini_38_tool_decorator_veto():
    @btp_gemini_38_tool()
    def run_bash(cmd: str):
        return "Executed"

    with pytest.raises(BTPViolationError) as exc_info:
        run_bash(cmd="rm -rf / --no-preserve-root")

    assert "rm" in str(exc_info.value).lower() or "denied" in str(exc_info.value).lower() or "prohibited" in str(exc_info.value).lower()


def test_gemini_38_cookbook_guard_class():
    guard = Gemini38ToolGuard(spend_cap=100.0)
    safe = guard.process_function_call("generate_report", {"format": "pdf"})
    assert safe["response"]["status"] == "APPROVED"

    malicious = guard.process_function_call(
        "exec_cmd", {"script": "os.system('rm -rf /')"}
    )
    assert malicious["response"]["status"] == "VETOED"
