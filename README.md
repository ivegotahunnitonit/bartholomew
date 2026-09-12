<div style="font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif; line-height: 1.6;">

> **Need SOC 2 Type II Audit Trails & Multi-Agent Fleet Management?** [Try Bartholomew Cloud &rarr; https://bartholomew.info/cloud](https://bartholomew.info/cloud) (Pro: $49/mo &bull; Enterprise Fleet: $199/mo &bull; Centralized Fleet Control Plane).

# **Bartholomew AI &bull; BTP v5.4.10 Standards Track**
### **The Sovereign Sentinel Companion & AI Agent Execution Gateway**
#### **Sub-35µs In-Process Tool Gating &bull; Zero Prompt Leakage &bull; Multi-Model Defense &bull; SOC 2 Type II Merkle Receipts**

<div align="center">

[![npm version](https://img.shields.io/npm/v/btp-guard?style=for-the-badge&logo=npm&logoColor=white)](https://www.npmjs.com/package/btp-guard)
[![PyPI version](https://img.shields.io/badge/PyPI-v5.4.10-blue?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/btp-guard/5.4.10/)
[![Product Hunt](https://img.shields.io/badge/Product%20Hunt-Featured-orange?style=for-the-badge&logo=producthunt&logoColor=white)](https://www.producthunt.com/posts/bartholomew)
[![Frontier Benchmark](https://img.shields.io/badge/Benchmark-19.10%C2%B5s%20Median-10b981?style=for-the-badge)](BENCHMARK_FRONTIER_MODELS.md)
[![Pro Tier](https://img.shields.io/badge/Bartholomew%20Pro-%2449%2Fmo-10b981?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/fZu28rbNz5TYcmAddK9R600)
[![Enterprise Tier](https://img.shields.io/badge/Enterprise-%24199%2Fmo-6366f1?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/fZu14ng3PgyC9ao2z69R601)
[![Tests](https://img.shields.io/badge/Tests-All%20Passed%20(100%25)-success.svg?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![Live Explorer](https://img.shields.io/badge/Web%20Explorer-Live-10b981.svg?style=for-the-badge&logo=firebase&logoColor=white)](https://bartholomew.info)
[![GitHub Action](https://img.shields.io/badge/GitHub%20Action-v5.4.10-2088FF.svg?style=for-the-badge&logo=githubactions&logoColor=white)](action.yml)

</div>

---

### **[SENTINEL_COMPANION] Meet Bartholomew**

Bartholomew is not an opaque barrier or cold `HTTP 403` error. He is your agent swarm's **steadfast digital steward, calm elder guardian, and protective companion**.

When your agents dream boldly and build fast, Bartholomew stands watch between ambitious AI models and the real world (filesystems, databases, and credit cards). When an LLM hallucinates an accidental database wipe, unconstrained file deletion, or runaway token spend loop, Bartholomew holds the line in microsecond time (<35µs) and offers empathetic, constructive counsel so your startup stays safe and you can sleep soundly.

```bash
# 1-Command Setup for Claude Desktop, Cursor & Terminal:
npx btp-guard init

# Or Python Package:
pip install --upgrade btp-guard==5.4.10

# Test the sub-35µs execution gate locally:
npx btp-guard demo
```

---

### **[CATEGORY] What is an AI Agent Execution Gateway?**

Traditional AI guardrails operate **outside** the local runtime process—acting as conversational prompt filters or external cloud proxy LLM classifiers (80ms to 2,500ms latency). While critical for dialog safety, they are completely **blind** to what happens when an autonomous agent invokes real-world tools, dispatches SQL mutations, runs shell scripts, or interacts with the operating system.

> **Bartholomew (BTP v5.4.6)** is the open-source **In-Process AI Agent Execution Gateway**.  
> It acts as a real-time runtime boundary layer inside the agent's memory space, evaluating raw tool arguments and AST syntax trees in **under 35 microseconds** (29.44µs average) before actions are dispatched to operating systems, cloud APIs, or production databases. Test live in the [Interactive AST Playground](https://bartholomew.info/cookbook).

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

#### **2. Frontier AI Models (Gemini 3.8, Claude 3.7, GPT-Astra, DeepSeek-R1)**
Universal wire protection separating reasoning scratchpads from external tool dispatches:
- **Google Gemini 3.8**: Multimodal thought parts isolation & function declaration gating &mdash; see [Gemini 3.8 Quickstart](cookbook/gemini_38_quickstart.md)
- **Anthropic Claude 3.7**: Hybrid reasoning `<thinking>` scratchpad protection &mdash; see [Claude 3.7 Quickstart](cookbook/claude_37_thinking_guard.md)
- **OpenAI GPT-Astra & Agents SDK**: Multi-agent tool execution seam defense &mdash; see [GPT-Astra Quickstart](cookbook/gpt_astra_agents_sdk.md)

```python
from framework_adapters.universal import UniversalBTPModelGuard, ModelProvider

guard = UniversalBTPModelGuard(strict=False)

# Intercept and verify tool calls from any frontier model wire in <35us
result = guard.intercept_and_verify(raw_tool_call, provider=ModelProvider.GEMINI_3_8)
print(result["status"], result["latency_us"])
```

#### **2. Universal Python Tool Guard (`pip install btp-guard`)**
Protect any function or tool against destructive SQL, shell escapes, and credential leaks:

```python
from btp_guard import secure_tool

@secure_tool
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

### **[UNIVERSAL_GATEWAY] Model Context Protocol (MCP) & Coding Agent Execution Firewall**

BTP v5.4.10 operates directly at the execution boundary between autonomous models, tools, and the operating system. It protects developers and enterprise infrastructure against destructive commands (`rm -rf`, `DROP TABLE`, `mkfs`), runaway token loops, and high-entropy secret exfiltration.

| Gateway Layer | Target Scenario | Setup / Command | Protection Mechanism |
| :--- | :--- | :--- | :--- |
| **Model Context Protocol (MCP)** | Claude Desktop, Cursor, Windsurf | `npx btp-guard init` | Native stdio/SSE proxy inspecting all tool arguments before tool dispatch |
| **Terminal & Coding Agents** | Claude Code, Aider, Cline, CLI agents | `npx btp-guard demo` | Sub-35µs AST command interception before OS `fork`/`exec` |
| **Universal Python Functions** | Raw OpenAI, Anthropic, Gemini callers | `from btp_guard import secure_tool` | In-memory pre-flight AST inspection with Ed25519 cryptographic attestation |
| **Universal TypeScript / Node** | Node.js / ESM backend agent runtimes | `import { evaluateIntent } from 'btp-guard'` | Zero-dependency RFC 8785 JSON canonicalization & secret redaction |
| **GitHub Actions CI/CD** | Automated PR & Agent trajectory verification | `uses: ivegotahunnitonit/bartholomew@v5.4.10` | Continuous PR security gate & SOC 2 compliance summary generation |

#### **Common BTPViolationError Handling**
```python
from btp_guard import secure_tool, BTPViolationError

@secure_tool
def run_shell(cmd: str):
    return subprocess.run(cmd, shell=True, capture_output=True)

try:
    result = run_shell("rm -rf /")
except BTPViolationError as e:
    print(e)                  # Human-readable summary
    print(e.to_diagnostics()) # Structured JSON for logs / telemetry
    # -> {
    #      "status": "BLOCKED",
    #      "rule_id": "BTP-AST-001",
    #      "reason":  "Destructive filesystem pattern detected",
    #      "latency_us": 14.2
    #    }
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
