# BTP Guard — Framework Cookbooks & Developer Templates

Zero-configuration, production-ready examples integrating Bartholomew Trust Protocol (`btp-guard`) into the four leading autonomous agent frameworks:

| Framework | Adapter Pattern | Security Invariants Enforced | Runnable Recipe |
| :--- | :--- | :--- | :--- |
| **CrewAI** | `CrewAIBTPTaskGuard` | Ed25519 Task Attestation, Credential Leak Shield, FS Isolation | [`examples/crewai_secure_coding_swarm/run_swarm.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/examples/crewai_secure_coding_swarm/run_swarm.py) |
| **LangGraph** | `LangGraphBTPGuard` | Node Execution Gating, Payload Tamper Resistance, Data Exfil Prevention | [`examples/langgraph_financial_analyst/run_workflow.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/examples/langgraph_financial_analyst/run_workflow.py) |
| **AutoGen** | `AutoGenBTPInterceptor` | Peer Message Validation, Threat Entropy Spikes, Dynamic Threshold Rebalancing | [`examples/autogen_multiagent_defense/run_groupchat.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/examples/autogen_multiagent_defense/run_groupchat.py) |
| **LlamaIndex** | `@btp_llamaindex_tool` | Sub-35µs AST Interception, Sovereign Agent Passports, Indirect Injection Veto | [`examples/llamaindex_rag_guard/run_rag.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/examples/llamaindex_rag_guard/run_rag.py) |

---

## 60-Second Quickstart

### 1. CrewAI Secure Coding Swarm
Wrap any CrewAI task execution logic to enforce cryptographic attestation:
```python
from framework_adapters.crewai.crewai_btp_task_guard import CrewAIBTPTaskGuard

guard = CrewAIBTPTaskGuard(trusted_authorities=[ROOT_KEY], recipient_id="Coder-01")
guarded_task = guard.wrap_task("build_task", my_build_function)

# Invariant violation (e.g. cat /etc/shadow or unauthorized FS write) is vetoed
guarded_task(task_args, btp_receipt=receipt)
```
Run the demo:
```bash
python examples/crewai_secure_coding_swarm/run_swarm.py
```

---

### 2. LangGraph Financial State Nodes
Protect LangGraph tool and node functions from unauthorized caller tampering:
```python
from framework_adapters.langgraph.langgraph_btp_guard import LangGraphBTPGuard

guard = LangGraphBTPGuard(trusted_authorities=[ROOT_KEY], agent_id="Financial-Node-01")

@guard.wrap_tool
def query_ledger(account_id: str, limit: int = 10):
    return db.query(...)
```
Run the demo:
```bash
python examples/langgraph_financial_analyst/run_workflow.py
```

---

### 3. AutoGen Multi-Agent GroupChat Defense
Intercept messages between peer agents and automatically elevate consensus quorums (`2-of-3` $\to$ `3-of-5` $\to$ `5-of-7`) when threat entropy rises:
```python
from framework_adapters.autogen.autogen_btp_interceptor import AutoGenBTPInterceptor
from src.ebpf_kernel_guard import DynamicThresholdRebalancer

interceptor = AutoGenBTPInterceptor(trusted_authorities=[ROOT_KEY], recipient_id="Manager-01")
rebalancer = DynamicThresholdRebalancer(baseline_threshold=2, baseline_total=3)

# Filter messages and auto-escalate threshold when attacks are detected
verified_message = interceptor.intercept_message(inbound_msg)
```
Run the demo:
```bash
python examples/autogen_multiagent_defense/run_groupchat.py
```

---

### 4. LlamaIndex RAG Query Engine Guard
Attach sovereign agent passports and intercept prompt injections at the AST layer in under 35 microseconds:
```python
from framework_adapters.llamaindex.llamaindex_btp_tool import btp_llamaindex_tool

@btp_llamaindex_tool(required_capability="rag:query_index")
def query_docs(query_str: str) -> str:
    return index.as_query_engine().query(query_str)
```
Run the demo:
```bash
python examples/llamaindex_rag_guard/run_rag.py
```
