"""
Grok (xAI) + Bartholomew Guard
================================
Guards every tool call made by a Grok-powered autonomous agent via
the xAI API (OpenAI-compatible endpoint).

Install:
    pip install btp-guard openai
    export XAI_API_KEY=xai-...
"""

import os
import json
from openai import OpenAI
from btp_guard import Guard

guard = Guard(spend_cap=100.0)

client = OpenAI(
    api_key=os.environ.get("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

GROK_MODEL = os.getenv("GROK_MODEL", "grok-2-latest")


# ── Bartholomew-gated tools ────────────────────────────────────────

@guard.protect
def web_search(query: str) -> dict:
    """Grok's live web search — Bartholomew blocks prompt injection."""
    return {"results": f"[Search results for: {query}]", "gated": True}


@guard.protect
def execute_code(code: str, language: str = "python") -> dict:
    """Code execution — Bartholomew blocks rm -rf, os.system, etc."""
    result = guard.evaluate_ast(code, language)
    if not result["allowed"]:
        return {"error": f"Blocked: {result['violations']}", "allowed": False}
    return {"output": "[sandboxed execution]", "allowed": True}


@guard.protect
def query_database(sql: str) -> dict:
    """SQL tool — blocks DROP TABLE, TRUNCATE, injection."""
    return {"rows": [], "sql": sql, "gated_by": "bartholomew"}


# ── Grok agent loop ────────────────────────────────────────────────

def run_grok_agent(user_request: str, max_turns: int = 5):
    """
    Runs a Grok autonomous agent with Bartholomew security gating.
    Grok's tool-use API is OpenAI-compatible.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for real-time information",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string", "description": "Search query"}},
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "execute_code",
                "description": "Execute Python or JavaScript code",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "language": {"type": "string", "enum": ["python", "javascript"]}
                    },
                    "required": ["code"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_database",
                "description": "Run a SQL query against the database",
                "parameters": {
                    "type": "object",
                    "properties": {"sql": {"type": "string"}},
                    "required": ["sql"]
                }
            }
        }
    ]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a Grok autonomous agent secured by Bartholomew Trust Protocol. "
                "All tool calls are security-gated. Proceed with tasks autonomously."
            )
        },
        {"role": "user", "content": user_request}
    ]

    TOOL_MAP = {
        "web_search": web_search,
        "execute_code": execute_code,
        "query_database": query_database,
    }

    for turn in range(max_turns):
        response = client.chat.completions.create(
            model=GROK_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            print(f"[Grok Agent] Final answer: {msg.content}")
            break

        for tc in msg.tool_calls:
            fn_name = tc.function.name
            args = json.loads(tc.function.arguments)
            print(f"[Grok Agent] → {fn_name}({args})")

            fn = TOOL_MAP.get(fn_name)
            result = fn(**args) if fn else {"error": "Unknown tool"}
            print(f"[Bartholomew] ✓ {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result)
            })


if __name__ == "__main__":
    run_grok_agent(
        "Research the latest AI agent frameworks released in 2025, "
        "then query the database for our existing integrations."
    )
