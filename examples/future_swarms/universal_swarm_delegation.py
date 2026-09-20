"""
Cookbook Recipe: Universal Swarm Delegation & Cryptographic A2A Protocol
=========================================================================
Demonstrates vendor-neutral, all-encompassing multi-agent delegation across
AutoGen, Cloudflare Agents, Google Gemini, and OpenAI swarms using:
  1. RFC 8785 Canonical Ed25519 Signed Envelopes (Non-Repudiation).
  2. Sovereign Passport Capability Attenuation (No Privilege Escalation).
  3. L402 Lightning Micropayment Token Headers (Pay-per-Handoff).
  4. Nonce-Based Replay Protection.

Run:
    python examples/future_swarms/universal_swarm_delegation.py
"""

import sys
import os
import time
from typing import Dict, Any

# Add repository root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.trust_protocol import BartholomewTrustAuthority
from src.a2a_protocol import AgentToAgentProtocol
from src.agent_passport import SovereignAgentPassport
from src.settlement.l402_protocol import L402ProtocolEngine
from cryptography.hazmat.primitives.asymmetric import ed25519


def main():
    print("=" * 78)
    print("  BTP Global Cookbook: Universal Swarm Delegation (A2A Protocol)")
    print("=" * 78)

    # 1. Initialize authorities and agent passports
    authority_planner = BartholomewTrustAuthority(ttl_seconds=300)
    owner_key = ed25519.Ed25519PrivateKey.generate()
    owner_pubkey_hex = owner_key.public_key().public_bytes_raw().hex()

    planner_passport = SovereignAgentPassport(
        agent_id="Swarm-Planner-01",
        worker_model="Gemini-3.8-Ultra / AutoGen",
        owner_pubkey=owner_pubkey_hex,
        granted_capabilities=["telemetry:read", "compute:run", "ast:strict"]
    )
    planner_passport.sign(owner_key)

    # 2. Setup L402 Lightning Micropayment Rail
    l402_engine = L402ProtocolEngine()
    challenge, preimage = l402_engine.create_challenge(
        agent_id="Swarm-Planner-01",
        action_type="TASK_EXECUTION",
        amount_satoshis=1000,
        ttl_seconds=120
    )
    l402_auth = f"L402 {challenge.macaroon_b64}:{preimage}"

    # 3. Create Signed A2A Delegation Envelope
    print("\n--- [1] Generating Signed A2A Swarm Delegation Envelope ---")
    signed_packet = AgentToAgentProtocol.create_signed_handoff(
        sender_authority=authority_planner,
        originating_agent="Swarm-Planner-01",
        target_agent="Swarm-Worker-Cloudflare",
        task_action="TASK_EXECUTION",
        task_payload={"task": "aggregate_fleet_metrics", "format": "JSON"},
        capability_scope=["telemetry:read", "ast:strict"],
        sender_passport=planner_passport,
        ttl_seconds=60,
        l402_auth=l402_auth
    )

    envelope = signed_packet["a2a_envelope"]
    print(f"[+] Protocol: {envelope['protocol']}")
    print(f"[+] Sender:   {envelope['sender_agent_id']} -> Recipient: {envelope['recipient_agent_id']}")
    print(f"[+] Nonce:    {envelope['envelope_nonce']}")
    print(f"[+] Scope:    {envelope['granted_scope']}")
    print(f"[+] Ed25519 Signature: {signed_packet['signature'][:32]}...")

    # 4. Target Agent Verifies Incoming Swarm Handoff
    print("\n--- [2] Target Agent Verifies Cryptographic Envelope & L402 Payment ---")
    is_valid, msg, verified_env = AgentToAgentProtocol.verify_incoming_handoff(
        signed_packet=signed_packet,
        expected_recipient="Swarm-Worker-Cloudflare",
        trusted_sender_pubkey=authority_planner.public_key_hex,
        required_capability="telemetry:read",
        l402_engine=l402_engine,
        required_satoshis=1000
    )
    print(f"[+] Verification Result: {is_valid} ({msg})")
    assert is_valid is True

    # 5. Prevent Privilege Escalation
    print("\n--- [3] Verifying Rejection of Unauthorized Capability Escalation ---")
    try:
        AgentToAgentProtocol.create_signed_handoff(
            sender_authority=authority_planner,
            originating_agent="Swarm-Planner-01",
            target_agent="Swarm-Worker-Cloudflare",
            task_action="ROOT_ADMIN_ACTION",
            task_payload={"cmd": "grant_all"},
            capability_scope=["SYSTEM_ROOT_ADMIN"],  # Not granted in planner_passport!
            sender_passport=planner_passport
        )
        assert False, "Should have blocked privilege escalation!"
    except ValueError as e:
        print(f"[!] Escalation Blocked by BTP: {e}")
        assert "Privilege escalation blocked" in str(e)

    print("\n" + "=" * 78)
    print("  Universal Swarm Delegation Complete: Cryptographically Sealed & Paid")
    print("=" * 78)
    return True


if __name__ == "__main__":
    main()
