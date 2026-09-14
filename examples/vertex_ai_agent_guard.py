"""
Google Vertex AI Agents + Bartholomew Guard
============================================
Guards every function call made by a Vertex AI Agent (Reasoning Engine)
or Gemini function-calling workflow. Bartholomew intercepts at the
function dispatch layer before execution.

Install:
    pip install btp-guard google-cloud-aiplatform
    gcloud auth application-default login
"""

import os
import json
from btp_guard import Guard

guard = Guard(spend_cap=200.0)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "acn-26670")
LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")
MODEL = os.getenv("VERTEX_MODEL", "gemini-2.0-flash-001")


# ── Bartholomew-gated tools ────────────────────────────────────────

@guard.protect
def execute_bigquery(sql: str, dataset: str = "main") -> dict:
    """Runs BigQuery SQL — Bartholomew blocks DROP, TRUNCATE, injection."""
    return {"rows": [], "sql": sql, "dataset": dataset, "gated": True}


@guard.protect
def call_cloud_function(function_name: str, payload: dict) -> dict:
    """Invokes a Cloud Function — Bartholomew validates payload."""
    return {"function": function_name, "payload": payload, "status": "gated"}


@guard.protect
def write_to_gcs(bucket: str, path: str, content: str) -> dict:
    """Writes to GCS — Bartholomew prevents sensitive data leaks."""
    result = guard.check(content)
    if not result["allowed"]:
        return {"error": f"Blocked: {result['reason']}"}
    return {"bucket": bucket, "path": path, "status": "written"}


# ── Vertex AI Reasoning Engine / Gemini function calling loop ──────

def run_vertex_agent(user_request: str, max_turns: int = 5):
    """
    Runs a Vertex AI / Gemini agent with Bartholomew gating.
    Compatible with Gemini function calling and Vertex AI Reasoning Engine.
    """
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    except ImportError:
        raise ImportError("pip install google-generativeai")

    tools = [
        {
            "function_declarations": [
                {
                    "name": "execute_bigquery",
                    "description": "Execute a BigQuery SQL query",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sql": {"type": "string", "description": "SQL query to execute"},
                            "dataset": {"type": "string", "description": "BigQuery dataset name"}
                        },
                        "required": ["sql"]
                    }
                },
                {
                    "name": "call_cloud_function",
                    "description": "Invoke a Google Cloud Function",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "function_name": {"type": "string"},
                            "payload": {"type": "object"}
                        },
                        "required": ["function_name", "payload"]
                    }
                },
                {
                    "name": "write_to_gcs",
                    "description": "Write content to Google Cloud Storage",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "bucket": {"type": "string"},
                            "path": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["bucket", "path", "content"]
                    }
                }
            ]
        }
    ]

    TOOL_MAP = {
        "execute_bigquery": execute_bigquery,
        "call_cloud_function": call_cloud_function,
        "write_to_gcs": write_to_gcs,
    }

    model = genai.GenerativeModel(model_name=MODEL, tools=tools)
    chat = model.start_chat()

    response = chat.send_message(user_request)

    for turn in range(max_turns):
        if not response.candidates[0].content.parts:
            break

        fn_call = None
        for part in response.candidates[0].content.parts:
            if hasattr(part, "function_call") and part.function_call:
                fn_call = part.function_call
                break

        if not fn_call:
            text = response.candidates[0].content.parts[0].text
            print(f"[Vertex Agent] {text}")
            break

        fn_name = fn_call.name
        args = dict(fn_call.args)
        print(f"[Vertex Agent] → {fn_name}({args})")

        fn = TOOL_MAP.get(fn_name)
        result = fn(**args) if fn else {"error": "Unknown tool"}
        print(f"[Bartholomew] ✓ {result}")

        response = chat.send_message(
            genai.protos.Part(
                function_response=genai.protos.FunctionResponse(
                    name=fn_name,
                    response={"result": result}
                )
            )
        )


if __name__ == "__main__":
    run_vertex_agent(
        "Query our BigQuery sales dataset for the top 10 products by revenue this month, "
        "then save the results to GCS bucket 'reports' as 'top_products.json'."
    )
