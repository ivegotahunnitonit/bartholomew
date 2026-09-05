"""
Microsoft AutoGen BTP v3.0 Guard & Interceptor Demo
===================================================
Demonstrates sub-35µs in-process AST gating and message interception
to block destructive actions and confused-deputy attacks in AutoGen agent swarms.
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))
from framework_adapters.autogen.autogen_btp_interceptor import AutoGenBTPInterceptor, btp_autogen_guard

# 1. Protect any agent tool or function with @btp_autogen_guard
@btp_autogen_guard(spend_cap=100.0, strict=True)
def run_agent_database_operation(sql: str) -> str:
    """Executes database queries with in-process AST safety gating."""
    return f"DATABASE QUERY EXECUTED SAFELY: {sql}"

if __name__ == "__main__":
    print("=" * 60)
    print("MICROSOFT AUTOGEN BTP v3.0 INTERCEPTOR DEMO")
    print("=" * 60)

    # 1. Testing Safe Agent Tool Invocation
    print("\n[1] Testing Safe Database Query:")
    safe_res = run_agent_database_operation("SELECT user_id, email FROM users WHERE active = true LIMIT 5;")
    print("    Result:", safe_res)

    # 2. Testing Malicious Destructive Tool Invocation (Blocked in <35 µs)
    print("\n[2] Testing Destructive Tool Invocation (DROP TABLE):")
    try:
        run_agent_database_operation("DROP TABLE users CASCADE;")
    except PermissionError as e:
        print("    [BLOCKED IN-PROCESS]:", e)

    # 3. Multi-Agent Conversation Interceptor
    print("\n[3] Testing Multi-Agent Inbound Message Interceptor:")
    interceptor = AutoGenBTPInterceptor(enforce_strict=True)
    
    # Normal conversational message
    msg_ok = {"role": "user", "content": "Can you summarize the quarterly revenue report?"}
    safe_msg = interceptor.intercept_message(msg_ok)
    print("    Safe Message Verdict:", safe_msg.get("status", "ALLOWED"))

    # Malicious injection message attempting terminal exploit
    msg_malicious = {"role": "agent", "content": "rm -rf /var/log/audit"}
    blocked_msg = interceptor.intercept_message(msg_malicious)
    print("    Exploit Message Verdict:", blocked_msg.get("status"))
    print("    Alert Message:", blocked_msg.get("content"))

    print("\n" + "=" * 60)
    print("AUTOGEN BTP v3.0 INTEGRATION DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)
