"""
Test Suite for Milestone 3.1: Sovereign Digital Passports & Peer Discovery (BTP v3.1.0)
Verifies:
1. SovereignAgentPassport Ed25519 signing and offline verification.
2. Tamper resistance (tampering payload invalidates signature).
3. Capability bounds enforcement.
4. Circuit breaker tripping and automatic suspension.
5. AgentPeerDiscoveryRegistry multi-attribute peer filtering.
6. MCP JSON-RPC integration for passport issuance, verification, and discovery.
"""

import json
import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519

from src.agent_passport import SovereignAgentPassport, AgentPeerDiscoveryRegistry
from mcp_server import BartholomewMCPServer


def test_passport_issuance_and_signing():
    privkey = ed25519.Ed25519PrivateKey.generate()
    pubkey_hex = privkey.public_key().public_bytes_raw().hex()

    passport = SovereignAgentPassport(
        agent_id="agent-gemini-pro-42",
        worker_model="Gemini-1.5-Pro",
        owner_pubkey=pubkey_hex,
        granted_capabilities=["data:read", "code:mutate", "test:run"],
        bonded_warranty_balance_usd=5000.0
    )

    sig = passport.sign(privkey)
    assert sig is not None
    assert len(sig) == 128  # 64 bytes in hex

    is_valid, msg = passport.verify_signature()
    assert is_valid is True
    assert "Valid" in msg


def test_passport_tamper_detection():
    privkey = ed25519.Ed25519PrivateKey.generate()
    pubkey_hex = privkey.public_key().public_bytes_raw().hex()

    passport = SovereignAgentPassport(
        agent_id="agent-claude-35",
        worker_model="Claude-3.5-Sonnet",
        owner_pubkey=pubkey_hex,
        granted_capabilities=["data:read"]
    )
    passport.sign(privkey)

    # Tamper with capabilities
    passport.granted_capabilities.append("admin:superuser")
    is_valid, msg = passport.verify_signature()
    assert is_valid is False
    assert "failed" in msg.lower()


def test_passport_capabilities_and_reputation():
    privkey = ed25519.Ed25519PrivateKey.generate()
    pubkey_hex = privkey.public_key().public_bytes_raw().hex()

    passport = SovereignAgentPassport(
        agent_id="agent-worker-01",
        worker_model="GPT-4o",
        owner_pubkey=pubkey_hex,
        granted_capabilities=["data:read", "tools:search"]
    )

    assert passport.has_capability("data:read") is True
    assert passport.has_capability("db:drop") is False

    # Reputation updates
    passport.record_successful_action(value_usd=250.0)
    assert passport.reputation_vector["verified_actions"] == 1
    assert passport.reputation_vector["settled_value_usd"] == 250.0


def test_passport_circuit_breaker_tripping():
    privkey = ed25519.Ed25519PrivateKey.generate()
    pubkey_hex = privkey.public_key().public_bytes_raw().hex()

    passport = SovereignAgentPassport(
        agent_id="agent-untrusted-01",
        worker_model="Custom-Llama-3",
        owner_pubkey=pubkey_hex,
        granted_capabilities=["data:read"]
    )
    passport.sign(privkey)
    assert passport.has_capability("data:read") is True

    # Trip breaker
    passport.trip_circuit_breaker(reason="Invariant breach: unauthorized file deletion attempted")
    assert passport.circuit_breaker_tripped is True
    assert passport.has_capability("data:read") is False

    is_valid, msg = passport.verify_signature()
    assert is_valid is False
    assert "circuit breaker" in msg.lower()


def test_peer_discovery_registry():
    registry = AgentPeerDiscoveryRegistry()
    priv1 = ed25519.Ed25519PrivateKey.generate()
    pub1_hex = priv1.public_key().public_bytes_raw().hex()

    p1 = SovereignAgentPassport(
        agent_id="worker-coder-01",
        worker_model="Claude-3.5-Sonnet",
        owner_pubkey=pub1_hex,
        granted_capabilities=["code:mutate", "git:commit"],
        bonded_warranty_balance_usd=10000.0,
        reputation_vector={"verified_actions": 50, "settled_value_usd": 15000.0, "violation_count": 0, "trust_score": 0.98}
    )
    p1.sign(priv1)
    ok, msg, _ = registry.register_passport(p1.to_dict())
    assert ok is True

    priv2 = ed25519.Ed25519PrivateKey.generate()
    pub2_hex = priv2.public_key().public_bytes_raw().hex()
    p2 = SovereignAgentPassport(
        agent_id="worker-analyst-01",
        worker_model="Gemini-1.5-Pro",
        owner_pubkey=pub2_hex,
        granted_capabilities=["data:read", "telemetry:emit"],
        bonded_warranty_balance_usd=1000.0,
        reputation_vector={"verified_actions": 5, "settled_value_usd": 50.0, "violation_count": 0, "trust_score": 0.75}
    )
    p2.sign(priv2)
    registry.register_passport(p2.to_dict())

    # Query 1: by capability
    coders = registry.query_peers(capability="code:mutate")
    assert len(coders) == 1
    assert coders[0]["agent_id"] == "worker-coder-01"

    # Query 2: by minimum reputation
    high_rep = registry.query_peers(min_reputation=0.90)
    assert len(high_rep) == 1
    assert high_rep[0]["agent_id"] == "worker-coder-01"

    # Query 3: by model family
    geminis = registry.query_peers(model_family="gemini")
    assert len(geminis) == 1
    assert geminis[0]["agent_id"] == "worker-analyst-01"

    # Query 4: by minimum bond
    high_bond = registry.query_peers(min_bond_usd=5000.0)
    assert len(high_bond) == 1
    assert high_bond[0]["bonded_warranty_balance_usd"] == 10000.0


def test_mcp_passport_tool_integration(tmp_path):
    server = BartholomewMCPServer(workspace_root=str(tmp_path))

    # 1. Issue passport via MCP
    issue_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 201,
        "method": "tools/call",
        "params": {
            "name": "btp_issue_agent_passport",
            "arguments": {
                "agent_id": "mcp-worker-01",
                "worker_model": "Claude-3.5-Sonnet",
                "granted_capabilities": ["code:mutate", "db:query"],
                "bonded_warranty_balance_usd": 7500.0
            }
        }
    })
    res = json.loads(server.process_message(issue_req))
    assert not res["result"].get("isError", False)
    passport_dict = json.loads(res["result"]["content"][0]["text"])
    assert passport_dict["agent_id"] == "mcp-worker-01"
    assert "signature" in passport_dict

    # 2. Verify passport via MCP
    verify_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 202,
        "method": "tools/call",
        "params": {
            "name": "btp_verify_agent_passport",
            "arguments": {
                "passport": passport_dict,
                "required_capability": "code:mutate"
            }
        }
    })
    v_res = json.loads(server.process_message(verify_req))
    assert not v_res["result"].get("isError", False)
    v_content = json.loads(v_res["result"]["content"][0]["text"])
    assert v_content["verified"] is True
    assert v_content["status"] == "AUTHORIZED"

    # 3. Discover peers via MCP
    discover_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 203,
        "method": "tools/call",
        "params": {
            "name": "btp_discover_agent_peers",
            "arguments": {
                "capability": "code:mutate"
            }
        }
    })
    d_res = json.loads(server.process_message(discover_req))
    assert not d_res["result"].get("isError", False)
    d_content = json.loads(d_res["result"]["content"][0]["text"])
    assert d_content["count"] == 1
    assert d_content["peers"][0]["agent_id"] == "mcp-worker-01"


def test_a2a_passport_delegation_and_privilege_boundary():
    from src.a2a_protocol import AgentToAgentProtocol
    from src.trust_protocol import BartholomewTrustAuthority

    auth_a = BartholomewTrustAuthority()
    priv_a = auth_a.private_key
    pub_a_hex = auth_a.public_key_hex

    # 1. Issue passport to Agent A with limited scope
    passport_a = SovereignAgentPassport(
        agent_id="agent-planner-01",
        worker_model="Claude-3.5-Sonnet",
        owner_pubkey=pub_a_hex,
        granted_capabilities=["data:read", "analytics:compute"],
        bonded_warranty_balance_usd=5000.0
    )
    passport_a.sign(priv_a)

    # 2. Legitimate delegation within passport scope
    payload = {"query": "SELECT count(*) FROM logs"}
    signed_packet = AgentToAgentProtocol.create_signed_handoff(
        sender_authority=auth_a,
        originating_agent="agent-planner-01",
        target_agent="agent-worker-02",
        task_action="QUERY_LOGS",
        task_payload=payload,
        capability_scope=["data:read"],
        sender_passport=passport_a
    )

    # Verify at recipient
    ok, msg, env = AgentToAgentProtocol.verify_incoming_handoff(
        signed_packet=signed_packet,
        expected_recipient="agent-worker-02",
        trusted_sender_pubkey=pub_a_hex,
        required_capability="data:read"
    )
    assert ok is True
    assert "sender_passport" in env
    assert env["sender_passport"]["agent_id"] == "agent-planner-01"

    # 3. Privilege escalation attempt: Agent A tries delegating capability it doesn't possess
    with pytest.raises(ValueError) as exc:
        AgentToAgentProtocol.create_signed_handoff(
            sender_authority=auth_a,
            originating_agent="agent-planner-01",
            target_agent="agent-worker-02",
            task_action="ROOT_MUTATION",
            task_payload={"cmd": "systemctl restart"},
            capability_scope=["system:admin"],
            sender_passport=passport_a
        )
    assert "Privilege escalation blocked" in str(exc.value)

    # 4. Target recipient requires capability that sender's passport lacks
    ok_fail, msg_fail, _ = AgentToAgentProtocol.verify_incoming_handoff(
        signed_packet=signed_packet,
        expected_recipient="agent-worker-02",
        trusted_sender_pubkey=pub_a_hex,
        required_capability="db:drop"
    )
    assert ok_fail is False
    assert "Missing Required Capability" in msg_fail

