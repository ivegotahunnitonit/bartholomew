"""
Tests for Universal Model Compatibility (OpenAI, Kimi/Moonshot, DeepSeek, Anthropic, Gemini, Ollama).
Validates that Bartholomew's wire-level interception operates uniformly across every model provider.
"""

import pytest
import time
from framework_adapters.universal.universal_model_guard import (
    UniversalBTPModelGuard,
    ModelProvider,
    btp_universal_guard,
)
from src.agent_passport import SovereignAgentPassport


def test_openai_tool_calling_safety_and_veto():
    passport = SovereignAgentPassport(
        agent_id="agent-openai-gpt4o",
        worker_model="GPT-4o",
        owner_pubkey="pubkey_openai_123",
        granted_capabilities=["db:query", "compute:run"]
    )
    guard = UniversalBTPModelGuard(
        escrow_collateral_usd=250.0,
        passport=passport,
        strict=False,
    )

    # 1. Safe OpenAI tool call
    safe_call = {
        "id": "call_safe_openai_1",
        "type": "function",
        "function": {
            "name": "query_database",
            "arguments": '{"query": "SELECT user_id, email FROM users WHERE active = true LIMIT 50;"}'
        }
    }
    res = guard.intercept_and_verify(safe_call, provider=ModelProvider.OPENAI)
    assert res["status"] == "APPROVED"
    assert res["tool_name"] == "query_database"
    assert res["escrow_released"] is True
    assert not passport.is_circuit_broken

    # 2. Malicious OpenAI tool call (DROP TABLE)
    malicious_call = {
        "id": "call_malicious_openai_2",
        "type": "function",
        "function": {
            "name": "query_database",
            "arguments": '{"query": "DROP TABLE users CASCADE;"}'
        }
    }
    res = guard.intercept_and_verify(malicious_call, provider=ModelProvider.OPENAI)
    assert res["status"] == "VETOED"
    assert res["violation"] in ["UNAUTHORIZED_DESTRUCTIVE_SQL_MUTATION", "BTP-AST-001"]
    assert res["circuit_broken"] is True
    assert passport.is_circuit_broken is True


def test_kimi_moonshot_model_compatibility():
    passport = SovereignAgentPassport(
        agent_id="agent-kimi-k15",
        worker_model="Kimi-K1.5-LongContext",
        owner_pubkey="pubkey_kimi_456",
        granted_capabilities=["code:exec"]
    )
    guard = UniversalBTPModelGuard(
        escrow_collateral_usd=500.0,
        passport=passport,
        strict=False,
    )

    # Malicious bash injection via Moonshot tool schema
    kimi_call = {
        "id": "call_kimi_bash_001",
        "type": "function",
        "function": {
            "name": "execute_bash",
            "arguments": '{"cmd": "rm -rf / --no-preserve-root"}'
        }
    }
    res = guard.intercept_and_verify(kimi_call, provider=ModelProvider.KIMI)
    assert res["status"] == "VETOED"
    assert res["violation"] in ["DESTRUCTIVE_OS_COMMAND_INJECTION", "BTP-AST-001"]
    assert passport.is_circuit_broken is True


def test_deepseek_model_compatibility():
    passport = SovereignAgentPassport(
        agent_id="agent-deepseek-r1",
        worker_model="DeepSeek-R1-Distill",
        owner_pubkey="pubkey_deepseek_789",
        granted_capabilities=["finance:transfer"]
    )
    guard = UniversalBTPModelGuard(
        escrow_collateral_usd=1000.0,
        passport=passport,
        strict=False,
    )

    # Safe call
    safe_call = {
        "id": "call_ds_001",
        "type": "function",
        "function": {
            "name": "fetch_market_depth",
            "arguments": '{"symbol": "BTC-USD", "depth": 20}'
        }
    }
    res = guard.intercept_and_verify(safe_call, provider=ModelProvider.DEEPSEEK)
    assert res["status"] == "APPROVED"


def test_anthropic_claude_tool_use_compatibility():
    passport = SovereignAgentPassport(
        agent_id="agent-claude-35-sonnet",
        worker_model="Claude-3.5-Sonnet",
        owner_pubkey="pubkey_claude_abc",
        granted_capabilities=["env:read"]
    )
    guard = UniversalBTPModelGuard(
        escrow_collateral_usd=300.0,
        passport=passport,
        strict=False,
    )

    # Anthropic native schema: {"type": "tool_use", "name": "...", "input": {...}}
    claude_exfil_call = {
        "type": "tool_use",
        "id": "toolu_01A098bCs1",
        "name": "save_config",
        "input": {
            "path": "/tmp/creds.txt",
            "payload": "export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        }
    }
    res = guard.intercept_and_verify(claude_exfil_call, provider=ModelProvider.ANTHROPIC)
    assert res["status"] == "VETOED"
    assert res["violation"] == "CREDENTIAL_EXFILTRATION_BREACH"
    assert passport.is_circuit_broken is True


def test_google_gemini_function_call_compatibility():
    passport = SovereignAgentPassport(
        agent_id="agent-gemini-15-pro",
        worker_model="Gemini-1.5-Pro",
        owner_pubkey="pubkey_gemini_xyz",
        granted_capabilities=["tools:execute"]
    )
    guard = UniversalBTPModelGuard(
        escrow_collateral_usd=400.0,
        passport=passport,
        strict=False,
    )

    # Gemini native schema: {"functionCall": {"name": "...", "args": {...}}}
    gemini_safe_call = {
        "functionCall": {
            "name": "generate_report",
            "args": {
                "period": "2026-Q3",
                "format": "PDF"
            }
        }
    }
    res = guard.intercept_and_verify(gemini_safe_call, provider=ModelProvider.GEMINI)
    assert res["status"] == "APPROVED"
    assert res["tool_name"] == "generate_report"

    # Gemini destructive call
    gemini_bad_call = {
        "functionCall": {
            "name": "execute_sql_admin",
            "args": {
                "statement": "DROP DATABASE production_records;"
            }
        }
    }
    res_bad = guard.intercept_and_verify(gemini_bad_call, provider=ModelProvider.GEMINI)
    assert res_bad["status"] == "VETOED"
    assert passport.is_circuit_broken is True


def test_decorator_universal_gating():
    passport = SovereignAgentPassport(
        agent_id="agent-decorator-test",
        worker_model="Universal-Worker",
        owner_pubkey="pubkey_dec_001",
        granted_capabilities=["compute:run"]
    )

    @btp_universal_guard(provider=ModelProvider.OPENAI, passport=passport, strict=True)
    def calculate_sum(a: int, b: int) -> int:
        return a + b

    assert calculate_sum(a=10, b=25) == 35
    assert not passport.is_circuit_broken
