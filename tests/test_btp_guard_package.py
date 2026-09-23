import unittest
import time
import btp_guard
from btp_guard import Guard, secure_tool, SecurityVetoException, wrap_client
from btp_guard.integrations import (
    crewai,
    langchain,
    langgraph,
    autogen,
    llamaindex,
    pydanticai,
    smolagents,
    swarm,
    BtpCrewAIGuard,
    BtpCallbackHandler,
    BtpToolGuard,
    LangGraphBTPGuard,
    AutoGenBTPInterceptor,
    LlamaIndexBTPToolGuard,
)


class TestBTPGuardPackage(unittest.TestCase):
    def test_version_and_exports(self):
        self.assertEqual(btp_guard.__version__, "5.4.20")
        self.assertTrue(callable(Guard))
        self.assertTrue(callable(secure_tool))
        self.assertTrue(issubclass(SecurityVetoException, Exception))

    def test_guard_execution_gate(self):
        g = Guard(spend_cap=50.0)
        # Safe command
        res_safe = g.check("echo 'hello world'")
        self.assertTrue(res_safe["allowed"])
        self.assertEqual(res_safe["verdict"], "ALLOW")

        # Dangerous command
        res_blocked = g.check("rm -rf /")
        self.assertFalse(res_blocked["allowed"])
        self.assertEqual(res_blocked["verdict"], "DENY")
        self.assertIn("BTP-AST-001", res_blocked["reason"])

    def test_secure_tool_decorator(self):
        @secure_tool
        def query_database(sql: str):
            return f"query:{sql}"

        # Safe execution
        self.assertEqual(query_database("SELECT id FROM users"), "query:SELECT id FROM users")

        # Intercepted dangerous execution
        with self.assertRaises(SecurityVetoException):
            query_database("DROP TABLE users")

    def test_framework_integrations_instantiation(self):
        # LangChain handler
        handler = BtpCallbackHandler(spend_cap=10.0)
        self.assertEqual(handler.spend_cap, 10.0)

        # CrewAI guard
        class DummyTool:
            name = "dummy"
            def run(self, cmd):
                return cmd

        tool = DummyTool()
        crew_guard = BtpCrewAIGuard(tool=tool, spend_cap=20.0)
        self.assertEqual(crew_guard.spend_cap, 20.0)

        # LangGraph guard
        self.assertTrue(callable(LangGraphBTPGuard))

        # AutoGen interceptor
        self.assertTrue(callable(AutoGenBTPInterceptor))

        # LlamaIndex guard
        self.assertTrue(callable(LlamaIndexBTPToolGuard))


if __name__ == "__main__":
    unittest.main()
