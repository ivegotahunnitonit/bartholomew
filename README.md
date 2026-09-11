<div style="font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif; line-height: 1.6;">

> **Need SOC 2 Type II Audit Trails & Multi-Agent Fleet Management?** [Try Bartholomew Cloud &rarr; https://bartholomew.info/cloud](https://bartholomew.info/cloud) (Pro: $49/mo &bull; Enterprise Fleet: $199/mo &bull; Centralized Fleet Control Plane).

# **Bartholomew AI &bull; BTP v5.4 Standards Track**
### **The AI Agent Execution Gateway &bull; Sub-35µs In-Process Tool Gating &bull; Zero Prompt Leakage &bull; SOC 2 Type II Merkle Receipts**

<div align="center">

[![Pro Tier](https://img.shields.io/badge/Bartholomew%20Pro-%2449%2Fmo-10b981?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/fZu28rbNz5TYcmAddK9R600)
[![Enterprise Tier](https://img.shields.io/badge/Enterprise-%24199%2Fmo-6366f1?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/fZu14ng3PgyC9ao2z69R601)
[![PyPI version](https://img.shields.io/pypi/v/btp-guard.svg?style=for-the-badge&logo=pypi&logoColor=white&color=blue)](https://pypi.org/project/btp-guard/)
[![npm version](https://img.shields.io/npm/v/btp-guard.svg?style=for-the-badge&logo=npm&logoColor=white&color=red)](https://www.npmjs.com/package/btp-guard)
[![Open VSX](https://img.shields.io/badge/Open%20VSX-750%2B%20Downloads-8957e5.svg?style=for-the-badge&logo=visualstudiocode&logoColor=white)](https://open-vsx.org/extension/Bartholomew/bartholomew-guard-vscode)
[![Interactive Playground](https://img.shields.io/badge/Playground-Sub--35%C2%B5s%20AST-blueviolet.svg?style=for-the-badge)](https://bartholomew.info/cookbook)
[![Tests](https://img.shields.io/badge/Tests-2%2C723%20Passed%20(100%25)-success.svg?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![Universal Cookbook](https://img.shields.io/badge/Cookbook-All%203%20Horizons%20%2B%20IDEs-orange.svg?style=for-the-badge)](COOKBOOK.md)
[![Live Explorer](https://img.shields.io/badge/Web%20Explorer-Live-10b981.svg?style=for-the-badge&logo=firebase&logoColor=white)](https://bartholomew.info)
[![GitHub Action](https://img.shields.io/badge/GitHub%20Action-v5.4.4-2088FF.svg?style=for-the-badge&logo=githubactions&logoColor=white)](action.yml)
[![Throughput](https://img.shields.io/badge/Throughput-1.05M%20evals%2Fsec-10b981.svg?style=for-the-badge&logo=speedtest&logoColor=white)](test_v25_kernel_benchmark.py)
[![Latency](https://img.shields.io/badge/Latency-%3C35%C2%B5s%20In--Process-6366f1.svg?style=for-the-badge)](paper_v3_0.pdf)
[![SOC 2 Type II](https://img.shields.io/badge/SOC%202%20Type%20II-CC7.1%20%2F%20CC7.2%20Ready-success.svg?style=for-the-badge)](scripts/generate_soc2_compliance_evidence.py)

</div>

---

### **[CATEGORY] What is an AI Agent Execution Gateway?**

Traditional AI guardrails operate **outside** the local runtime process—acting as conversational prompt filters or external cloud proxy LLM classifiers (80ms to 2,500ms latency). While critical for dialog safety, they are completely **blind** to what happens when an autonomous agent invokes real-world tools, dispatches SQL mutations, runs shell scripts, or interacts with the operating system.

> **Bartholomew (BTP v5.4.4)** is the open-source **In-Process AI Agent Execution Gateway**.  
> It acts as a real-time runtime boundary layer inside the agent's memory space, evaluating raw tool arguments and AST syntax trees in **under 35 microseconds** before actions are dispatched to operating systems, cloud APIs, or production databases. Test live in the [Interactive AST Playground](https://bartholomew.info/cookbook).

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
|  LAYER 2: BARTHOLOMEW IN-PROCESS EXECUTION GATEWAY (BTP v5.4.4)               |
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

| Security Dimension | External Prompt Rails (NeMo / Guardrails AI) | OS Sandboxes (Docker / gVisor / E2B) | Bartholomew In-Process Gateway (BTP v5.4.4) |
| :--- | :--- | :--- | :--- |
| **Inspection Point** | Prompt & Completion Text | OS Syscalls / Kernel Boundary | **Raw Tool Arguments & Memory Before Dispatch** |
| **Evaluation Latency**| 80ms – 2,500ms (LLM classifier) | Microsecond Syscall Filter | **<35 Microseconds (Deterministic In-Process AST)** |
| **Destructive Command Gating** | [BLIND] Blind to in-process tool args | [WARNING] Isolated inside container (still wipes data) | **[BLOCK] Hard-Blocks `rm -rf`, `DROP TABLE` in <35µs** |
| **In-Flight Secret Scrubbing** | Text PII scrubbing | [BLIND] Blind to memory mutations | **[PASS] Scrubs API keys/JWTs across tool args & logs** |
| **Runaway Spend & Loop Clamping**| [NONE] No financial quota bounds | [NONE] No semantic loop damping | **[PASS] Strict USD spend caps & LDMU retry damping** |
| **Audit Compliance Trail** | External cloud logs | Container syslog | **[VERIFIED] Tamper-Evident SHA-256 Merkle Receipts** |

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

#### **2. CrewAI, LangGraph, AutoGen & LlamaIndex**
Protect agent tool swarms against accidental drops, runaway spend loops, and shell escapes:
- **CrewAI**: `from framework_adapters.crewai import btp_crewai_tool` &mdash; see [CrewAI Quickstart](cookbook/crewai_quickstart.md)
- **LangGraph**: `from framework_adapters.langgraph import btp_langchain_tool` &mdash; see [LangGraph Quickstart](cookbook/langgraph_quickstart.md)
- **Microsoft AutoGen**: `from framework_adapters.autogen import btp_autogen_guard` &mdash; see [AutoGen Quickstart](cookbook/autogen_quickstart.md)
- **LlamaIndex**: `from framework_adapters.llamaindex import btp_llamaindex_tool` &mdash; see [LlamaIndex Quickstart](cookbook/llamaindex_quickstart.md)

```python
from framework_adapters.crewai import btp_crewai_tool

@btp_crewai_tool(spend_cap=25.0)
def execute_sql_query(query: str):
    # Destructive operations (DROP TABLE, TRUNCATE) are blocked in <25us before execution
    return db.query(query)
```

#### **3. TypeScript & Node.js (`npm install btp-guard`)**
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

#### **5. Cursor & VS Code Extension ([Open VSX](https://open-vsx.org/extension/Bartholomew/bartholomew-guard-vscode))**
Install directly in Cursor, VS Code, or VSCodium:
* Search **`Bartholomew`** in your editor's Extensions sidebar (`Ctrl+Shift+X`) and click **Install**.
* Or install via terminal:
  ```bash
  code --install-extension Bartholomew.bartholomew-guard-vscode
  # or in Cursor:
  cursor --install-extension Bartholomew.bartholomew-guard-vscode
  ```

#### **6. Autonomous Micro-Escrow & Automated Slashing (`@guard.escrow_collateral`)**
```python
# Stake micro-escrow collateral (L402 Lightning or EVM) before high-risk execution
@guard.escrow_collateral(amount_usd=250.0, action_type="FINANCIAL_TRADE", rail="L402_LIGHTNING")
def execute_large_trade(trade_payload: dict):
    # If clean: escrow is released & passport reputation increments
    # If invariant breached: collateral is liquidated automatically to claimant payee!
    return broker.submit(trade_payload)
```

#### **7. 1-Line GitHub Actions CI Security Gate**
Drop this into `.github/workflows/ci.yml` to automatically block prompt injection and unverified tool mutations on every pull request:
```yaml
- name: "Bartholomew Autonomous AI Security Gate"
  uses: ivegotahunnitonit/bartholomew@v5.4.4
  with:
    fail-on-violation: "true"
    generate-compliance-pack: "true"
```

---

### **[FRAMEWORK_ADAPTERS] Production-Ready Framework Middleware**

BTP v5.4.4 ships identical `BTPViolationError` semantics across **all major agentic frameworks**, providing structured diagnostics, latency tracking, and optional `on_violation` callbacks — no try/except boilerplate required.

| Framework | Adapter Location | Decorator / Class | Protection Mechanism |
| :--- | :--- | :--- | :--- |
| **Microsoft AutoGen** | [`framework_adapters/autogen/`](framework_adapters/autogen/) | `@btp_autogen_guard`, `AutoGenBTPInterceptor` | Multi-agent message interceptor; structured `BTPViolationError` with `to_diagnostics()` |
| **LangChain & LangGraph** | [`framework_adapters/langgraph/`](framework_adapters/langgraph/) | `@btp_langchain_tool`, `LangGraphBTPGuard` | AST gating of tool args + kwargs; `BTPViolationError` with escrow slash |
| **CrewAI** | [`framework_adapters/crewai/`](framework_adapters/crewai/) | `@btp_crewai_tool`, `CrewAIBTPTaskGuard` | Task-level invariant bounds; `BTPViolationError` anti-confused deputy isolation |
| **LlamaIndex** | [`framework_adapters/llamaindex/`](framework_adapters/llamaindex/) | `@btp_llamaindex_tool`, `BartholomewLlamaIndexTool` | Sub-35µs AST inspection blocking indirect prompt injections |
| **GitHub Actions** | [`action.yml`](action.yml) | `ivegotahunnitonit/bartholomew@v5.4.4` | Continuous PR security gate & SOC 2 audit summary table generation |

#### **Common BTPViolationError API (all adapters)**
```python
try:
    result = guarded_tool("DROP TABLE users;")
except BTPViolationError as e:
    print(e)                  # Human-readable summary
    print(e.to_diagnostics()) # Structured JSON for logs / telemetry
    # → {
    #     "status": "BLOCKED",
    #     "rule_id": "BTP-AST-001",
    #     "reason":  "Destructive SQL pattern detected",
    #     "latency_us": 12.4,
    #     ...
    #   }
```

---

### **[AUTOGEN_RECIPE] Microsoft AutoGen Security Recipe**

Bartholomew's AutoGen integration is documented as an official security recipe for the Microsoft AutoGen multi-agent framework.  
See: [`examples/autogen_btp_security_recipe.py`](examples/autogen_btp_security_recipe.py) &bull; [`examples/autogen_btp_security_recipe.ipynb`](examples/autogen_btp_security_recipe.ipynb)

```python
from framework_adapters.autogen import btp_autogen_guard, AutoGenBTPInterceptor, BTPViolationError

# 1. Decorate any AutoGen tool with a single line
@btp_autogen_guard
def execute_sql(query: str) -> str:
    return db.execute(query)

# 2. Intercept in-flight agent messages before tool dispatch
interceptor = AutoGenBTPInterceptor()
safe_message = interceptor.intercept_message(inbound_message)

# 3. Handle violations with full structured diagnostics
@btp_autogen_guard(on_violation=lambda e: {"error": e.to_diagnostics()})
def run_shell_command(cmd: str) -> dict:
    return subprocess.run(cmd, shell=True, capture_output=True)
```

---

### **[UNIVERSAL_COOKBOOK] Universal Cookbook for ALL Agents (Past, Present, & Future)**

Full interactive documentation is available at **[`COOKBOOK.md`](COOKBOOK.md)** and the **[Live Interactive Web Explorer & Playground](https://bartholomew.info/cookbook)**.

| Horizon | Recipe | Target Scenario | File Location |
| :--- | :--- | :--- | :--- |
| **Horizon 1** | **HTTP Sidecar Reverse Proxy** | Intercept existing legacy agent REST calls with zero code changes | [`cookbook/already_built/http_sidecar_proxy.py`](cookbook/already_built/http_sidecar_proxy.py) |
| **Horizon 1** | **CLI Subprocess Gate** | Sandbox arbitrary agent binaries & CLI scripts at runtime | [`cookbook/already_built/cli_process_gate.py`](cookbook/already_built/cli_process_gate.py) |
| **Horizon 2** | **OpenAI Tool-Calling Guard** | Pre-flight AST gating for raw `tools` calling loops | [`cookbook/already_built/openai_tool_calling_guard.py`](cookbook/already_built/openai_tool_calling_guard.py) |
| **Horizon 2** | **Anthropic Computer Use Guard** | Guard Claude bash execution and OS computer actions | [`cookbook/already_built/anthropic_computer_use_guard.py`](cookbook/already_built/anthropic_computer_use_guard.py) |
| **Horizon 2** | **Google Gemini Function Guard** | Ed25519-signed function execution receipts for Gemini | [`cookbook/already_built/gemini_function_calling_guard.py`](cookbook/already_built/gemini_function_calling_guard.py) |
| **Horizon 2** | **TypeScript / Node.js Agent** | Native npm package integration for web agent backends | [`cookbook/already_built/typescript_node_agent.ts`](cookbook/already_built/typescript_node_agent.ts) |
| **Horizon 2** | **Rust Sub-5µs Fast-Path** | Zero-copy SIMD invariant validation for high-frequency agents | [`cookbook/being_built/rust_fast_path_guard.rs`](cookbook/being_built/rust_fast_path_guard.rs) |
| **Horizon 3** | **Sovereign Agent Passports** | Ed25519 digital passports & peer discovery mesh for swarms | [`cookbook/future_swarms/sovereign_agent_passport_mesh.py`](cookbook/future_swarms/sovereign_agent_passport_mesh.py) |
| **Horizon 3** | **ZK Privacy Compliance** | Homomorphic Pedersen commitments proving compliance with 0 leaks | [`cookbook/future_swarms/zk_privacy_auditing.py`](cookbook/future_swarms/zk_privacy_auditing.py) |
| **Horizon 3** | **Confidential Hardware Enclave** | AWS Nitro / AMD SEV-SNP golden PCR attestation anchoring | [`cookbook/future_swarms/confidential_enclave_anchor.py`](cookbook/future_swarms/confidential_enclave_anchor.py) |
| **Horizon 3** | **L402 Autonomous Micro-Escrow** | Programmatic collateral lock & automated regression slashing | [`cookbook/future_swarms/l402_autonomous_escrow.py`](cookbook/future_swarms/l402_autonomous_escrow.py) |

---

### **[AI_IDES] AI Developer IDE Guardrails**

Drop-in invariant enforcement across all leading AI coding assistants:

* **Cursor**: [`.cursorrules`](cookbook/ides/cursor/.cursorrules) & [`mcp.json`](cookbook/ides/cursor/mcp.json)
* **Windsurf**: [`.windsurfrules`](cookbook/ides/windsurf/.windsurfrules) & [`mcp_config.json`](cookbook/ides/windsurf/mcp_config.json)
* **VS Code / Copilot**: [`settings.json`](cookbook/ides/vscode/settings.json) & [Extension](https://open-vsx.org/extension/Bartholomew/bartholomew-guard-vscode)
* **Cline / Roo Code**: [`cline_mcp_settings.json`](cookbook/ides/cline_roo_code/cline_mcp_settings.json)
* **Zed**: [`zed_settings.json`](cookbook/ides/zed/zed_settings.json)
* **Google Antigravity**: [`AGENTS.md`](cookbook/ides/antigravity/AGENTS.md)

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

### **[COMMERCIAL] Commercial Editions & Cloud Fleet Management**

| Tier | Price | Features | Direct Checkout |
| :--- | :--- | :--- | :--- |
| **Community** | **Free Forever** | Offline in-memory AST gating, Ed25519 local signing, secret scrubbing, local SQLite audit trail | Included in repo |
| **Bartholomew Pro** | **$49 / month** | Real-time Cloud Telemetry dashboard, Slack threat alerts, SIEM event streaming, priority MCP indexing | [**Upgrade to Pro &rarr;**](https://buy.stripe.com/fZu28rbNz5TYcmAddK9R600) |
| **Enterprise Fleet** | **$199 / month** | Multi-tenant workspace isolation, continuous SOC 2 Type II audit packs, eBPF syscall tracing, dedicated CISO ledger | [**Upgrade to Enterprise &rarr;**](https://buy.stripe.com/fZu14ng3PgyC9ao2z69R601) |

* **Fleet Dashboard:** [https://bartholomew.info/cloud](https://bartholomew.info/cloud)
* **Live Pricing & Portal:** [https://bartholomew.info/pricing](https://bartholomew.info/pricing)

---

© 2026 Bartholomew AI & Contributors. Distributed under the Open Source & Dual Commercial Licensing Model.
</div>
