# Bartholomew — Authorization Gate MVP

**Authorization and policy layer for autonomous agents** — gate risky actions before execution, record proof of the decision, and emit telemetry for downstream policy and billing layers.

[![CI](https://github.com/ivegotahunnitonit/bartholomew/actions/workflows/ci.yml/badge.svg)](https://github.com/ivegotahunnitonit/bartholomew/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/btp-guard?logo=pypi&logoColor=white)](https://pypi.org/project/btp-guard/)
[![npm](https://img.shields.io/npm/v/btp-guard?logo=npm&logoColor=white)](https://www.npmjs.com/package/btp-guard)
[![Marketplace](https://img.shields.io/badge/GitHub%20Marketplace-Bartholomew%20Security%20Gate-2ea44f?logo=githubactions&logoColor=white)](https://github.com/marketplace/actions/bartholomew-ai-security-gate-soc-2-auditor)
[![smithery badge](https://smithery.ai/badge/itsubsolomon/calls_10k)](https://smithery.ai/servers/itsubsolomon/calls_10k)
[![Glama](https://img.shields.io/badge/Glama.ai-Bartholomew%20Registry-7C3AED)](https://glama.ai/mcp)
[![Deploy to Cloudflare](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/ivegotahunnitonit/bartholomew/tree/main/examples/future_swarms/cloudflare)
[![Cloud Console](https://img.shields.io/badge/Cloud-Console-8b5cf6)](https://bartholomew.info/cloud)
[![Pricing](https://img.shields.io/badge/Pricing-Plans-10b981)](https://bartholomew.info/pricing)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-2879%20passing-brightgreen)](tests/)

[![Gemini 3.8](https://img.shields.io/badge/Google%20Gemini-3.8%20Ultra-4285F4?logo=google&logoColor=white)](examples/README.md)
[![Claude 3.7](https://img.shields.io/badge/Anthropic-Claude%203.7%20Sonnet-D97706?logo=anthropic&logoColor=white)](examples/README.md)
[![GPT-Astra](https://img.shields.io/badge/OpenAI-GPT--Astra%20%2F%20Agents%20SDK-10A37F?logo=openai&logoColor=white)](examples/README.md)
[![Cloudflare](https://img.shields.io/badge/Cloudflare-Workers%20AI%20%2F%20Agents-F38020?logo=cloudflare&logoColor=white)](examples/README.md)
[![AutoGen](https://img.shields.io/badge/Microsoft-AutoGen%20Swarm-00A4EF?logo=microsoft&logoColor=white)](examples/README.md)
[![Copilot / Cursor](https://img.shields.io/badge/IDE-Copilot%20%2F%20Cursor%20%2F%20Windsurf-7C3AED?logo=githubcopilot&logoColor=white)](examples/README.md)

---

## What it does

Bartholomew is the execution gate for autonomous agents.

It sits between an agent and a real-world action and decides whether the action should be allowed before it runs. The current MVP is intentionally narrow and focused on the action boundary:

- evaluate an action before execution
- inspect the payload for policy violations and risky patterns
- enforce allow / deny decisions with a clear rule id
- return a receipt hash for auditability
- emit telemetry for observability and downstream governance

This is the foundation for a trusted authorization layer for autonomous systems.

**Current policy checks include:**
- destructive shell commands (`rm -rf`, `mkfs`, `dd`)
- dangerous SQL mutations (`DROP TABLE`, `TRUNCATE`)
- credential exfiltration (`sk-*`, `ghp_*`, `AKIA*`)
- prompt-injection attempts
- blocked action types and spend caps under policy

**Positioning:** Bartholomew is not a broad platform story. It is the authorization layer that decides whether an autonomous agent can act.

---

## MVP quickstart

```python
from src.btp_guard.authorization_gate import AuthorizationGate

policy = {
    "allow_destructive": False,
    "max_spend_usd": 5.0,
    "allowed_action_types": ["shell", "read", "search"],
}

gate = AuthorizationGate(policy=policy)

safe = gate.evaluate({
    "agent_id": "worker-1",
    "action_type": "shell",
    "payload": {"command": "ls -la /tmp"},
    "policy": policy,
})

unsafe = gate.evaluate({
    "agent_id": "worker-1",
    "action_type": "shell",
    "payload": {"command": "rm -rf /tmp/data"},
    "policy": policy,
})

print(safe)
print(unsafe)
```

Example output:

```json
{
  "verdict": "ALLOW",
  "reason": "No policy violations detected",
  "rule_id": null,
  "latency_ms": 0.047,
  "timestamp": "2026-09-15T22:07:07.752116+00:00",
  "receipt_sha256": "71754d8ac4339c2aaa9a71bb4d8337439cafcb81dcef72e6e7a3fc48141fed93"
}
```

```json
{
  "verdict": "DENY",
  "reason": "Destructive shell pattern detected",
  "rule_id": "BTP-SHELL-001",
  "latency_ms": 0.025,
  "timestamp": "2026-09-15T22:07:07.752206+00:00",
  "receipt_sha256": "7808a40a1b7afafc2575e0f23c26c574eacca562ba7cf2a7a2fa5be8ee2e17d1"
}
```

This is the execution guard MVP for the bartholomew strategy.

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

### MCP — Claude Desktop, Cursor, Windsurf, Smithery.ai & Glama.ai

```bash
# 1-Click install via Smithery.ai CLI:
npx -y @smithery/cli install bartholomew --client claude

# Or run direct stdio MCP server proxy:
python mcp_server.py
```

### Cursor & VS Code Extension

Install the official pre-built extension for real-time AST threat notifications in Cursor / VS Code:
```bash
code --install-extension packages/vscode-extension/bartholomew-guard-vscode-5.4.12.vsix
```

### Cloudflare Workers AI — Edge Security Proxy

Deploy a sub-50µs AST security gate across Cloudflare's 300+ city global network with 1 click:
[![Deploy to Cloudflare Workers](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/ivegotahunnitonit/bartholomew/tree/main/examples/future_swarms/cloudflare)

```bash
cd examples/future_swarms/cloudflare
npx wrangler deploy
```

### GitHub Actions (GitHub Marketplace)

Add automated AST security audits and credential scanning to every pull request:
```yaml
- name: Bartholomew AI Security Gate & SOC 2 Auditor
  uses: ivegotahunnitonit/bartholomew@v5.4.12
  with:
    fail-on-violation: "true"
    generate-compliance-pack: "true"
```

### Bitcoin Lightning & L402 Swarm Settlements (Alby Hub)

Manage your 24/7 self-custodial Lightning node and issue machine-to-machine micropayments:
```bash
# Check node health & spendable satoshi balance
python cli.py lightning status
python cli.py lightning balance

# Mint a live Lightning Network invoice for tool audit fees
python cli.py lightning invoice --sats 30000 --desc "Swarm AST Execution Pool"
```

---

## Editions & Cloud Console

Bartholomew is fully open-source and offline for local developer workflows. For engineering teams deploying multi-agent swarms in production, the Cloud Console provides centralized fleet monitoring, instant threat alerts, and automated compliance reports:

| Edition | Pricing | Ideal For | Core Capabilities |
|---|---|---|---|
| **Community (OSS)** | **Free Forever** | Solo Devs & Local Scripts | In-process sub-35µs AST gate, offline Ed25519 receipts, secret scrubber, MIT license |
| **Pro / Team** | **$49 / month** | Startups & Engineering Teams | [Cloud Telemetry Dashboard](https://bartholomew.info/cloud), instant Slack/Discord threat alerts, fleet API keys, policy sync |
| **Enterprise** | **$199 / month** | Scale-ups, FinTech & Healthcare | Continuous 1-click SOC 2 Type II evidence bundles, multi-tenant workspace isolation, dedicated CISO ledger, priority SLA |

👉 **Get Started & Upgrade:**
- **Pro Edition ($49/mo):** [Direct Stripe Checkout](https://buy.stripe.com/fZu28rbNz5TYcmAddK9R600)
- **Enterprise Edition ($199/mo):** [Direct Stripe Checkout](https://buy.stripe.com/fZu14ng3PgyC9ao2z69R601)
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

## Framework & Frontier Partner Adapters

| Frontier Partner / Swarm | Integration Guard | Recipe Path |
|---|---|---|
| **Google Gemini 3.8 Ultra** | `@btp_gemini_38_tool()` / Thought Scratchpad Gate | [`examples/being_built/google_gemini38_guard.py`](examples/being_built/google_gemini38_guard.py) |
| **Anthropic Claude 3.7 Sonnet** | `Claude37ToolGuard` / Hybrid Thinking Interceptor | [`examples/being_built/anthropic_claude37_guard.py`](examples/being_built/anthropic_claude37_guard.py) |
| **GPT-Astra / OpenAI Agents SDK** | `OpenAIToolGuard` / Dynamic Schema Verifier | [`examples/being_built/openai_agents_sdk_guard.py`](examples/being_built/openai_agents_sdk_guard.py) |
| **Cloudflare Workers AI & Agents** | Sub-50µs Edge AST Gate & KV Replay Defense | [`examples/future_swarms/cloudflare_edge_agent_guard.ts`](examples/future_swarms/cloudflare_edge_agent_guard.ts) |
| **Microsoft AutoGen Swarm** | `@btp_autogen_guard` / Consensus Quorum & AWU Barter | [`examples/future_swarms/autogen_swarm_consensus.py`](examples/future_swarms/autogen_swarm_consensus.py) |
| **GitHub Copilot / Cursor / Windsurf** | MCP Stdio Proxy / `.cursorrules` / `.mdc` Sentry | [`examples/ides/`](examples/ides/) & [`mcp_server.py`](mcp_server.py) |
| **Universal Swarm (A2A)** | `UniversalSwarmDelegator` (Ed25519 + L402 Rails) | [`examples/future_swarms/universal_swarm_delegation.py`](examples/future_swarms/universal_swarm_delegation.py) |

Full documentation and quickstarts in the [Master Cookbook](examples/README.md).

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
