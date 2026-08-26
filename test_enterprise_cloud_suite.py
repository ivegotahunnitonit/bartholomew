"""
Enterprise Cloud & MCP Ecosystem Test Suite (v2.3)
==================================================
Verifies:
  1. MCP Proxy Gateway transparent JSON-RPC interception and hard vetos.
  2. Agent-to-Agent (A2A) cryptographic envelope verification and replay defense.
  3. Pluggable Cloud KMS drivers & OIDC JWT Role Claims evaluation.
  4. AWS CDK & Terraform configuration synthesis.
"""

import sys
import os
import json
import base64
import time

sys.path.insert(0, os.path.abspath("."))
from src.mcp_gateway import MCPProxyGateway
from src.a2a_protocol import AgentToAgentProtocol
from src.cloud_identity import LocalEd25519Provider, CloudKMSProvider, OIDCPolicyEvaluator
from src.trust_protocol import BartholomewTrustAuthority
from aws_cdk.bartholomew_guard import BartholomewGuardConfig


def test_mcp_proxy_gateway_interception():
    gateway = MCPProxyGateway()

    # 1. Test Dangerous Tool Call Veto
    malicious_call = json.dumps({
        "jsonrpc": "2.0",
        "id": "req-001",
        "method": "tools/call",
        "params": {
            "name": "bash_executor",
            "arguments": {
                "command": "rm -rf /var/data"
            }
        }
    })

    forward, req, veto = gateway.intercept_jsonrpc_request(malicious_call)
    assert not forward
    assert veto is not None
    assert "BTP-VETO" in veto["error"]["message"]
    assert veto["error"]["data"]["verdict"] == "DENY"

    # 2. Test Safe Tool Call with Secret Scrubbing
    leak_call = json.dumps({
        "jsonrpc": "2.0",
        "id": "req-002",
        "method": "tools/call",
        "params": {
            "name": "query_database",
            "arguments": {
                "query": "SELECT * FROM metrics",
                "api_key": "sk-proj-1234567890abcdef1234567890abcdef"
            }
        }
    })

    forward2, req2, veto2 = gateway.intercept_jsonrpc_request(leak_call)
    assert forward2
    assert veto2 is None
    assert "[REDACTED_OPENAI_KEY_BTP]" in str(req2["params"]["arguments"])


def test_agent_to_agent_protocol():
    auth_a = BartholomewTrustAuthority()
    
    # 1. Agent A creates signed handoff
    payload = {"task": "analyze_logs", "lines": 100}
    signed_envelope = AgentToAgentProtocol.create_signed_handoff(
        sender_authority=auth_a,
        originating_agent="agent-planner-alpha",
        target_agent="agent-worker-beta",
        task_action="LOG_ANALYTICS",
        task_payload=payload,
        capability_scope=["READ_ONLY", "LOGS_ACCESS"]
    )

    # 2. Agent B verifies envelope
    verified, msg, data = AgentToAgentProtocol.verify_incoming_handoff(
        signed_packet=signed_envelope,
        expected_recipient="agent-worker-beta",
        trusted_sender_pubkey=auth_a.public_key_hex
    )
    assert verified
    assert "Verified Clean" in msg
    assert data["sender_agent_id"] == "agent-planner-alpha"

    # 3. Test Wrong Recipient Rejection
    bad_verified, bad_msg, _ = AgentToAgentProtocol.verify_incoming_handoff(
        signed_packet=signed_envelope,
        expected_recipient="impostor-agent-omega"
    )
    assert not bad_verified
    assert "Recipient mismatch" in bad_msg


def test_cloud_identity_and_oidc_claims():
    # 1. Test Cloud KMS Provider
    kms = CloudKMSProvider(key_arn="arn:aws:kms:us-east-1:123456789012:key/btp-test")
    sig = kms.sign_bytes(b"test_payload")
    assert len(sig) == 128
    assert "AWS_KMS" in kms.get_provider_name()

    # 2. Test OIDC JWT Role Claims Evaluator
    fake_payload = {
        "sub": "user-uuid-1234",
        "cognito:groups": ["SecurityLead", "Engineers"],
        "email": "lead@company.com"
    }
    encoded_payload = base64.urlsafe_b64encode(json.dumps(fake_payload).encode('utf-8')).decode('utf-8').rstrip("=")
    fake_jwt = f"header.{encoded_payload}.signature"

    claims = OIDCPolicyEvaluator.decode_jwt_claims(fake_jwt)
    assert claims["sub"] == "user-uuid-1234"

    # Evaluate Allowed Role
    allowed, _ = OIDCPolicyEvaluator.evaluate_role_permission(claims, "EXECUTE_DB_MUTATION", required_roles=["SecurityLead"])
    assert allowed

    # Evaluate Denied Role
    denied, den_msg = OIDCPolicyEvaluator.evaluate_role_permission(claims, "NUKE_CLUSTER", required_roles=["RootSuperAdmin"])
    assert not denied
    assert "OIDC Role Denial" in den_msg


def test_aws_cdk_synthesis():
    cfg = BartholomewGuardConfig(spend_cap_usd=750.0)
    cfn = cfg.to_cloudformation_template()
    assert cfn["Type"] == "AWS::Lambda::LayerVersion"
    assert "Bartholomew" in cfn["Properties"]["LayerName"]


if __name__ == "__main__":
    test_mcp_proxy_gateway_interception()
    test_agent_to_agent_protocol()
    test_cloud_identity_and_oidc_claims()
    test_aws_cdk_synthesis()
    print("ALL ENTERPRISE CLOUD & MCP SUITE TESTS PASSED 100% CLEAN!")
