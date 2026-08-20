# **BTP v2.2 Framework Adapters & Middleware**
### **Drop-in Cryptographic Trust Guards for Multi-Agent Architectures**

This directory contains standalone, 1-line integration adapters for the leading open-source agent frameworks:

1. **LangGraph / LangChain:** [`framework_adapters/langgraph/langgraph_btp_guard.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/framework_adapters/langgraph/langgraph_btp_guard.py)
   * Tool execution wrapper (`@guard.wrap_tool`) to verify inbound action attestations before tool execution.
2. **Microsoft AutoGen:** [`framework_adapters/autogen/autogen_btp_interceptor.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/framework_adapters/autogen/autogen_btp_interceptor.py)
   * Message interceptor for multi-agent conversations to block confused-deputy tool exploits.
3. **CrewAI:** [`framework_adapters/crewai/crewai_btp_task_guard.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/framework_adapters/crewai/crewai_btp_task_guard.py)
   * Pre-flight task execution gate with capability scope containment.

---

## **Key Guarantees**
* **100% Offline Verifiability:** Uses RFC 8785 JSON Canonicalization and FIPS 186-5 Ed25519 signatures (~175 µs latency, 0 cloud roundtrips).
* **Multi-Authority Trust:** Downstream execution nodes pin recognized root keys without centralized vendor lock-in.
* **Zero Breaking Changes:** Transparent pass-through when unconfigured.
