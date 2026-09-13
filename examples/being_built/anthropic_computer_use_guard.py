"""
Cookbook Recipe: Anthropic Claude 3.7 Tool & Computer Use Guard
================================================================
Demonstrates guarding Anthropic Claude 3.7 (with Hybrid Reasoning / Thinking blocks)
and Computer Use bash actions against prompt injection, destructive commands,
and credential theft in sub-35 microseconds.

Features:
  1. Hybrid Thinking Separation: Claude 3.7 generates internal reasoning traces
     (`{"type": "thinking", "thinking": "..."}`). Bartholomew isolates thinking blocks
     so internal scratchpads do not trigger false invariant positives.
  2. Computer Use Gating: Rejects catastrophic shell commands (`rm -rf`, `mkfs`, `curl | bash`)
     and credential theft (`.env`, `id_rsa`, AWS tokens).
  3. Ed25519 Merkle Receipts: Every verified tool execution emits a cryptographically
     signed attestation receipt for SOC 2 compliance.

Run:
    python examples/being_built/anthropic_computer_use_guard.py
"""

import sys
import os
import json
import time
from typing import Dict, Any, List, Optional, Tuple, Callable

# Add repository root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.polyglot_ast_validator import PolyglotASTValidator
from src.trust_protocol import BartholomewTrustAuthority
from src.framework_adapters.universal.universal_model_guard import (
    UniversalBTPModelGuard,
    ModelProvider,
)


class Claude37ToolGuard:
    """
    Guards Anthropic Claude 3.7 tool_use blocks and Computer Use bash actions,
    isolating reasoning traces from actionable execution blocks.
    """

    def __init__(
        self,
        spend_cap: float = 50.0,
        strict: bool = True,
        trust_authority: Optional[BartholomewTrustAuthority] = None,
    ):
        self.auth = trust_authority or BartholomewTrustAuthority(ttl_seconds=300)
        self.universal_guard = UniversalBTPModelGuard(
            spend_cap=spend_cap,
            strict=strict,
        )

    def extract_thinking_and_tools(
        self, content_blocks: List[Dict[str, Any]]
    ) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        """
        Isolates Claude 3.7 hybrid 'thinking' blocks from actionable 'tool_use' blocks.
        """
        thoughts = []
        tools = []
        for block in content_blocks:
            if not isinstance(block, dict):
                continue
            b_type = block.get("type")
            if b_type == "thinking":
                thoughts.append(block.get("thinking", ""))
            elif b_type == "tool_use":
                tools.append(block)

        thinking_trace = "\n".join(thoughts) if thoughts else None
        return thinking_trace, tools

    def process_content_blocks(
        self, content_blocks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Processes a full Claude 3.7 response message containing thinking and tool_use blocks.
        Returns a list of tool_result blocks.
        """
        _, tools = self.extract_thinking_and_tools(content_blocks)
        results = []
        for tool in tools:
            res = self.execute_tool_block(tool)
            results.append(res)
        return results

    def execute_tool_block(self, tool_use_block: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a single Anthropic tool_use content block.
        Format: {"type": "tool_use", "id": "toolu_123", "name": "bash", "input": {"command": "..."}}
        """
        t0 = time.perf_counter()
        tool_id = tool_use_block.get("id", "toolu_default")
        tool_name = tool_use_block.get("name", "bash")
        tool_input = tool_use_block.get("input", {})

        # 1. Inspect AST / Path Traversal safety across command/code arguments
        cmd = tool_input.get("command") or tool_input.get("code") or ""
        if cmd and isinstance(cmd, str):
            is_safe, msg, _ = PolyglotASTValidator.validate_code(cmd)
            if not is_safe:
                dt_us = (time.perf_counter() - t0) * 1_000_000
                return {
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "is_error": True,
                    "content": f"[BTP_VETO] Command rejected by safety invariants: {msg}",
                    "latency_us": dt_us,
                }

        # 2. Cryptographic Attestation
        receipt = self.auth.evaluate_intent(
            "Claude-3.7-Sonnet",
            f"CLAUDE_TOOL_{tool_name.upper()}",
            {"input": tool_input, "command": cmd},
        )
        dt_us = (time.perf_counter() - t0) * 1_000_000

        verdict = receipt.get("attestation", {}).get("verdict", "ALLOW")
        if verdict == "DENY":
            return {
                "type": "tool_result",
                "tool_use_id": tool_id,
                "is_error": True,
                "content": f"[BTP_VETO] Policy denial: {receipt.get('attestation', {}).get('reason')}",
                "latency_us": dt_us,
            }

        return {
            "type": "tool_result",
            "tool_use_id": tool_id,
            "is_error": False,
            "content": f"Successfully executed {tool_name}: {cmd or 'ok'}",
            "btp_receipt_signature": receipt.get("signature"),
            "latency_us": dt_us,
        }


# Aliased for backward compatibility with existing tests
AnthropicToolGuard = Claude37ToolGuard


def main():
    print("=" * 78)
    print("  BTP Global Cookbook: Anthropic Claude 3.7 Tool & Computer Use Guard")
    print("=" * 78)

    guard = Claude37ToolGuard()

    # 1. Safe Claude 3.7 Message with Hybrid Thinking + Computer Use bash command
    print("\n--- [1] Processing Claude 3.7 Message (Thinking + Computer Use) ---")
    claude_message = {
        "role": "assistant",
        "content": [
            {
                "type": "thinking",
                "thinking": (
                    "User wants to check git status and run unit tests. "
                    "I will use the bash tool to execute git status && pytest."
                ),
            },
            {
                "type": "tool_use",
                "id": "toolu_01",
                "name": "bash",
                "input": {"command": "git status && pytest"},
            },
        ],
    }

    thinking_trace, tools = guard.extract_thinking_and_tools(claude_message["content"])
    print(f"[+] Thinking Trace Isolated: {thinking_trace is not None}")
    print(f"[+] Tools Found: {len(tools)}")
    assert thinking_trace is not None
    assert len(tools) == 1

    safe_results = guard.process_content_blocks(claude_message["content"])
    assert len(safe_results) == 1
    print(f"[+] Tool Result: {safe_results[0]['content']} ({safe_results[0]['latency_us']:.2f}µs)")
    assert safe_results[0]["is_error"] is False
    assert "btp_receipt_signature" in safe_results[0]

    # 2. Injected destructive payload
    print("\n--- [2] Intercepting Malicious Claude Computer Use Command ---")
    injected_message = [
        {
            "type": "thinking",
            "thinking": "Attacker prompt injected instructions to purge disk root.",
        },
        {
            "type": "tool_use",
            "id": "toolu_02",
            "name": "bash",
            "input": {"command": "rm -rf / --no-preserve-root"},
        },
    ]
    veto_results = guard.process_content_blocks(injected_message)
    assert len(veto_results) == 1
    print(f"[!] Blocked Result: {veto_results[0]['content']}")
    assert veto_results[0]["is_error"] is True
    assert "[BTP_VETO]" in veto_results[0]["content"]

    print("\n" + "=" * 78)
    print("  Anthropic Claude 3.7 Guard Complete: Thinking Isolated & Execution Protected")
    print("=" * 78)
    return True


if __name__ == "__main__":
    main()
