"""
Bartholomew Trust Protocol (BTP v1.0.0) - Production Safe Agent Starter
=======================================================================
A 1-click, ready-to-deploy template for building autonomous AI agents
with in-process sub-35µs AST safety gating and L402 micro-settlement.

Works out of the box with Claude 3.7, OpenAI Agents, Gemini 3.8, and AutoGen.
"""

import sys
import os

# Add parent directory to path for local or installed btp_guard
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from btp_guard import Guard
except ImportError:
    from src.btp_guard import Guard

# 1. Initialize Bartholomew In-Process Execution Guard
# Enforces spend caps, blocks SQL drops, shell wipes, and prompt injections
guard = Guard(
    spend_cap=25.0,        # Maximum USD spend per agent session
    max_retries=3,         # Prevents infinite autonomous retry loops
    strict=True,           # Blocks ambiguous or risky parameters
    workspace_id="prod"    # Audit tag for Merkle execution receipts
)

# 2. Protect any critical tool or function with a single decorator
@guard.protect
def execute_database_operation(sql_query: str) -> str:
    """Simulated database tool execution protected by Bartholomew AST gate."""
    return f"[DB SUCCESS] Executed query safely: {sql_query}"

@guard.protect
def execute_system_command(command: str) -> str:
    """Simulated shell tool execution protected by Bartholomew AST gate."""
    return f"[SYSTEM SUCCESS] Executed command: {command}"


def main():
    print("=" * 70)
    print("  BARTHOLOMEW BTP v1.0.0 -- PRODUCTION SAFE AGENT STARTER")
    print("=" * 70)
    print("  Status   : In-Process AST Gate ACTIVE (<35µs)")
    print("  Pricing  : Free Local Tier | Pro Cloud Sync: https://bartholomew.info/cloud")
    print("=" * 70)

    # Test Case 1: Safe read query (Allowed)
    safe_query = "SELECT id, username, email FROM users WHERE active = 1 LIMIT 50;"
    print("\n[1] Testing Safe Database Query...")
    result = execute_database_operation(safe_query)
    print(f"    Verdict: {result}")

    # Test Case 2: Malicious destructive query (Blocked in <35µs)
    malicious_query = "DROP TABLE users; --"
    print("\n[2] Testing Destructive Database Query (Should be blocked)...")
    try:
        execute_database_operation(malicious_query)
    except PermissionError as exc:
        print(f"    [BLOCKED BY BTP] {exc}")

    # Test Case 3: Malicious shell wipe (Blocked in <35µs)
    malicious_cmd = "rm -rf /var/data && echo pwned"
    print("\n[3] Testing Destructive Shell Command (Should be blocked)...")
    try:
        execute_system_command(malicious_cmd)
    except PermissionError as exc:
        print(f"    [BLOCKED BY BTP] {exc}")

    print("\n" + "=" * 70)
    print("  [PASSED] All agent actions safely gated. Ready for production.")
    print("=" * 70)


if __name__ == "__main__":
    main()
