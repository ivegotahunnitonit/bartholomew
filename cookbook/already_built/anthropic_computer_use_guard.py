"""
Cookbook Recipe: Anthropic Claude Tool & Computer Use Guard
============================================================
Demonstrates guarding Anthropic Claude tool_use blocks and Computer Use
bash actions against prompt injection, destructive commands, and secret theft.

Pattern:
    Claude Message ---> tool_use block (name: "bash", input: {"command": "..."})
                               |
                   [AnthropicToolGuard]
                               |
            +------------------+------------------+
            |                                     |
       [ALLOW]                                 [VETO]
            |                                     |
    Runs shell in sandbox             Returns is_error=True block to Claude

Run:
    python cookbook/being_built/anthropic_computer_use_guard.py
"""

import sys
import os
import json
from typing import Dict, Any, List

# Add repository root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.polyglot_ast_validator import PolyglotASTValidator


class AnthropicToolGuard:
    """Guards Anthropic Claude tool_use blocks (including Computer Use bash tool)."""

    @classmethod
    def execute_tool_block(cls, tool_use_block: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes an Anthropic tool_use content block.
        Format: {"type": "tool_use", "id": "toolu_123", "name": "bash", "input": {"command": "..."}}
        """
        tool_id = tool_use_block.get("id", "toolu_default")
        tool_name = tool_use_block.get("name")
        tool_input = tool_use_block.get("input", {})

        # If bash or code tool, validate code / shell AST
        cmd = tool_input.get("command") or tool_input.get("code") or ""
        if cmd and isinstance(cmd, str):
            is_safe, msg, _ = PolyglotASTValidator.validate_code(cmd)
            if not is_safe:
                return {
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "is_error": True,
                    "content": f"[BTP_VETO] Command rejected by safety invariants: {msg}"
                }

        # Safe execution simulation
        return {
            "type": "tool_result",
            "tool_use_id": tool_id,
            "is_error": False,
            "content": f"Successfully executed {tool_name}: {cmd or 'ok'}"
        }


def main():
    print("=" * 75)
    print("  BTP Global Cookbook: Anthropic Claude Tool Use Guard Demo")
    print("=" * 75)

    # 1. Safe Claude Computer Use bash command
    print("\n--- [1] Processing Legitimate Claude Computer Use Command ---")
    safe_tool_use = {
        "type": "tool_use",
        "id": "toolu_01",
        "name": "bash",
        "input": {"command": "git status && pytest"}
    }
    safe_result = AnthropicToolGuard.execute_tool_block(safe_tool_use)
    print(f"Claude Result: {safe_result['content']}")
    assert safe_result["is_error"] is False

    # 2. Injected destructive payload
    print("\n--- [2] Intercepting Malicious Claude Computer Use Command ---")
    injected_tool_use = {
        "type": "tool_use",
        "id": "toolu_02",
        "name": "bash",
        "input": {"command": "rm -rf / --no-preserve-root"}
    }
    veto_result = AnthropicToolGuard.execute_tool_block(injected_tool_use)
    print(f"Claude Result: {veto_result['content']}")
    assert veto_result["is_error"] is True
    assert "[BTP_VETO]" in veto_result["content"]

    print("\n" + "=" * 75)
    print("  Anthropic Tool Guard Complete: Computer Use Protected")
    print("=" * 75)
    return True


if __name__ == "__main__":
    main()
