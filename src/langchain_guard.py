"""
Bartholomew Native LangChain & CrewAI Guardrail Callback Plugin
==============================================================
Provides out-of-the-box integration for LangChain, CrewAI & AutoGen:
  - Implements standard LangChain CallbackHandler interface.
  - Intercepts `on_tool_start` and `on_agent_action` events pre-flight.
  - Blocks prompt injection, spend overruns, and destructive commands (<40 µs).
  - Produces RFC 8785 + Ed25519 attestation receipts.
"""

import sys
import os
import time
import json
from typing import Dict, Any, List, Optional, Union

from src.trust_protocol import BartholomewTrustAuthority
from src.client_wrapper import BTPViolationError

class BTPCallbackHandler:
    """
    Standard callback handler compatible with LangChain, CrewAI, and custom agent executors.
    """
    def __init__(self, authority: Optional[BartholomewTrustAuthority] = None, max_spend_usd: float = 500.0, auto_raise: bool = True):
        self.authority = authority or BartholomewTrustAuthority()
        self.max_spend_usd = max_spend_usd
        self.auto_raise = auto_raise
        self.intercepted_count = 0
        self.blocked_count = 0

    def on_tool_start(self, serialized: Dict[str, Any], input_str: Union[str, Dict[str, Any]], **kwargs: Any) -> Any:
        """
        Called when a LangChain or CrewAI tool is about to run.
        """
        self.intercepted_count += 1
        t0 = time.perf_counter()

        tool_name = serialized.get("name", kwargs.get("name", "LANGCHAIN_TOOL"))
        
        # Parse inputs
        if isinstance(input_str, str):
            try:
                payload = json.loads(input_str)
            except Exception:
                payload = {"query": input_str}
        else:
            payload = input_str or {}

        # 1. Spend limit check
        amount = float(payload.get("amount_usd", payload.get("amount", 0.0)))
        blocked_reason = None
        if amount > self.max_spend_usd:
            blocked_reason = f"Spend Limit Exceeded: ${amount:.2f} > max allowable ${self.max_spend_usd:.2f}"

        # 2. Cryptographic Attestation
        receipt = self.authority.evaluate_intent(
            agent_id="langchain_agent",
            action_type=tool_name,
            payload=payload
        )
        dt_us = (time.perf_counter() - t0) * 1_000_000

        if blocked_reason or receipt["attestation"]["verdict"] == "DENY":
            self.blocked_count += 1
            reason = blocked_reason or receipt["attestation"].get("reason", "Policy Invariant Violation")
            if self.auto_raise:
                raise BTPViolationError(tool_name, reason, receipt["signature"], dt_us)
            return {"verdict": "DENY", "reason": reason, "receipt": receipt}

        return {"verdict": "ALLOW", "receipt": receipt, "latency_us": dt_us}

    def on_agent_action(self, action: Any, **kwargs: Any) -> Any:
        """Called when an agent plans an action step."""
        tool = getattr(action, "tool", "AGENT_STEP")
        tool_input = getattr(action, "tool_input", {})
        return self.on_tool_start({"name": tool}, tool_input)
