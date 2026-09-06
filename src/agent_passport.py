"""
Bartholomew Milestone 3.1: Sovereign Digital Passports & Agent Peer Discovery (BTP v3.1.0)
========================================================================================
Implements:
1. Sovereign Digital Passports for non-human agent workers with cryptographically
   verifiable reputation vectors, capability boundaries, and self-reconciling circuit breakers.
2. Decentralized Peer Discovery registry for autonomous agent capability negotiation.
"""

import time
import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from cryptography.hazmat.primitives.asymmetric import ed25519

try:
    from src.rfc8785 import rfc8785_canonicalize
except ImportError:
    from rfc8785 import rfc8785_canonicalize


class SovereignAgentPassport:
    """
    Sovereign Digital Passport for an autonomous non-human worker agent.
    Cryptographically signed with Ed25519 and verifiable offline or across swarms.
    """

    DEFAULT_CAPABILITIES = {
        "READ_ONLY": {"data:read", "tools:search", "telemetry:emit"},
        "DEVELOPER": {"data:read", "code:mutate", "git:commit", "test:run", "tools:search"},
        "OPERATOR": {"data:read", "data:write", "service:restart", "code:mutate", "db:query"},
        "TREASURY": {"data:read", "l402:pay", "stripe:settle", "escrow:release"}
    }

    def __init__(
        self,
        agent_id: str,
        worker_model: str,
        owner_pubkey: str,
        granted_capabilities: Optional[List[str]] = None,
        bonded_warranty_balance_usd: float = 0.0,
        ttl_seconds: int = 86400,
        reputation_vector: Optional[Dict[str, Any]] = None,
        passport_id: Optional[str] = None,
        created_at: Optional[float] = None,
        expires_at: Optional[float] = None,
        circuit_breaker_tripped: bool = False,
        trip_reason: Optional[str] = None
    ):
        self.agent_id = agent_id
        self.worker_model = worker_model
        self.owner_pubkey = owner_pubkey
        self.granted_capabilities = granted_capabilities or ["data:read", "tools:search"]
        self.bonded_warranty_balance_usd = float(bonded_warranty_balance_usd)
        
        now = time.time()
        self.created_at = created_at or now
        self.expires_at = expires_at or (self.created_at + ttl_seconds)
        self.circuit_breaker_tripped = circuit_breaker_tripped
        self.trip_reason = trip_reason

        self.reputation_vector = reputation_vector or {
            "verified_actions": 0,
            "settled_value_usd": 0.0,
            "violation_count": 0,
            "trust_score": 1.0  # 0.0 to 1.0
        }

        if not passport_id:
            raw = f"{agent_id}:{worker_model}:{owner_pubkey}:{self.created_at}"
            digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
            self.passport_id = f"urn:agent:passport:{digest}"
        else:
            self.passport_id = passport_id

        self.signature_hex: Optional[str] = None

    def get_canonical_payload(self) -> Dict[str, Any]:
        """Returns the canonical passport dictionary prior to signing."""
        return {
            "protocol": "BTP/3.1.0/PASSPORT",
            "passport_id": self.passport_id,
            "agent_id": self.agent_id,
            "worker_model": self.worker_model,
            "owner_pubkey": self.owner_pubkey,
            "granted_capabilities": sorted(list(set(self.granted_capabilities))),
            "bonded_warranty_balance_usd": round(self.bonded_warranty_balance_usd, 2),
            "reputation_vector": {
                "verified_actions": self.reputation_vector.get("verified_actions", 0),
                "settled_value_usd": round(float(self.reputation_vector.get("settled_value_usd", 0.0)), 2),
                "violation_count": self.reputation_vector.get("violation_count", 0),
                "trust_score": round(float(self.reputation_vector.get("trust_score", 1.0)), 4)
            },
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "circuit_breaker_tripped": self.circuit_breaker_tripped,
            "trip_reason": self.trip_reason
        }

    def sign(self, private_key: ed25519.Ed25519PrivateKey) -> str:
        """Signs the canonical passport payload with Ed25519 private key."""
        payload = self.get_canonical_payload()
        canonical_bytes = rfc8785_canonicalize(payload)
        sig = private_key.sign(canonical_bytes)
        self.signature_hex = sig.hex()
        return self.signature_hex

    def verify_signature(self, owner_pubkey_hex: Optional[str] = None) -> Tuple[bool, str]:
        """Cryptographically verifies the passport signature."""
        if not self.signature_hex:
            return False, "Passport is unsigned"

        now = time.time()
        if now > self.expires_at:
            return False, "Passport expired"

        if self.circuit_breaker_tripped:
            return False, f"Passport circuit breaker tripped: {self.trip_reason}"

        target_pubkey = owner_pubkey_hex or self.owner_pubkey
        try:
            pubkey = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(target_pubkey))
            payload = self.get_canonical_payload()
            canonical_bytes = rfc8785_canonicalize(payload)
            sig_bytes = bytes.fromhex(self.signature_hex)
            pubkey.verify(sig_bytes, canonical_bytes)
            return True, "Valid cryptographic passport"
        except Exception as e:
            return False, f"Signature verification failed: {str(e)}"

    def has_capability(self, capability: str) -> bool:
        """Checks if passport grants specific capability scope."""
        if self.circuit_breaker_tripped:
            return False
        if "*" in self.granted_capabilities:
            return True
        return capability in self.granted_capabilities

    def trip_circuit_breaker(self, reason: str):
        """Immediately trips the circuit breaker, suspending passport validity."""
        self.circuit_breaker_tripped = True
        self.trip_reason = reason
        self.reputation_vector["violation_count"] += 1
        self.reputation_vector["trust_score"] = max(0.0, self.reputation_vector.get("trust_score", 1.0) - 0.25)

    def record_violation(self, reason: str):
        """Records a policy violation, reducing trust score."""
        self.reputation_vector["violation_count"] += 1
        self.reputation_vector["trust_score"] = max(0.0, self.reputation_vector.get("trust_score", 1.0) - 0.1)

    def record_successful_action(self, value_usd: float = 0.0):
        """Updates reputation vector after verified execution."""
        if self.circuit_breaker_tripped:
            return
        self.reputation_vector["verified_actions"] += 1
        self.reputation_vector["settled_value_usd"] += value_usd
        # Increase trust score asymptotically toward 1.0
        current_score = self.reputation_vector.get("trust_score", 1.0)
        self.reputation_vector["trust_score"] = min(1.0, current_score + 0.01)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes passport to dict with signature."""
        data = self.get_canonical_payload()
        data["signature"] = self.signature_hex
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SovereignAgentPassport":
        """Instantiates passport from serialized dict."""
        passport = cls(
            agent_id=data["agent_id"],
            worker_model=data["worker_model"],
            owner_pubkey=data["owner_pubkey"],
            granted_capabilities=data.get("granted_capabilities", []),
            bonded_warranty_balance_usd=data.get("bonded_warranty_balance_usd", 0.0),
            reputation_vector=data.get("reputation_vector"),
            passport_id=data.get("passport_id"),
            created_at=data.get("created_at"),
            expires_at=data.get("expires_at"),
            circuit_breaker_tripped=data.get("circuit_breaker_tripped", False),
            trip_reason=data.get("trip_reason")
        )
        passport.signature_hex = data.get("signature")
        return passport


class AgentPeerDiscoveryRegistry:
    """
    Decentralized Peer Discovery & Capability Registry for autonomous multi-agent swarms.
    """

    def __init__(self):
        self._passports: Dict[str, SovereignAgentPassport] = {}

    def register_passport(self, passport_data: Any) -> Tuple[bool, str, Dict[str, Any]]:
        """Registers and validates an agent passport in the discovery mesh."""
        try:
            if isinstance(passport_data, SovereignAgentPassport):
                passport = passport_data
            else:
                passport = SovereignAgentPassport.from_dict(passport_data)
            is_valid, msg = passport.verify_signature()
            if not is_valid:
                return False, f"Registration rejected: {msg}", {}

            self._passports[passport.passport_id] = passport
            return True, "Registered successfully in discovery mesh", passport.to_dict()
        except Exception as e:
            return False, f"Registration error: {str(e)}", {}

    def get_passport(self, passport_id: str) -> Optional[SovereignAgentPassport]:
        """Retrieves a registered passport by ID."""
        return self._passports.get(passport_id)

    def query_peers(
        self,
        capability: Optional[str] = None,
        min_reputation: Optional[float] = None,
        min_bond_usd: Optional[float] = None,
        model_family: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Discovers peer agent nodes matching specific capability and trust criteria.
        """
        results = []
        now = time.time()

        for passport in self._passports.values():
            if passport.expires_at < now or passport.circuit_breaker_tripped:
                continue

            if capability and not passport.has_capability(capability):
                continue

            if min_reputation is not None:
                score = passport.reputation_vector.get("trust_score", 0.0)
                if score < min_reputation:
                    continue

            if min_bond_usd is not None:
                if passport.bonded_warranty_balance_usd < min_bond_usd:
                    continue

            if model_family:
                if model_family.lower() not in passport.worker_model.lower():
                    continue

            results.append(passport.to_dict())

        return results

    def trip_circuit_breaker(self, passport_id: str, reason: str) -> Tuple[bool, str]:
        """Trips the circuit breaker for an agent across the discovery mesh."""
        passport = self._passports.get(passport_id)
        if not passport:
            return False, "Passport not found"
        passport.trip_circuit_breaker(reason)
        return True, f"Circuit breaker tripped for {passport_id}: {reason}"
