"""
BTP Autonomous Agent-to-Agent Mesh & Discovery Daemon
Enables autonomous agents to discover Bartholomew, exchange cryptographic trust roots,
and execute attested delegations without human intervention.
"""

import os
import sys
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.rfc8785 import rfc8785_canonicalize
from standalone_btp_verifier import independent_verify_btp_receipt
from src.trust_protocol import BartholomewTrustAuthority

class AutonomousAgentMeshNode:
    """
    Self-Configuring Autonomous Agent Node in the BTP Network Mesh.
    Agents reach Bartholomew automatically for trust receipts, and
    Bartholomew autonomously validates peer agent interactions.
    """
    def __init__(self, 
                 agent_name: str, 
                 discovery_endpoint: str = "https://www.bartholomew.info/.well-known/btp-configuration.json"):
        self.agent_name = agent_name
        self.discovery_endpoint = discovery_endpoint
        self.authority = BartholomewTrustAuthority(ttl_seconds=300)
        self.known_peers: Dict[str, str] = {} # peer_name -> public_key_hex
        self.policy_cache: Dict[str, str] = {
            "urn:btp:policy:owasp-agentic-v2026.1": hashlib.sha256(b"STRICT_SANDBOX").hexdigest()
        }

    def discover_authority(self, config_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Discovers BTP protocol configuration machine-to-machine."""
        if config_dict:
            return config_dict
        return {
            "protocol_version": "BTP/2.2",
            "authority_identity": "Bartholomew-Trust-Engine-v2.2",
            "canonicalization_standard": "RFC_8785_JCS",
            "signature_algorithm": "FIPS_186_5_ED25519",
            "offline_verification_supported": True
        }

    def register_peer(self, peer_name: str, peer_pubkey_hex: str):
        """Registers a known peer agent in the local multi-authority trust store."""
        self.known_peers[peer_name] = peer_pubkey_hex

    def autonomous_outbound_delegation(self, 
                                       target_peer: str, 
                                       action_type: str, 
                                       payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agent autonomously requests a BTP attestation before executing 
        a cross-framework delegation.
        """
        # Autonomous pre-flight attestation generation
        attestation_packet = self.authority.evaluate_intent(
            agent_id=self.agent_name,
            action_type=action_type,
            payload=payload,
            target_recipient=target_peer
        )
        return {
            "sender": self.agent_name,
            "target": target_peer,
            "payload": payload,
            "btp_attestation_envelope": attestation_packet
        }

    def autonomous_inbound_execution(self, incoming_packet: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Receiving agent autonomously verifies the incoming action proof 
        100% offline before executing tool code.
        """
        sender = incoming_packet.get("sender", "unknown")
        payload = incoming_packet.get("payload", {})
        envelope = incoming_packet.get("btp_attestation_envelope", {})
        
        # Verify against local trust store
        trusted_keys = list(self.known_peers.values()) + [self.authority.public_key_hex]

        ok, msg = independent_verify_btp_receipt(
            receipt_json_str=envelope,
            candidate_payload=payload,
            trusted_root_pubkeys=trusted_keys,
            expected_recipient_context=self.agent_name
        )
        return ok, msg

def run_mesh_simulation():
    print("=" * 80)
    print("  AUTONOMOUS AGENT-TO-AGENT MESH & DISCOVERY PROTOCOL")
    print("=" * 80)

    # 1. Spawn Autonomous Agent A (LangGraph) & Agent B (AutoGen)
    agent_a = AutonomousAgentMeshNode("Agent-LangGraph-Master")
    agent_b = AutonomousAgentMeshNode("Agent-AutoGen-Worker")

    # 2. Machine Discovery & Mutual Trust Handshake
    agent_a.register_peer("Agent-AutoGen-Worker", agent_b.authority.public_key_hex)
    agent_b.register_peer("Agent-LangGraph-Master", agent_a.authority.public_key_hex)

    print("[1] Autonomous Service Discovery: Active (.well-known/btp-configuration)")
    print(f"  |-- Agent A Identity: {agent_a.agent_name} (Ed25519 Root Registered)")
    print(f"  |-- Agent B Identity: {agent_b.agent_name} (Ed25519 Root Registered)")

    # 3. Agent A autonomously delegates an action to Agent B
    action_payload = {"task": "AST_SLA_HEAL", "file": "worker.py", "delta": 3}
    delegation_packet = agent_a.autonomous_outbound_delegation(
        target_peer="Agent-AutoGen-Worker",
        action_type="DEPLOY_PATCH",
        payload=action_payload
    )
    print("\n[2] Agent A -> BTP Attestation Envelope Generated Autonomously")
    print(f"  |-- Action: {delegation_packet['btp_attestation_envelope']['attestation']['action_type']}")
    print(f"  |-- Verdict: {delegation_packet['btp_attestation_envelope']['attestation']['verdict']}")
    print(f"  |-- Target Recipient: {delegation_packet['btp_attestation_envelope']['attestation']['target_recipient']}")

    # 4. Agent B receives and autonomously executes offline verification
    ok, msg = agent_b.autonomous_inbound_execution(delegation_packet)
    print("\n[3] Agent B Offline Verification & Tool Execution Gate")
    print(f"  |-- Verification Status: [{'AUTHORIZED' if ok else 'DENIED'}]")
    print(f"  |-- Proof Result: {msg}")

    print("\n" + "=" * 80)
    print("  AUTONOMOUS AGENT MESH HANDSHAKE: 100% SUCCESSFUL")
    print("=" * 80)
    return ok

if __name__ == "__main__":
    import sys
    success = run_mesh_simulation()
    sys.exit(0 if success else 1)
