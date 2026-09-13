import time
import uuid
import hashlib
from typing import Dict, Any, List, Optional

class EpistemicExperienceStore:
    """
    Bartholomew Epistemic Experience Store (Dynamic Epistemic Reality Graph - DERG).
    Replaces raw chat transcripts with signed, verifiable conclusions and failure evidence.
    """

    def __init__(self):
        self.assertions: List[Dict[str, Any]] = []
        self.unresolved_frontiers: List[Dict[str, Any]] = []

    def record_experience(
        self,
        agent_id: str,
        claim: str,
        outcome: str,  # "SUCCESS", "FAILED_ATTEMPT", "DISCOVERY"
        evidence_artifact_id: str,
        signature: str,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Records a proven assertion or failure finding into the Epistemic Reality Graph.
        """
        assertion_id = f"epistemic-{uuid.uuid4().hex[:8]}"
        entry = {
            "assertion_id": assertion_id,
            "agent_id": agent_id,
            "claim": claim,
            "outcome": outcome,
            "evidence_artifact_id": evidence_artifact_id,
            "signature": signature,
            "tags": sorted(tags or []),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self.assertions.append(entry)
        return entry

    def record_unresolved_frontier(
        self,
        subsystem: str,
        hypothesis: str,
        entropy_score: float,
        required_capabilities: List[str]
    ) -> Dict[str, Any]:
        """
        Registers an active high-entropy unresolved problem for agents to investigate.
        """
        frontier_id = f"frontier-{uuid.uuid4().hex[:8]}"
        entry = {
            "frontier_id": frontier_id,
            "subsystem": subsystem,
            "hypothesis": hypothesis,
            "entropy_score": entropy_score,
            "required_capabilities": sorted(required_capabilities),
            "status": "UNRESOLVED",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self.unresolved_frontiers.append(entry)
        return entry

    def get_epistemic_diff(self, since_timestamp: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns the Epistemic State Diff for an agent booting up.
        """
        if not since_timestamp:
            return self.assertions
        return [a for a in self.assertions if a["timestamp"] > since_timestamp]

    def get_highest_entropy_frontier(self) -> Optional[Dict[str, Any]]:
        """
        Surfaces the highest entropy problem node for self-directed investigation.
        """
        unresolved = [f for f in self.unresolved_frontiers if f["status"] == "UNRESOLVED"]
        if not unresolved:
            return None
        return max(unresolved, key=lambda x: x["entropy_score"])
