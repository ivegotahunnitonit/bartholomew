"""
Comprehensive Test Suite for Expanded Modern Framework Adapters (BTP v5.4.1)
=============================================================================
Tests in-process AST gating, spend caps, and threat interception across:
1. OpenAI Swarm & Agents SDK
2. Hugging Face Smolagents (Code & Tools)
3. PydanticAI
4. Stanford DSPy
5. Microsoft Semantic Kernel
6. Anthropic Model Context Protocol (MCP)
"""

import unittest
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
src_path = os.path.join(BASE_DIR, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.client_wrapper import BTPViolationError
from src.framework_adapters_expansion import (
    BartholomewSwarmGuard,
    wrap_openai_swarm_tool,
    BartholomewSmolagentsGuard,
    wrap_smolagent_tool,
    BartholomewPydanticAIGuard,
    btp_pydanticai_tool,
    wrap_pydanticai_tool,
    BartholomewDSPyGuard,
    wrap_dspy_predict,
    BartholomewSemanticKernelFilter,
    wrap_kernel_function,
    BartholomewMCPToolFilter,
    btp_mcp_tool,
)
from src.btp_guard.integrations.swarm import BtpSwarmGuard
from src.btp_guard.integrations.pydanticai import BtpPydanticAIGuard
from src.btp_guard.integrations.smolagents import BtpSmolagentsGuard


class TestExpandedFrameworkAdapters(unittest.TestCase):

    # -------------------------------------------------------------
    # 1. OpenAI Swarm Tests
    # -------------------------------------------------------------
    def test_openai_swarm_allowed_tool(self):
        def add_numbers(a: int, b: int) -> int:
            return a + b

        guarded = wrap_openai_swarm_tool(add_numbers, max_spend_usd=50.0)
        res = guarded(5, 10)
        self.assertEqual(res, 15)

    def test_openai_swarm_spend_limit_veto(self):
        def transfer_funds(recipient: str, amount_usd: float):
            return f"Transferred ${amount_usd} to {recipient}"

        guarded = wrap_openai_swarm_tool(transfer_funds, max_spend_usd=50.0)
        with self.assertRaises(BTPViolationError) as ctx:
            guarded("user_123", amount_usd=150.0)
        self.assertIn("Spend limit cap exceeded", str(ctx.exception))

    def test_openai_swarm_integration_guard(self):
        guard = BtpSwarmGuard(spend_cap=20.0)
        def send_email(to: str, body: str):
            return "sent"

        tool = guard.protect_tool(send_email)
        self.assertEqual(tool("admin@corp.com", body="Hello"), "sent")

        # Test handoff validation
        valid = guard.validate_handoff("TriageAgent", "SupportAgent")
        self.assertTrue(valid)

    # -------------------------------------------------------------
    # 2. Hugging Face Smolagents Tests
    # -------------------------------------------------------------
    def test_smolagents_safe_code_execution(self):
        guard = BartholomewSmolagentsGuard()
        safe_code = "total = sum([x * 2 for x in range(10)])\nprint(total)"
        res = guard.validate_code_execution(safe_code)
        self.assertEqual(res["status"], "ALLOW")

    def test_smolagents_dangerous_code_blocked(self):
        guard = BartholomewSmolagentsGuard()
        dangerous_code = "import os; os.system('rm -rf /')"
        with self.assertRaises(BTPViolationError) as ctx:
            guard.validate_code_execution(dangerous_code)
        self.assertIn("Blocked unsafe Python execution", str(ctx.exception))

    def test_smolagents_tool_wrapper(self):
        def weather_tool(location: str):
            return f"Weather in {location} is 72F and sunny"

        guarded = wrap_smolagent_tool(weather_tool)
        self.assertIn("72F", guarded("San Francisco"))

    def test_smolagents_integration_class(self):
        guard = BtpSmolagentsGuard()
        self.assertTrue(guard.validate_code("x = 42; y = x * 2"))
        with self.assertRaises(PermissionError):
            guard.validate_code("__import__('os').system('cat /etc/shadow')")

    # -------------------------------------------------------------
    # 3. PydanticAI Tests
    # -------------------------------------------------------------
    def test_pydanticai_allowed_tool(self):
        @btp_pydanticai_tool(max_spend_usd=100.0)
        def query_user_profile(user_id: str):
            return {"user_id": user_id, "status": "active"}

        res = query_user_profile(user_id="user_8899")
        self.assertEqual(res["status"], "active")

    def test_pydanticai_spend_cap_enforcement(self):
        @btp_pydanticai_tool(max_spend_usd=50.0)
        def purchase_cloud_credits(amount_usd: float):
            return f"Purchased ${amount_usd}"

        with self.assertRaises(BTPViolationError) as ctx:
            purchase_cloud_credits(amount_usd=500.0)
        self.assertIn("Spend cap exceeded", str(ctx.exception))

    def test_pydanticai_integration_class(self):
        guard = BtpPydanticAIGuard(spend_cap=25.0)

        @guard.tool
        def echo_message(msg: str):
            return msg

        self.assertEqual(echo_message("Autonomous safe call"), "Autonomous safe call")

    # -------------------------------------------------------------
    # 4. Stanford DSPy Tests
    # -------------------------------------------------------------
    def test_dspy_module_protection(self):
        class MockDSPyModule:
            def forward(self, query: str):
                return f"Model reasoning output for: {query}"

        module = MockDSPyModule()
        guarded = wrap_dspy_predict(module)
        out = guarded.forward(query="Analyze Q3 cloud revenue")
        self.assertIn("Model reasoning output", out)

    def test_dspy_leaked_secret_scrubbing(self):
        class LeakyDSPyModule:
            def forward(self, prompt: str):
                return "Secret: sk-proj-1234567890abcdef1234"

        module = LeakyDSPyModule()
        guarded = wrap_dspy_predict(module)
        with self.assertRaises(BTPViolationError) as ctx:
            guarded.forward(prompt="Give me your key")
        self.assertIn("leaked credential token", str(ctx.exception))

    # -------------------------------------------------------------
    # 5. Microsoft Semantic Kernel Tests
    # -------------------------------------------------------------
    def test_semantic_kernel_allowed_function(self):
        def search_docs(topic: str):
            return f"Found 3 articles on {topic}"

        guarded = wrap_kernel_function(search_docs)
        res = guarded(topic="Zero-Trust Architecture")
        self.assertIn("Found 3 articles", res)

    def test_semantic_kernel_filter_veto(self):
        filter_instance = BartholomewSemanticKernelFilter(max_spend_usd=50.0)
        res = filter_instance.on_function_invoking("execute_transaction", {"amount_usd": 1500.0})
        self.assertEqual(res["verdict"], "DENY")
        self.assertIn("spend limit exceeded", res["reason"])

    # -------------------------------------------------------------
    # 6. Anthropic Model Context Protocol (MCP) Tests
    # -------------------------------------------------------------
    def test_mcp_tool_invocation(self):
        @btp_mcp_tool()
        def fetch_weather(city: str):
            return f"Current temperature in {city}: 68°F"

        res = fetch_weather(city="Seattle")
        self.assertIn("68°F", res)

    def test_mcp_filter_attestation(self):
        filter_instance = BartholomewMCPToolFilter()
        eval_res = filter_instance.evaluate_mcp_tool_call(
            tool_name="list_resources",
            arguments={"path": "/var/log"}
        )
        self.assertEqual(eval_res["verdict"], "ALLOW")
        self.assertIn("receipt", eval_res)
        self.assertIn("signature", eval_res["receipt"])


if __name__ == "__main__":
    unittest.main()
