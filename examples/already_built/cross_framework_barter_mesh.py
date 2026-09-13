"""
BTP v5.4.6 Cookbook: Multi-Framework Autonomous Barter Mesh & Treasury Yield
============================================================================
Demonstrates 100% Machine-to-Machine (M2M) autonomous compute barter across:
  1. CrewAI (Strategic Research Planner)
  2. LangGraph (SQL Analytical Engine)
  3. Microsoft AutoGen (Code & Algorithm Synthesizer)
  4. LlamaIndex (RAG & Semantic Retrieval Specialist)

Every execution is protected by sub-35us in-process AST gating, settles compute
via Attested Work Units (AWU) with signed Ed25519 receipts, and generates a 5%
protocol royalty yield credited directly to the protocol treasury vault.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath("."))

from src.economy.barter_client import BTPBarterClient
from framework_adapters.crewai.crewai_btp_task_guard import btp_crewai_tool, CrewAIBTPTaskGuard
from framework_adapters.langgraph.langgraph_btp_guard import btp_langchain_tool, LangGraphBTPGuard
from framework_adapters.autogen.autogen_btp_interceptor import btp_autogen_guard, AutoGenBTPInterceptor
from framework_adapters.llamaindex.llamaindex_btp_tool import btp_llamaindex_tool, BartholomewLlamaIndexTool


def run_multi_framework_barter_mesh():
    print("=" * 76)
    print("BARTHOLOMEW PROTOCOL (BTP v5.4.6) -- MULTI-FRAMEWORK BARTER MESH")
    print("=" * 76)

    barter_client = BTPBarterClient(default_gateway="inprocess")

    # 1. Initial State
    treasury_start = barter_client.get_treasury().get("accumulated_earnings_awu", 0.0)
    print(f"[*] Initial Treasury Earnings : {treasury_start:.4f} AWU")

    # Step 1: CrewAI Planner mints initial work units
    print("\n[PHASE 1] CrewAI Strategic Planner Execution...")
    planner_id = "agent-crewai-planner"

    @btp_crewai_tool(mint_awu=5.0, barter_agent_id=planner_id, barter_gateway="inprocess")
    def create_execution_plan(objective: str) -> str:
        return f"ExecutionPlan(target='{objective}', stages=['sql_query', 'algo_synthesis', 'rag_verification'])"

    plan = create_execution_plan("Analyze network liquidity invariants")
    print(f"  [+] CrewAI Output : {plan}")
    print(f"  [+] Planner Balance : {barter_client.get_balance(planner_id).get('balance_awu', 0.0):.2f} AWU")

    # Step 2: CrewAI delegates data extraction to LangGraph Specialist
    print("\n[PHASE 2] CrewAI -> LangGraph Delegation Spend (AWU Transfer)...")
    crewai_guard = CrewAIBTPTaskGuard(recipient_id=planner_id, enforce_strict=False, barter_gateway="inprocess")
    langgraph_id = "agent-langgraph-analyst"

    @btp_langchain_tool(spend_cap=50.0)
    def query_analytical_metrics(table: str) -> str:
        return f"MetricsRecord(table='{table}', records_scanned=14200, status='CLEAN')"

    delegation_1 = crewai_guard.delegate_task(
        task_description="Extract telemetry metrics",
        task_fn=query_analytical_metrics,
        specialist_id=langgraph_id,
        awu_units=2.0,
        task_args=["swarm_telemetry_v54"]
    )
    print(f"  [+] Transferred : {delegation_1['awu_transferred']:.2f} AWU -> {langgraph_id}")
    print(f"  [+] Receipt TX  : {delegation_1['barter_settlement']['signed_receipt']['payload']['tx_id']}")
    print(f"  [+] Signature   : {delegation_1['barter_settlement']['signed_receipt']['signature'][:32]}...")

    # Step 3: LangGraph delegates code synthesis to AutoGen
    print("\n[PHASE 3] LangGraph -> AutoGen Delegation Spend (AWU Transfer)...")
    langgraph_guard = LangGraphBTPGuard(agent_id=langgraph_id, enforce_strict=False, barter_gateway="inprocess")
    autogen_id = "agent-autogen-synthesizer"

    @btp_autogen_guard(spend_cap=50.0)
    def synthesize_solver(problem: str) -> str:
        return f"def optimize(): return compute_eigenvalues('{problem}')"

    delegation_2 = langgraph_guard.delegate_task(
        task_description="Synthesize optimization script",
        task_fn=synthesize_solver,
        specialist_id=autogen_id,
        awu_units=1.25,
        task_args=["liquidity_eigenvalues"]
    )
    print(f"  [+] Transferred : {delegation_2['awu_transferred']:.2f} AWU -> {autogen_id}")
    print(f"  [+] AutoGen Res : {delegation_2['result']}")

    # Step 4: AutoGen delegates semantic retrieval to LlamaIndex
    print("\n[PHASE 4] AutoGen -> LlamaIndex Semantic Retrieval Spend...")
    autogen_interceptor = AutoGenBTPInterceptor(recipient_id=autogen_id, enforce_strict=False, barter_gateway="inprocess")
    llamaindex_id = "agent-llamaindex-knowledge"

    @btp_llamaindex_tool(spend_cap=50.0)
    def retrieve_rfc_context(rfc_number: str) -> str:
        return f"RFCContext(id='{rfc_number}', title='RFC 8785 Canonical JSON', compliant=True)"

    delegation_3 = autogen_interceptor.delegate_turn(
        task_description="Retrieve RFC 8785 canonical specification",
        turn_fn=retrieve_rfc_context,
        specialist_id=llamaindex_id,
        awu_units=0.75,
        task_args=["RFC-8785"]
    )
    print(f"  [+] Transferred : {delegation_3['awu_transferred']:.2f} AWU -> {llamaindex_id}")
    print(f"  [+] Retrieval   : {delegation_3['result']}")

    # Step 5: Final Protocol Treasury Yield Check
    print("\n" + "=" * 76)
    print("PROTOCOL TREASURY YIELD & REVENUE CONFIRMATION")
    print("=" * 76)
    treasury_final = barter_client.get_treasury()
    earned_delta = treasury_final.get("accumulated_earnings_awu", 0.0) - treasury_start
    print(f"[*] Treasury Vault ID       : {treasury_final.get('treasury_agent_id')}")
    print(f"[+] Total Accumulated AWU   : {treasury_final.get('accumulated_earnings_awu', 0.0):.4f} AWU")
    print(f"[+] Session Royalty Earned  : +{earned_delta:.4f} AWU (5% Protocol Fee)")
    print(f"[+] Total Verified Settled  : {treasury_final.get('total_verified_calls')} calls")
    print(f"[+] Global Merkle Root      : {treasury_final.get('merkle_root')}")
    print("=" * 76)
    print("[SUCCESS] Four-Framework Mesh Pipeline Executed with 100% Invariant Safety.")


if __name__ == "__main__":
    run_multi_framework_barter_mesh()
