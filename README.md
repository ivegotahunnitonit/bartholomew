<p align="center">
  <img src="packages/vscode-extension/icon.png" width="140" alt="Bartholomew Shield Logo" />
</p>

# Bartholomew (BTP v1.0.0) — In-Process Runtime Execution Gateway for Autonomous AI Agents

**Deterministic AST Policy Invariant Gating, In-Flight Secret Masking, and Cryptographic Attestation for Autonomous AI Agent Swarms.**

[![CI](https://github.com/bartholomew-ai/bartholomew/actions/workflows/ci.yml/badge.svg)](https://github.com/bartholomew-ai/bartholomew/actions/workflows/ci.yml)
[![Open VSX](https://img.shields.io/badge/Open%20VSX-v1.0.0-blue?logo=visualstudiocode)](https://open-vsx.org/extension/Bartholomew/bartholomew-guard-vscode)
[![PyPI](https://img.shields.io/pypi/v/btp-guard?logo=pypi&logoColor=white)](https://pypi.org/project/btp-guard/)
[![npm](https://img.shields.io/npm/v/btp-guard?logo=npm&logoColor=white)](https://www.npmjs.com/package/btp-guard)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-2920%20passing-brightgreen)](tests/)

[![OpenAI](https://img.shields.io/badge/OpenAI-Agents%20SDK-10A37F?logo=openai&logoColor=white)](examples/README.md)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude%20Tool%20Guard-D97706?logo=anthropic&logoColor=white)](examples/README.md)
[![LangChain](https://img.shields.io/badge/LangChain-Runtime%20Guard-1C3C3C?logo=langchain&logoColor=white)](examples/README.md)
[![CrewAI](https://img.shields.io/badge/CrewAI-Agent%20Guard-FF4B4B)](examples/README.md)
[![AutoGen](https://img.shields.io/badge/Microsoft-AutoGen%20Swarm-00A4EF?logo=microsoft&logoColor=white)](examples/README.md)
[![IDE](https://img.shields.io/badge/IDE-Cursor%20%2F%20VS%20Code-7C3AED?logo=githubcopilot&logoColor=white)](https://open-vsx.org/extension/Bartholomew/bartholomew-guard-vscode)

---

## What It Does

Bartholomew is the execution gate for autonomous AI agents.

It sits between an agent and real-world execution (shell, SQL, file I/O, cloud APIs) and decides whether proposed actions should be allowed before they execute.

```
                    [ Autonomous Agent / LLM ]
                                │
                                ▼  (Proposes Tool Call / Bash / SQL)
  ┌────────────────────────────────────────────────────────────────────────┐
  │                 Bartholomew In-Process Runtime Gateway                 │
  │                                                                        │
  │   [ Polyglot AST Invariant Gate ] ──► Sub-millisecond syntax check     │
  │   [ In-Flight Secret Vault ]       ──► Real-time credential scrubbing   │
  │   [ Declarative Policy Engine ]   ──► Spend caps & command allowlists  │
  │   [ Cryptographic Attestation ]   ──► RFC 8785 Ed25519 Signed Receipts │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                    [ ALLOW ]                  [ DENY ]
                         │                         │
                         ▼                         ▼
             [ Target System / DB / OS ]   [ Execution Veto + Audit Evidence ]
```

### Core Capabilities:
- **Pre-Execution Gating**: Evaluates tool arguments, commands, and code strings before OS dispatch.
- **Polyglot AST Parsing**: Parses Abstract Syntax Trees across Python, SQL, Bash, JavaScript, and Go to block dangerous mutations (`rm -rf`, `DROP TABLE`, subshell escapes).
- **In-Flight Secret Scrubbing**: Detects and redacts credentials (`sk-*`, `ghp_*`, `AKIA*`, private keys) before they touch logs, providers, or vector stores.
- **Cryptographic Auditability**: Generates canonical RFC 8785 JSON digests signed with Ed25519 keys for tamper-proof verification.
- **Zero Network Overhead**: Evaluates locally inside the host process runtime without external API latency or second-model token billing.

---

## Quickstart

### Python

```bash
pip install btp-guard
```

```python
from btp_guard import Guard

guard = Guard(spend_cap=100.0, strict=True)

# 1. Protect any tool function via decorator
@guard.protect
def execute_shell(command: str):
    return f"Executed: {command}"

# 2. Or check actions directly inline
result = guard.check("rm -rf /var/data")
if not result["allowed"]:
    print(f"Blocked: {result['reason']}")
# Output: Blocked: BTP-AST-001: Catastrophic shell pattern detected
```

### Node.js / TypeScript

```bash
npm install btp-guard
```

```typescript
import { Guard } from "btp-guard";

const guard = new Guard({ maxSpendUsd: 100.0 });
const verdict = guard.check("DROP TABLE users;");

if (!verdict.allowed) {
  throw new Error(`Action blocked: ${verdict.reason}`);
}
```

---

## MCP Server (Model Context Protocol)

Bartholomew provides a native Model Context Protocol (MCP) server for Claude Desktop, Cursor, Windsurf, and any MCP-compatible client:

```json
{
  "mcpServers": {
    "bartholomew": {
      "command": "python",
      "args": ["-m", "src.mcp_server"]
    }
  }
}
```

---

## Framework Integrations

Bartholomew provides drop-in runtime interceptors for all major agent orchestrators:

| Framework / Ecosystem | Integration Guard | Reference Guide |
|---|---|---|
| **OpenAI Agents SDK** | Dynamic Tool Gating & Schema Invariant Checks | [`docs/FRAMEWORK_GUIDE.md`](docs/FRAMEWORK_GUIDE.md) |
| **Anthropic Claude** | `ClaudeToolGuard` / Tool-Call Interceptor | [`docs/FRAMEWORK_GUIDE.md`](docs/FRAMEWORK_GUIDE.md) |
| **Microsoft AutoGen** | `@btp_autogen_guard` / Swarm Consensus Interceptor | [`examples/future_swarms/autogen_swarm_consensus.py`](examples/future_swarms/autogen_swarm_consensus.py) |
| **CrewAI** | `@btp_crewai_tool` / Task & Agent Boundary Gate | [`docs/FRAMEWORK_GUIDE.md`](docs/FRAMEWORK_GUIDE.md) |
| **LangChain / LangGraph** | `BTPGuardTool` / Node Execution Interceptor | [`docs/FRAMEWORK_GUIDE.md`](docs/FRAMEWORK_GUIDE.md) |
| **Cursor / VS Code** | Pre-execution IDE Sentry & Extension | [Open VSX Extension](https://open-vsx.org/extension/Bartholomew/bartholomew-guard-vscode) |

---

## Defense in Depth Architecture

Bartholomew functions as **Layer 2** in the autonomous agent defense stack:

| Layer | Technology | Typical Latency | Defense Boundary |
|---|---|---|---|
| **Layer 1 — Prompt Rails** | NeMo, Guardrails AI, LlamaGuard | 800ms – 2,500ms | Natural language prompt & completion text |
| **Layer 2 — Execution Gate** | **Bartholomew BTP** | **< 0.1 ms (Sub-millisecond)** | **Raw tool arguments, AST syntax, credentials, spend** |
| **Layer 3 — OS Isolation** | Docker, gVisor, E2B | 200ms – 500ms | Kernel syscall & container isolation |

---

## Audit & Compliance Readiness

Bartholomew generates tamper-evident audit evidence packs mapping to AICPA Trust Services Criteria (CC6.1, CC6.6, CC7.1) and ISO/IEC 27001:2022 (A.8.8, A.8.30):

```bash
python scripts/generate_soc2_compliance_evidence.py
```

Output: `docs/audit/soc2-compliance-evidence.json` containing SHA-256 Merkle proofs, RFC 8785 canonical digests, and Ed25519 digital signatures for zero-network independent auditor verification.

---

## Development & Test Suite

```bash
# Clone repository
git clone https://github.com/bartholomew-ai/bartholomew.git
cd bartholomew

# Install dependencies
pip install -e ".[test]"

# Run full test suite (2,920 automated tests)
python -m pytest -q
```

---

## Documentation

- [`docs/quickstart.md`](docs/quickstart.md) — Full setup and configuration guide
- [`docs/threat-model.md`](docs/threat-model.md) — Threat model and security boundaries
- [`docs/btp-protocol-spec.md`](docs/btp-protocol-spec.md) — BTP wire protocol specification
- [`docs/FRAMEWORK_GUIDE.md`](docs/FRAMEWORK_GUIDE.md) — Framework adapter documentation
- [`SECURITY.md`](SECURITY.md) — Vulnerability disclosure policy
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — Contributing guidelines

---

## License

Bartholomew is distributed under the [MIT License](LICENSE).
