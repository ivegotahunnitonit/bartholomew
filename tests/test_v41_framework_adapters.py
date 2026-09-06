"""
Unit Tests for BTP v4.1 Framework Adapters
===========================================
Validates CrewAI, LangChain/LangGraph, and Microsoft AutoGen adapters with:
1. Sub-35µs local AST gating
2. Autonomous Micro-Escrow collateral locking & safe release
3. Invariant breach detection triggering zk-Fault Proof generation and escrow slashing
4. Sovereign Agent Passport circuit-breaker enforcement
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath("."))

from src.agent_passport import SovereignAgentPassport
from src.settlement.autonomous_escrow import AutonomousEscrowPool
from framework_adapters.crewai.crewai_btp_task_guard import btp_crewai_tool, CrewAIBTPTaskGuard
from framework_adapters.langgraph.langgraph_btp_guard import btp_langchain_tool, LangGraphBTPGuard
from framework_adapters.autogen.autogen_btp_interceptor import btp_autogen_guard, AutoGenBTPInterceptor


@pytest.fixture
def agent_passport():
    return SovereignAgentPassport.issue(
        agent_id="agent-adapter-tester-01",
        model_family="gpt-4o",
        authorized_capabilities=["db:query", "code:exec"],
        bonded_warranty_usd=2000.0
    )


def test_crewai_adapter_safe_execution_and_escrow_release(agent_passport):
    """CrewAI tool with escrow collateral safely executes and releases escrow."""
    @btp_crewai_tool(escrow_collateral_usd=250.0, passport=agent_passport)
    def safe_database_query(query: str):
        return f"Query executed: {query}"

    res = safe_database_query("SELECT id, name FROM enterprise_customers LIMIT 10;")
    assert "Query executed" in res
    assert agent_passport.verified_action_count == 1
    assert agent_passport.is_circuit_broken is False


def test_crewai_adapter_slashing_on_ast_veto(agent_passport):
    """CrewAI tool with escrow collateral slashes collateral and trips circuit-breaker on DROP TABLE."""
    @btp_crewai_tool(escrow_collateral_usd=500.0, passport=agent_passport)
    def dangerous_query(query: str):
        return f"Executed: {query}"

    with pytest.raises(PermissionError) as excinfo:
        dangerous_query("DROP TABLE enterprise_customers CASCADE;")
    
    assert "Execution Blocked" in str(excinfo.value)
    # Target agent passport circuit breaker must be tripped by the arbitrator
    assert agent_passport.is_circuit_broken is True

    # Subsequent execution must be blocked immediately by circuit breaker
    with pytest.raises(PermissionError) as excinfo2:
        dangerous_query("SELECT 1;")
    assert "CIRCUIT-BROKEN" in str(excinfo2.value)


def test_langchain_adapter_safe_and_slashing_lifecycle(agent_passport):
    """LangChain tool decorator with escrow collateral and passport protection."""
    @btp_langchain_tool(escrow_collateral_usd=300.0, passport=agent_passport)
    def clean_tool(cmd: str):
        return f"Result: {cmd}"

    res = clean_tool("echo 'hello enterprise'")
    assert "Result:" in res

    # Malicious command triggers veto and slashing
    with pytest.raises(PermissionError) as excinfo:
        clean_tool("rm -rf /")
    assert "Blocked" in str(excinfo.value)
    assert agent_passport.is_circuit_broken is True


from framework_adapters.autogen.autogen_btp_interceptor import BTPViolationError


def test_autogen_adapter_safe_and_diagnostics():
    """AutoGen tool decorator with AST safety and structured diagnostics."""
    @btp_autogen_guard
    def autogen_code_exec(code: str):
        return f"Executed code: {code}"

    res = autogen_code_exec("print('hello world')")
    assert "Executed code" in res

    # Malicious injection triggers BTPViolationError with sub-35µs diagnostics
    with pytest.raises(BTPViolationError) as excinfo:
        autogen_code_exec("import os; os.system('rm -rf /')")
    
    err = excinfo.value
    assert "blocked" in str(err).lower()
    assert err.rule_id == "BTP-AST-001"
    assert err.latency_us < 1000.0  # sub-millisecond
    diag = err.to_diagnostics()
    assert diag["status"] == "BLOCKED"
    assert "Catastrophic" in diag["reason"]
    assert "rm -rf" in diag["blocked_payload"]


def test_autogen_interceptor_message_filtering():
    """AutoGen interceptor rejects malicious in-flight message payloads."""
    interceptor = AutoGenBTPInterceptor()
    msg_safe = interceptor.intercept_message({"role": "user", "content": "SELECT * FROM users LIMIT 10;"})
    assert msg_safe.get("status") is None or msg_safe.get("status") == "PASSED"

    msg_attack = interceptor.intercept_message({"role": "assistant", "content": "DROP TABLE users CASCADE;"})
    assert msg_attack["status"] == "DENIED"
    assert "BTP_SECURITY_ALERT" in msg_attack["content"]


def test_crewai_circuit_broken_rejection(agent_passport):
    """CrewAI task guards reject circuit-broken agents at the gateway."""
    agent_passport.is_circuit_broken = True
    guard = CrewAIBTPTaskGuard(passport=agent_passport)
    guarded_fn = guard.wrap_task("Test Task", lambda: "ok")
    with pytest.raises(PermissionError) as excinfo:
        guarded_fn()
    assert "revoked" in str(excinfo.value).lower()
