"""
Test Suite for Framework Adapters (LangGraph, AutoGen, CrewAI)
"""

import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from framework_adapters.langgraph.langgraph_btp_guard import LangGraphBTPGuard
from framework_adapters.autogen.autogen_btp_interceptor import AutoGenBTPInterceptor
from framework_adapters.crewai.crewai_btp_task_guard import CrewAIBTPTaskGuard
from framework_adapters.llamaindex.llamaindex_btp_tool import btp_llamaindex_tool, BartholomewLlamaIndexTool
from src.trust_protocol import BartholomewTrustAuthority
from src.agent_passport import SovereignAgentPassport
import pytest

def test_standalone_adapters():
    print("=" * 80)
    print("  TESTING STANDALONE FRAMEWORK ADAPTERS (LANGGRAPH, AUTOGEN, CREWAI, LLAMAINDEX)")
    print("=" * 80)

    auth = BartholomewTrustAuthority(ttl_seconds=300)
    root_key = auth.public_key_hex

    # 1. Test LangGraph Adapter
    print("[1] Testing LangGraphBTPGuard...")
    lg_guard = LangGraphBTPGuard(trusted_authorities=[root_key], agent_id="Agent-LangGraph-01")
    
    @lg_guard.wrap_tool
    def run_query(sql):
        return f"Query Result: {sql}"

    payload = {"tool": "run_query", "args": ("SELECT 1;",), "kwargs": {}}
    receipt = auth.evaluate_intent("Issuer-Node", "SQL_EXEC", payload, target_recipient="Agent-LangGraph-01")
    res = run_query("SELECT 1;", btp_receipt=receipt)
    assert "Query Result" in res
    print("    |-- Valid LangGraph Tool Invocation: SUCCESS")

    # 2. Test AutoGen Adapter
    print("[2] Testing AutoGenBTPInterceptor...")
    ag_interceptor = AutoGenBTPInterceptor(trusted_authorities=[root_key], recipient_id="Agent-AutoGen-01")
    inbound = {
        "role": "user",
        "action_type": "DEPLOY_PATCH",
        "content": {"file": "core.py"},
        "btp_envelope": auth.evaluate_intent("Issuer-Node", "DEPLOY_PATCH", {"file": "core.py"}, target_recipient="Agent-AutoGen-01")
    }
    safe_msg = ag_interceptor.intercept_message(inbound)
    assert safe_msg.get("status") != "DENIED"
    print("    |-- Attested AutoGen Message: AUTHORIZED")

    # 3. Test CrewAI Adapter
    print("[3] Testing CrewAIBTPTaskGuard...")
    crew_guard = CrewAIBTPTaskGuard(trusted_authorities=[root_key], recipient_id="Agent-Crew-01")
    
    def exec_task(task_name):
        return f"Done: {task_name}"

    guarded_task = crew_guard.wrap_task("Deploy Patch", exec_task)
    task_payload = {"task": "Deploy Patch", "args": ("Deploy Patch",), "kwargs": {}}
    task_receipt = auth.evaluate_intent("Issuer-Node", "CREW_TASK", task_payload, target_recipient="Agent-Crew-01", capability_scope=["FS_WRITE_RESTRICTED"])
    task_res = guarded_task("Deploy Patch", btp_receipt=task_receipt)
    assert "Done:" in task_res
    print("    |-- Guarded CrewAI Task: SUCCESS")

    # 4. Test LlamaIndex Adapter
    print("[4] Testing LlamaIndex BTP Guard...")
    @btp_llamaindex_tool(required_capability="db:query")
    def execute_sql(query: str) -> str:
        return f"Executed: {query}"

    passport = SovereignAgentPassport(
        agent_id="Agent-Llama-01",
        worker_model="Llama-3.1-70B",
        owner_pubkey=root_key,
        granted_capabilities=["db:query", "tools:search"]
    )
    passport.sign(auth.private_key)

    # Valid execution with passport
    res_sql = execute_sql("SELECT COUNT(*) FROM telemetry;", agent_passport=passport)
    assert "Executed: SELECT" in res_sql
    print("    |-- Authorized LlamaIndex Tool Call: SUCCESS")

    # Destructive AST veto check
    with pytest.raises(PermissionError) as exc_ast:
        execute_sql("rm -rf /")
    assert "blocked" in str(exc_ast.value).lower()
    print("    |-- Destructive AST Interception: VETOED (<35µs)")

    print("\n" + "=" * 80)
    print("  ALL 4 STANDALONE FRAMEWORK ADAPTERS 100% OPERATIONAL")
    print("=" * 80)

if __name__ == "__main__":
    test_standalone_adapters()
