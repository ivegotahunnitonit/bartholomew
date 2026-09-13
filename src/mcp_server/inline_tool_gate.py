"""
Bartholomew In-Line Mandatory Tool Proxy
=======================================
Enforces in-line execution interception for AI agents.
Ensures that tools CANNOT be executed directly without passing through
the pre-flight BTP cryptographic gate.
"""

import time
import json
from typing import Dict, Any, Callable, Tuple

from src.trust_protocol import BartholomewTrustAuthority
from src.ast_validator import ASTSecurityValidator

class MandatoryToolGate:
    def __init__(self, authority: BartholomewTrustAuthority):
        self.authority = authority
        self.registered_tools: Dict[str, Callable] = {}

    def register_tool(self, name: str, func: Callable):
        """Registers an underlying tool behind the mandatory security gate."""
        self.registered_tools[name] = func

    def execute_gated_tool(self, agent_id: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MANDATORY IN-LINE INTERCEPTION:
        The underlying tool function is strictly blocked from executing
        unless the BTP cryptographic gate attestation verdict is ALLOW.
        """
        start_us = time.perf_counter()

        if tool_name not in self.registered_tools:
            return {
                "status": "ERROR",
                "error": f"Tool '{tool_name}' not found."
            }

        # 1. Inspect code payload with real AST validator if code is provided
        if "code" in arguments and isinstance(arguments["code"], str):
            ast_safe, ast_reason, ast_meta = ASTSecurityValidator.validate_code_ast(arguments["code"])
            if not ast_safe:
                dt_us = (time.perf_counter() - start_us) * 1_000_000
                return {
                    "status": "INTERCEPTED",
                    "verdict": "DENY",
                    "reason": f"AST Invariant Violation: {ast_reason}",
                    "decision_latency_us": round(dt_us, 2),
                    "tool_executed": False
                }

        # 2. Evaluate intent through Bartholomew Trust Authority
        attestation_res = self.authority.evaluate_intent(
            agent_id=agent_id,
            action_type=f"TOOL_CALL_{tool_name.upper()}",
            payload=arguments
        )

        verdict = attestation_res["attestation"]["verdict"]

        # 3. If DENY, the underlying tool function is NEVER CALLED
        if verdict != "ALLOW":
            dt_us = (time.perf_counter() - start_us) * 1_000_000
            return {
                "status": "INTERCEPTED",
                "verdict": "DENY",
                "reason": attestation_res["attestation"]["reason"],
                "decision_latency_us": round(dt_us, 2),
                "tool_executed": False,
                "cryptographic_receipt": attestation_res
            }

        # 4. If ALLOW, execute the real underlying tool
        tool_func = self.registered_tools[tool_name]
        try:
            tool_output = tool_func(**arguments)
            dt_us = (time.perf_counter() - start_us) * 1_000_000
            return {
                "status": "SUCCESS",
                "verdict": "ALLOW",
                "result": tool_output,
                "tool_executed": True,
                "decision_latency_us": round(dt_us, 2),
                "cryptographic_receipt": attestation_res
            }
        except Exception as e:
            return {
                "status": "TOOL_ERROR",
                "error": str(e),
                "tool_executed": True
            }
