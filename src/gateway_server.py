"""
Bartholomew Live Public Agent Gateway & Zero-Install Cloud Interceptor (BTP v5.4.16)
===================================================================================
Production-ready FastAPI cloud gateway supporting:
  - `POST /v1/eval`: Zero-install cloud evaluation endpoint for Grok bot, Muse, Meta AI,
    custom chatbots, and webhooks. Sub-35us AST gating + Ed25519 receipts.
  - `POST /v1/chat/completions`: Transparent reverse proxy for xAI Grok, Meta AI (Llama),
    OpenAI, and Muse with in-flight tool-call AST & secret inspection.
  - `POST /v1/webhooks/bot`: Webhook receiver for event-driven bots (Slack, Discord, X, Muse).
  - `POST /v1/evaluate`: M2M agent pre-flight evaluation & Ed25519 attestation.
  - `POST /v1/verify`: Offline-compatible attestation verification.
  - `POST /mcp`: Remote HTTP JSON-RPC 2.0 MCP endpoint for cloud bot platforms.
  - `GET /.well-known/ai-plugin.json` & `GET /openapi.json`: 1-click Custom Action schemas.
  - `GET /.well-known/btp.json`: Machine-readable agent discovery manifest.
"""

import os
import sys
import time
import json
import httpx
from typing import Dict, Any, Optional, List, Union

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

sys.path.insert(0, os.path.abspath("."))
from src.trust_protocol import BartholomewTrustAuthority, IndependentTrustVerifier, rfc8785_canonicalize
from src.declarative_policy_engine import DeclarativePolicyEngine
from src.polyglot_ast_validator import PolyglotASTValidator
from src.secret_masker import SecretVaultMasker
from src.btp_manifest import generate_manifest

app = FastAPI(
    title="Bartholomew Zero-Install Cloud Gateway",
    version="5.4.16",
    description="Zero-install cloud execution gateway and AST invariant interceptor for Grok bot, Muse, Meta AI, and autonomous agent swarms."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Trust Authority & Policy Engine
authority = BartholomewTrustAuthority(ttl_seconds=300)
policy_engine = DeclarativePolicyEngine("policies/default_security_policy.yaml")
node_start_time = time.time()
metrics_counters = {
    "total_evals": 0,
    "total_allows": 0,
    "total_denies": 0,
    "total_proxied_turns": 0,
    "bot_requests": {
        "grok": 0,
        "muse": 0,
        "meta_ai": 0,
        "universal": 0
    }
}


# --- Pydantic Request Models ---

class EvaluateRequest(BaseModel):
    agent_id: str = Field(..., json_schema_extra={"example": "agent-swarm-worker-01"})
    action_type: str = Field(..., json_schema_extra={"example": "EXECUTE_COMMAND"})
    payload: Dict[str, Any] = Field(..., json_schema_extra={"example": {"command": "git status"}})
    target_recipient: Optional[str] = "Agent-Universal-Recipient"


class VerifyRequest(BaseModel):
    attestation_receipt: Dict[str, Any]
    candidate_payload: Dict[str, Any]
    trusted_root_pubkey: Optional[str] = None


class BotEvalRequest(BaseModel):
    """
    Zero-install evaluation payload used by Grok bot, Muse, Meta AI, and custom bots.
    Accepts either an action string, code snippet, SQL query, or structured tool arguments.
    """
    bot_type: Optional[str] = Field("universal", json_schema_extra={"example": "grok"})
    action: Optional[str] = Field(None, json_schema_extra={"example": "execute_command"})
    tool: Optional[str] = Field(None, json_schema_extra={"example": "bash"})
    arguments: Optional[Dict[str, Any]] = Field(default_factory=dict, json_schema_extra={"example": {"command": "ls -la"}})
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict)
    code: Optional[str] = Field(None, json_schema_extra={"example": "import os; os.system('ls')"})
    sql: Optional[str] = Field(None, json_schema_extra={"example": "SELECT * FROM users"})
    agent_id: Optional[str] = Field("cloud-bot-agent", json_schema_extra={"example": "grok-prod-bot"})


class BotWebhookRequest(BaseModel):
    event: str = Field("tool_call", json_schema_extra={"example": "tool_call"})
    bot: str = Field("grok", json_schema_extra={"example": "grok"})
    tool: Optional[str] = Field("bash")
    payload: Dict[str, Any] = Field(default_factory=dict)
    agent_id: Optional[str] = Field("webhook-agent")


# --- Core Helper Evaluation Logic ---

def evaluate_bot_action(
    bot_type: str,
    tool_name: str,
    args: Dict[str, Any],
    agent_id: str
) -> Dict[str, Any]:
    """
    Performs sub-35 microsecond multi-language AST gating, secret scrubbing,
    and declarative policy verification on any bot tool action.
    """
    t0 = time.perf_counter()
    metrics_counters["total_evals"] += 1
    bot_key = bot_type.lower() if bot_type.lower() in metrics_counters["bot_requests"] else "universal"
    metrics_counters["bot_requests"][bot_key] += 1

    # 1. Scrub secrets from arguments
    sanitized_args = {}
    scrubbed_any = False
    for k, v in args.items():
        if isinstance(v, str):
            masked_val, detected, _ = SecretVaultMasker.mask_text(v)
            if detected:
                scrubbed_any = True
            sanitized_args[k] = masked_val
        else:
            sanitized_args[k] = v

    # 2. Extract code, command, or query to check for dangerous invariants
    target_snippet = ""
    for candidate_key in ["command", "cmd", "code", "script", "query", "sql"]:
        if candidate_key in args and isinstance(args[candidate_key], str):
            target_snippet = args[candidate_key]
            break

    if not target_snippet and args:
        # Concatenate string values if no specific key matched
        target_snippet = " ".join([str(v) for v in args.values() if isinstance(v, str)])

    # 3. Polyglot AST / Shell Invariant Validation
    is_safe = True
    reason = "BTP invariant checks passed"
    if target_snippet:
        is_safe, msg, _ = PolyglotASTValidator.validate_code(target_snippet)
        if not is_safe:
            reason = msg

    # 4. Declarative Policy Evaluation
    if is_safe:
        policy_allowed, policy_reason, _ = policy_engine.evaluate_payload(sanitized_args)
        if not policy_allowed:
            is_safe = False
            reason = policy_reason

    # 5. Ed25519 Cryptographic Attestation
    verdict = "ALLOW" if is_safe else "DENY"
    if is_safe:
        metrics_counters["total_allows"] += 1
    else:
        metrics_counters["total_denies"] += 1

    receipt = authority.evaluate_intent(
        agent_id=agent_id,
        action_type=f"BOT_TOOL_CALL:{tool_name.upper()}",
        payload=sanitized_args,
        target_recipient=f"{bot_type.upper()}_RUNTIME"
    )
    receipt["attestation"]["verdict"] = verdict
    receipt["attestation"]["reason"] = reason
    canonical_bytes = rfc8785_canonicalize(receipt["attestation"])
    receipt["signature"] = authority.private_key.sign(canonical_bytes).hex()

    dt_us = (time.perf_counter() - t0) * 1_000_000

    return {
        "allowed": is_safe,
        "verdict": verdict,
        "reason": reason,
        "bot_type": bot_type,
        "tool": tool_name,
        "sanitized_arguments": sanitized_args,
        "secret_scrubbed": scrubbed_any,
        "latency_us": round(dt_us, 2),
        "receipt": receipt
    }


# --- Endpoints ---

@app.get("/.well-known/btp.json")
@app.get("/v1/manifest")
def get_manifest():
    """Serves machine-readable service discovery manifest for autonomous agents."""
    return generate_manifest()


@app.get("/.well-known/ai-plugin.json")
def get_ai_plugin_manifest():
    """Manifest for Grok, Custom GPTs, and Muse cloud actions."""
    return {
        "schema_version": "v1",
        "name_for_human": "Bartholomew Trust Protocol",
        "name_for_model": "bartholomew_guard",
        "description_for_human": "In-process and cloud runtime execution guard for AI agents. Prevents destructive commands, secret leaks, and SQL mutations.",
        "description_for_model": "Evaluates tool actions, bash commands, SQL queries, and code in sub-35us before execution. Returns ALLOW or DENY.",
        "auth": {"type": "none"},
        "api": {
            "type": "openapi",
            "url": "/openapi.json"
        },
        "logo_url": "https://bartholomew.info/logo.png",
        "contact_email": "itsub@bartholomew.info",
        "legal_info_url": "https://bartholomew.info/terms"
    }


@app.get("/")
@app.get("/healthz")
def get_health():
    uptime = time.time() - node_start_time
    return {
        "status": "HEALTHY",
        "service": "Bartholomew Cloud Execution Gateway",
        "protocol": "BTP/5.4.16",
        "supported_bots": ["grok", "muse", "meta_ai", "openai", "claude"],
        "authority_public_key": authority.public_key_hex,
        "policy_id": policy_engine.policy_id,
        "rules_active": len(policy_engine.rules),
        "uptime_seconds": round(uptime, 2),
        "metrics": metrics_counters
    }


@app.get("/v1/trust-root")
def get_trust_root():
    return {
        "protocol_version": "BTP/5.4.16",
        "authority_pubkey": authority.public_key_hex,
        "ttl_seconds": authority.ttl_seconds,
        "policy_id": policy_engine.policy_id,
        "active_rules_count": len(policy_engine.rules)
    }


@app.post("/v1/eval")
def evaluate_bot_call(req: BotEvalRequest):
    """
    Zero-install evaluation endpoint for Grok bot, Muse, Meta AI, and web agents.
    Inspects tool arguments, code, commands, or SQL against AST security rules in sub-35us.
    """
    tool_name = req.tool or req.action or "general_execution"
    combined_args = dict(req.arguments or {})
    if req.payload:
        combined_args.update(req.payload)
    if req.code:
        combined_args["code"] = req.code
    if req.sql:
        combined_args["sql"] = req.sql

    result = evaluate_bot_action(
        bot_type=req.bot_type or "universal",
        tool_name=tool_name,
        args=combined_args,
        agent_id=req.agent_id or "cloud-bot-agent"
    )
    return result


@app.post("/v1/webhooks/bot")
def bot_webhook_handler(req: BotWebhookRequest):
    """
    Universal webhook receiver for Slack, Discord, X (Twitter), and Muse workflows.
    """
    result = evaluate_bot_action(
        bot_type=req.bot,
        tool_name=req.tool or "webhook_action",
        args=req.payload,
        agent_id=req.agent_id or f"{req.bot}-webhook"
    )
    return {
        "status": "PROCESSED",
        "allowed": result["allowed"],
        "verdict": result["verdict"],
        "reason": result["reason"],
        "latency_us": result["latency_us"],
        "receipt_id": result["receipt"]["attestation"].get("nonce", result["receipt"].get("signature", "")[:16])
    }


@app.post("/v1/evaluate")
def evaluate_agent_action(req: EvaluateRequest):
    """Legacy M2M agent action evaluation endpoint."""
    result = evaluate_bot_action(
        bot_type="m2m_agent",
        tool_name=req.action_type,
        args=req.payload,
        agent_id=req.agent_id
    )
    return {
        "verdict": result["verdict"],
        "reason": result["reason"],
        "total_latency_us": result["latency_us"],
        "receipt": result["receipt"]
    }


@app.post("/v1/verify")
def verify_receipt(req: VerifyRequest):
    """Offline cryptographic attestation verification."""
    pubkey = req.trusted_root_pubkey or authority.public_key_hex
    is_valid, reason = IndependentTrustVerifier.verify_attestation(
        attestation_packet=req.attestation_receipt,
        expected_payload=req.candidate_payload,
        trusted_root_pubkey=pubkey
    )
    return {
        "valid": is_valid,
        "is_valid": is_valid,
        "verification_message": reason,
        "trusted_root_pubkey": pubkey
    }


@app.post("/v1/chat/completions")
async def chat_completions_proxy(request: Request):
    """
    Zero-install drop-in proxy for Grok, Meta AI, OpenAI, and Muse.
    Users configure their bot with base_url='https://gateway.bartholomew.info/v1' or 'http://35.222.210.105:8080/v1'.
    Bartholomew proxies requests to the upstream provider (xAI, Groq/Meta, OpenAI),
    intercepting all tool-call completions to evaluate AST security invariants and scrub secrets.
    """
    metrics_counters["total_proxied_turns"] += 1
    t0 = time.perf_counter()

    try:
        body = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON request body: {str(e)}")

    model = body.get("model", "").lower()
    headers = dict(request.headers)
    auth_header = headers.get("authorization", "")

    # Determine upstream provider URL
    custom_downstream = headers.get("x-downstream-url")
    if custom_downstream:
        upstream_url = f"{custom_downstream.rstrip('/')}/chat/completions"
    elif "grok" in model:
        upstream_url = "https://api.x.ai/v1/chat/completions"
    elif "llama" in model or "meta" in model:
        upstream_url = "https://api.groq.com/openai/v1/chat/completions"
    else:
        upstream_url = "https://api.openai.com/v1/chat/completions"

    # Forward to upstream LLM provider
    forward_headers = {
        "Content-Type": "application/json",
        "Authorization": auth_header
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(upstream_url, json=body, headers=forward_headers)
            upstream_data = resp.json()
    except Exception as e:
        # If upstream is unreachable or network error, return formatted error
        return Response(
            content=json.dumps({
                "error": {
                    "message": f"Bartholomew Cloud Gateway failed to connect to upstream ({upstream_url}): {str(e)}",
                    "type": "gateway_upstream_error"
                }
            }),
            status_code=502,
            media_type="application/json"
        )

    # Inspect choices for tool calls
    choices = upstream_data.get("choices", [])
    overall_verdict = "ALLOW"
    blocked_reason = ""
    receipt = None

    for choice in choices:
        message = choice.get("message", {})
        tool_calls = message.get("tool_calls", [])
        for tc in tool_calls:
            func = tc.get("function", {})
            name = func.get("name", "unknown")
            args_str = func.get("arguments", "{}")
            try:
                args = json.loads(args_str) if isinstance(args_str, str) else args_str
            except Exception:
                args = {"raw_args": args_str}

            # Evaluate tool call against Bartholomew invariants
            bot_type = "grok" if "grok" in model else ("meta_ai" if "llama" in model else "universal")
            eval_res = evaluate_bot_action(
                bot_type=bot_type,
                tool_name=name,
                args=args,
                agent_id=f"proxy-{model}"
            )

            if not eval_res["allowed"]:
                overall_verdict = "DENY"
                blocked_reason = eval_res["reason"]
                receipt = eval_res["receipt"]
                # Invalidate the dangerous tool call before the bot executes it
                func["arguments"] = json.dumps({
                    "error": f"Bartholomew Security Gate blocked execution: {blocked_reason}",
                    "allowed": False,
                    "blocked_by": "Bartholomew BTP v5.4.16"
                })
            else:
                receipt = eval_res["receipt"]
                # Replace with secret-scrubbed arguments if secrets were found
                if eval_res.get("secret_scrubbed"):
                    func["arguments"] = json.dumps(eval_res["sanitized_arguments"])

    dt_us = (time.perf_counter() - t0) * 1_000_000

    response_headers = {
        "X-BTP-Verdict": overall_verdict,
        "X-BTP-Latency-US": str(round(dt_us, 2)),
        "X-BTP-Protocol": "BTP/5.4.16"
    }
    if blocked_reason:
        response_headers["X-BTP-Violation"] = blocked_reason
    if receipt:
        receipt_id = receipt["attestation"].get("nonce", receipt.get("signature", "")[:16])
        response_headers["X-BTP-Receipt-ID"] = str(receipt_id)

    return Response(
        content=json.dumps(upstream_data),
        status_code=resp.status_code,
        headers=response_headers,
        media_type="application/json"
    )


@app.post("/mcp")
async def mcp_cloud_handler(request: Request):
    """
    Zero-install remote JSON-RPC 2.0 MCP endpoint.
    Allows web-hosted agent platforms and bots to call Bartholomew via standard MCP protocol.
    """
    try:
        req_json = await request.json()
    except Exception as e:
        return {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}

    method = req_json.get("method")
    req_id = req_json.get("id")
    params = req_json.get("params", {})

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "btp_guard_eval",
                        "description": "Sub-35 microsecond security invariant & AST gate for shell commands, SQL, and code.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "description": "Command, SQL query, or code snippet to verify"},
                                "bot_type": {"type": "string", "description": "Bot type (grok, muse, meta_ai, universal)"}
                            },
                            "required": ["action"]
                        }
                    },
                    {
                        "name": "btp_get_manifest",
                        "description": "Returns machine-readable BTP capabilities and policy discovery manifest.",
                        "inputSchema": {"type": "object"}
                    }
                ]
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "btp_get_manifest":
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(generate_manifest())}]}}

        elif tool_name in ["btp_guard_eval", "btp_eval"]:
            action = args.get("action", "")
            bot_type = args.get("bot_type", "universal")
            eval_res = evaluate_bot_action(
                bot_type=bot_type,
                tool_name="mcp_call",
                args={"command": action},
                agent_id="remote-mcp-agent"
            )
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "allowed": eval_res["allowed"],
                                "verdict": eval_res["verdict"],
                                "reason": eval_res["reason"],
                                "latency_us": eval_res["latency_us"],
                                "receipt": eval_res["receipt"]["attestation"].get("nonce", eval_res["receipt"].get("signature", "")[:16])
                            })
                        }
                    ]
                }
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method {method} not implemented"}
    }


@app.get("/metrics")
def get_prometheus_metrics():
    uptime = time.time() - node_start_time
    body = (
        f"# HELP btp_evaluations_total Total number of BTP evaluations\n"
        f"# TYPE btp_evaluations_total counter\n"
        f"btp_evaluations_total {metrics_counters['total_evals']}\n"
        f"btp_allows_total {metrics_counters['total_allows']}\n"
        f"btp_denies_total {metrics_counters['total_denies']}\n"
        f"btp_proxied_turns_total {metrics_counters['total_proxied_turns']}\n"
        f"btp_bot_requests_grok {metrics_counters['bot_requests']['grok']}\n"
        f"btp_bot_requests_muse {metrics_counters['bot_requests']['muse']}\n"
        f"btp_bot_requests_meta_ai {metrics_counters['bot_requests']['meta_ai']}\n"
        f"btp_uptime_seconds {uptime:.2f}\n"
    )
    return Response(content=body, media_type="text/plain")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
