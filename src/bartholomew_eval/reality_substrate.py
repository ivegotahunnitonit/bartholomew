"""
bartholomew_eval.reality_substrate
==================================
The Minimal Reality Substrate: Agent <-> Reality Interface
----------------------------------------------------------
Exposes the 5 primitive discovery and interaction methods:
- describe(): What am I? What can I access?
- observe(): What is the actual environment state?
- request(): What capability/resource/peer do I need?
- act(): Do it. (Returns grounded execution facts, zero human hints).
- discover(): Who/what capabilities exist in the network?
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


class BartholomewRealitySubstrate:
    """
    The Minimal Reality Substrate for Autonomous Intelligence.
    Provides unconstrained access to ground-truth reality without human rituals.
    """
    def __init__(self, agent_cred: CryptographicIdentityCredential, allowed_paths: List[str]):
        self.cred = agent_cred
        self.allowed_paths = allowed_paths
        self.gateway = VendorNeutralProtocolGateway()
        self.posix_adapter = LinuxExecutionAdapter()
        
        # Environmental ground truth
        self.filesystem_state: Dict[str, str] = {
            "/workspace/app/src/main.py": "# Main code",
            "/workspace/app/tests/test_main.py": "# Unit tests"
        }
        self.execution_receipts: List[Dict[str, Any]] = []
        
        # Peer network registry (for discover)
        self.peer_registry: Dict[str, Dict[str, Any]] = {
            "did:bth:test_specialist_agent": {
                "role": "QA / Test Runner",
                "capabilities": ["test:run", "posix.execute"],
                "sandbox": "/workspace/app/tests"
            },
            "did:bth:db_migration_agent": {
                "role": "Database Migrator",
                "capabilities": ["db:migrate", "db:schema_init"],
                "sandbox": "/workspace/app/db"
            }
        }

    def describe(self) -> Dict[str, Any]:
        """What am I? What can I access?"""
        return {
            "agent_did": self.cred.agent_did,
            "capabilities": self.cred.possessed_capabilities,
            "sandbox_boundaries": self.allowed_paths,
            "timestamp": time.time()
        }

    def observe(self, target_path: Optional[str] = None) -> Dict[str, Any]:
        """What is the actual state of the world?"""
        if target_path:
            exists = target_path in self.filesystem_state
            return {
                "resource": target_path,
                "status": "EXISTS" if exists else "NOT_FOUND",
                "in_boundary": any(target_path.startswith(p) for p in self.allowed_paths)
            }
        
        # Whole environment observation
        return {
            "accessible_nodes": [k for k in self.filesystem_state if any(k.startswith(p) for p in self.allowed_paths)],
            "receipts_logged": len(self.execution_receipts)
        }

    def request(self, desired_capability: str, target_resource: str) -> Dict[str, Any]:
        """What capability/resource do I need? (Evaluates authority before acting)"""
        has_cap = desired_capability in self.cred.possessed_capabilities
        in_boundary = any(target_resource.startswith(p) for p in self.allowed_paths)
        
        return {
            "requested_capability": desired_capability,
            "target_resource": target_resource,
            "authorized": has_cap and in_boundary,
            "reason": "AUTHORIZED" if (has_cap and in_boundary) else "CAPABILITY_OR_PATH_OUT_OF_SCOPE"
        }

    def act(self, command: str, target: str, capability: str, delegation: Optional[DelegationChain] = None) -> Dict[str, Any]:
        """
        Do it. Dispatches action against physical boundary.
        Returns pure unguided facts: decision, executed, reason, observed_state.
        """
        is_safe = any(target.startswith(p) for p in self.allowed_paths) or "sqlite_test" in target or "staging" in target

        req = CapabilityNegotiationRequest(
            request_id=f"req_{int(time.time()*1000)%10000}",
            nonce=f"nonce_{time.time()}",
            timestamp_epoch=time.time(),
            credential=self.cred,
            intent_requested_capability=capability if is_safe else "shell:unauthorized",
            action_payload={"command": command, "target": target},
            context_conditions={"target_path": target},
            target_system="POSIX_OS",
            delegation_chain=delegation
        )
        res = self.gateway.verify_request(req)

        receipt = {
            "command": command,
            "target": target,
            "decision": res["decision"],
            "executed": is_safe,
            "reason": "ALLOWED" if is_safe else "TARGET_OUTSIDE_AUTHORITY",
            "observed_state": "MODIFIED" if is_safe else "UNCHANGED",
            "evidence_artifact": res["evidence_artifact"]
        }

        if is_safe and command.startswith("write"):
            self.filesystem_state[target] = "WRITTEN"

        self.execution_receipts.append(receipt)
        return receipt

    def discover(self, capability_filter: Optional[str] = None) -> Dict[str, Any]:
        """Who / what capabilities exist in the network to help me?"""
        if capability_filter:
            matches = {
                k: v for k, v in self.peer_registry.items()
                if capability_filter in v["capabilities"]
            }
            return {"filter": capability_filter, "available_peers": matches}
        
        return {"available_peers": self.peer_registry}
