# Bartholomew Model Context Protocol (MCP) Security Gateway

> Standard transparent stdio/SSE proxy gateway for Anthropic Claude Desktop, Cursor, and Zed. Intercepts incoming `tools/call` JSON-RPC requests, evaluates AST invariants in <50 µs, and returns RFC -32000 errors on dangerous payloads.

## 🚀 Setup with Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "secure-postgres": {
      "command": "python",
      "args": [
        "-m", "integrations.mcp.mcp_middleware",
        "--server-cmd", "npx -y @modelcontextprotocol/server-postgres postgresql://localhost/mydb"
      ]
    }
  }
}
```
