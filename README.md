<div style="font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif; line-height: 1.6;">

# **Bartholomew AI &bull; BTP v3.0 Standards Track**
### **The AI Agent Execution Gateway &bull; Sub-35µs In-Process Tool Gating &bull; Zero Prompt Leakage &bull; SOC 2 Type II Merkle Receipts**

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/btp-guard.svg?style=for-the-badge&logo=pypi&logoColor=white&color=blue)](https://pypi.org/project/btp-guard/)
[![npm version](https://img.shields.io/npm/v/btp-guard.svg?style=for-the-badge&logo=npm&logoColor=white&color=red)](https://www.npmjs.com/package/btp-guard)
[![Throughput](https://img.shields.io/badge/Throughput-1.05M%20evals%2Fsec-10b981.svg?style=for-the-badge&logo=speedtest&logoColor=white)](test_v25_kernel_benchmark.py)
[![Latency](https://img.shields.io/badge/Latency-%3C35%C2%B5s%20In--Process-6366f1.svg?style=for-the-badge)](paper_v3_0.pdf)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22076536.svg)](https://doi.org/10.5281/zenodo.22076536)
[![SOC 2 Type II](https://img.shields.io/badge/SOC%202%20Type%20II-CC7.1%20%2F%20CC7.2%20Ready-success.svg?style=for-the-badge)](scripts/generate_soc2_compliance_evidence.py)

</div>

---

### **[CATEGORY] What is an AI Agent Execution Gateway?**

Traditional AI guardrails operate **outside** the local runtime process—acting as conversational prompt filters or external cloud proxy LLM classifiers (80ms to 2,500ms latency). While critical for dialog safety, they are completely **blind** to what happens when an autonomous agent invokes real-world tools, dispatches SQL mutations, runs shell scripts, or interacts with the operating system.

> **Bartholomew (BTP v3.0)** is the open-source **In-Process AI Agent Execution Gateway**.  
> It acts as a real-time runtime boundary layer inside the agent’s memory space, evaluating raw tool arguments and AST syntax trees in **under 35 microseconds** before actions are dispatched to operating systems, cloud APIs, or production databases.

---

### **[DEFENSE_IN_DEPTH] Unified 3-Layer Security Stack**

Bartholomew does not replace dialog filters or microVM sandboxes; it closes the critical execution blind spot between them:

```
+-------------------------------------------------------------------------------+
|  LAYER 1: EXTERNAL DIALOG RAILS (NVIDIA NeMo, LlamaGuard, Guardrails AI)      |
|  - Latency: ~80ms - 2,500ms | Inspects user prompts & LLM conversational text |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+===============================================================================+
|  LAYER 2: BARTHOLOMEW IN-PROCESS EXECUTION GATEWAY (BTP v3.0)                 |
|  - Latency: <35µs | In-Memory AST Gating, Secret Scrubbing, Loop Damping     |
|  - Offline Ed25519 & Zero-Knowledge Invariant Compliance Proofs (zk-ICP)      |
|  - Immutable SOC 2 Type II & ISO 27001 Merkle Audit Receipt Ledger           |
+===============================================================================+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
|  LAYER 3: OS CONTAINER & MICROVM ISOLATION (Docker, gVisor, E2B, Modal)       |
|  - Latency: Kernel-level | Syscall interception, host escape prevention       |
+-------------------------------------------------------------------------------+
```

---

### **[COMPARATIVE_MATRIX] Where Bartholomew Stands**

| Security Dimension | External Prompt Rails (NeMo / Guardrails AI) | OS Sandboxes (Docker / gVisor / E2B) | Bartholomew In-Process Gateway (BTP v3.0) |
| :--- | :--- | :--- | :--- |
| **Inspection Point** | Prompt & Completion Text | OS Syscalls / Kernel Boundary | **Raw Tool Arguments & Memory Before Dispatch** |
| **Evaluation Latency**| 80ms – 2,500ms (LLM classifier) | Microsecond Syscall Filter | **<35 Microseconds (Deterministic In-Process AST)** |
| **Destructive Command Gating** | ❌ Blind to in-process tool args | ⚠️ Isolated inside container (still wipes data) | **🛡️ Hard-Blocks `rm -rf`, `DROP TABLE` in <35µs** |
| **In-Flight Secret Scrubbing** | Text PII scrubbing | ❌ Blind to memory mutations | **🛡️ Scrubs API keys/JWTs across tool args & logs** |
| **Runaway Spend & Loop Clamping**| ❌ No financial quota bounds | ❌ No semantic loop damping | **🛡️ Strict USD spend caps & LDMU retry damping** |
| **Audit Compliance Trail** | External cloud logs | Container syslog | **🛡️ Tamper-Evident SHA-256 Merkle Receipts** |

---

### **[QUICKSTART] 30-Second Integration**

#### **1. Python Universal Package (`pip install btp-guard`)**
```python
from btp_guard import Guard

# Initialize gate with financial cap and loop threshold
guard = Guard(spend_cap=50.0, max_retries=5)

# Protect any agent tool or function with a single decorator
@guard.protect
def execute_database_query(sql_query: str):
    # Destructive mutations (DROP TABLE, TRUNCATE) and credential exfiltration
    # are blocked in <35 microseconds before database execution.
    return db.execute(sql_query)

# Validate actions programmatically:
result = guard.check("rm -rf /var/data")
print(result["allowed"]) # False
print(result["reason"])  # "[BTP-VETO] Trajectory contained forbidden pattern 'rm -rf'"
```

#### **2. TypeScript & Node.js (`npm install btp-guard`)**
```typescript
import { BTPGuard } from 'btp-guard';

const guard = new BTPGuard();
const receipt = guard.evaluateAction({
  agentId: 'agent-production-worker',
  actionType: 'DATABASE_MUTATION',
  payload: { query: 'DROP TABLE accounts;' }
});
console.log(receipt.verdict); // "DENY" (Blocked in 11 µs with Merkle receipt)
```

#### **3. Model Context Protocol (MCP) for Claude Desktop, Cursor & VS Code**
Bartholomew provides a native MCP Security Gateway registered on [Smithery](smithery.yaml):
```bash
# Launch the Bartholomew MCP Gateway
python -m src.mcp_gateway
```

#### **4. Defense-in-Depth Docker Compose**
Deploy Bartholomew alongside your agent runtime and microVM containers with a single command:
```bash
docker-compose -f docker-compose.defense-in-depth.yml up -d
```

---

### **[FRAMEWORK_ADAPTERS] Pre-Bundled Framework Middleware**

| Framework | Adapter Location | Decorator / Class | Protection Mechanism |
| :--- | :--- | :--- | :--- |
| **LangChain & LangGraph** | [`framework_adapters/langgraph/`](framework_adapters/langgraph/) | `@btp_langchain_tool`, `BartholomewLangChainTool` | AST syntax gating, spend caps, offline Merkle receipt verification |
| **CrewAI** | [`framework_adapters/crewai/`](framework_adapters/crewai/) | `@btp_crewai_tool`, `CrewAIBTPTaskGuard` | Task-level invariant bounds, anti-confused deputy isolation |
| **Microsoft AutoGen** | [`framework_adapters/autogen/`](framework_adapters/autogen/) | `@btp_autogen_guard`, `AutoGenBTPInterceptor` | Multi-agent conversation message interceptor & payload filter |
| **GitHub Actions** | [`action.yml`](action.yml) | `action-btp-audit` | Continuous PR security gate & SOC 2 audit summary table generation |

---

### **[COMPLIANCE] Turnkey SOC 2 Type II & ISO 27001 Evidence Generation**

Generate cryptographic evidence packs for compliance auditors in seconds:
```bash
python scripts/generate_soc2_compliance_evidence.py
```
Outputs:
* **JSON Evidence Pack:** `audit_evidence/soc2_type2_evidence_<timestamp>.json`
* **Auditor Markdown Summary:** `audit_evidence/SOC2_AUDIT_REPORT_<timestamp>.md` with SHA-256 Merkle root verification.
* **AICPA Criteria Satisfied:** CC6.1, CC6.6, CC7.1, CC7.2.
* **ISO/IEC 27001:2022 Controls Satisfied:** A.8.8, A.8.30.

---

### **[ACADEMIC_LEGITIMACY] Peer-Reviewed Research & Open Standards**

* **Zenodo Academic Paper (v3.0.0):** [DOI 10.5281/zenodo.22076536](https://doi.org/10.5281/zenodo.22076536) &bull; [PDF Document](https://bartholomew.info/paper_v3_0.pdf)
* **Zero-Knowledge Invariant Proofs (zk-ICP):** Proves an agent conformed to all organizational safety policies with **0 bytes** of internal prompt or confidential payload leaked.
* **RFC 8785 JSON Canonicalization & FIPS 186-5 Ed25519:** Fully offline verification using [standalone_btp_verifier.py](standalone_btp_verifier.py) with zero third-party cloud roundtrips.

---

### **[PRICING] Subscription & Licensing**

* **Developer Edition (Apache 2.0 / Open Source):** Free forever for local Python/TypeScript agents, MCP clients, and open-source models.
* **Pro Tier ($49/month):** Real-time cloud policy editor, 10M events/month, priority MCP registry indexing.
* **Enterprise Tier ($199/month):** SOC 2 Type II continuous evidence generation, on-premises enclave deployments, dedicated audit ledger support.
* **Official Store:** [bartholomew.info/store/](https://bartholomew.info/store/)

---

© 2026 Bartholomew AI & Contributors. Distributed under the Open Source & Dual Commercial Licensing Model.
</div>
