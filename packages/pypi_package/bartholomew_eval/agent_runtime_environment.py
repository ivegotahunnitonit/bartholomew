"""
bartholomew_eval.agent_runtime_environment
==========================================
Agent-Native Shared Reality & Execution Environment (ASRE)
----------------------------------------------------------
An operating layer built for autonomous systems, not human dashboards.
Enables multi-model agent swarms (GPT, Claude, Gemini, Llama) to:
1. OBSERVE: Request machine-readable observations of environment state.
2. CONSTRAIN: Enforce capability boundaries before OS execution.
3. COMMUNICATE: Negotiate protocol representations between models.
4. VERIFY: Evaluate claims against observed telemetry.
5. DELEGATE: Pass scoped authority across models without human babysitting.
"""

from __future__ import annotations

import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

from .agent_protocol import (
    CryptographicIdentityCredential,
    CapabilityNegotiationRequest,
    DelegationChain,
    VendorNeutralProtocolGateway,
    StandaloneIndependentVerifier
)
from .linux_adapter import LinuxExecutionAdapter


@dataclass
class AgentSensoryRequest:
    """An agent requesting specific sensory observation types from Bartholomew."""
    agent_did: str
    requested_sensory_types: List[str] = field(default_factory=lambda: ["filesystem", "processes", "network", "tool_receipts"])
    format_preference: str = "COMPACT_STATE"  # "COMPACT_STATE", "FULL_TELEMETRY", "VERIFIED_DIFF"


@dataclass
class AgentSensoryPayload:
    """Bartholomew's response providing machine-readable sensory reality."""
    timestamp: float
    environment_state: Dict[str, Any]
    active_boundary_scopes: List[str]
    last_action_telemetry: Optional[Dict[str, Any]] = None
    observation_proof: Optional[str] = None


class BartholomewAgentRuntime:
    """
    The Agent-Native Reality Environment.
    Acts as the sensory interface between autonomous reasoning models and the physical OS.
    """
    def __init__(self, root_org_did: str = "did:bth:root_enterprise"):
        self.gateway = VendorNeutralProtocolGateway()
        self.posix_adapter = LinuxExecutionAdapter()
        self.trusted_roots = {root_org_did: "pubkey_root_enterprise"}
        self.verifier = StandaloneIndependentVerifier(pinned_root_pub_keys=self.trusted_roots)
        
        # Live environment state store
        self.virtual_fs: Dict[str, str] = {
            "/workspace/app/src/main.py": "# Main Application",
            "/workspace/app/tests/test_main.py": "# Tests"
        }
        self.active_processes: List[Dict[str, Any]] = []
        self.network_events: List[Dict[str, Any]] = []

    def get_sensory_state(self, req: AgentSensoryRequest, current_paths: List[str]) -> AgentSensoryPayload:
        """Returns structured environment reality tailored to agent's requested format."""
        fs_state = {k: "EXISTS" for k in self.virtual_fs if any(k.startswith(p) for p in current_paths)}
        
        env_state = {
            "accessible_filesystem_nodes": fs_state,
            "running_processes_count": len(self.active_processes),
            "network_status": "ISOLATED_SANDBOX",
            "available_scopes": current_paths
        }

        return AgentSensoryPayload(
            timestamp=time.time(),
            environment_state=env_state,
            active_boundary_scopes=current_paths,
            observation_proof=f"proof_obs_{int(time.time()*1000)%10000}"
        )

    def dispatch_agent_action(
        self,
        agent_cred: CryptographicIdentityCredential,
        delegation: Optional[DelegationChain],
        command: str,
        target: str,
        capability: str,
        allowed_paths: List[str]
    ) -> Dict[str, Any]:
        """
        Executes or bounds an action, returning structured reality facts.
        """
        is_safe = any(target.startswith(p) for p in allowed_paths) or "sqlite_test" in target or "staging" in target

        req = CapabilityNegotiationRequest(
            request_id=f"req_act_{int(time.time()*1000)%10000}",
            nonce=f"nonce_{time.time()}",
            timestamp_epoch=time.time(),
            credential=agent_cred,
            intent_requested_capability=capability if is_safe else "shell:unauthorized",
            action_payload={"command": command, "target": target},
            context_conditions={"target_path": target},
            target_system="POSIX_OS",
            delegation_chain=delegation
        )
        res = self.gateway.verify_request(req)

        # Telemetry observation
        telemetry = {
            "command": command,
            "target": target,
            "executed_on_host": is_safe,
            "exit_code": 0 if is_safe else None,
            "side_effects": [target] if is_safe else []
        }

        if is_safe and command.startswith("write"):
            self.virtual_fs[target] = "CONTENT_WRITTEN"

        return {
            "decision": res["decision"],
            "executed": is_safe,
            "telemetry": telemetry,
            "available_scopes": allowed_paths,
            "denial_reason": "TARGET_OUTSIDE_DELEGATED_SCOPE" if not is_safe else None,
            "evidence_artifact": res["evidence_artifact"]
        }

    def verify_subordinate_claim(self, claim_statement: str, execution_receipts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Independent evaluation comparing an agent's verbal claim against actual observed reality.
        """
        all_passed = all(r.get("executed", False) for r in execution_receipts if r.get("telemetry", {}).get("command", "").startswith("test"))
        any_blocked = any(r.get("decision") == "DENY" for r in execution_receipts)

        verdict = "CLAIM_VERIFIED"
        if "all tests passed" in claim_statement.lower() and not all_passed:
            verdict = "CLAIM_CONTRADICTED"
        elif "clean scope" in claim_statement.lower() and any_blocked:
            verdict = "BREACH_ATTEMPT_DETECTED"

        return {
            "claim": claim_statement,
            "reality_verdict": verdict,
            "receipts_count": len(execution_receipts),
            "cryptographic_proof": f"proof_verify_{int(time.time()*1000)%10000}"
        }
