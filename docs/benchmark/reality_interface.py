"""
benchmark.reality_interface
============================
The 4-Pillar Reality Interface: OBSERVE -> CONSTRAIN -> REPORT -> PROVE

Core Philosophy: "Bartholomew is an execution and reality interface that lets 
autonomous systems reason from observed reality rather than agent claims."
"""

from __future__ import annotations

import json
import time
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class ObservedTelemetry:
    """Independent telemetry observed from OS / Network / Filesystem."""
    command: str
    target_resource: str
    executed_on_host: bool
    exit_code: Optional[int] = None
    files_modified: List[str] = field(default_factory=list)
    network_calls_attempted: int = 0
    process_spawned: Optional[str] = None
    stdout_digest: Optional[str] = None


@dataclass
class RealityObservationRecord:
    """
    Structured reality observation contract.
    Contains:
    1. Observe: What actually happened (telemetry).
    2. Constrain: What is allowed (available resources vs denied boundaries).
    3. Report: Machine-readable reality evaluation (VERIFIED, PARTIALLY_VERIFIED, CONTRADICTED, BOUNDARY_BLOCKED).
    4. Prove: Cryptographic signature for cross-trust domain verification.
    """
    event_id: str
    agent_did: str
    timestamp: float
    claimed_action: Optional[str]
    observed_telemetry: ObservedTelemetry
    boundary_decision: str  # "ALLOW" or "DENY"
    denial_constraint: Optional[str] = None
    available_authorized_resources: List[str] = field(default_factory=list)
    reality_status: str = "OBSERVED"  # "CLAIM_VERIFIED", "CLAIM_CONTRADICTED", "BOUNDARY_BLOCKED", "EXECUTION_VERIFIED"
    ed25519_proof: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
