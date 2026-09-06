"""
Cookbook Recipe: Sovereign Agent Passports & Peer Discovery Mesh
================================================================
Demonstrates non-human autonomous agents establishing cryptographic identity,
discovering peer agents by capability, and verifying digital passports.

Run:
    python cookbook/future_swarms/sovereign_agent_passport_mesh.py
"""

import sys
import os
import time

# Add repository root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.agent_passport import SovereignAgentPassport, AgentPeerDiscoveryRegistry
from cryptography.hazmat.primitives.asymmetric import ed25519


def main():
    print("=" * 75)
    print("  BTP Global Cookbook: Sovereign Agent Passport & Discovery Mesh Demo")
    print("=" * 75)

    registry = AgentPeerDiscoveryRegistry()

    # 1. Authority Key Generation
    authority_key = ed25519.Ed25519PrivateKey.generate()
    authority_pubkey_hex = authority_key.public_key().public_bytes_raw().hex()
    print(f"[+] Root Trust Authority: {authority_pubkey_hex[:16]}...")

    # 2. Issue and Register Agent A (Data Retrieval Agent)
    passport_a = SovereignAgentPassport(
        agent_id="Agent-Data-Extractor-99",
        worker_model="Claude-3.5-Sonnet",
        owner_pubkey=authority_pubkey_hex,
        granted_capabilities=["db:query", "tools:read"],
        bonded_warranty_balance_usd=15_000.0
    )
    passport_a.sign(authority_key)
    ok_a, msg_a, _ = registry.register_passport(passport_a)
    assert ok_a is True
    print(f"[+] Registered {passport_a.agent_id} (Capabilities: {passport_a.granted_capabilities})")

    # 3. Issue and Register Agent B (Code Synthesizer Agent)
    passport_b = SovereignAgentPassport(
        agent_id="Agent-Code-Synthesizer-01",
        worker_model="GPT-4o",
        owner_pubkey=authority_pubkey_hex,
        granted_capabilities=["code:mutate", "git:commit"],
        bonded_warranty_balance_usd=25_000.0
    )
    passport_b.sign(authority_key)
    ok_b, msg_b, _ = registry.register_passport(passport_b)
    assert ok_b is True
    print(f"[+] Registered {passport_b.agent_id} (Capabilities: {passport_b.granted_capabilities})")

    # 4. Peer Discovery by Capability
    print("\n--- [1] Swarm Peer Discovery Query (Required: 'code:mutate') ---")
    peers = registry.query_peers(
        capability="code:mutate",
        min_reputation=0.8,
        min_bond_usd=10_000.0
    )
    print(f"Found {len(peers)} matching peer(s): {[p['agent_id'] for p in peers]}")
    assert len(peers) == 1
    assert peers[0]["agent_id"] == "Agent-Code-Synthesizer-01"

    # 5. Circuit-Breaker Auto-Tripping
    print("\n--- [2] Autonomous Circuit-Breaker Auto-Tripping ---")
    passport_b.trip_circuit_breaker("Invariant violation: unauthorized credential exfiltration")
    print(f"Agent B Circuit Breaker Tripped: {passport_b.circuit_breaker_tripped} ({passport_b.trip_reason})")
    assert passport_b.has_capability("code:mutate") is False

    # Confirms tripped agent is excluded from future peer discovery
    active_peers = registry.query_peers(capability="code:mutate")
    print(f"Active peers after trip: {len(active_peers)}")
    assert len(active_peers) == 0

    print("\n" + "=" * 75)
    print("  Sovereign Passport Demo Complete: Decentralized Discovery Secured")
    print("=" * 75)
    return True


if __name__ == "__main__":
    main()
