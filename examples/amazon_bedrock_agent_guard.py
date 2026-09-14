"""
Amazon Bedrock Agents + Bartholomew Guard
==========================================
Guards every action group call made by a Bedrock autonomous agent.
Bartholomew intercepts at the Lambda action group layer — before any
tool executes — providing sub-35µs AST gating.

Install:
    pip install btp-guard boto3
    export AWS_DEFAULT_REGION=us-east-1
"""

import os
import json
import boto3
from btp_guard import Guard

guard = Guard(spend_cap=200.0)

bedrock_agent = boto3.client(
    "bedrock-agent-runtime",
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)


# ── Lambda action group handler (deploy this as your Bedrock Lambda) ──

def lambda_handler(event: dict, context=None) -> dict:
    """
    Bedrock Agent action group Lambda handler with Bartholomew gating.
    Deploy this as the Lambda function for your Bedrock Agent action group.
    """
    api_path = event.get("apiPath", "")
    request_body = event.get("requestBody", {})
    parameters = request_body.get("content", {}).get("application/json", {}).get("properties", [])

    # Extract parameters
    params = {p["name"]: p["value"] for p in parameters}
    action_input = params.get("query") or params.get("command") or str(params)

    # Bartholomew gate — sub-35µs
    check = guard.check(action_input)
    if not check["allowed"]:
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event.get("actionGroup"),
                "apiPath": api_path,
                "httpMethod": event.get("httpMethod"),
                "httpStatusCode": 403,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps({
                            "error": "Blocked by Bartholomew Trust Protocol",
                            "reason": check["reason"],
                            "latency_us": check["latency_us"]
                        })
                    }
                }
            }
        }

    # Tool dispatch
    result = _dispatch_tool(api_path, params)

    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup"),
            "apiPath": api_path,
            "httpMethod": event.get("httpMethod"),
            "httpStatusCode": 200,
            "responseBody": {
                "application/json": {
                    "body": json.dumps(result)
                }
            }
        }
    }


def _dispatch_tool(api_path: str, params: dict) -> dict:
    """Route to actual tool implementations."""
    if api_path == "/execute-query":
        return {"rows": [], "query": params.get("query"), "status": "ok"}
    elif api_path == "/run-command":
        return {"output": f"[safe exec]: {params.get('command')}", "status": "ok"}
    return {"status": "unknown_tool", "path": api_path}


# ── Invoke a Bedrock Agent with Bartholomew ────────────────────────

def run_bedrock_agent(user_prompt: str, agent_id: str, agent_alias_id: str):
    """
    Invokes an Amazon Bedrock Agent. Tool calls are automatically
    gated by the Lambda handler above before execution.
    """
    import uuid
    session_id = str(uuid.uuid4())

    response = bedrock_agent.invoke_agent(
        agentId=agent_id,
        agentAliasId=agent_alias_id,
        sessionId=session_id,
        inputText=user_prompt
    )

    output = ""
    for event in response.get("completion", []):
        if "chunk" in event:
            output += event["chunk"]["bytes"].decode()

    print(f"[Bedrock Agent] {output}")
    return output


if __name__ == "__main__":
    # Local test of the Lambda gate
    test_event = {
        "actionGroup": "DatabaseActions",
        "apiPath": "/execute-query",
        "httpMethod": "POST",
        "requestBody": {
            "content": {
                "application/json": {
                    "properties": [
                        {"name": "query", "value": "SELECT * FROM users LIMIT 10"}
                    ]
                }
            }
        }
    }
    result = lambda_handler(test_event)
    print(json.dumps(result, indent=2))
