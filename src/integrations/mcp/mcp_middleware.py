"""
Bartholomew MCP Security Middleware & Proxy
===========================================
Official Model Context Protocol (MCP) transparent stdio proxy.
Intercepts all incoming JSON-RPC 2.0 `tools/call` requests from Claude Desktop
and Cursor, evaluates AST invariants in <50 µs, and returns RFC -32000 errors
on unsafe payloads before touching downstream tool servers.

Claude Desktop Config (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "secure-postgres": {
      "command": "python",
      "args": [
        "-m", "btp_guard.mcp",
        "--server-cmd", "npx -y @modelcontextprotocol/server-postgres postgresql://localhost/mydb"
      ]
    }
  }
}
```
"""

import sys
import os
import json
import time

try:
    from src.mcp_gateway import MCPProxyGateway
except ImportError:
    from btp_guard.src.mcp_gateway import MCPProxyGateway


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Bartholomew MCP Security Gateway")
    parser.add_argument("--server-cmd", required=True, help="Downstream MCP command to wrap")
    parser.add_argument("--spend-cap", type=float, default=500.0, help="Spend limit in USD")
    args = parser.parse_args()

    gateway = MCPProxyGateway(spend_cap_usd=args.spend_cap)
    print(f"[*] Starting Bartholomew MCP Tier-0 Proxy for: {args.server_cmd}", file=sys.stderr)
    gateway.run_stdio_proxy(args.server_cmd)


if __name__ == "__main__":
    main()
