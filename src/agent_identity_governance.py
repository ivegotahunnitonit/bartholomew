"""
Bartholomew Non-Human Identity (NHI) & Agent Governance (BTP v2.5.0)
===================================================================
Treats autonomous AI agents as managed non-human identities with:
  1. Sovereign Ed25519 Identity Keys bound per agent process.
  2. Role-Based Capability Access Control (RBAC) scopes:
     - `ANALYST`: Read-only data queries, search, telemetry.
     - `DEVELOPER`: Workspace mutations, code refactors, git commits.
     - `OPERATOR`: Production database modifications, service reloads.
     - `ADMIN`: Invariant policy reloads, security credential rotations.
  3. Automated Cryptographic Revocation:
     - Detects anomalous behavior or policy invariant breaches.
     - Automatically revokes the identity token upon 2 violations.
     - Issues a signed Revocation Certificate broadcast to downstream verifiers.
"""

import time
import hashlib
from typing import Dict, Any, List, Optional, Set, Tuple
from src.trust_protocol import BartholomewTrustAuthority, rfc8785_canonicalize

class AgentIdentity:
    """Represents an authenticated Non-Human Identity (NHI)."""
    def __init__(
        self,
        agent_id: str,
        role: str,
        capabilities: Set[str],
        public_key_hex: str,
        max_spend_per_hour_usd: float = 100.0
    ):
        self.agent_id = agent_id
        self.role = role.upper()
        self.capabilities = capabilities
        self.public_key_hex = public_key_hex
        self.max_spend_per_hour_usd = max_spend_per_hour_usd
        self.hourly_spend_usd = 0.0
        self.violation_count = 0
        self.is_revoked = False
        self.revoked_at: Optional[float] = None
        self.revocation_reason: Optional[str] = None
        self.created_at = time.time()


class AgentIdentityGovernanceRegistry:
    """
    Central governance directory validating agent capabilities and enforcing
    cryptographic least-privilege boundaries.
    """
    ROLE_DEFAULT_CAPABILITIES = {
        "ANALYST": {"tools:search", "data:read", "telemetry:emit"},
        "DEVELOPER": {"tools:search", "data:read", "code:mutate", "git:commit", "test:run"},
        "OPERATOR": {"tools:search", "data:read", "data:write", "service:restart", "code:mutate"},
        "ADMIN": {"*"}  # Unrestricted
    }

    def __init__(self, authority: Optional[BartholomewTrustAuthority] = None):
        self.authority = authority or BartholomewTrustAuthority()
        self.identities: Dict[str, AgentIdentity] = {}
        self.revocation_log: List[Dict[str, Any]] = []

    def register_identity(
        self,
        agent_id: str,
        role: str = "DEVELOPER",
        custom_capabilities: Optional[Set[str]] = None,
        max_spend_hourly_usd: float = 500.0
    ) -> AgentIdentity:
        """Provisions a new sovereign Non-Human Identity."""
        caps = custom_capabilities or self.ROLE_DEFAULT_CAPABILITIES.get(role.upper(), {"data:read"})
        # Generate identity keypair
        sub_authority = BartholomewTrustAuthority()
        identity = AgentIdentity(
            agent_id=agent_id,
            role=role,
            capabilities=set(caps),
            public_key_hex=sub_authority.public_key_hex,
            max_spend_per_hour_usd=max_spend_hourly_usd
        )
        self.identities[agent_id] = identity
        return identity

    def verify_action_authorization(
        self,
        agent_id: str,
        required_capability: str,
        amount_usd: float = 0.0
    ) -> Tuple[bool, str]:
        """
        Enforces RBAC capability scopes and hourly spend bounds.
        Returns (is_authorized, reason).
        """
        identity = self.identities.get(agent_id)
        if not identity:
            return False, f"BTP-NHI-001: Unregistered agent identity '{agent_id}'. Unauthorized caller."

        if identity.is_revoked:
            return False, f"BTP-NHI-002: Identity '{agent_id}' is REVOKED (Reason: {identity.revocation_reason})."

        # Check spend cap
        if (identity.hourly_spend_usd + amount_usd) > identity.max_spend_per_hour_usd:
            return False, f"BTP-NHI-003: Hourly spend cap breached (${identity.hourly_spend_usd + amount_usd:.2f} > ${identity.max_spend_per_hour_usd:.2f})."

        # Check capability
        if "*" in identity.capabilities or required_capability in identity.capabilities:
            identity.hourly_spend_usd += amount_usd
            return True, "Authorized"

        # Action not permitted for role
        return False, f"BTP-NHI-004: Insufficient privileges. Role '{identity.role}' lacks capability '{required_capability}'."

    def record_violation(self, agent_id: str, violation_reason: str) -> Optional[Dict[str, Any]]:
        """
        Increments violation counter. Upon 2 breaches, issues an authenticated Revocation Certificate.
        """
        identity = self.identities.get(agent_id)
        if not identity:
            return None

        identity.violation_count += 1

        if identity.violation_count >= 2 and not identity.is_revoked:
            identity.is_revoked = True
            identity.revoked_at = time.time()
            identity.revocation_reason = violation_reason

            revocation_certificate = {
                "protocol": "BTP/2.5.0",
                "type": "IDENTITY_REVOCATION_CERTIFICATE",
                "agent_id": agent_id,
                "public_key_hex": identity.public_key_hex,
                "revoked_at": identity.revoked_at,
                "reason": violation_reason,
                "violations_accumulated": identity.violation_count
            }

            # Sign revocation certificate with Trust Authority
            canon = rfc8785_canonicalize(revocation_certificate)
            signature = self.authority.private_key.sign(canon).hex()
            revocation_certificate["authority_signature"] = signature
            revocation_certificate["authority_public_key"] = self.authority.public_key_hex

            self.revocation_log.append(revocation_certificate)
            return revocation_certificate

        return None
