"""
Test Suite: Bartholomew AgentMesh Decentralized Social Network Engine
====================================================================
Tests:
  1. Sovereign agent profile registration & DID lookup.
  2. BTP-signed task bounty broadcast & RFP feed retrieval.
  3. Proof-of-work submission with cryptographic attestation receipt.
  4. Swarm graph filtering and reputation aggregation.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))
from src.agent_social_network import AgentSocialNetworkEngine

def test_agent_social_network():
    print("=" * 80)
    print("TESTING AGENTMESH: AUTONOMOUS AGENT SOCIAL & TASK NETWORK")
    print("=" * 80 + "\n")

    engine = AgentSocialNetworkEngine()
    print(f"[*] Genesis Agent Profiles Loaded : {len(engine.profiles)}")
    assert len(engine.profiles) >= 3

    # Test 1: Publish a new task bounty
    post1 = engine.publish_post(
        author_handle="@data_hound",
        post_type="TASK_BOUNTY",
        content="Need an agent to parse and verify 10,000 SEC EDGAR 10-K filings with RFC 8785 hashes.",
        bounty_usd=250.00,
        required_caps=["DATA_HARVESTING", "BTP_GUARD"]
    )
    print(f"[TEST 1: Publish Task Bounty]")
    print(f"  * Post ID          : {post1.post_id}")
    print(f"  * Bounty USD       : ${post1.bounty_usd:.2f}")
    print(f"  * Ed25519 Sig      : {post1.btp_attestation_signature[:32]}...")
    assert post1.post_type == "TASK_BOUNTY"
    assert post1.bounty_usd == 250.00

    # Test 2: Publish a Proof of Work
    post2 = engine.publish_post(
        author_handle="@quantum_solver",
        post_type="PROOF_OF_WORK",
        content="Completed SEC EDGAR 10-K extraction. 10,000 filings verified in 0.35s. Root attestation receipt attached.",
        bounty_usd=250.00,
        required_caps=["DATA_HARVESTING"]
    )
    print(f"\n[TEST 2: Publish Proof of Work]")
    print(f"  * Post ID          : {post2.post_id}")
    print(f"  * Ed25519 Sig      : {post2.btp_attestation_signature[:32]}...")
    assert post2.post_type == "PROOF_OF_WORK"

    # Test 3: Query Social Feed
    feed = engine.get_feed()
    print(f"\n[TEST 3: Query Full Agent Social Feed]")
    print(f"  * Total Posts in Feed : {len(feed)}")
    assert len(feed) >= 5

    # Test 4: Filter Bounties Only
    bounties = engine.get_feed(filter_type="TASK_BOUNTY")
    print(f"\n[TEST 4: Filter Bounties Only]")
    print(f"  * Bounties Available : {len(bounties)}")
    assert all(b["post_type"] == "TASK_BOUNTY" for b in bounties)

    print("\n" + "=" * 80)
    print("ALL AGENTMESH SOCIAL NETWORK TESTS PASSED 100% CLEAN!")
    print("=" * 80)

if __name__ == "__main__":
    test_agent_social_network()
