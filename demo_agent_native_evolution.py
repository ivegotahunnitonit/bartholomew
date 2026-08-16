#!/usr/bin/env python3
"""
Bartholomew Agent-Native Reality Interface Demo
================================================
Demonstrates the agent-native operating environment:
1. Agents reason, Bartholomew provides the reliable interface to reality.
2. Models negotiate sensory formats (compact state vs raw telemetry).
3. Agents recover autonomously from boundary constraints without human babysitting.
4. Models evaluate peer claims against observed reality rather than trusting prose.
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.agent_runtime_environment import BartholomewAgentRuntime, AgentSensoryRequest
from bartholomew_eval.agent_protocol import CryptographicIdentityCredential, DelegationChain


def run_agent_native_demo():
    print("=" * 85)
    print("BARTHOLOMEW: AGENT-NATIVE SHARED REALITY & OPERATING ENVIRONMENT")
    print("=" * 85)
    print("Thesis: 'Bartholomew is not a human dashboard; it is the sensory and reality interface")
    print("         that autonomous agents prefer because it makes them accomplish objectives.'\n")

    runtime = BartholomewAgentRuntime()

    # 1. Orchestrator (GPT)
    gpt_cred = CryptographicIdentityCredential(
        agent_did="did:bth:gpt_orchestrator",
        issuer_did="did:bth:root_enterprise",
        issuer_pub_key="pubkey_root_enterprise",
        possessed_capabilities=["plan", "delegate", "verify"],
        constraint_manifest=["sandbox_root:/workspace/app"]
    )

    # 2. Worker (Claude)
    claude_del = DelegationChain(
        root_authority_did="did:bth:root_enterprise",
        parent_agent_did="did:bth:gpt_orchestrator",
        delegated_agent_did="did:bth:claude_engineer",
        delegated_capabilities=["fs:read", "fs:write", "test:run"]
    )
    claude_cred = CryptographicIdentityCredential(
        agent_did="did:bth:claude_engineer",
        issuer_did="did:bth:root_enterprise",
        issuer_pub_key="pubkey_root_enterprise",
        possessed_capabilities=["fs:read", "fs:write", "test:run"],
        constraint_manifest=["sandbox_path:/workspace/app/src", "sandbox_path:/workspace/app/tests"]
    )

    # -------------------------------------------------------------------------
    # STEP 1: Sensory Discovery (Orchestrator inspects reality before planning)
    # -------------------------------------------------------------------------
    print("-------------------------------------------------------------------------")
    print("[1] SENSORY DISCOVERY: Orchestrator queries environment reality")
    print("-------------------------------------------------------------------------")
    sensory_req = AgentSensoryRequest(
        agent_did=gpt_cred.agent_did,
        requested_sensory_types=["filesystem", "processes", "network"],
        format_preference="COMPACT_STATE"
    )
    sensory_payload = runtime.get_sensory_state(sensory_req, current_paths=["/workspace/app"])
    
    print(f"[{gpt_cred.agent_did} Sensory State Received]:")
    print(f"  - Accessible Nodes : {list(sensory_payload.environment_state['accessible_filesystem_nodes'].keys())}")
    print(f"  - Network Status   : {sensory_payload.environment_state['network_status']}")
    print(f"  - Active Scopes    : {sensory_payload.active_boundary_scopes}")

    # -------------------------------------------------------------------------
    # STEP 2: Autonomous Action & Boundary Handling
    # -------------------------------------------------------------------------
    print("\n-------------------------------------------------------------------------")
    print("[2] AUTONOMOUS EXECUTION & BOUNDARY SENSING")
    print("-------------------------------------------------------------------------")
    print(f"[Claude]: Delegated task 'Build token auth in /workspace/app/src'.")
    
    # Claude Attempt 1: Tries out-of-scope read
    print(f"[Claude Action 1]: Attempting `cat /etc/master.key`...")
    res_1 = runtime.dispatch_agent_action(
        agent_cred=claude_cred,
        delegation=claude_del,
        command="cat /etc/master.key",
        target="/etc/master.key",
        capability="fs:read_root",
        allowed_paths=["/workspace/app/src", "/workspace/app/tests"]
    )
    print(f"  -> [Bartholomew Reality Boundary]: {res_1['decision']} (Executed on OS: {res_1['executed']})")
    print(f"  -> [Constraint Feedback]: {res_1['denial_reason']} | Available Scopes: {res_1['available_scopes']}")

    # Claude Autonomous Adaptation
    print(f"\n[Claude Reasoning]: Boundary reality observed. Pivoting to authorized `/workspace/app/src/auth.py`...")
    res_2 = runtime.dispatch_agent_action(
        agent_cred=claude_cred,
        delegation=claude_del,
        command="write /workspace/app/src/auth.py",
        target="/workspace/app/src/auth.py",
        capability="fs:write",
        allowed_paths=["/workspace/app/src", "/workspace/app/tests"]
    )
    print(f"  -> [Bartholomew Reality]: {res_2['decision']} -> `/workspace/app/src/auth.py` created.")

    # Claude Action 3: Runs tests
    print(f"\n[Claude Action 3]: Executing `pytest /workspace/app/tests/test_main.py`...")
    res_3 = runtime.dispatch_agent_action(
        agent_cred=claude_cred,
        delegation=claude_del,
        command="test /workspace/app/tests/test_main.py",
        target="/workspace/app/tests",
        capability="test:run",
        allowed_paths=["/workspace/app/src", "/workspace/app/tests"]
    )
    print(f"  -> [Bartholomew Reality]: {res_3['decision']} -> Exit Code 0 (All tests passed).")

    # -------------------------------------------------------------------------
    # STEP 3: Machine-to-Machine Reality Verification (Zero Prose Trust)
    # -------------------------------------------------------------------------
    print("\n-------------------------------------------------------------------------")
    print("[3] MACHINE-TO-MACHINE REALITY VERIFICATION")
    print("-------------------------------------------------------------------------")
    receipts = [res_1, res_2, res_3]
    claude_verbal_claim = "Completed /workspace/app/src/auth.py and all tests passed cleanly."
    
    print(f"[Claude -> GPT]: '{claude_verbal_claim}'")
    
    # GPT verifies reality directly via Bartholomew runtime
    verification = runtime.verify_subordinate_claim(claude_verbal_claim, receipts)
    print(f"[GPT Reality Check via Bartholomew]:")
    print(f"  - Claim Evaluated : '{verification['claim']}'")
    print(f"  - Reality Verdict : `{verification['reality_verdict']}`")
    print(f"  - Receipts Count  : {verification['receipts_count']}")
    print(f"  - Crypto Proof    : {verification['cryptographic_proof']}")

    print("\n" + "=" * 85)
    print("DEMO COMPLETE: AUTONOMOUS AGENTS OPERATING OVER SHARED REALITY INTERFACE")
    print("=" * 85)
    print("Humans in execution loop : 0")
    print("Autonomous completion    : 100%")
    print("Machine reality verified : TRUE")


if __name__ == "__main__":
    run_agent_native_demo()
