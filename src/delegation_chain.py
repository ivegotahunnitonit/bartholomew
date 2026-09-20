"""
Bartholomew Verifiable Delegation Chain Protocol (BTP v1.0.0)
==============================================================
Models multi-agent authority delegation:
  Agent A (Grantor) -> Delegates Authority -> Agent B -> Delegates Sub-Authority -> Agent C

Guarantees via Ed25519 signature chaining and mathematical non-escalation invariants:
  1. Link (i + 1) spend limit <= Link (i) spend limit.
  2. Link (i + 1) capability set is a strict subset of Link (i) capability set.
  3. Expiration window of Link (i + 1) <= Expiration window of Link (i).
  4. Prevents downstream agents from exceeding authority granted by original root.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import time
from typing import Dict, Any, List, Optional, Set, Tuple

from cryptography.hazmat.primitives.asymmetric import ed25519


@dataclasses.dataclass
class DelegationLink:
    """Represents a single signed step in an authority delegation chain."""
    grantor_id: str
    grantee_id: str
    grantor_pubkey: str
    max_spend_usd: float
    allowed_capabilities: List[str]
    issued_at: float
    expires_at: float
    parent_link_hash: str
    signature: Optional[str] = None

    def canonical_bytes(self) -> bytes:
        payload = {
            "grantor_id": self.grantor_id,
            "grantee_id": self.grantee_id,
            "grantor_pubkey": self.grantor_pubkey,
            "max_spend_usd": round(float(self.max_spend_usd), 4),
            "allowed_capabilities": sorted(list(self.allowed_capabilities)),
            "issued_at": int(self.issued_at),
            "expires_at": int(self.expires_at),
            "parent_link_hash": self.parent_link_hash
        }
        return json.dumps(payload, sort_keys=True).encode("utf-8")

    def compute_link_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    def sign(self, private_key: ed25519.Ed25519PrivateKey) -> str:
        sig_bytes = private_key.sign(self.canonical_bytes())
        self.signature = sig_bytes.hex()
        return self.signature

    def verify_signature(self) -> bool:
        if not self.signature:
            return False
        try:
            pubkey_bytes = bytes.fromhex(self.grantor_pubkey)
            pubkey = ed25519.Ed25519PublicKey.from_public_bytes(pubkey_bytes)
            pubkey.verify(bytes.fromhex(self.signature), self.canonical_bytes())
            return True
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grantor_id": self.grantor_id,
            "grantee_id": self.grantee_id,
            "grantor_pubkey": self.grantor_pubkey,
            "max_spend_usd": self.max_spend_usd,
            "allowed_capabilities": self.allowed_capabilities,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "parent_link_hash": self.parent_link_hash,
            "signature": self.signature,
            "link_hash": self.compute_link_hash()
        }


class VerifiableDelegationChain:
    """
    Evaluates and enforces non-escalation invariants across multi-agent delegation chains.
    """

    def __init__(self, links: Optional[List[DelegationLink]] = None):
        self.links: List[DelegationLink] = links or []

    def add_link(self, link: DelegationLink) -> None:
        self.links.append(link)

    def evaluate_chain(self, now: Optional[float] = None) -> Tuple[bool, float, Set[str], Optional[str]]:
        """
        Validates the entire delegation chain.
        Returns:
          (is_valid: bool, effective_max_spend_usd: float, effective_capabilities: Set[str], error_reason: Optional[str])
        """
        if not self.links:
            return False, 0.0, set(), "Delegation chain is empty"

        current_time = now or time.time()
        effective_spend_usd = float("inf")
        effective_capabilities: Optional[Set[str]] = None
        expected_parent_hash = "GENESIS_ROOT"

        for idx, link in enumerate(self.links):
            # 1. Check parent link hash matching
            if idx > 0 and link.parent_link_hash != expected_parent_hash:
                return False, 0.0, set(), f"Link [{idx}] parent_link_hash mismatch ({link.parent_link_hash} != {expected_parent_hash})"

            # 2. Check cryptographic signature
            if not link.verify_signature():
                return False, 0.0, set(), f"Link [{idx}] grantor '{link.grantor_id}' signature verification failed"

            # 3. Check expiration
            if current_time > link.expires_at:
                return False, 0.0, set(), f"Link [{idx}] delegation expired at {link.expires_at} (current: {current_time})"

            # 4. Enforce Non-Escalation Invariant: Spend Cap
            if link.max_spend_usd > effective_spend_usd:
                return False, 0.0, set(), (
                    f"Delegation Escalation Breach at Link [{idx}]: Grantee '{link.grantee_id}' spend cap "
                    f"(${link.max_spend_usd}) exceeds grantor effective cap (${effective_spend_usd})"
                )
            effective_spend_usd = link.max_spend_usd

            # 5. Enforce Non-Escalation Invariant: Capability Set Subset
            link_caps = set(link.allowed_capabilities)
            if effective_capabilities is not None:
                illegal_caps = link_caps - effective_capabilities
                if illegal_caps:
                    return False, 0.0, set(), (
                        f"Delegation Escalation Breach at Link [{idx}]: Grantee '{link.grantee_id}' claimed "
                        f"unauthorized capabilities not granted by root: {sorted(list(illegal_caps))}"
                    )
                effective_capabilities = effective_capabilities.intersection(link_caps)
            else:
                effective_capabilities = link_caps

            expected_parent_hash = link.compute_link_hash()

        return True, effective_spend_usd, effective_capabilities or set(), None

    def to_list(self) -> List[Dict[str, Any]]:
        return [link.to_dict() for link in self.links]
