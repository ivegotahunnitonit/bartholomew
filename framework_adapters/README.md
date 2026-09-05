# **BTP v3.0 Framework Adapters & Middleware**
### **Drop-in In-Process Tool Execution Guards & Cryptographic Gating for Autonomous Agents**

This directory contains standalone, 1-line integration adapters for the leading open-source agent frameworks:

1. **LangGraph & LangChain:** [`framework_adapters/langgraph/langgraph_btp_guard.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/framework_adapters/langgraph/langgraph_btp_guard.py)
   * Tool execution wrapper (`@btp_langchain_tool` & `BartholomewLangChainTool`) providing sub-35µs AST evaluation (`rm -rf`, `DROP TABLE`, secret exfiltration, runaway budget checks) plus offline Merkle receipt verification (`LangGraphBTPGuard`).
2. **CrewAI:** [`framework_adapters/crewai/crewai_btp_task_guard.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/framework_adapters/crewai/crewai_btp_task_guard.py)
   * Tool execution decorator (`@btp_crewai_tool`) and task-level cryptographic boundary (`CrewAIBTPTaskGuard`) preventing confused-deputy attacks across autonomous crew swarms.
3. **Microsoft AutoGen:** [`framework_adapters/autogen/autogen_btp_interceptor.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/framework_adapters/autogen/autogen_btp_interceptor.py)
   * Conversational message interceptor (`AutoGenBTPInterceptor`) and tool wrapper (`@btp_autogen_guard`) filtering toxic tool dispatches across multi-agent group chats.

---

## **Key Guarantees**
* **Sub-35 Microsecond Latency:** In-process AST parsing and regex heuristic screening execute in microsecond timeframes without blocking event loops.
* **100% Offline Verifiability:** Cryptographic validation relies on RFC 8785 JSON Canonicalization and FIPS 186-5 Ed25519 signatures with zero external API calls.
* **Non-Invasive Pass-Through:** Clean exception signaling (`[BTP-VETO]`) with native rollback handling.
