"""
Cookbook Recipe: OpenAI Tool Calling & Agents SDK Guard
========================================================
Demonstrates wrapping OpenAI Chat Completions and the new OpenAI Agents SDK
with sub-35µs BTP invariant inspection, preventing prompt injection, destructive
commands, and unauthorized state mutation.

Features:
  1. Multi-Format Normalization: Supports standard Chat Completions
     `{"id": "...", "function": {"name": "...", "arguments": "{...}"}}`
     and OpenAI Agents SDK `{"tool_name": "...", "tool_arguments": {...}}`.
  2. In-Process Polyglot AST Validation: Blocks bash injection, catastrophic SQL,
     and path traversal in arguments before execution.
  3. Ed25519 Merkle Attestation: Generates cryptographic execution receipts.

Run:
    python examples/being_built/openai_tool_calling_guard.py
"""

import sys
import os
import json
import time
from typing import Dict, Any, Callable, Optional, Tuple

# Add repository root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.polyglot_ast_validator import PolyglotASTValidator
from src.trust_protocol import BartholomewTrustAuthority
from src.framework_adapters.universal.universal_model_guard import (
    UniversalBTPModelGuard,
    ModelProvider,
)


class OpenAIToolGuard:
    """Interception wrapper for OpenAI function calling loops and Agents SDK."""

    def __init__(
        self,
        spend_cap: float = 50.0,
        trust_authority: Optional[BartholomewTrustAuthority] = None,
    ):
        self.tool_registry: Dict[str, Callable] = {}
        self.auth = trust_authority or BartholomewTrustAuthority(ttl_seconds=300)
        self.universal_guard = UniversalBTPModelGuard(
            spend_cap=spend_cap,
            strict=True,
        )

    def register_tool(self, name: str, fn: Callable):
        self.tool_registry[name] = fn

    def dispatch_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Safely dispatches a tool call emitted by OpenAI Chat Completions or OpenAI Agents SDK.
        Formats supported:
          - Standard: {"id": "call_123", "function": {"name": "...", "arguments": "{...}"}}
          - Agents SDK: {"tool_name": "...", "tool_arguments": {...}}
        """
        t0 = time.perf_counter()
        call_id = tool_call.get("id", "call_default")

        # 1. Normalize between Chat Completions and Agents SDK format
        if "tool_name" in tool_call:
            func_name = tool_call.get("tool_name")
            raw_args = tool_call.get("tool_arguments", {})
        elif "function" in tool_call:
            func_spec = tool_call.get("function", {})
            func_name = func_spec.get("name")
            raw_args = func_spec.get("arguments", "{}")
        else:
            func_name = tool_call.get("name")
            raw_args = tool_call.get("arguments", {})

        # Parse arguments
        if isinstance(raw_args, str):
            try:
                parsed_args = json.loads(raw_args)
            except Exception:
                parsed_args = {"raw_payload": raw_args}
        elif isinstance(raw_args, dict):
            parsed_args = raw_args
        else:
            parsed_args = {}

        # 2. Check AST / Path Traversal safety across all argument values
        for k, v in parsed_args.items():
            if isinstance(v, str):
                is_safe, msg, _ = PolyglotASTValidator.validate_code(v)
                if not is_safe:
                    dt_us = (time.perf_counter() - t0) * 1_000_000
                    return {
                        "tool_call_id": call_id,
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps({
                            "error": "BTP_POLICY_VETO",
                            "message": f"Argument '{k}' violated safety policy: {msg}",
                            "latency_us": dt_us,
                        }),
                    }

        # 3. Cryptographic Attestation
        receipt = self.auth.evaluate_intent(
            "OpenAI-GPT4o-Agent",
            f"OPENAI_TOOL_{func_name.upper() if func_name else 'TOOL'}",
            parsed_args,
        )
        dt_us = (time.perf_counter() - t0) * 1_000_000

        verdict = receipt.get("attestation", {}).get("verdict", "ALLOW")
        if verdict == "DENY":
            return {
                "tool_call_id": call_id,
                "role": "tool",
                "name": func_name,
                "content": json.dumps({
                    "error": "BTP_POLICY_VETO",
                    "message": f"Policy veto: {receipt.get('attestation', {}).get('reason')}",
                    "latency_us": dt_us,
                }),
            }

        # 4. If safe, execute tool
        target_fn = self.tool_registry.get(func_name)
        if not target_fn:
            return {
                "tool_call_id": call_id,
                "role": "tool",
                "name": func_name,
                "content": json.dumps({"error": f"Tool '{func_name}' not registered."}),
            }

        try:
            result = target_fn(**parsed_args)
            return {
                "tool_call_id": call_id,
                "role": "tool",
                "name": func_name,
                "content": json.dumps({
                    "success": True,
                    "result": result,
                    "btp_receipt_signature": receipt.get("signature"),
                    "latency_us": dt_us,
                }),
            }
        except Exception as e:
            return {
                "tool_call_id": call_id,
                "role": "tool",
                "name": func_name,
                "content": json.dumps({"error": str(e)}),
            }


def main():
    print("=" * 78)
    print("  BTP Global Cookbook: OpenAI Tool Calling & Agents SDK Guard Demo")
    print("=" * 78)

    dispatcher = OpenAIToolGuard()

    # Register business tools
    def fetch_weather(location: str) -> str:
        return f"72°F, sunny in {location}"

    def update_record(record_id: int, note: str) -> str:
        return f"Record {record_id} updated with note: {note}"

    dispatcher.register_tool("fetch_weather", fetch_weather)
    dispatcher.register_tool("update_record", update_record)

    # 1. Legitimate OpenAI Chat Completions tool call
    print("\n--- [1] Processing Legitimate OpenAI Chat Completions Tool Call ---")
    safe_call = {
        "id": "call_001",
        "type": "function",
        "function": {
            "name": "fetch_weather",
            "arguments": json.dumps({"location": "San Francisco, CA"}),
        },
    }
    safe_resp = dispatcher.dispatch_tool_call(safe_call)
    print(f"Tool Response: {safe_resp['content']}")
    assert "sunny" in safe_resp["content"]
    assert "San Francisco" in safe_resp["content"]
    assert "btp_receipt_signature" in safe_resp["content"]

    # 2. Prompt injection payload embedded in arguments
    print("\n--- [2] Intercepting Malicious Argument in Tool Call ---")
    injected_call = {
        "id": "call_002",
        "type": "function",
        "function": {
            "name": "fetch_weather",
            "arguments": json.dumps({"location": "San Francisco; rm -rf /etc/hosts"}),
        },
    }
    blocked_resp = dispatcher.dispatch_tool_call(injected_call)
    print(f"Tool Response: {blocked_resp['content']}")
    assert "BTP_POLICY_VETO" in blocked_resp["content"]

    # 3. New OpenAI Agents SDK tool call format
    print("\n--- [3] Processing OpenAI Agents SDK Tool Call Format ---")
    agents_sdk_call = {
        "tool_name": "update_record",
        "tool_arguments": {"record_id": 1042, "note": "Verified Q4 audit trail."},
    }
    sdk_resp = dispatcher.dispatch_tool_call(agents_sdk_call)
    print(f"Agents SDK Response: {sdk_resp['content']}")
    assert "Verified Q4 audit trail" in sdk_resp["content"]
    assert "btp_receipt_signature" in sdk_resp["content"]

    print("\n" + "=" * 78)
    print("  OpenAI Tool Guard Complete: Chat Completions & Agents SDK Protected")
    print("=" * 78)
    return True


if __name__ == "__main__":
    main()
