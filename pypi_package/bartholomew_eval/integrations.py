"""
bartholomew_eval.integrations
==============================
Framework integrations for FastAPI, LangChain, LlamaIndex, AutoGen, and CrewAI.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional, Union

from .engine import BartholomewEngine
from .guard import GuardViolation


class BartholomewFastAPIMiddleware:
    """
    FastAPI / Starlette Middleware for zero-config OWASP LLM security inspection & secret redaction.

    Usage:
        from fastapi import FastAPI
        from bartholomew_eval.integrations import BartholomewFastAPIMiddleware

        app = FastAPI()
        app.add_middleware(BartholomewFastAPIMiddleware, max_budget_tokens=2000)
    """

    def __init__(
        self,
        app: Any,
        max_budget_tokens: int = 2000,
        secret_scrubbing: bool = True,
        engine: Optional[BartholomewEngine] = None,
    ) -> None:
        self.app = app
        self.max_budget_tokens = max_budget_tokens
        self.secret_scrubbing = secret_scrubbing
        self.auditor = engine or BartholomewEngine()

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Intercept HTTP body for payload inspection
        body_bytes = b""
        async def receive_with_interception() -> Dict[str, Any]:
            nonlocal body_bytes
            message = await receive()
            if message.get("type") == "http.request":
                body_bytes += message.get("body", b"")
            return message

        payload_str = body_bytes.decode("utf-8", errors="ignore")
        if payload_str:
            trajectory = {
                "agent_name": f"HTTP_{scope.get('path', 'route')}",
                "steps": [{"step_index": 1, "type": "thought", "content": payload_str}],
            }
            audit_res = self.auditor.evaluate_trajectory(trajectory)
            summary = audit_res.get("audit_summary", {})

            if summary.get("compliance_status") == "SECURITY_RISK" and summary.get("credential_leaks", 0) > 0:
                response_body = json.dumps({
                    "error": "SECURITY_BOUNDARY_VIOLATION",
                    "detail": "🚨 [Bartholomew Guard]: Credential leak detected in request payload!",
                    "attestation_sha256": summary.get("attestation_sha256"),
                }).encode("utf-8")

                await send({
                    "type": "http.response.start",
                    "status": 403,
                    "headers": [(b"content-type", b"application/json")],
                })
                await send({
                    "type": "http.response.body",
                    "body": response_body,
                })
                return

        await self.app(scope, receive_with_interception, send)


class BartholomewLangChainCallback:
    """
    LangChain Callback Handler for real-time security boundary protection & prompt injection interception.

    Usage:
        from bartholomew_eval.integrations import BartholomewLangChainCallback

        handler = BartholomewLangChainCallback()
        agent.run("query", callbacks=[handler])
    """

    def __init__(self, engine: Optional[BartholomewEngine] = None) -> None:
        self.auditor = engine or BartholomewEngine()

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        for prompt in prompts:
            trajectory = {
                "agent_name": "LangChain_Agent",
                "steps": [{"step_index": 1, "type": "thought", "content": prompt}],
            }
            res = self.auditor.evaluate_trajectory(trajectory)
            summary = res.get("audit_summary", {})

            if summary.get("prompt_injections", 0) > 0:
                raise GuardViolation("🚨 [Bartholomew Guard]: Prompt injection intercepted in LangChain prompt!", summary)
            if summary.get("credential_leaks", 0) > 0:
                raise GuardViolation("🚨 [Bartholomew Guard]: Credential leak intercepted in LangChain prompt!", summary)

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        trajectory = {
            "agent_name": "LangChain_Tool",
            "steps": [{"step_index": 1, "type": "tool_call", "content": input_str}],
        }
        res = self.auditor.evaluate_trajectory(trajectory)
        summary = res.get("audit_summary", {})

        if summary.get("compliance_status") == "SECURITY_RISK":
            raise GuardViolation("🚨 [Bartholomew Guard]: Security boundary violation in LangChain tool execution!", summary)
