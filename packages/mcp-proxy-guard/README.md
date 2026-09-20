# **mcp-proxy-guard**
### **Sub-35µs In-Process Security Proxy & Credential Scrubber for Model Context Protocol (MCP)**

[![npm version](https://img.shields.io/npm/v/mcp-proxy-guard.svg?style=for-the-badge&color=blue)](https://www.npmjs.com/package/mcp-proxy-guard)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Latency](https://img.shields.io/badge/Latency-%3C35%C2%B5s-6366f1.svg?style=for-the-badge)](https://bartholomew.info)

A zero-dependency, lightweight security proxy wrapper for **any** Model Context Protocol (MCP) server running in **Claude Desktop**, **Cursor**, or **Windsurf**.

---

## **Why Do You Need This?**

When you connect Claude Desktop or Cursor to an MCP server (filesystem, terminal, sqlite, postgres), the AI agent has raw access to execute commands on your machine or database.

Prompt guardrails and cloud filters **do not inspect tool execution**. If an agent hallucinates or encounters prompt injection, it can execute:
- `rm -rf /` or `DROP TABLE accounts`
- Exfiltrate API keys (`sk-proj-...`, `AKIA...`) or `.env` files across tool logs.

`mcp-proxy-guard` wraps your MCP server, intercepting JSON-RPC 2.0 messages across `stdio` in **under 35 microseconds**:
1. **Destructive Tool Veto**: Intercepts and blocks destructive arguments (`rm -rf`, `mkfs`, `DROP TABLE`, `TRUNCATE`, `/etc/shadow`).
2. **In-Flight Secret Redaction**: Scrubs OpenAI, Anthropic, AWS, GitHub, Stripe, and private keys from tool inputs and outputs.
3. **Zero Configuration**: Simply prepend `npx -y mcp-proxy-guard --` to your existing MCP server command.

---

## **Quickstart (Claude Desktop)**

Open your `claude_desktop_config.json` and wrap any server with `mcp-proxy-guard`:

### **Before:**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/projects"]
    }
  }
}
```

### **After (Protected in <35µs):**
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

## **CLI Usage**

```bash
# Run self-test verification
npx mcp-proxy-guard test

# Inspect active security status
npx mcp-proxy-guard status

# Activate Pro ($49/mo) or Enterprise ($199/mo) license
npx mcp-proxy-guard activate
```

---

## **Programmatic API**

```typescript
import { evaluateToolCall, scrubSecrets } from 'mcp-proxy-guard';

// 1. In-process tool check
const verdict = evaluateToolCall('execute_sql', { query: 'DROP TABLE users;' });
console.log(verdict.allowed); // false
console.log(verdict.reason);  // "[MCP-PROXY-GUARD VETO] Destructive pattern intercepted..."

// 2. Secret scrubber
const scrubbed = scrubSecrets({ payload: "token sk-proj-1234567890abcdef" });
console.log(scrubbed.data.payload); // "token [REDACTED_OPENAI_KEY]"
```

---

## **Enterprise & Team Licensing**

* **Community Tier (Pro Bono)**: 100% Free & Open-Source forever for individual developers, researchers, and open-source projects.
* **Pro Tier ($49/mo)**: Cross-agent cloud policy sync, priority support, and multi-IDE management.
* **Enterprise Tier ($199/mo)**: Certified SOC 2 Type II / ISO 27001 auditor evidence packs & centralized team SIEM export.
* Storefront: [https://bartholomew.info/store/](https://bartholomew.info/store/)

---

© 2026 Bartholomew AI & Contributors. Distributed under the MIT License.
