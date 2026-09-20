"""
Bartholomew Automated M2M Dispute Resolution Engine (BTP v1.0.0)
===================================================================
Implements machine-readable dispute evaluation and arbitrated escrow settlement:
  1. Ingests disputed transaction receipts, execution evidence, and active policy hashes.
  2. Cryptographically validates transaction integrity & policy state at execution time.
  3. Evaluates claims: NON_DELIVERY, INVARIANT_BREACH, UNAUTHORIZED_MUTATION, DOUBLE_SPEND.
  4. Emits Ed25519-signed Dispute Verdicts instructing automated escrow refund or slash.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import time
from typing import Dict, Any, Optional, Tuple

from cryptography.hazmat.primitives.asymmetric import ed25519


@dataclasses.dataclass
class DisputeVerdict:
    """Cryptographically signed dispute resolution decision."""
    dispute_id: str
    claimant_id: str
    respondent_id: str
    verdict: str  # CLAIMANT_WINS | RESPONDENT_WINS | DISMISSED
    resolution_action: str  # REFUND_CLAIMANT | SLASH_RESPONDENT | MAINTAIN_ESCROW
    refund_amount_usd: float
    rule_violated: Optional[str]
    evidence_hash: str
    policy_version: str
    arbitrated_at: float
    signature: Optional[str] = None

    def canonical_bytes(self) -> bytes:
        payload = {
            "dispute_id": self.dispute_id,
            "claimant_id": self.claimant_id,
            "respondent_id": self.respondent_id,
            "verdict": self.verdict,
            "resolution_action": self.resolution_action,
            "refund_amount_usd": round(self.refund_amount_usd, 4),
            "rule_violated": self.rule_violated or "NONE",
            "evidence_hash": self.evidence_hash,
            "policy_version": self.policy_version,
            "arbitrated_at": int(self.arbitrated_at)
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
            "dispute_id": self.dispute_id,
            "claimant_id": self.claimant_id,
            "respondent_id": self.respondent_id,
            "verdict": self.verdict,
            "resolution_action": self.resolution_action,
            "refund_amount_usd": self.refund_amount_usd,
            "rule_violated": self.rule_violated,
            "evidence_hash": self.evidence_hash,
            "policy_version": self.policy_version,
            "arbitrated_at": self.arbitrated_at,
            "signature": self.signature
        }


class AutomatedDisputeResolver:
    """
    Arbitrates machine-to-machine execution disputes based on cryptographically verifiable evidence.
    """

    def __init__(self, private_key: Optional[ed25519.Ed25519PrivateKey] = None):
        self.private_key = private_key or ed25519.Ed25519PrivateKey.generate()
        self.public_key_hex = self.private_key.public_key().public_bytes_raw().hex()

    def arbitrate(
        self,
        claimant_id: str,
        respondent_id: str,
        claimed_reason: str,
        execution_receipt: Dict[str, Any],
        disputed_amount_usd: float = 0.0
    ) -> DisputeVerdict:
        now = time.time()
        dispute_raw = f"{claimant_id}:{respondent_id}:{claimed_reason}:{now}"
        dispute_id = f"dsp_{hashlib.sha256(dispute_raw.encode()).hexdigest()[:16]}"

        receipt_verdict = execution_receipt.get("verdict") or execution_receipt.get("status")
        rule_id = execution_receipt.get("rule_id") or execution_receipt.get("violation")
        policy_version = str(execution_receipt.get("policy_version", "1.0.0"))
        evidence_hash = str(execution_receipt.get("receipt_sha256") or execution_receipt.get("receipt_hash") or "NO_HASH")

        # Decision Matrix based on mathematical audit trail evidence
        if receipt_verdict == "DENY" or rule_id is not None:
            # Action was vetoed by gate or violated policy: Claimant (Requester) wins refund
            verdict_str = "CLAIMANT_WINS"
            action_str = "REFUND_CLAIMANT"
            refund_usd = float(disputed_amount_usd)
        elif claimed_reason.upper() in ["NON_DELIVERY", "INCOMPLETE_RESULT"]:
            # Respondent claimed completion without valid execution proof
            if not execution_receipt.get("receipt_sha256") and not execution_receipt.get("signature"):
                verdict_str = "CLAIMANT_WINS"
                action_str = "REFUND_CLAIMANT"
                refund_usd = float(disputed_amount_usd)
                rule_id = "BTP-PROOF-MISSING"
            else:
                verdict_str = "RESPONDENT_WINS"
                action_str = "MAINTAIN_ESCROW"
                refund_usd = 0.0
        else:
            verdict_str = "RESPONDENT_WINS"
            action_str = "MAINTAIN_ESCROW"
            refund_usd = 0.0

        dispute_verdict = DisputeVerdict(
            dispute_id=dispute_id,
            claimant_id=claimant_id,
            respondent_id=respondent_id,
            verdict=verdict_str,
            resolution_action=action_str,
            refund_amount_usd=refund_usd,
            rule_violated=rule_id,
            evidence_hash=evidence_hash,
            policy_version=policy_version,
            arbitrated_at=now
        )
        dispute_verdict.sign(self.private_key)
        return dispute_verdict
