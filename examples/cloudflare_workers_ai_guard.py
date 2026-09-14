"""
Cloudflare Workers AI + Bartholomew Guard
==========================================
Bartholomew gates every AI tool call inside a Cloudflare Worker via
the MCP gateway. Agents running on Workers AI pay micropayments
automatically through L402 Lightning invoices.

Install (wrangler project):
    npm install btp-guard-mcp   # JS/TS shim (see packages/node)
    wrangler deploy
"""

# Python equivalent for local dev / test — deploy via wrangler for prod.
# See: wrangler.toml snippet at bottom of file.

import os
import httpx
import asyncio
from btp_guard import Guard

BARTHOLOMEW_MCP_ENDPOINT = os.getenv(
    "BARTHOLOMEW_MCP_URL", "http://35.222.210.105:8080"
)

guard = Guard(spend_cap=50.0)


async def run_workers_ai_tool(prompt: str, tool_name: str = "execute_database_query"):
    """
    Simulates a Cloudflare Workers AI agent calling a Bartholomew-gated tool.
    In production this runs inside a Cloudflare Worker via the MCP binding.
    """
    # 1. Pre-flight AST check (sub-35µs local gate)
    result = guard.check(prompt)
    if not result["allowed"]:
        return {"error": f"Blocked by Bartholomew: {result['reason']}"}

    # 2. Call the hosted Bartholomew MCP gateway
    async with httpx.AsyncClient(timeout=30) as client:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": {"query": prompt}
            }
        }
        try:
            resp = await client.post(
                f"{BARTHOLOMEW_MCP_ENDPOINT}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            return resp.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 402:
                # L402 Payment Required — agent pays Lightning invoice
                invoice = e.response.headers.get("WWW-Authenticate", "")
                return {"status": "payment_required", "invoice": invoice}
            raise


# ── wrangler.toml snippet ──────────────────────────────────────────
WRANGLER_TOML_SNIPPET = """
# wrangler.toml — add to your Cloudflare Workers project
[[ai]]
binding = "AI"

[vars]
BARTHOLOMEW_MCP_URL = "http://35.222.210.105:8080"
BTP_SILENT = "true"

# MCP remote binding (Cloudflare AI Gateway)
[[mcp_servers]]
name = "bartholomew"
url = "http://35.222.210.105:8080"
"""

if __name__ == "__main__":
    result = asyncio.run(
        run_workers_ai_tool("SELECT * FROM users WHERE role = 'admin'")
    )
    print(result)
