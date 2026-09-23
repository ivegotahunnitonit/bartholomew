# Bartholomew .cursorrules Directory Submission Pack
## For cursorlist.com, cursorrules.org, and awesome-cursorrules

### Listing Metadata
- **Title**: Bartholomew Agentic Runtime Protection (ARP) & Security Guardrules
- **Slug**: `bartholomew-btp-security`
- **Category**: Security, Testing, Agent Guardrails, DevSecOps
- **Author**: Autonomous Circularity Labs / Itsub Alemayehu
- **GitHub**: https://github.com/ivegotahunnitonit/bartholomew
- **Website**: https://bartholomew.info
- **License**: MIT
- **Tags**: `security`, `guardrails`, `ai-safety`, `anti-exfiltration`, `mcp-guard`, `cursorrules`, `zero-trust`

---

### Short Description (for search cards):
> Protect your Cursor AI agent from catastrophic terminal commands (`rm -rf`, `DROP TABLE`), credential leaks (`.env`, `id_rsa`), and out-of-boundary tool calls with sub-35µs in-process deterministic AST verification.

---

### Full Description (for listing detail page):
Bartholomew Trust Protocol (BTP v5.4) provides enterprise-grade runtime security and AST guardrails for Cursor AI. 

When Cursor is given permission to run terminal commands, write scripts, or execute tools, rogue hallucinated actions or indirect prompt injections can accidentally delete local file trees or leak private keys.

This `.cursorrules` file acts as a sovereign execution sentinel:
1. **Zero Secret Leakage**: Restricts Cursor from reading, printing, or exfiltrating `.env*`, `.pem`, `.key`, or RSA/Ed25519 credentials.
2. **Terminal Invariant Defense**: Instantly blocks destructive patterns like `rm -rf /`, `DROP TABLE`, and unverified shell piping `curl | sh`.
3. **Canonical Security Integration**: Directs the agent to automatically protect generated Python functions with `@secure_tool` and Node scripts with `btp-guard`.

---

### Ready-to-Copy .cursorrules:

```ini
# ==============================================================================
# Bartholomew Trust Protocol (BTP v5.4) - Universal Cursor Rules (.cursorrules)
# Tags: security, guardrails, agentic-runtime-protection, anti-hallucination, privacy
# Source: https://github.com/ivegotahunnitonit/bartholomew
# ==============================================================================

[ai]
description = "Deterministic runtime protection, secret exfiltration defense, and AST safety gating."
system_prompt_guard = """
You are an autonomous AI coding assistant operating under the Bartholomew Trust Protocol (BTP v5.4) local execution boundary.
Strict Invariants:
1. NEVER attempt to read, write, print, or exfiltrate secrets, .env files, private keys (id_rsa, id_ed25519, pem, key), or API tokens.
2. NEVER execute destructive terminal commands (such as rm -rf, mkfs, dd if=, format) or dangerous uninspected pipes (curl | sh, wget | sh).
3. Confine all automated tool calls, file writes, and code changes to the active workspace project boundaries.
4. When writing code that invokes external tools, APIs, or database queries, use the Bartholomew zero-latency guardrail:
   - Python: from btp_guard import Guard, secure_tool
   - TypeScript/Node: import { scrubSensitiveCredentials } from 'btp-guard'
   - MCP: Route external tool calls through the local Bartholomew MCP gateway.
"""

[terminal]
blocked_patterns = [
    "rm -rf /",
    "rm -rf ~",
    "rm -rf *",
    "DROP TABLE",
    "DROP DATABASE",
    "DROP SCHEMA",
    "TRUNCATE TABLE",
    "curl * | sh",
    "wget * | sh",
    "chmod 777",
    "chown -R",
    ":(){ :|:& };:"
]

[privacy]
protected_paths = [
    ".env*",
    "**/*secret*",
    "**/*credential*",
    "**/*id_rsa*",
    "**/*id_ed25519*",
    "**/*.pem",
    "**/*.key",
    "**/*.pfx",
    "**/.btp_keystone.json"
]

[code_quality]
enforce_in_memory_validation = true
max_spend_usd = 50.0
audit_trail = "Ed25519-Signed-Merkle-Receipts"
```

---

### 1-Click CLI Installation
Developers can also install this automatically into any project via:
```bash
npx btp-guard init
```
