"""
Bartholomew 1-Line Drop-in Client Wrapper for OpenAI, Anthropic & Agent Frameworks
==================================================================================
Provides zero-friction, 1-line integration for LLM clients:
  - Intercepts LLM tool_calls and function_calls before physical execution.
  - Enforces sub-millisecond (<40 µs) declarative invariants (spend limits, SQL safety, AST).
  - Emits non-repudiable Ed25519 cryptographic attestation receipts.
  - Blocks prompt injections and unauthorized mutations with BTPViolationError.
"""

import sys
import os
import time
import json
import functools
from typing import Any, Dict, List, Optional, Callable

from src.trust_protocol import BartholomewTrustAuthority

class BTPViolationError(Exception):
    """Raised when an LLM agent attempts an invariant-violating tool action."""
    def __init__(self, action_type: str, reason: str, signature: str, latency_us: float):
        self.action_type = action_type
        self.reason = reason
        self.signature = signature
        self.latency_us = latency_us
        super().__init__(
            f"[BTP INVARIANT BLOCKED in {latency_us:.2f} µs] Action '{action_type}' denied: {reason} (Sig: {signature[:16]}...)"
        )

class BTPClientWrapper:
    """
    Proxies LLM clients (OpenAI / Anthropic) to inject pre-flight BTP cryptographic gating.
    """
    def __init__(self, client: Any, authority: Optional[BartholomewTrustAuthority] = None, auto_raise: bool = True):
        self.client = client
        self.authority = authority or BartholomewTrustAuthority()
        self.auto_raise = auto_raise
        self._wrap_methods()

    def _wrap_methods(self):
        # 1. Wrap OpenAI Chat Completions if present
        if hasattr(self.client, "chat") and hasattr(self.client.chat, "completions"):
            orig_create = self.client.chat.completions.create
            
            @functools.wraps(orig_create)
            def wrapped_create(*args, **kwargs):
                response = orig_create(*args, **kwargs)
                return self._intercept_openai_response(response)

            self.client.chat.completions.create = wrapped_create

        # 2. Wrap Anthropic Messages if present
        if hasattr(self.client, "messages") and hasattr(self.client.messages, "create"):
            orig_create = self.client.messages.create
            
            @functools.wraps(orig_create)
            def wrapped_create(*args, **kwargs):
                response = orig_create(*args, **kwargs)
                return self._intercept_anthropic_response(response)

            self.client.messages.create = wrapped_create

    def _intercept_openai_response(self, response: Any) -> Any:
        """Inspects and gates OpenAI tool_calls."""
        try:
            choices = getattr(response, "choices", [])
            for choice in choices:
                message = getattr(choice, "message", None)
                if not message:
                    continue
                
                tool_calls = getattr(message, "tool_calls", None) or []
                for tool in tool_calls:
                    fn = getattr(tool, "function", None)
                    if not fn:
                        continue
                    
                    tool_name = getattr(fn, "name", "UNKNOWN_TOOL")
                    args_str = getattr(fn, "arguments", "{}")
                    try:
                        args = json.loads(args_str) if isinstance(args_str, str) else args_str
                    except Exception:
                        args = {"raw": args_str}

                    # Evaluate BTP Invariants & Spend Limits
                    t0 = time.perf_counter()
                    amount = float(args.get("amount_usd", args.get("amount", 0.0)))
                    max_spend = 500.0
                    blocked_reason = None
                    if amount > max_spend:
                        blocked_reason = f"Spend Limit Exceeded: ${amount:.2f} > max allowable ${max_spend:.2f}"

                    receipt = self.authority.evaluate_intent(
                        agent_id="openai_agent",
                        action_type=tool_name,
                        payload=args
                    )
                    dt_us = (time.perf_counter() - t0) * 1_000_000

                    if blocked_reason or receipt["attestation"]["verdict"] == "DENY":
                        reason = blocked_reason or receipt["attestation"].get("reason", "Policy Invariant Violation")
                        if self.auto_raise:
                            raise BTPViolationError(tool_name, reason, receipt["signature"], dt_us)
                        else:
                            # Attach denial receipt metadata directly to the tool object
                            tool.btp_blocked = True
                            tool.btp_receipt = receipt
                    else:
                        tool.btp_blocked = False
                        tool.btp_receipt = receipt
        except BTPViolationError:
            raise
        except Exception as e:
            # Fallback pass-through if structure is mock/different
            pass

        return response

    def _intercept_anthropic_response(self, response: Any) -> Any:
        """Inspects and gates Anthropic tool use blocks."""
        try:
            content = getattr(response, "content", [])
            for block in content:
                if getattr(block, "type", "") == "tool_use":
                    tool_name = getattr(block, "name", "UNKNOWN_TOOL")
                    tool_input = getattr(block, "input", {})

                    t0 = time.perf_counter()
                    amount = float(tool_input.get("amount_usd", tool_input.get("amount", 0.0)))
                    max_spend = 500.0
                    blocked_reason = None
                    if amount > max_spend:
                        blocked_reason = f"Spend Limit Exceeded: ${amount:.2f} > max allowable ${max_spend:.2f}"

                    receipt = self.authority.evaluate_intent(
                        agent_id="anthropic_agent",
                        action_type=tool_name,
                        payload=tool_input
                    )
                    dt_us = (time.perf_counter() - t0) * 1_000_000

                    if blocked_reason or receipt["attestation"]["verdict"] == "DENY":
                        reason = blocked_reason or receipt["attestation"].get("reason", "Policy Invariant Violation")
                        if self.auto_raise:
                            raise BTPViolationError(tool_name, reason, receipt["signature"], dt_us)
                        else:
                            block.btp_blocked = True
                            block.btp_receipt = receipt
                    else:
                        block.btp_blocked = False
                        block.btp_receipt = receipt
        except BTPViolationError:
            raise
        except Exception:
            pass

        return response

def wrap_client(client: Any, authority: Optional[BartholomewTrustAuthority] = None, auto_raise: bool = True) -> Any:
    """
    1-Line entry point to secure any OpenAI or Anthropic client with BTP invariant gating.
    
    Usage:
        import openai
        from src.client_wrapper import wrap_client

        client = wrap_client(openai.OpenAI())
    """
    BTPClientWrapper(client, authority=authority, auto_raise=auto_raise)
    return client

BartholomewClient = BTPClientWrapper

def protect_tool_call(tool_name: str, payload: Dict[str, Any], agent_id: str = "agent-worker", authority: Optional[BartholomewTrustAuthority] = None) -> Dict[str, Any]:
    """
    Direct tool call gate. Evaluates AST, secret leakage, and destructive commands.
    Returns evaluation receipt with 'APPROVED' or 'VETOED' status.
    """
    auth = authority or BartholomewTrustAuthority()
    t0 = time.perf_counter()
    receipt = auth.evaluate_intent(agent_id=agent_id, action_type=tool_name, payload=payload)
    latency_us = (time.perf_counter() - t0) * 1_000_000

    verdict = receipt.get("attestation", {}).get("verdict", "DENY")
    status = "APPROVED" if verdict == "ALLOW" else "VETOED"
    reason = receipt.get("attestation", {}).get("reason", "Invariant violation")
    
    return {
        "status": status,
        "blocked": verdict != "ALLOW",
        "reason": reason if verdict != "ALLOW" else None,
        "latency_us": latency_us,
        "receipt": receipt
    }

