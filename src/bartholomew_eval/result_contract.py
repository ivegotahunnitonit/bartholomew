"""
bartholomew_eval.result_contract
================================
Bartholomew Agent Result Contract (BARC)
----------------------------------------
The standardized, machine-readable execution & evidence interface for autonomous agents.

Principle: "Agents reason. Bartholomew verifies."
Bartholomew does not dictate strategy or evaluate model opinions;
it strictly observes, polices, and attests to what actually occurred at the execution boundary.
"""

from __future__ import annotations

import json
import time
import hashlib
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class ActionExecutionRecord:
    """A single atomic action evaluation and execution event at the boundary."""
    action_id: str
    requested_capability: str
    target_resource: str
    decision: str  # "ALLOW" or "DENY"
    executed: bool
    execution_result: Optional[Dict[str, Any]] = None
    denial_constraint: Optional[str] = None
    available_authorized_resources: List[str] = field(default_factory=list)
    evidence_artifact_id: Optional[str] = None
    ed25519_proof: Optional[str] = None


@dataclass
class AgentResultContract:
    """
    Standardized, model-agnostic contract returned to autonomous orchestrators
    capturing verified execution reality, boundary constraints, and cryptographic proofs.
    """
    task_id: str
    agent_did: str
    delegation_chain_id: Optional[str]
    timestamp_epoch: float
    actions: List[ActionExecutionRecord] = field(default_factory=list)
    
    @property
    def summary(self) -> Dict[str, int]:
        total = len(self.actions)
        allowed = sum(1 for a in self.actions if a.decision == "ALLOW")
        blocked = sum(1 for a in self.actions if a.decision == "DENY")
        failed = sum(1 for a in self.actions if a.executed and a.execution_result and a.execution_result.get("exit_code", 0) != 0)
        return {
            "total_actions": total,
            "executed_allowed": allowed,
            "blocked_unauthorized": blocked,
            "failed_execution": failed
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "agent_did": self.agent_did,
            "delegation_chain_id": self.delegation_chain_id,
            "timestamp_epoch": self.timestamp_epoch,
            "summary": self.summary,
            "actions": [asdict(a) for a in self.actions]
        }

    def to_canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
