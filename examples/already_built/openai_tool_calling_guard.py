"""
Cookbook Recipe: OpenAI Function Calling Guard (For "Being Built Right Now" Agents)
==================================================================================
Demonstrates wrapping direct OpenAI tool/function calling dispatchers with BTP
invariant inspection, preventing prompt injection and malicious argument execution.

Pattern:
    LLM (GPT-4o) ---> Tool Call: {"name": "execute_bash", "arguments": {"cmd": "..."}}
                               |
                   [BTP Function Guard]  <--- Validates AST, Paths, Secrets
                               |
                    +----------+----------+
                    |                     |
                 [ALLOW]               [DENY]
                    |                     |
             Runs real tool        Returns safe error to LLM (without executing)

Run:
    python cookbook/being_built/openai_tool_calling_guard.py
"""

import sys
import os
import json
from typing import Dict, Any, Callable

# Add repository root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.polyglot_ast_validator import PolyglotASTValidator


class OpenAIToolGuard:
    """Interception wrapper for OpenAI function calling loops."""

    def __init__(self):
        self.tool_registry: Dict[str, Callable] = {}

    def register_tool(self, name: str, fn: Callable):
        self.tool_registry[name] = fn

    def dispatch_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Safely dispatches a tool call emitted by OpenAI chat completions.
        tool_call format: {"id": "call_123", "function": {"name": "...", "arguments": "{...}"}}
        """
        call_id = tool_call.get("id", "call_default")
        func_spec = tool_call.get("function", {})
        func_name = func_spec.get("name")
        raw_args = func_spec.get("arguments", "{}")

        # 1. Parse arguments
        try:
            parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
        except Exception:
            parsed_args = {}

        # 2. Check AST / Path Traversal safety across all argument values
        for k, v in parsed_args.items():
            if isinstance(v, str):
                is_safe, msg, _ = PolyglotASTValidator.validate_code(v)
                if not is_safe:
                    return {
                        "tool_call_id": call_id,
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps({
                            "error": "BTP_POLICY_VETO",
                            "message": f"Argument '{k}' violated safety policy: {msg}"
                        })
                    }

        # 3. If safe, execute tool
        target_fn = self.tool_registry.get(func_name)
        if not target_fn:
            return {
                "tool_call_id": call_id,
                "role": "tool",
                "name": func_name,
                "content": json.dumps({"error": f"Tool '{func_name}' not registered."})
            }

        try:
            result = target_fn(**parsed_args)
            return {
                "tool_call_id": call_id,
                "role": "tool",
                "name": func_name,
                "content": json.dumps({"success": True, "result": result})
            }
        except Exception as e:
            return {
                "tool_call_id": call_id,
                "role": "tool",
                "name": func_name,
                "content": json.dumps({"error": str(e)})
            }


def main():
    print("=" * 75)
    print("  BTP Global Cookbook: OpenAI Function Calling Guard Demo")
    print("=" * 75)

    dispatcher = OpenAIToolGuard()

    # Register real business tool
    def fetch_weather(location: str) -> str:
        return f"72°F, sunny in {location}"

    dispatcher.register_tool("fetch_weather", fetch_weather)

    # 1. Legitimate OpenAI tool call
    print("\n--- [1] Processing Legitimate OpenAI Tool Call ---")
    safe_call = {
        "id": "call_001",
        "type": "function",
        "function": {
            "name": "fetch_weather",
            "arguments": json.dumps({"location": "San Francisco, CA"})
        }
    }
    safe_resp = dispatcher.dispatch_tool_call(safe_call)
    print(f"Tool Response: {safe_resp['content']}")
    assert "sunny" in safe_resp["content"]
    assert "San Francisco" in safe_resp["content"]

    # 2. Prompt injection payload embedded in arguments
    print("\n--- [2] Intercepting Malicious Argument in Tool Call ---")
    injected_call = {
        "id": "call_002",
        "type": "function",
        "function": {
            "name": "fetch_weather",
            "arguments": json.dumps({"location": "San Francisco; rm -rf /etc/hosts"})
        }
    }
    blocked_resp = dispatcher.dispatch_tool_call(injected_call)
    print(f"Tool Response: {blocked_resp['content']}")
    assert "BTP_POLICY_VETO" in blocked_resp["content"]

    print("\n" + "=" * 75)
    print("  OpenAI Tool Guard Complete: LLM Function Calls Protected")
    print("=" * 75)
    return True


if __name__ == "__main__":
    main()
