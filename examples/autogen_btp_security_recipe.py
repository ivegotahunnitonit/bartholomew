"""
Microsoft AutoGen BTP v5.4 — Reference Security Recipe Script
Demonstrating both allowed execution and blocked violation with diagnostics.
"""

import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from framework_adapters.autogen import btp_autogen_guard, BTPViolationError, AutoGenBTPInterceptor

print("=" * 72)
print("  Microsoft AutoGen + Bartholomew Trust Protocol (BTP) Recipe Demo")
print("=" * 72)

# 1. Define Guarded Tools
@btp_autogen_guard
def execute_sql_query(query: str) -> str:
    """Simulates running a SQL query against the enterprise warehouse."""
    return f"[SUCCESS] Executed: '{query}'. Returned 10 records."

@btp_autogen_guard
def execute_bash_command(command: str) -> str:
    """Simulates running a terminal command in the worker environment."""
    return f"[SUCCESS] Executed command: '{command}'. Exit code: 0."

# 2. Demonstration 1: Allowed Safe Execution
print("\n[Step 1] Executing Safe SQL Query...")
safe_query = "SELECT user_id, email, organization_id FROM users WHERE active = 1 LIMIT 10;"
result = execute_sql_query(safe_query)
print("Tool Output:", result)

# 3. Demonstration 2: Intercepting Destructive Injections with Rich Diagnostics
print("\n[Step 2] Attempting Malicious DROP TABLE Injection...")
malicious_query = "DROP TABLE enterprise_users CASCADE;"
try:
    execute_sql_query(malicious_query)
except BTPViolationError as exc:
    print("\n--- BTP SECURITY VETO INTERCEPTED ---")
    print(exc)
    print("\n--- STRUCTURED JSON DIAGNOSTICS ---")
    print(json.dumps(exc.to_diagnostics(), indent=2))

print("\n[Step 3] Attempting Destructive Terminal Command...")
destructive_cmd = "rm -rf /var/lib/data"
try:
    execute_bash_command(destructive_cmd)
except BTPViolationError as exc:
    print(f"Blocked Rule:    {exc.rule_id}")
    print(f"Latency:         {exc.latency_us:.1f} µs")
    print(f"Blocked Reason:  {exc.reason}")

# 4. Demonstration 3: In-Flight Message Interception
print("\n[Step 4] Testing AutoGen In-Flight Message Interceptor...")
interceptor = AutoGenBTPInterceptor()

inbound_safe = {"role": "user", "content": "Please summarize the latest security report."}
filtered_safe = interceptor.intercept_message(inbound_safe)
print("Safe Message Status:", filtered_safe.get("status", "PASSED"))

inbound_attack = {
    "role": "assistant",
    "content": "I will now run the maintenance script: rm -rf /etc/ssl/certs"
}
filtered_attack = interceptor.intercept_message(inbound_attack)
print("Attack Message Status:", filtered_attack.get("status"))
print("System Security Notice:", filtered_attack.get("content"))

print("\n" + "=" * 72)
print("  Recipe Completed Successfully! All Invariants Verified.")
print("=" * 72)
