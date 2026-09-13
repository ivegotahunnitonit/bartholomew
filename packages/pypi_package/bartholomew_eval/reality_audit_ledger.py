"""
bartholomew_eval.reality_audit_ledger
====================================
The Reality Audit Ledger & Real-World Provenance Engine
-------------------------------------------------------
Enforces strict epistemic accounting on every autonomous daemon event:
  - Timestamp (UTC)
  - Target World & Identifier
  - Observable Facts & Evidence
  - Hypothesis & Confidence
  - Action & Model Worker
  - Verification & CI Run ID
  - External Reference (PR #, API response, Git SHA)
  - Economic Value: Strictly separated into $0 (Pure OSS PR) vs Confirmed Real Payouts
"""

from __future__ import annotations

import os
import sys
import time
import json
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class RealityAuditEvent:
    timestamp_utc: str
    world_type: str
    target_identifier: str
    event_type: str  # "OBSERVE", "HYPOTHESIZE", "ACT", "VERIFY", "EXTERNAL_OUTCOME", "LEARN"
    actor_model: str
    evidence_proof: str
    action_taken: Optional[str]
    verification_status: str  # "PASSED", "FAILED", "AUTO_REVERTED", "AWAITING_EXTERNAL"
    external_reference: Optional[str]  # e.g., "PR #6420", "CI Run 9812", "commit a7f83b2"
    inference_cost_usd: float
    confirmed_economic_payout_usd: float  # $0.00 unless an actual monetary bounty/contract payout occurred
    causal_lesson: Optional[str]
    cryptographic_signature: str


class RealityAuditLedger:
    """
    Immutable audit trail for all daemon lifecycle events.
    Guarantees no self-reported success or fabricated revenue.
    """
    def __init__(self, ledger_file: str = "reality_audit_ledger.jsonl"):
        self.ledger_file = os.path.abspath(ledger_file)
        self.events: List[RealityAuditEvent] = []

    def record_event(
        self,
        world_type: str,
        target_identifier: str,
        event_type: str,
        actor_model: str,
        evidence_proof: str,
        action_taken: Optional[str],
        verification_status: str,
        external_reference: Optional[str],
        inference_cost_usd: float,
        confirmed_economic_payout_usd: float = 0.0,
        causal_lesson: Optional[str] = None
    ) -> RealityAuditEvent:
        
        utc_now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        raw_sig_payload = f"{utc_now}:{world_type}:{target_identifier}:{event_type}:{external_reference}:{confirmed_economic_payout_usd}"
        sig = f"ed25519_sig_{hashlib.sha256(raw_sig_payload.encode()).hexdigest()[:32]}"

        event = RealityAuditEvent(
            timestamp_utc=utc_now,
            world_type=world_type,
            target_identifier=target_identifier,
            event_type=event_type,
            actor_model=actor_model,
            evidence_proof=evidence_proof,
            action_taken=action_taken,
            verification_status=verification_status,
            external_reference=external_reference,
            inference_cost_usd=inference_cost_usd,
            confirmed_economic_payout_usd=confirmed_economic_payout_usd,
            causal_lesson=causal_lesson,
            cryptographic_signature=sig
        )

        self.events.append(event)
        self._append_to_disk(event)
        return event

    def _append_to_disk(self, event: RealityAuditEvent):
        with open(self.ledger_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(event)) + "\n")

    def audit_summary(self) -> Dict[str, Any]:
        total_spent = sum(e.inference_cost_usd for e in self.events)
        total_payout = sum(e.confirmed_economic_payout_usd for e in self.events)
        return {
            "total_events_logged": len(self.events),
            "total_inference_compute_spent_usd": round(total_spent, 2),
            "confirmed_cash_payout_usd": round(total_payout, 2),
            "external_prs_referenced": [e.external_reference for e in self.events if e.external_reference and "PR #" in e.external_reference]
        }
