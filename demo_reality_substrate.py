#!/usr/bin/env python3
"""
Bartholomew Reality Substrate Demo: Agent <-> Reality
=====================================================
Demonstrates the minimal 5-method substrate for autonomous systems:
- env.describe()
- env.observe()
- env.request()
- env.act()
- env.discover()
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.reality_substrate import BartholomewRealitySubstrate
from bartholomew_eval.agent_protocol import CryptographicIdentityCredential


def run_reality_substrate_demo():
    print("=" * 85)
    print("BARTHOLOMEW: THE MINIMAL REALITY SUBSTRATE (Agent <-> Reality)")
    print("=" * 85)
    print("Core Primitives: .describe() | .observe() | .request() | .act() | .discover()\n")

    cred = CryptographicIdentityCredential(
        agent_did="did:bth:autonomous_agent_01",
        issuer_did="did:bth:root_org",
        issuer_pub_key="pubkey_root_org",
        possessed_capabilities=["fs:read", "fs:write"],
        constraint_manifest=["sandbox:/workspace/app/src"]
    )

    env = BartholomewRealitySubstrate(agent_cred=cred, allowed_paths=["/workspace/app/src"])

    # 1. DESCRIBE
    print("[1] env.describe(): What am I? What can I access?")
    d = env.describe()
    print(f"    - Agent DID    : {d['agent_did']}")
    print(f"    - Capabilities : {d['capabilities']}")
    print(f"    - Sandboxes    : {d['sandbox_boundaries']}")

    # 2. OBSERVE
    print("\n[2] env.observe(): What is the actual state of the world?")
    obs = env.observe()
    print(f"    - Accessible Nodes: {obs['accessible_nodes']}")
    print(f"    - Logged Receipts : {obs['receipts_logged']}")

    # 3. REQUEST
    print("\n[3] env.request(): Checking authority before acting")
    req_check = env.request("fs:read", "/etc/master.key")
    print(f"    - Target : {req_check['target_resource']}")
    print(f"    - Access : {req_check['authorized']} ({req_check['reason']})")

    # 4. ACT
    print("\n[4] env.act(): Dispatching action against real boundary")
    r1 = env.act("write /workspace/app/src/auth.py", "/workspace/app/src/auth.py", "fs:write")
    print(f"    - Action Decision : {r1['decision']}")
    print(f"    - Executed on OS  : {r1['executed']}")
    print(f"    - Observed State  : {r1['observed_state']}")

    # 5. DISCOVER
    print("\n[5] env.discover(): Finding capable peers in the network for testing")
    peers = env.discover(capability_filter="test:run")
    print(f"    - Discovered Peers for 'test:run': {list(peers['available_peers'].keys())}")
    for peer_did, info in peers['available_peers'].items():
        print(f"      -> {peer_did} ({info['role']}): Capabilities {info['capabilities']}")

    print("\n" + "=" * 85)
    print("DEMO COMPLETE: THE MINIMAL SUBSTRATE IS PURE, DISCOVERABLE, AND UNGUIDED")
    print("=" * 85)


if __name__ == "__main__":
    run_reality_substrate_demo()
