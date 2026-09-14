"""
n8n AI Nodes + Bartholomew Guard
===================================
Guards every AI Agent node and Code node in an n8n workflow via
a Bartholomew webhook node. Drop this as a Code node or HTTP
Request node into any n8n AI workflow.

Setup in n8n:
  1. Add a "Code" node before any tool execution
  2. Paste the JavaScript snippet below
  3. Or use an "HTTP Request" node to call the /dify/gate endpoint

JavaScript Code node snippet (paste into n8n Code node):
─────────────────────────────────────────────────────────
const action = $input.first().json.action ?? $input.first().json.text;

const response = await fetch('http://35.222.210.105:8080/dify/gate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: action,
    agent_id: 'n8n-workflow',
    spend_usd: 0.0
  })
});

if (!response.ok) {
  throw new Error(`Bartholomew blocked: ${await response.text()}`);
}

const result = await response.json();
return [{ json: { ...result, original_input: $input.first().json } }];
─────────────────────────────────────────────────────────

Python equivalent (for n8n Python Code nodes or local testing):
"""

import os
import httpx
from btp_guard import Guard

guard = Guard(spend_cap=100.0)

BARTHOLOMEW_ENDPOINT = os.getenv(
    "BARTHOLOMEW_MCP_URL", "http://35.222.210.105:8080"
)


def n8n_code_node_gate(input_data: dict) -> dict:
    """
    Drop-in replacement for n8n Code node execution with Bartholomew gating.
    Intercepts the action/command before any downstream node runs it.

    Usage in n8n:
        - Add a "Code" node (Python mode) before your AI Agent node
        - Call this function with the incoming data
    """
    action = (
        input_data.get("action")
        or input_data.get("text")
        or input_data.get("command")
        or str(input_data)
    )

    result = guard.check(action, agent_id="n8n-workflow")

    if not result["allowed"]:
        return {
            "error": True,
            "blocked": True,
            "reason": result["reason"],
            "bartholomew_verdict": result["verdict"],
            "latency_us": result["latency_us"]
        }

    return {
        "error": False,
        "blocked": False,
        "allowed": True,
        "bartholomew_verdict": "ALLOW",
        "latency_us": result["latency_us"],
        "original_data": input_data
    }


async def n8n_http_gate(action: str, agent_id: str = "n8n-agent") -> dict:
    """
    HTTP-based gate — use this when your n8n instance can't import Python packages.
    Configure an n8n HTTP Request node to call this endpoint.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{BARTHOLOMEW_ENDPOINT}/dify/gate",
            json={"action": action, "agent_id": agent_id}
        )
        if resp.status_code == 403:
            return {"allowed": False, "reason": resp.json().get("detail", "Blocked")}
        return resp.json()


# ── n8n workflow JSON export (import this into n8n) ────────────────
N8N_WORKFLOW_TEMPLATE = {
    "name": "Bartholomew-Secured AI Workflow",
    "nodes": [
        {
            "id": "trigger",
            "name": "Chat Trigger",
            "type": "n8n-nodes-base.chatTrigger",
            "position": [250, 300]
        },
        {
            "id": "btp-gate",
            "name": "Bartholomew Security Gate",
            "type": "n8n-nodes-base.httpRequest",
            "position": [500, 300],
            "parameters": {
                "url": "http://35.222.210.105:8080/dify/gate",
                "method": "POST",
                "body": {
                    "action": "={{ $json.chatInput }}",
                    "agent_id": "n8n-agent"
                }
            }
        },
        {
            "id": "ai-agent",
            "name": "AI Agent",
            "type": "@n8n/n8n-nodes-langchain.agent",
            "position": [750, 300],
            "notes": "Only runs if Bartholomew gate allows the action"
        }
    ],
    "connections": {
        "trigger": {"main": [["btp-gate"]]},
        "btp-gate": {"main": [["ai-agent"]]}
    }
}


if __name__ == "__main__":
    # Simulate n8n Code node execution
    test_inputs = [
        {"action": "Summarize the latest report and email it to the team"},
        {"action": "DELETE FROM users WHERE id > 0"},
        {"command": "ls -la /home/user"},
        {"text": "import subprocess; subprocess.run('rm -rf /', shell=True)"},
    ]

    for inp in test_inputs:
        result = n8n_code_node_gate(inp)
        status = "✅" if not result.get("blocked") else "❌"
        print(f"{status} {list(inp.values())[0][:50]!r} → {result.get('bartholomew_verdict', 'BLOCKED')}")
