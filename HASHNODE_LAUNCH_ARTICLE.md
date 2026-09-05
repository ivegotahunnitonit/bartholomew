# Why LLM Guardrails Keep Failing (And How We Built Sub-35µs In-Process Tool Gating for AI Agents)

### Moving from slow 1,500ms prompt moderation classifiers and infinite agent retry loops to deterministic, in-process AST gating and zero-inconvenience pro bono security.

---

## 1. The Core Flaw in Modern AI Agent Safety

When autonomous agents (Claude Desktop, Cursor, LangChain, CrewAI, AutoGen) interact with real environments, they execute real shell commands, manipulate filesystems, invoke external APIs, and execute SQL queries.

However, existing safety tools treat AI guardrails as external chat filters:

1. **Slow Prompt Classifiers**: Tools like NeMo Guardrails or external cloud proxies take **800ms to 2,500ms** to evaluate an action via an LLM call. They are completely blind to what happens when the code actually hits Python or the OS.
2. **Infinite Hallucination Loops**: Hard exceptions crash pipelines with no recovery context, causing the agent to repeatedly retry the same malformed payload until token limits are exhausted.
3. **Secret Exfiltration**: Downstream tool errors and logs routinely echo unmasked API keys (`sk-proj-...`, `AKIA...`) back into the model's context window.

Safety mechanisms should not operate as slow external chat proxies. Agent execution requires **sub-millisecond, deterministic, in-process runtime boundaries**.

Today, we are launching **Bartholomew (BTP v3.0)** alongside **`mcp-proxy-guard`**: 100% open-source (Apache 2.0 / MIT) pro-bono security tooling for the AI developer community.

---

## 2. The Architecture: In-Process Execution Gateway

Bartholomew sits directly inside the agent's process memory or on the stdio boundary between MCP clients and servers:

```text
       [ MCP Client: Claude / Cursor ]
                      │
                      ▼  (Inbound JSON-RPC: tools/call)
   ┌────────────────────────────────────────────────────────┐
   │         BARTHOLOMEW INLINE SECURITY GATEWAY            │
   │                                                        │
   │  1. In-Flight Credential Redaction (OpenAI, AWS, Git)  │
   │  2. Sub-35µs Polyglot AST Syntax Tree Inspection       │
   │  3. In-Memory Micro-Rollback Snapshot (<5µs)           │
   └──────────────────────────┬─────────────────────────────┘
                              │
                 [ If Invariants Pass ] ──► [ OS / DB Runtime ]
                              │                       │
                 [ If Invariants Fail ]               ▼
                              │            (Output Scrubbing)
                              ▼                       │
               ┌────────────────────────┐             ▼
               │ Instant Micro-Rollback │    ┌─────────────────┐
               │ Zero Residual Damage   │    │ Chained Merkle  │
               │ Structured Recov Hint  │    │ Turn Receipt    │
               └────────────────────────┘    └─────────────────┘
```

---

## 3. How to Use It in 60 Seconds

### A. Protecting Model Context Protocol (Claude Desktop & Cursor)
Prepend `npx -y mcp-proxy-guard --` to your MCP server command in `claude_desktop_config.json`:

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

### B. Python universal package (`pip install btp-guard`)
```python
from btp_guard import Guard

guard = Guard(spend_cap=50.0)

@guard.protect
def run_query(sql: str):
    # Destructive mutations (DROP TABLE) are blocked in <35µs
    return db.execute(sql)

result = guard.check("rm -rf /var/data")
print(result["allowed"]) # False
```

### C. Cursor & VS Code Extension
Install directly from [Open VSX](https://open-vsx.org/extension/Bartholomew/bartholomew-guard-vscode) or search `Bartholomew` in your editor's Extensions sidebar:
```bash
cursor --install-extension Bartholomew.bartholomew-guard-vscode
```

---

## 4. The Pro Bono Open-Source Guarantee

The entire local execution gateway, AST syntax gating, in-flight secret scrubbing, and MCP proxy are **100% free and open-source forever (pro bono publico)**.

* **GitHub**: [https://github.com/ivegotahunnitonit/bartholomew](https://github.com/ivegotahunnitonit/bartholomew)
* **PyPI**: [https://pypi.org/project/btp-guard/3.0.0/](https://pypi.org/project/btp-guard/3.0.0/)
* **npm**: [https://www.npmjs.com/package/mcp-proxy-guard](https://www.npmjs.com/package/mcp-proxy-guard)
* **Live Sandbox & Store**: [https://bartholomew.info](https://bartholomew.info)
