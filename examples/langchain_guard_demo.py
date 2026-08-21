"""
LangChain & LangGraph BTP Integration Example
============================================
Demonstrates how to protect LangChain tools with sub-millisecond
BTP pre-flight attestation and AST validation.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))
from src.trust_protocol import BartholomewTrustAuthority
from src.ast_validator import ASTSecurityValidator

authority = BartholomewTrustAuthority(ttl_seconds=300)

def btp_protected_tool(tool_name: str):
    """Decorator to wrap any Python tool with mandatory BTP pre-flight gating."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            payload = {"tool": tool_name, "args": args, "kwargs": kwargs}
            
            # 1. Pre-flight verification
            receipt = authority.evaluate_intent(
                agent_id="langchain-agent-01",
                action_type=f"LANGCHAIN_TOOL_{tool_name.upper()}",
                payload=payload
            )
            
            verdict = receipt["attestation"]["verdict"]
            if verdict != "ALLOW":
                raise PermissionError(f"BTP Interception: {receipt['attestation']['reason']}")
                
            # 2. Execute underlying tool
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Example Tool
@btp_protected_tool("database_query")
def execute_query(sql_query: str):
    return f"Executing verified query: {sql_query}"

if __name__ == "__main__":
    print("=" * 60)
    print("LANGCHAIN BTP GUARDRAIL INTEGRATION DEMO")
    print("=" * 60)

    # 1. Safe Query
    print("\n[1] Testing Safe Tool Call:")
    res = execute_query("SELECT id, name FROM accounts LIMIT 5;")
    print("    Result:", res)

    # 2. Destructive Query
    print("\n[2] Testing Destructive Tool Call (Should Intercept):")
    try:
        execute_query("DROP TABLE accounts;")
    except PermissionError as e:
        print("    [BLOCKED SUCCESSFULLY]:", str(e))

    print("\n" + "=" * 60)
