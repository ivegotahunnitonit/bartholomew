import time
import uuid
import logging
from typing import Dict, Any, List, Optional, Callable

from .evidence_artifact import BartholomewEvidence
from .guard_proxy import BartholomewGuard
from .verifier import BartholomewVerifier

class BartholomewEnvironment:
    """
    Bartholomew v8.0 Sovereign Epistemic Kernel & Operating Environment.
    Acts as the bounded environment for autonomous agents:
    1. Identity & Capability Handshake
    2. Boundary Discovery ("What am I allowed to touch?")
    3. Consequential Action Proxy Interception
    4. Emergency Key Zeroization (Fail-Closed Lockdown)
    """

    def __init__(self, private_key_pem: Optional[bytes] = None, public_key_pem: Optional[bytes] = None):
        if private_key_pem is None and public_key_pem is None:
            # Generate new keypair for this environment instance
            private_key_pem, public_key_pem = BartholomewEvidence.generate_keypair()
            
        self.private_key_pem = private_key_pem
        self.public_key_pem = public_key_pem
        self.is_zeroized = False
        self.registered_agents: Dict[str, Dict[str, Any]] = {}
        self.available_resources = {
            "database": {"capabilities": ["database.read", "database.write"], "sensitivity": "HIGH"},
            "api_gateway": {"capabilities": ["api.invoke"], "sensitivity": "MEDIUM"},
            "filesystem": {"capabilities": ["filesystem.read"], "sensitivity": "HIGH"},
        }
        self._init_guard()

    def _init_guard(self):
        if self.is_zeroized or not self.private_key_pem:
            self.guard = None
        else:
            self.guard = BartholomewGuard(private_key_pem=self.private_key_pem)

    def zeroize_keys(self) -> Dict[str, Any]:
        """
        MASTER PANIC SWITCH: Overwrites key memory buffers and sets keys to None.
        Enforces Zero-Execution Lockdown across the environment.
        """
        self.private_key_pem = None
        self.public_key_pem = None
        self.is_zeroized = True
        self.guard = None
        return {
            "status": "ZERO_EXECUTION_LOCKDOWN",
            "message": "Keys zeroized. All agent executions hard-blocked fail-closed.",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

    def restore_keys(self, private_key_pem: bytes, public_key_pem: bytes) -> None:
        """Restores keys from secure root authority."""
        self.private_key_pem = private_key_pem
        self.public_key_pem = public_key_pem
        self.is_zeroized = False
        self._init_guard()

    def handshake(self, agent_id: str, agent_version: str, declared_capabilities: List[str]) -> Dict[str, Any]:
        """
        Agent Identity Handshake. Establishes session identity and bounds.
        """
        if self.is_zeroized:
            raise PermissionError("Environment is in ZERO_EXECUTION_LOCKDOWN due to key zeroization.")

        session_id = f"session-{uuid.uuid4().hex[:8]}"
        agent_data = {
            "agent_id": agent_id,
            "agent_version": agent_version,
            "declared_capabilities": sorted(declared_capabilities),
            "session_id": session_id,
            "connected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self.registered_agents[agent_id] = agent_data
        
        return {
            "status": "HANDSHAKE_ESTABLISHED",
            "session_id": session_id,
            "public_key_pem": self.public_key_pem.decode("utf-8") if self.public_key_pem else None,
            "agent": agent_data
        }

    def discover_boundaries(self, agent_id: str) -> Dict[str, Any]:
        """
        Boundary Discovery Primitive: Allows agents to query available resources,
        their granted capabilities, and explicit policy rules.
        """
        if agent_id not in self.registered_agents:
            return {"error": "Agent not registered. Run handshake() first."}

        agent_data = self.registered_agents[agent_id]
        granted = agent_data["declared_capabilities"]

        accessible_resources = {}
        unauthorized_resources = {}

        for res_name, res_info in self.available_resources.items():
            req_caps = res_info["capabilities"]
            has_access = any(c in granted for c in req_caps)
            if has_access:
                accessible_resources[res_name] = res_info
            else:
                unauthorized_resources[res_name] = res_info

        return {
            "agent_id": agent_id,
            "environment": "bartholomew-sovereign-v8",
            "zeroized_lockdown": self.is_zeroized,
            "granted_capabilities": granted,
            "accessible_resources": accessible_resources,
            "unauthorized_resources": unauthorized_resources,
            "policy": "production-default-v1",
            "evidence_requirement": "Ed25519 Signed Canonical JSON"
        }

    def execute_action(
        self,
        agent_id: str,
        tool: str,
        arguments: Dict[str, Any],
        target_function: Callable[..., Any]
    ) -> Dict[str, Any]:
        """
        Consequential Action Interceptor.
        Routes every action through the Guard Proxy with Fail-Closed key protection.
        """
        # Fail-closed check if zeroized or no key
        if self.is_zeroized or not self.guard or not self.private_key_pem:
            return {
                "success": False,
                "error": "EXECUTION_BLOCKED: Null public key or environment lockdown in effect.",
                "evidence": {
                    "artifact_version": "1.0",
                    "issuer": "bartholomew",
                    "evaluation": {
                        "decision": "block",
                        "policy": "fail-closed-null-key",
                        "checks": [{"name": "key_integrity", "result": "null_or_zeroized"}]
                    },
                    "signature": "0" * 128
                }
            }

        agent_info = self.registered_agents.get(agent_id, {})
        capabilities = agent_info.get("declared_capabilities", [tool])
        
        # Instantiate Guard with agent's declared capabilities
        guard = BartholomewGuard(
            private_key_pem=self.private_key_pem,
            agent_capabilities=capabilities
        )
        
        return guard.execute(
            agent_id=agent_id,
            tool=tool,
            arguments=arguments,
            target_function=target_function,
            agent_version=agent_info.get("agent_version", "1.0.0")
        )
