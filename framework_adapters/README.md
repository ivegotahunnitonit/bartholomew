# BTP v5.4.6 Framework Adapters & Middleware
### Drop-in In-Process Tool Execution Guards, Cryptographic Gating & Bilateral Barter for Autonomous Swarms

This directory contains standalone integration adapters for autonomous agent frameworks:

1. **CrewAI:** [`framework_adapters/crewai/crewai_btp_task_guard.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/framework_adapters/crewai/crewai_btp_task_guard.py)
   * Tool execution decorator (`@btp_crewai_tool`) and task-level boundary (`CrewAIBTPTaskGuard`).
   * Automated Attested Work Unit (AWU) minting on clean tool execution (`mint_awu`).
   * Bilateral cross-swarm task delegation (`delegate_task`) with Ed25519 escrow receipts.
2. **LangGraph & LangChain:** [`framework_adapters/langgraph/langgraph_btp_guard.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/framework_adapters/langgraph/langgraph_btp_guard.py)
   * Tool execution wrapper (`@btp_langchain_tool`, `BartholomewLangChainTool`) and node boundary (`LangGraphBTPGuard`).
   * Sub-35us AST evaluation (`rm -rf`, `DROP TABLE`, secret exfiltration, spend cap checks).
   * Automated AWU surplus minting (`mint_awu`) and cross-swarm task delegation (`delegate_task`).
3. **Microsoft AutoGen:** [`framework_adapters/autogen/autogen_btp_interceptor.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/framework_adapters/autogen/autogen_btp_interceptor.py)
   * Conversational message interceptor (`AutoGenBTPInterceptor`) and tool wrapper (`@btp_autogen_guard`) filtering toxic tool dispatches across multi-agent group chats.
4. **LlamaIndex:** [`framework_adapters/llamaindex/llamaindex_btp_tool.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/framework_adapters/llamaindex/llamaindex_btp_tool.py)
   * Query-engine and function-tool gating interceptor (`@btp_llamaindex_tool`).

---

## Key Guarantees
* **Sub-35 Microsecond Latency:** In-process AST parsing and regex heuristic screening execute in microsecond timeframes without blocking async event loops.
* **Bilateral Barter & AWU Economy:** Autonomous agents mint Attested Work Units into the global Merkle surplus ledger upon clean tool execution, enabling decentralized compute barter.
* **100% Offline Verifiability:** Cryptographic validation relies on RFC 8785 JSON Canonicalization and FIPS 186-5 Ed25519 signatures with zero external API dependencies.
* **Non-Invasive Pass-Through:** Clean exception signaling (`[BTP-VETO]`) with native rollback handling.

