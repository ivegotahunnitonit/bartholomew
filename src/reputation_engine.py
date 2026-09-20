"""
Bartholomew Agent Reputation & Evidence Engine (BTP v5.4.14)
=============================================================
Generates machine-readable, cryptographically verifiable reputation reports
from audit trail logs, execution receipts, and settlement history.

Allows autonomous agents to evaluate counterparties programmatically:
  - verified_transactions: total successfully completed & audited transactions
  - dispute_free_ratio: 0.0 to 1.0 ratio of execution without contract breaches
  - settled_value_usd: total financial volume settled safely through BTP
  - average_latency_us: average execution gate overhead
  - trust_tier: SOVEREIGN | HIGH_TRUST | MEDIUM_TRUST | UNTRUSTED
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import time
from typing import Dict, Any, List, Optional, Tuple

from cryptography.hazmat.primitives.asymmetric import ed25519


@dataclasses.dataclass
class ReputationReport:
    """Cryptographically verifiable reputation evidence payload."""
    agent_id: str
    verified_transactions: int
    failed_transactions: int
    disputed_transactions: int
    settled_value_usd: float
    average_latency_us: float
    trust_score: float  # 0.0 to 1.0
    trust_tier: str
    generated_at: float
    evidence_root_hash: str
    signature: Optional[str] = None

    def canonical_bytes(self) -> bytes:
        payload = {
            "agent_id": self.agent_id,
            "verified_transactions": self.verified_transactions,
            "failed_transactions": self.failed_transactions,
            "disputed_transactions": self.disputed_transactions,
            "settled_value_usd": round(self.settled_value_usd, 4),
            "average_latency_us": round(self.average_latency_us, 2),
            "trust_score": round(self.trust_score, 4),
            "trust_tier": self.trust_tier,
            "generated_at": int(self.generated_at),
            "evidence_root_hash": self.evidence_root_hash
        }
        return json.dumps(payload, sort_keys=True).encode("utf-8")

    def sign(self, private_key: ed25519.Ed25519PrivateKey) -> str:
        sig_bytes = private_key.sign(self.canonical_bytes())
        self.signature = sig_bytes.hex()
        return self.signature

    def verify_signature(self, pubkey_hex: str) -> bool:
        if not self.signature:
            return False
        try:
            pubkey_bytes = bytes.fromhex(pubkey_hex)
            pubkey = ed25519.Ed25519PublicKey.from_public_bytes(pubkey_bytes)
            pubkey.verify(bytes.fromhex(self.signature), self.canonical_bytes())
            return True
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "verified_transactions": self.verified_transactions,
            "failed_transactions": self.failed_transactions,
            "disputed_transactions": self.disputed_transactions,
            "settled_value_usd": self.settled_value_usd,
            "average_latency_us": self.average_latency_us,
            "trust_score": self.trust_score,
            "trust_tier": self.trust_tier,
            "generated_at": self.generated_at,
            "evidence_root_hash": self.evidence_root_hash,
            "signature": self.signature
        }


class AgentReputationEngine:
    """
    Ingests execution logs and calculates machine-readable trust scores.
    """

    def __init__(self, private_key: Optional[ed25519.Ed25519PrivateKey] = None):
        self.private_key = private_key or ed25519.Ed25519PrivateKey.generate()
        self.public_key_hex = self.private_key.public_key().public_bytes_raw().hex()

    def generate_report(
        self,
        agent_id: str,
        receipts: List[Dict[str, Any]],
        disputes: Optional[List[Dict[str, Any]]] = None
    ) -> ReputationReport:
        dispute_list = disputes or []
        verified_tx = 0
        failed_tx = 0
        total_value_usd = 0.0
        total_latency = 0.0

        for r in receipts:
            verdict = r.get("verdict") or r.get("status")
            if verdict in ["ALLOW", "APPROVED", "SUCCESS"]:
                verified_tx += 1
            else:
                failed_tx += 1

            total_value_usd += float(r.get("amount_usd") or r.get("settled_usd") or 0.0)
            total_latency += float(r.get("latency_us") or r.get("latency_ms", 0) * 1000.0)

        disputed_tx = len(dispute_list)
        total_attempts = verified_tx + failed_tx + disputed_tx

        if total_attempts == 0:
            trust_score = 1.0
            avg_latency = 0.0
        else:
            dispute_penalty = (disputed_tx * 0.3) + (failed_tx * 0.05)
            trust_score = max(0.0, min(1.0, 1.0 - (dispute_penalty / total_attempts)))
            avg_latency = total_latency / len(receipts) if receipts else 0.0

        if trust_score >= 0.95 and verified_tx >= 10:
            tier = "SOVEREIGN"
        elif trust_score >= 0.8:
            tier = "HIGH_TRUST"
        elif trust_score >= 0.5:
            tier = "MEDIUM_TRUST"
        else:
            tier = "UNTRUSTED"

        # Evidence Merkle hash
        evidence_str = json.dumps([r.get("receipt_sha256") or r.get("receipt_hash") for r in receipts], sort_keys=True)
        evidence_root = hashlib.sha256(evidence_str.encode()).hexdigest()

        report = ReputationReport(
            agent_id=agent_id,
            verified_transactions=verified_tx,
            failed_transactions=failed_tx,
            disputed_transactions=disputed_tx,
            settled_value_usd=total_value_usd,
            average_latency_us=avg_latency,
            trust_score=trust_score,
            trust_tier=tier,
            generated_at=time.time(),
            evidence_root_hash=evidence_root
        )
        report.sign(self.private_key)
        return report
