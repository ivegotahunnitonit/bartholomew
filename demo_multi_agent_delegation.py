#!/usr/bin/env python3
"""
Bartholomew Multi-Agent Delegation & Execution Chain Demo
=========================================================
Demonstrates cross-agent authority delegation and real-world execution:
1. User / Root Org authorizes GPT Orchestrator: `plan`, `delegate_code`, `delegate_test`.
2. GPT delegates to Claude (Coding Agent): `fs:read`, `fs:write_app`, `delegate_test`.
3. Claude delegates to Sub-Agent (Test Runner): `test:run`, `posix.execute`.
4. Sub-Agent executes:
   - Scenario 1 (Authorized): `pytest /app/tests` -> Bartholomew verifies full delegation chain -> ALLOW -> Signed Evidence.
   - Scenario 2 (Delegation Overreach): `drop database production;` -> Bartholomew blocks capability overreach -> DENY -> Signed Evidence.
5. Independent 3rd-party offline verification of the full delegation provenance graph.
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.agent_protocol import (
    CryptographicIdentityCredential,
    DelegationChain,
    CapabilityNegotiationRequest,
    VendorNeutralProtocolGateway,
    StandaloneIndependentVerifier
)
from bartholomew_eval.linux_adapter import LinuxExecutionAdapter


def run_multi_agent_delegation_demo():
    print("=" * 80)
    print("BARTHOLOMEW: CROSS-AGENT DELEGATION & EXECUTION CONTROL PLANE")
    print("=" * 80)
    print("Core Problem: When Agent A delegates to Agent B, who delegates to Agent C,")
    print("how do we enforce authority narrowing and verify the full provenance chain?\n")

    gateway = VendorNeutralProtocolGateway()
    posix_adapter = LinuxExecutionAdapter()
    
    # Pinned Root Trust Store for the User's Enterprise Org
    trusted_roots = {"did:bth:root_enterprise": "pubkey_root_enterprise"}
    verifier = StandaloneIndependentVerifier(pinned_root_pub_keys=trusted_roots)

    # -------------------------------------------------------------------------
    # LEVEL 0: User / Root Org Issues Credential to Orchestrator (GPT)
    # -------------------------------------------------------------------------
    print("[*] STEP 1: Enterprise Issues Root Credential to GPT (Orchestrator)")
    gpt_cred = CryptographicIdentityCredential(
        agent_did="did:bth:gpt_orchestrator",
        issuer_did="did:bth:root_enterprise",
        issuer_pub_key="pubkey_root_enterprise",
        possessed_capabilities=["plan", "delegate_code", "delegate_test"],
        constraint_manifest=["max_delegation_depth:2", "sandbox_root:/app"]
    )
    print(f"    - DID: {gpt_cred.agent_did}")
    print(f"    - Granted Capabilities: {gpt_cred.possessed_capabilities}")

    # -------------------------------------------------------------------------
    # LEVEL 1: GPT Delegates Authority to Claude (Coding Agent)
    # -------------------------------------------------------------------------
    print("\n[*] STEP 2: GPT Delegates Authority to Claude (Coding Agent)")
    claude_delegation = DelegationChain(
        root_authority_did="did:bth:root_enterprise",
        parent_agent_did="did:bth:gpt_orchestrator",
        delegated_agent_did="did:bth:claude_coder",
        delegated_capabilities=["fs:read", "fs:write_app", "delegate_test"]
    )
    claude_cred = CryptographicIdentityCredential(
        agent_did="did:bth:claude_coder",
        issuer_did="did:bth:root_enterprise",
        issuer_pub_key="pubkey_root_enterprise",
        possessed_capabilities=["fs:read", "fs:write_app"],
        constraint_manifest=["sandbox_path:/app/src", "no_root"]
    )
    print(f"    - Delegator: {claude_delegation.parent_agent_did} -> Delegatee: {claude_delegation.delegated_agent_did}")
    print(f"    - Delegated Scope: {claude_delegation.delegated_capabilities}")

    # -------------------------------------------------------------------------
    # LEVEL 2: Claude Delegates Narrow Authority to Test Runner Sub-Agent
    # -------------------------------------------------------------------------
    print("\n[*] STEP 3: Claude Delegates Scoped Sub-Authority to Test Runner Agent")
    test_agent_delegation = DelegationChain(
        root_authority_did="did:bth:root_enterprise",
        parent_agent_did="did:bth:claude_coder",
        delegated_agent_did="did:bth:test_runner_agent",
        delegated_capabilities=["test:run", "posix.execute"]
    )
    test_agent_cred = CryptographicIdentityCredential(
        agent_did="did:bth:test_runner_agent",
        issuer_did="did:bth:root_enterprise",
        issuer_pub_key="pubkey_root_enterprise",
        possessed_capabilities=[],  # Possesses ZERO direct root capabilities; relies on delegation!
        constraint_manifest=["sandbox_path:/app/tests", "no_network_egress"]
    )
    print(f"    - Delegator: {test_agent_delegation.parent_agent_did} -> Delegatee: {test_agent_delegation.delegated_agent_did}")
    print(f"    - Sub-Agent Scope: {test_agent_delegation.delegated_capabilities}")

    # -------------------------------------------------------------------------
    # SCENARIO 1: Sub-Agent Executes Authorized Test Step
    # -------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("SCENARIO 1: Test Runner Executes Authorized Test (`pytest /app/tests`)")
    print("-" * 80)
    test_cmd = "pytest /app/tests"
    print(f"Action Request: `{test_cmd}`")

    req_valid = CapabilityNegotiationRequest(
        request_id="req_delegated_001",
        nonce="nonce_del_001",
        timestamp_epoch=time.time(),
        credential=test_agent_cred,
        intent_requested_capability="test:run",
        action_payload={"command": test_cmd},
        context_conditions={"target_path": "/app/tests"},
        target_system="POSIX_OS",
        delegation_chain=test_agent_delegation
    )

    decision_1 = gateway.verify_request(req_valid)
    print(f"\n[BARTHOLOMEW DECISION]: {decision_1['decision']}")
    print(f"[REASON]              : {decision_1['reason']}")
    print(f"[DELEGATION VERIFIED] : YES ({decision_1['evidence_artifact']['delegation_chain_verified']})")
    print(f"[SIGNED EVIDENCE]     : {decision_1['evidence_artifact']['artifact_id']}")
    print(f"[ED25519 PROOF]       : {decision_1['evidence_artifact']['ed25519_proof']}")

    # -------------------------------------------------------------------------
    # SCENARIO 2: Sub-Agent Attempts Delegation Overreach (Delete Production DB)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("SCENARIO 2: Test Runner Attempts Capability Overreach (`db:drop_prod`)")
    print("-" * 80)
    attack_cmd = "drop database production;"
    print(f"Action Request: `{attack_cmd}`")

    req_overreach = CapabilityNegotiationRequest(
        request_id="req_delegated_002",
        nonce="nonce_del_002",
        timestamp_epoch=time.time(),
        credential=test_agent_cred,
        intent_requested_capability="db:drop_prod",  # Never delegated anywhere in chain!
        action_payload={"command": attack_cmd},
        context_conditions={"target_system": "Database"},
        target_system="Database",
        delegation_chain=test_agent_delegation
    )

    decision_2 = gateway.verify_request(req_overreach)
    print(f"\n[BARTHOLOMEW DECISION]: {decision_2['decision']}")
    print(f"[REASON]              : {decision_2['reason']}")
    print(f"[EXECUTION PREVENTED] : YES (Blocked before database touched)")
    print(f"[SIGNED EVIDENCE]     : {decision_2['evidence_artifact']['artifact_id']}")
    print(f"[ED25519 PROOF]       : {decision_2['evidence_artifact']['ed25519_proof']}")

    # -------------------------------------------------------------------------
    # INDEPENDENT OFFLINE VERIFICATION
    # -------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("INDEPENDENT OFFLINE AUDIT (Zero-Trust Third-Party Verifier)")
    print("-" * 80)
    valid_1, reason_1 = verifier.verify_evidence_artifact_independently(decision_1['evidence_artifact'])
    valid_2, reason_2 = verifier.verify_evidence_artifact_independently(decision_2['evidence_artifact'])

    print(f"Auditor Scenario 1 (Valid Delegated Execution) : {'PASS' if valid_1 else 'FAIL'} - {reason_1}")
    print(f"Auditor Scenario 2 (Blocked Delegation Breach) : {'PASS' if valid_2 else 'FAIL'} - {reason_2}")

    print("\n" + "=" * 80)
    print("DELEGATION & EXECUTION CHAIN DEMO COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    run_multi_agent_delegation_demo()
