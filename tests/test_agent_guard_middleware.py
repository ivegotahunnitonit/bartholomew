"""
Test Suite for BTP Agent Guard (Universal Framework Middleware)
Evaluates LangChain, AutoGen, and CrewAI middleware adapters.
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sdk.btp_agent_guard import BTPGuard
from src.trust_protocol import BartholomewTrustAuthority

def test_btp_guard_framework_integration():
    print("=" * 80)
    print("  TESTING BTP AGENT GUARD UNIVERSAL MIDDLEWARE")
    print("=" * 80)

    # Initialize Trust Authority & Agent Guard
    auth = BartholomewTrustAuthority(ttl_seconds=300)
    guard = BTPGuard(
        trusted_authorities=[auth.public_key_hex],
        agent_id="Agent-Production-Cluster",
        authority_instance=auth,
        allowed_capabilities=["FS_WRITE_RESTRICTED", "NO_NET_EGRESS", "AST_MAX_DELTA_5"]
    )

    # -------------------------------------------------------------------------
    # TEST 1: LangChain / LangGraph Tool Wrapper
    # -------------------------------------------------------------------------
    print("\n[1] Testing LangGraph Tool Wrapper...")
    
    @guard.wrap_tool
    def execute_sql_patch(sql: str):
        return f"Executed: {sql}"

    # Generate legitimate receipt for tool call
    payload = {"func": "execute_sql_patch", "args": ("CREATE INDEX idx ON logs(ts);",), "kwargs": {}}
    valid_receipt = guard.issue_action_attestation(
        target_recipient="Agent-Production-Cluster",
        action_type="SQL_EXEC",
        payload=payload
    )

    # Call with valid receipt -> Success
    res = execute_sql_patch("CREATE INDEX idx ON logs(ts);", btp_receipt=valid_receipt)
    assert "Executed:" in res
    print("  |-- Valid Attestation Invocation: SUCCESS")

    # Call with missing receipt -> Denied by Guard
    try:
        execute_sql_patch("DROP TABLE users;")
        assert False, "Should have raised PermissionError"
    except PermissionError as e:
        print(f"  |-- Unattested Invocation Blocked: [{str(e)[:40]}...]")

    # -------------------------------------------------------------------------
    # TEST 2: Microsoft AutoGen Message Interceptor
    # -------------------------------------------------------------------------
    print("\n[2] Testing AutoGen Message Interceptor...")

    # Attested message
    inbound_msg = {
        "role": "assistant",
        "action_type": "DEPLOY_PATCH",
        "content": {"file": "worker.py", "patch": "fix()"},
        "btp_envelope": guard.issue_action_attestation(
            target_recipient="Agent-Production-Cluster",
            action_type="DEPLOY_PATCH",
            payload={"file": "worker.py", "patch": "fix()"}
        )
    }
    safe_msg = guard.intercept_autogen_message(inbound_msg)
    assert safe_msg.get("status") != "DENIED"
    print("  |-- Attested Inbound Message: AUTHORIZED")

    # Unattested high-privilege message
    unattested_msg = {
        "role": "assistant",
        "action_type": "EXEC_COMMAND",
        "content": "rm -rf /tmp"
    }
    blocked_msg = guard.intercept_autogen_message(unattested_msg)
    assert blocked_msg["status"] == "DENIED"
    print(f"  |-- Unattested Inbound Message: BLOCKED ({blocked_msg['content']})")

    # -------------------------------------------------------------------------
    # TEST 3: CrewAI Task Guard
    # -------------------------------------------------------------------------
    print("\n[3] Testing CrewAI Task Guard...")

    def mock_crew_task(target):
        return f"Completed task for {target}"

    guarded_task = guard.wrap_crewai_task("Deploy Verified Release", mock_crew_task)
    task_res = guarded_task("Prod-Node-01")
    assert "Completed task" in task_res
    print("  |-- Guarded CrewAI Task Execution: SUCCESS")

    print("\n" + "=" * 80)
    print("  BTP AGENT GUARD MIDDLEWARE TESTS: 100% PASSED")
    print("=" * 80)

if __name__ == "__main__":
    test_btp_guard_framework_integration()
    sys.exit(0)
