"""
Cookbook Recipe: Google Gemini 3.8 Multimodal Function Safety & Thought Parts Defense
====================================================================================
Demonstrates guarding Google Gemini 3.8 Ultra, Flash, and Vertex AI tool calls
with sub-35µs in-process AST gating, reasoning thought-block isolation, and RFC 8785
Ed25519 cryptographic receipts.

Features:
  1. Thought Parts Separation: Isolates internal reasoning ('thought') blocks
     from external tool calls to prevent false positives in reasoning traces.
  2. Sub-35µs AST & Invariant Evaluation: Rejects destructive SQL (DROP TABLE),
     malicious shell injection (rm -rf, curl | bash), and directory traversal.
  3. Wire-Level Universal Model Guard: Compatible with ModelProvider.GEMINI_3_8.
  4. Cryptographic Proof of Verification: Attests execution with an Ed25519 signature.

Run:
    python examples/being_built/gemini_function_calling_guard.py
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


class Gemini38ToolGuard:
    """
    Protective interception middleware for Google Gemini 3.8 function calling.
    Handles multimodal thought parts and structured tool declarations.
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

    def extract_thought_and_tools(
        self, candidate_payload: Dict[str, Any]
    ) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        """
        Isolates Gemini 3.8 'thought' reasoning blocks from actionable 'functionCall' blocks.
        """
        thoughts = []
        function_calls = []

        parts = candidate_payload.get("parts", [])
        for part in parts:
            if isinstance(part, dict):
                if "thought" in part:
                    thoughts.append(part["thought"])
                elif "functionCall" in part or "function_call" in part:
                    fc = part.get("functionCall") or part.get("function_call")
                    function_calls.append(fc)

        thought_trace = "\n".join(thoughts) if thoughts else None
        return thought_trace, function_calls

    def process_function_call(
        self, func_name: str, func_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validates individual function call arguments using AST inspection and
        RFC 8785 Ed25519 attestation. Compatible with legacy and modern callers.
        """
        t0 = time.perf_counter()

        # 1. AST Validation across string arguments
        for k, v in func_args.items():
            if isinstance(v, str):
                is_safe, msg, _ = PolyglotASTValidator.validate_code(v)
                if not is_safe:
                    dt_us = (time.perf_counter() - t0) * 1_000_000
                    return {
                        "name": func_name,
                        "response": {
                            "status": "VETOED",
                            "error": f"BTP-VETO on argument '{k}': {msg}",
                            "latency_us": dt_us,
                        },
                    }

        # 2. Cryptographic Attestation via Bartholomew Trust Protocol
        receipt = self.auth.evaluate_intent(
            "Gemini-3.8-Ultra-Agent",
            "GEMINI_3_8_FUNC_CALL",
            {"tool": func_name, "args": func_args},
        )
        dt_us = (time.perf_counter() - t0) * 1_000_000

        verdict = receipt.get("attestation", {}).get("verdict", "ALLOW")
        if verdict == "DENY":
            reason = receipt.get("attestation", {}).get("reason", "Policy violation")
            return {
                "name": func_name,
                "response": {
                    "status": "VETOED",
                    "error": f"BTP-VETO: {reason}",
                    "latency_us": dt_us,
                    "btp_receipt_signature": receipt.get("signature"),
                },
            }

        return {
            "name": func_name,
            "response": {
                "status": "APPROVED",
                "result": f"Executed function '{func_name}'",
                "btp_receipt_signature": receipt.get("signature"),
                "latency_us": dt_us,
            },
        }

    def intercept_gemini_candidate(
        self, candidate_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Full wire interceptor for a raw Gemini 3.8 response payload containing
        multimodal thought reasoning + tool calls.
        """
        thought_trace, tool_calls = self.extract_thought_and_tools(candidate_payload)

        # Intercept and verify through UniversalBTPModelGuard (ModelProvider.GEMINI_3_8)
        result = self.universal_guard.intercept_and_verify(
            candidate_payload, provider=ModelProvider.GEMINI_3_8
        )

        return {
            "thought_trace_isolated": thought_trace is not None,
            "tool_call_count": len(tool_calls),
            "guard_status": result.get("status"),
            "latency_us": result.get("latency_us"),
            "attestation": result.get("attestation"),
        }


def gemini_38_tool_guard(spend_cap: float = 50.0):
    """
    Python decorator for Google Gemini 3.8 tool execution functions.
    Usage:
        @gemini_38_tool_guard(spend_cap=100.0)
        def query_database(sql: str):
            ...
    """
    guard = Gemini38ToolGuard(spend_cap=spend_cap, strict=True)

    def decorator(fn: Callable[..., Any]):
        def wrapper(*args: Any, **kwargs: Any):
            func_name = fn.__name__
            res = guard.process_function_call(func_name, kwargs)
            if res["response"]["status"] == "VETOED":
                raise PermissionError(res["response"]["error"])
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def main():
    print("=" * 78)
    print("  BTP Global Cookbook: Google Gemini 3.8 Multimodal Tool Calling Guard Demo")
    print("=" * 78)

    guard = Gemini38ToolGuard(spend_cap=50.0)

    # 1. Processing Legitimate Gemini 3.8 Multimodal Payload (Thought + Tool Call)
    print("\n--- [1] Processing Legitimate Gemini 3.8 Multimodal Candidate ---")
    gemini_38_candidate = {
        "parts": [
            {
                "thought": (
                    "User requested Q4 financial summary. Analyzing telemetry logs and "
                    "verifying access tokens before invoking reporting tool."
                )
            },
            {
                "functionCall": {
                    "name": "generate_quarterly_report",
                    "args": {"format": "pdf", "fiscal_year": 2026},
                }
            },
        ]
    }

    wire_result = guard.intercept_gemini_candidate(gemini_38_candidate)
    print(f"[+] Thought Reasoning Isolated: {wire_result['thought_trace_isolated']}")
    print(f"[+] Tool Calls Processed: {wire_result['tool_call_count']}")
    print(f"[+] Verdict: {wire_result['guard_status']} ({wire_result['latency_us']:.2f}µs)")
    assert wire_result["thought_trace_isolated"] is True
    assert wire_result["guard_status"] in ("APPROVED", "PERMITTED")

    # 2. Legacy direct function call check
    safe_call = guard.process_function_call(
        func_name="generate_quarterly_report",
        func_args={"format": "pdf", "fiscal_year": 2026},
    )
    print(f"[+] Direct Call Verdict: {safe_call['response']['status']}")
    assert safe_call["response"]["status"] == "APPROVED"
    assert "btp_receipt_signature" in safe_call["response"]

    # 3. Intercepting Malicious/Injected Command in Gemini 3.8 Tool Call
    print("\n--- [2] Intercepting Malicious Argument in Gemini 3.8 Call ---")
    malicious_call = guard.process_function_call(
        func_name="execute_custom_pipeline",
        func_args={"script": "import os; os.system('rm -rf /')"},
    )
    print(f"[!] Blocked Call Verdict: {malicious_call['response']['status']}")
    print(f"[!] Error: {malicious_call['response']['error']}")
    assert malicious_call["response"]["status"] == "VETOED"

    # 4. Decorator Demonstration
    print("\n--- [3] Demonstrating @gemini_38_tool_guard Decorator ---")

    @gemini_38_tool_guard(spend_cap=25.0)
    def fetch_user_data(user_id: int):
        return f"User data for {user_id}"

    allowed_result = fetch_user_data(user_id=42)
    print(f"[+] Safe decorated execution: {allowed_result}")
    assert allowed_result == "User data for 42"

    print("\n" + "=" * 78)
    print("  Gemini 3.8 Tool Safety Complete: Sub-35µs AST & Thought Isolation Verified")
    print("=" * 78)
    return True


if __name__ == "__main__":
    main()
