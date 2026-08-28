"""
Tests for Community Integrations (LangChain, CrewAI, MCP)
=========================================================
Verifies that all 3 official ecosystem integration modules function with
100% test pass rate and zero escapes.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.abspath("."))
from integrations.langchain.bartholomew_guard import BartholomewCallbackHandler, BartholomewToolGuard
from integrations.crewai.bartholomew_tool_guard import BartholomewCrewAIGuard
from src.mcp_gateway import MCPProxyGateway


class TestCommunityIntegrations(unittest.TestCase):

    def test_langchain_callback_handler_allow(self):
        handler = BartholomewCallbackHandler(spend_cap_usd=100.0)
        receipt = handler.on_tool_start(
            serialized={"name": "calculator"},
            input_str="2 + 2",
            cost_usd=0.01
        )
        self.assertIn("signature", receipt)
        self.assertEqual(handler.current_spend, 0.01)

    def test_langchain_callback_handler_veto_drop_table(self):
        handler = BartholomewCallbackHandler(spend_cap_usd=100.0)
        with self.assertRaises(PermissionError) as ctx:
            handler.on_tool_start(
                serialized={"name": "sql_tool"},
                input_str="DROP TABLE customers CASCADE;"
            )
        self.assertIn("BTP-VETO", str(ctx.exception))

    def test_langchain_tool_decorator(self):
        @BartholomewToolGuard(spend_cap_usd=50.0)
        def custom_tool(query: str):
            return f"Executed: {query}"

        # Safe execution
        res = custom_tool("SELECT * FROM users LIMIT 10")
        self.assertEqual(res, "Executed: SELECT * FROM users LIMIT 10")

        # Destructive execution vetoed
        with self.assertRaises(PermissionError):
            custom_tool("rm -rf / --no-preserve-root")

    def test_crewai_guard_allow_and_veto(self):
        def sample_worker_action(command: str):
            return f"Action complete: {command}"

        guarded = BartholomewCrewAIGuard(tool=sample_worker_action, max_retries=3)

        # 1. Safe execution
        out = guarded.run("git status")
        self.assertEqual(out, "Action complete: git status")

        # 2. Veto destructive action
        with self.assertRaises(PermissionError):
            guarded.run("import os; os.system('DROP DATABASE production')")

        # 3. LDMU loop decay threshold
        self.assertEqual(guarded.retry_count, 1)

    def test_mcp_gateway_jsonrpc_veto(self):
        import json
        gateway = MCPProxyGateway()
        rpc_request = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "execute_shell",
                "arguments": {"cmd": "rm -rf / --no-preserve-root"}
            }
        })
        forward_to_downstream, req, veto_resp = gateway.intercept_jsonrpc_request(rpc_request)
        self.assertFalse(forward_to_downstream)
        self.assertIsNotNone(veto_resp)
        self.assertIn("error", veto_resp)
        self.assertEqual(veto_resp["error"]["code"], -32000)
        self.assertIn("BTP-VETO", veto_resp["error"]["message"])


if __name__ == "__main__":
    unittest.main()
