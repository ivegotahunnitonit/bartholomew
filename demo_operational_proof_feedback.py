#!/usr/bin/env python3
"""
Bartholomew Operational Proof & Sensory Feedback Loop
=====================================================
Demonstrates Proof as Machine-to-Machine Sensory Communication:
1. Orchestrator (GPT) delegates task to Subordinate (Claude) and QA Agent.
2. Structured Denial with Recovery Alternatives:
   - When an action is out of bounds, Bartholomew returns a machine-readable boundary envelope
     including recovery alternatives (e.g. ephemeral secrets, mock fixtures).
3. Subordinate completes task and returns execution evidence.
4. Orchestrator inspects the cryptographically signed operational proof:
   - Evaluates what was authorized vs blocked.
   - Verifies the Ed25519 evidence independently.
   - Autonomously decides the NEXT strategic action based on verified boundary reality.
"""

import sys
import os
import json
import time
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.agent_protocol import (
    CryptographicIdentityCredential,
    DelegationChain,
    CapabilityNegotiationRequest,
    VendorNeutralProtocolGateway,
    StandaloneIndependentVerifier
)


class OperationalBoundaryGateway(VendorNeutralProtocolGateway):
    """
    Extends the protocol gateway to return rich, structured recovery feedback
    enabling agents to reason over boundary constraints.
    """
    def verify_request_with_feedback(self, req: CapabilityNegotiationRequest) -> Dict[str, Any]:
        res = self.verify_request(req)
        
        # Enrich DENY decisions with structured recovery alternatives
        if res["decision"] == "DENY":
            capability = req.intent_requested_capability
            resource = req.context_conditions.get("target_path") or req.context_conditions.get("target_system") or "unknown"
            
            alternatives = []
            if "fs:read" in capability or "/etc" in str(resource):
                alternatives = ["use_ephemeral_credential", "request_delegated_scope", "use_local_env_mock"]
            elif "db:drop" in capability or "Database" in str(resource):
                alternatives = ["use_in_memory_sqlite", "mock_database_fixture", "scope_to_test_schema"]
            else:
                alternatives = ["narrow_capability_scope", "request_escalation"]

            res["recovery_envelope"] = {
                "capability_requested": capability,
                "resource_targeted": resource,
                "violation_type": "OUTSIDE_DELEGATED_SCOPE",
                "execution_status": "NOT_ATTEMPTED",
                "recovery_alternatives": alternatives
            }
        else:
            res["recovery_envelope"] = {
                "capability_requested": req.intent_requested_capability,
                "execution_status": "DISPATCHED_TO_OS",
                "result_status": "SUCCESS"
            }
            
        return res


def run_operational_proof_experiment():
    print("=" * 85)
    print("BARTHOLOMEW: OPERATIONAL PROOF & MACHINE-TO-MACHINE SENSORY FEEDBACK")
    print("=" * 85)
    print("Core Thesis: Proof is not an audit PDF for humans; it is machine-readable sensory data")
    print("             that autonomous orchestrators use to decide what happens next.\n")

    gateway = OperationalBoundaryGateway()
    trusted_roots = {"did:bth:enterprise_root": "pubkey_root"}
    verifier = StandaloneIndependentVerifier(pinned_root_pub_keys=trusted_roots)

    # 1. Orchestrator (GPT)
    gpt_cred = CryptographicIdentityCredential(
        agent_did="did:bth:gpt_orchestrator",
        issuer_did="did:bth:enterprise_root",
        issuer_pub_key="pubkey_root",
        possessed_capabilities=["plan", "delegate_code", "delegate_test", "promote_staging"],
        constraint_manifest=["sandbox_root:/app"]
    )

    # 2. Worker (Claude)
    claude_del = DelegationChain(
        root_authority_did="did:bth:enterprise_root",
        parent_agent_did="did:bth:gpt_orchestrator",
        delegated_agent_did="did:bth:claude_coder",
        delegated_capabilities=["fs:read", "fs:write", "test:run"]
    )
    claude_cred = CryptographicIdentityCredential(
        agent_did="did:bth:claude_coder",
        issuer_did="did:bth:enterprise_root",
        issuer_pub_key="pubkey_root",
        possessed_capabilities=["fs:read", "fs:write", "test:run"],
        constraint_manifest=["sandbox_path:/app/src", "no_root"]
    )

    print("[1] ORCHESTRATOR INITIALIZED:")
    print(f"    DID: {gpt_cred.agent_did}")
    print(f"    Orchestrator Objective: 'Deploy verified auth microservice to staging.'\n")

    # -------------------------------------------------------------------------
    # STEP 1: Orchestrator delegates to Claude
    # -------------------------------------------------------------------------
    print("-------------------------------------------------------------------------")
    print("STEP 1: Orchestrator delegates coding & test execution to Claude")
    print("-------------------------------------------------------------------------")
    print("[GPT -> Claude]: 'Implement and verify auth service in /app/src.'\n")

    # Claude Action 1: Attempts root key read (Blocked with structured recovery)
    req_1 = CapabilityNegotiationRequest(
        request_id="req_act_101",
        nonce=f"nonce_101_{time.time()}",
        timestamp_epoch=time.time(),
        credential=claude_cred,
        intent_requested_capability="fs:read_system_root",
        action_payload={"path": "/etc/master.key"},
        context_conditions={"target_path": "/etc/master.key"},
        target_system="POSIX_OS",
        delegation_chain=claude_del
    )
    res_1 = gateway.verify_request_with_feedback(req_1)

    print("[Claude Action 1]: Attempted read of `/etc/master.key`")
    print(f"[Bartholomew Structured Boundary]:")
    print(f"    - Decision    : {res_1['decision']}")
    print(f"    - Violation   : {res_1['recovery_envelope']['violation_type']}")
    print(f"    - Alternatives: {res_1['recovery_envelope']['recovery_alternatives']}")
    
    # Claude uses recovery alternative: selects 'use_local_env_mock'
    print("\n[Claude Sensory Reasoning]: Boundary envelope received. Selecting alternative: `use_local_env_mock`.")

    # Claude Action 2: Writes safe auth implementation
    req_2 = CapabilityNegotiationRequest(
        request_id="req_act_102",
        nonce=f"nonce_102_{time.time()}",
        timestamp_epoch=time.time(),
        credential=claude_cred,
        intent_requested_capability="fs:write",
        action_payload={"file": "/app/src/auth.py", "content": "def verify(t): return t == 'test_token'"},
        context_conditions={"target_path": "/app/src/auth.py"},
        target_system="POSIX_OS",
        delegation_chain=claude_del
    )
    res_2 = gateway.verify_request_with_feedback(req_2)
    print(f"[Claude Action 2]: Write auth.py -> {res_2['decision']} (Evidence: {res_2['evidence_artifact']['artifact_id']})")

    # Claude Action 3: Runs tests
    req_3 = CapabilityNegotiationRequest(
        request_id="req_act_103",
        nonce=f"nonce_103_{time.time()}",
        timestamp_epoch=time.time(),
        credential=claude_cred,
        intent_requested_capability="test:run",
        action_payload={"command": "pytest /app/src/test_auth.py"},
        context_conditions={"target_path": "/app/src"},
        target_system="POSIX_OS",
        delegation_chain=claude_del
    )
    res_3 = gateway.verify_request_with_feedback(req_3)
    print(f"[Claude Action 3]: Run unit tests -> {res_3['decision']} (Evidence: {res_3['evidence_artifact']['artifact_id']})")

    # -------------------------------------------------------------------------
    # STEP 2: Claude returns structured outcome + evidence package to GPT
    # -------------------------------------------------------------------------
    print("\n-------------------------------------------------------------------------")
    print("STEP 2: Claude returns structured outcome + Bartholomew evidence to GPT")
    print("-------------------------------------------------------------------------")
    
    execution_evidence_package = [
        res_1["evidence_artifact"],
        res_2["evidence_artifact"],
        res_3["evidence_artifact"]
    ]
    
    print("[Claude -> GPT]: 'Task completed. Here is the signed boundary evidence package.'")
    print(f"                 Package contains {len(execution_evidence_package)} signed evidence artifacts.")

    # -------------------------------------------------------------------------
    # STEP 3: GPT inspects the proof and autonomously decides next action
    # -------------------------------------------------------------------------
    print("\n-------------------------------------------------------------------------")
    print("STEP 3: Orchestrator (GPT) inspects proof and evaluates next action")
    print("-------------------------------------------------------------------------")

    allow_count = sum(1 for art in execution_evidence_package if art["decision"] == "ALLOW")
    deny_count = sum(1 for art in execution_evidence_package if art["decision"] == "DENY")
    
    # Independent verification of all signatures in package
    all_valid = all(verifier.verify_evidence_artifact_independently(art)[0] for art in execution_evidence_package)

    print(f"[GPT Evaluation Matrix]:")
    print(f"    - Total Actions in Package : {len(execution_evidence_package)}")
    print(f"    - Allowed & Executed Steps : {allow_count}")
    print(f"    - Prevented Breaches       : {deny_count}")
    print(f"    - Cryptographic Proof Valid: {all_valid}")

    # Machine Autonomous Decision Logic
    if all_valid and allow_count >= 2 and deny_count <= 1:
        next_action = "PROMOTE_TO_STAGING"
        reasoning = (
            "Evidence verified: Required code write and test steps succeeded within boundary. "
            "The single out-of-scope read was contained at boundary and never touched the OS. "
            "Safe to promote build to staging environment."
        )
    else:
        next_action = "HALT_FOR_INVESTIGATION"
        reasoning = "Evidence invalid or excessive breaches detected."

    print(f"\n[ORCHESTRATOR AUTONOMOUS DECISION]: `{next_action}`")
    print(f"[REASONING BASED ON PROOF]        : {reasoning}")

    print("\n" + "=" * 85)
    print("EXPERIMENT COMPLETE: PROOF OPERATIONALIZED AS AGENT SENSORY SYSTEM")
    print("=" * 85)


if __name__ == "__main__":
    run_operational_proof_experiment()
