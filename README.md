# Bartholomew — BTP v5.4.10

**In-Process AI Agent Execution Gateway** — sub-35µs AST gating, secret scrubbing, and tamper-evident audit receipts for autonomous agent runtimes.

[![CI](https://github.com/ivegotahunnitonit/bartholomew/actions/workflows/ci.yml/badge.svg)](https://github.com/ivegotahunnitonit/bartholomew/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/btp-guard?logo=pypi&logoColor=white)](https://pypi.org/project/btp-guard/)
[![npm](https://img.shields.io/npm/v/btp-guard?logo=npm&logoColor=white)](https://www.npmjs.com/package/btp-guard)
[![Cloud Console](https://img.shields.io/badge/Cloud-Console-8b5cf6)](https://bartholomew.info/cloud)
[![Pricing](https://img.shields.io/badge/Pricing-Plans-10b981)](https://bartholomew.info/pricing)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-2837%20passing-brightgreen)](tests/)

---

## What it does

Traditional guardrails operate on prompt text — they are blind to what happens when an autonomous agent invokes real-world tools. Bartholomew closes that gap by sitting **inside the agent's memory space**, inspecting raw tool arguments and AST syntax trees in **under 35 microseconds** before actions reach the OS, a database, or an external API.

```
Prompt rails (NeMo, Guardrails AI)   ~80–2500ms  ─┐
                                                    ├─ BLIND SPOT
Bartholomew in-process gate          <35µs       ──┤  ← fills here
                                                    │
OS / container boundary (Docker)     kernel-level ──┘
```

**What it blocks:**
- Destructive shell commands (`rm -rf`, `mkfs`, `dd`)
- Destructive SQL mutations (`DROP TABLE`, `TRUNCATE`)
- Credential exfiltration (`sk-*`, `ghp_*`, `AKIA*`) in thought logs or tool args
- Runaway token spend loops beyond configured USD caps
- Prompt-injection-driven tool hijacks across multi-agent swarms

---

## Install

```bash
# Python
pip install btp-guard

# Node.js / MCP
npx btp-guard init
```

**Requirements:** Python ≥ 3.10 · No mandatory cloud dependency · Works fully offline

---

## Quickstart

### Python — decorator guard

```python
from btp_guard import Guard, BTPViolationError

guard = Guard(spend_cap_usd=50.0, max_retries=5)

@guard.protect
def execute_query(sql: str):
    return db.execute(sql)

try:
    execute_query("DROP TABLE accounts;")
except BTPViolationError as e:
    print(e.to_diagnostics())
    # {"status": "BLOCKED", "rule_id": "BTP-SQL-001",
    #  "reason": "Destructive SQL mutation detected", "latency_us": 18.4}
```

### Python — inline check

```python
from btp_guard import Guard

guard = Guard()
result = guard.check("rm -rf /var/data")
# {"allowed": False, "reason": "[BTP-AST-001] Destructive filesystem pattern"}
```

### TypeScript / Node.js

```typescript
import { BTPGuard } from 'btp-guard';

const guard = new BTPGuard();
const receipt = guard.evaluateAction({
  agentId: 'worker-1',
  actionType: 'DATABASE_MUTATION',
  payload: { query: 'DROP TABLE users;' }
});
// receipt.verdict === "DENY"  (blocked in ~11µs, Merkle receipt attached)
```

### MCP — Claude Desktop, Cursor, Windsurf

```bash
# Starts the BTP stdio/SSE proxy — all tool calls pass through it
python -m src.mcp_server
```

Config examples for each IDE are in [`examples/ides/`](examples/ides/).

### GitHub Actions

```yaml
- name: BTP Security Gate
  uses: ivegotahunnitonit/bartholomew@v5.4.10
  with:
    fail-on-violation: "true"
    generate-compliance-pack: "true"
```

---

## Editions & Cloud Console

Bartholomew is fully open-source and offline for local developer workflows. For engineering teams deploying multi-agent swarms in production, the Cloud Console provides centralized fleet monitoring, instant threat alerts, and automated compliance reports:

| Edition | Pricing | Ideal For | Core Capabilities |
|---|---|---|---|
| **Community (OSS)** | **Free Forever** | Solo Devs & Local Scripts | In-process sub-35µs AST gate, offline Ed25519 receipts, secret scrubber, MIT license |
| **Pro / Team** | **$49 / month** | Startups & Engineering Teams | [Cloud Telemetry Dashboard](https://bartholomew.info/cloud), instant Slack/Discord threat alerts, fleet API keys, policy sync |
| **Enterprise** | **$299 / month** | Scale-ups, FinTech & Healthcare | Continuous 1-click SOC 2 Type II evidence bundles, multi-tenant workspace isolation, dedicated CISO ledger, priority SLA |

👉 **Get Started & Upgrade:**
- **Pro Edition ($49/mo):** [Direct Stripe Checkout](https://buy.stripe.com/fZu28rbNz5TYcmAddK9R600)
- **Enterprise Edition ($299/mo):** [Direct Stripe Checkout](https://buy.stripe.com/fZu14ng3PgyC9ao2z69R601)
- **CLI Activation:** Run `npx btp-guard activate <key>` or `btp-guard pricing`
- **Pricing & Storefront:** [https://bartholomew.info/pricing](https://bartholomew.info/pricing)

---

## Architecture

```
cmd/bartholomew/          # Go CLI entry point
src/
  btp_guard/              # Core Python guard engine
  framework_adapters/     # LangChain, LangGraph, AutoGen, CrewAI wrappers
  bartholomew_eval/       # Bayesian risk engine & AST fuzzer
  mcp_server/             # MCP stdio/SSE gateway
  go_services/            # High-throughput Go verifier service
  rust_verifier/          # Sub-5µs Rust fast-path (experimental)
  daemon/                 # Background approval queue & tray manager
  ebpf/                   # eBPF kernel-level syscall hooks (Linux)
examples/                 # Integration recipes (already_built, being_built, future_swarms, ides)
packages/                 # SDKs: pypi_package, npm_package, sdk_go, sdk_rust, sdk_typescript, vscode-extension
deploy/                   # Docker, K8s, Terraform, CDK, GCP, Helm, Systemd
tests/                    # 2,837-test suite (pytest -o 'pythonpath=src .')
docs/                     # Specs: threat-model.md, btp-protocol-spec.md, quickstart.md
```

---

## Framework adapters

| Framework | Import |
|---|---|
| LangChain | `from src.framework_adapters.langchain_guard import BTPLangChainGuard` |
| LangGraph | `from src.framework_adapters.langgraph_guard import BTPLangGraphGuard` |
| AutoGen | `from src.framework_adapters.autogen_guard import BTPAutoGenGuard` |
| CrewAI | `from src.framework_adapters.crewai_guard import BTPCrewAIGuard` |
| Semantic Kernel | `from src.framework_adapters.semantic_kernel_guard import BTPSemanticKernelGuard` |
| Raw OpenAI | `from src.framework_adapters.universal import UniversalBTPModelGuard` |
| Raw Anthropic | `from src.framework_adapters.universal import UniversalBTPModelGuard` |

Full recipes in [`examples/`](examples/).

---

## Defense layers

Bartholomew is **Layer 2** in a standard defense-in-depth stack:

| Layer | Tool | Latency | Scope |
|---|---|---|---|
| 1 — Prompt rails | NeMo, Guardrails AI, LlamaGuard | 80–2500ms | Prompt & completion text |
| **2 — Execution gate** | **Bartholomew BTP** | **<35µs** | **Raw tool args, AST, secrets, spend** |
| 3 — OS sandbox | Docker, gVisor, E2B | kernel | Syscall interception |

---

## Audit & compliance

Generate a tamper-evident SOC 2 Type II evidence pack:

```bash
python scripts/audit_firm_ledger.py
```

Output: `docs/audit/` — SHA-256 Merkle receipt JSON + auditor markdown summary.  
Controls satisfied: AICPA CC6.1, CC6.6, CC7.1, CC7.2 · ISO 27001:2022 A.8.8, A.8.30.

---

## Development

```bash
# Clone & install in editable mode
git clone https://github.com/ivegotahunnitonit/bartholomew.git
cd bartholomew
pip install -e ".[test]"

# Run the full test suite
pytest tests/ -o "pythonpath=src ." -q

# Lint
pip install ruff && ruff check src/ tests/
```



---

## Documentation

- [`docs/quickstart.md`](docs/quickstart.md) — full setup guide
- [`docs/threat-model.md`](docs/threat-model.md) — threat model & security boundaries
- [`docs/btp-protocol-spec.md`](docs/btp-protocol-spec.md) — BTP wire protocol specification
- [`docs/cookbook.md`](docs/cookbook.md) — all integration recipes
- [`SECURITY.md`](SECURITY.md) — vulnerability disclosure policy
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contributing guide

---

© 2026 Bartholomew AI & Contributors. MIT License.
