"""
Meta Llama (via Ollama / Together AI / Replicate) + Bartholomew Guard
======================================================================
Guards every tool call made by a Llama-powered autonomous agent.
Works with llama.cpp, Ollama, Together AI, Replicate, and any
OpenAI-compatible Llama endpoint.

Install:
    pip install btp-guard ollama openai
"""

import os
from btp_guard import Guard, secure_tool

guard = Guard(spend_cap=100.0)

LLAMA_ENDPOINT = os.getenv("LLAMA_ENDPOINT", "http://localhost:11434/v1")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "llama3.1:70b")


# ── Guarded tools the Llama agent can call ─────────────────────────

@guard.protect
def execute_shell_command(command: str) -> dict:
    """Bartholomew gates this — blocks rm -rf, secret leaks, etc."""
    import subprocess
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return {"stdout": result.stdout, "returncode": result.returncode}


@guard.protect
def query_database(sql: str) -> dict:
    """Blocks DROP TABLE, TRUNCATE, and injection attempts."""
    return {"rows": [], "query": sql, "status": "gated_by_bartholomew"}


# ── Llama agent loop ───────────────────────────────────────────────

def run_llama_agent(user_request: str):
    """
    Runs a Llama autonomous agent with Bartholomew security gating.
    Works with Ollama locally or Together/Replicate remotely.
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("pip install openai")

    client = OpenAI(
        base_url=LLAMA_ENDPOINT,
        api_key=os.getenv("TOGETHER_API_KEY", "ollama"),  # "ollama" for local
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "execute_shell_command",
                "description": "Run a shell command (Bartholomew-gated)",
                "parameters": {
                    "type": "object",
                    "properties": {"command": {"type": "string"}},
                    "required": ["command"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_database",
                "description": "Run a SQL query (Bartholomew-gated)",
                "parameters": {
                    "type": "object",
                    "properties": {"sql": {"type": "string"}},
                    "required": ["sql"]
                }
            }
        }
    ]

    messages = [{"role": "user", "content": user_request}]
    response = client.chat.completions.create(
        model=LLAMA_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    msg = response.choices[0].message
    if msg.tool_calls:
        for tc in msg.tool_calls:
            fn = tc.function.name
            import json
            args = json.loads(tc.function.arguments)
            print(f"[Llama Agent] Calling tool: {fn}({args})")
            if fn == "execute_shell_command":
                result = execute_shell_command(**args)
            elif fn == "query_database":
                result = query_database(**args)
            print(f"[Bartholomew] Result: {result}")
    else:
        print(f"[Llama Agent] {msg.content}")


if __name__ == "__main__":
    run_llama_agent("List all files in /tmp and show the 10 largest ones")
