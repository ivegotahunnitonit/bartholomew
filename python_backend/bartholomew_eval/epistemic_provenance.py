import math
import time
import uuid
from typing import Dict, Any, List, Optional

class EpistemicProvenanceNode:
    """
    7-Dimensional Epistemic Node in the Dynamic Epistemic Reality Graph (DERG).
    Replaces single float confidence scores with multi-dimensional provenance vectors:
    - Status: OBSERVED, CLAIMED, INFERRED, VERIFIED, DISPUTED, DISPROVEN
    - Vector: (evidence_strength, source_reliability, recency, independence, contradiction, confirmations)
    """

    DECAY_RATES = {
        "invariant": 0.0,          # Never decays (math, physics, core logic)
        "code_ast": 0.001,         # Slow decay
        "api_spec": 0.05,          # Moderate decay
        "runtime_config": 0.5,     # Fast decay
        "market_pricing": 2.0      # Very fast decay
    }

    def __init__(
        self,
        claim: str,
        status: str = "CLAIMED",
        domain: str = "code_ast",
        evidence_strength: float = 0.5,
        source_reliability: float = 0.5,
        independence: float = 0.0,
        contradiction_score: float = 0.0,
        evidence_refs: Optional[List[str]] = None,
        source: str = "agent-unknown"
    ):
        self.node_id = f"derg-{uuid.uuid4().hex[:8]}"
        self.claim = claim
        self.status = status  # OBSERVED, CLAIMED, INFERRED, VERIFIED, DISPUTED, DISPROVEN
        self.domain = domain
        self.evidence_strength = max(0.0, min(1.0, evidence_strength))
        self.source_reliability = max(0.0, min(1.0, source_reliability))
        self.independence = max(0.0, min(1.0, independence))
        self.contradiction_score = max(0.0, min(1.0, contradiction_score))
        self.evidence_refs = evidence_refs or []
        self.source = source
        self.confirmations = 1
        self.created_at = time.time()
        self.last_verified_at = time.time()

    def compute_decayed_recency(self, current_time: Optional[float] = None) -> float:
        """
        Calculates belief decay score based on domain decay rate lambda.
        S(t) = S0 * e^(-lambda * (t - t0))
        """
        now = current_time or time.time()
        elapsed_days = max(0.0, (now - self.created_at) / 86400.0)
        decay_rate = self.DECAY_RATES.get(self.domain, 0.05)
        return math.exp(-decay_rate * elapsed_days)

    def to_provenance_vector(self) -> Dict[str, Any]:
        """Returns 7-dimensional provenance representation."""
        recency = self.compute_decayed_recency()
        return {
            "node_id": self.node_id,
            "claim": self.claim,
            "epistemic_status": self.status,
            "domain": self.domain,
            "provenance_vector": {
                "evidence_strength": round(self.evidence_strength, 3),
                "source_reliability": round(self.source_reliability, 3),
                "recency": round(recency, 3),
                "independence": round(self.independence, 3),
                "contradiction": round(self.contradiction_score, 3),
                "independent_confirmations": self.confirmations
            },
            "evidence_refs": self.evidence_refs,
            "source": self.source
        }

class ContradictionEngine:
    """
    Detects evidence conflict between incoming assertions and existing DERG nodes.
    Prevents silent overwrites by flagging disputed claims and creating investigation branches.
    """

    def __init__(self):
        self.nodes: Dict[str, EpistemicProvenanceNode] = {}
        self.disputed_conflicts: List[Dict[str, Any]] = []

    def ingest_claim(
        self,
        claim: str,
        status: str,
        domain: str,
        evidence_strength: float,
        source_reliability: float,
        evidence_refs: Optional[List[str]] = None,
        source: str = "agent-4592"
    ) -> Dict[str, Any]:
        """
        Ingests a new claim into the Epistemic Reality Graph.
        Checks for contradiction with existing beliefs before adding.
        """
        # 1. Contradiction Detection Check
        conflicting_node = self._find_contradiction(claim)
        
        if conflicting_node:
            # 🔴 CONTRADICTION DETECTED! Do NOT overwrite existing claim.
            conflict_event = {
                "conflict_id": f"conflict-{uuid.uuid4().hex[:8]}",
                "existing_node_id": conflicting_node.node_id,
                "existing_claim": conflicting_node.claim,
                "incoming_claim": claim,
                "incoming_source": source,
                "status": "UNRESOLVED_CONTRADICTION",
                "detected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            conflicting_node.status = "DISPUTED"
            conflicting_node.contradiction_score = min(1.0, conflicting_node.contradiction_score + 0.5)
            self.disputed_conflicts.append(conflict_event)

            new_node = EpistemicProvenanceNode(
                claim=claim,
                status="DISPUTED",
                domain=domain,
                evidence_strength=evidence_strength,
                source_reliability=source_reliability,
                contradiction_score=0.8,
                evidence_refs=evidence_refs,
                source=source
            )
            self.nodes[new_node.node_id] = new_node

            return {
                "action": "CONTRADICTION_FLAGGED",
                "conflict": conflict_event,
                "node": new_node.to_provenance_vector()
            }

        # 2. Duplicate / Confirmation Check
        existing_duplicate = self._find_matching_claim(claim)
        if existing_duplicate:
            existing_duplicate.confirmations += 1
            existing_duplicate.independence = min(1.0, existing_duplicate.independence + 0.2)
            existing_duplicate.evidence_strength = min(1.0, existing_duplicate.evidence_strength + 0.1)
            if existing_duplicate.status == "CLAIMED":
                existing_duplicate.status = "VERIFIED"
            return {
                "action": "CLAIM_CONFIRMED",
                "node": existing_duplicate.to_provenance_vector()
            }

        # 3. New Independent Node
        node = EpistemicProvenanceNode(
            claim=claim,
            status=status,
            domain=domain,
            evidence_strength=evidence_strength,
            source_reliability=source_reliability,
            evidence_refs=evidence_refs,
            source=source
        )
        self.nodes[node.node_id] = node
        return {
            "action": "NODE_CREATED",
            "node": node.to_provenance_vector()
        }

    def _find_contradiction(self, claim: str) -> Optional[EpistemicProvenanceNode]:
        """Detects negation / contradiction between claims using semantic overlap."""
        claim_words = set(claim.lower().split())
        negations = {"not", "never", "no", "cannot", "fails", "failed", "unsupported", "invalid"}
        
        has_negation = bool(claim_words & negations)
        core_words = claim_words - negations
        
        for node in self.nodes.values():
            node_words = set(node.claim.lower().split())
            node_has_negation = bool(node_words & negations)
            node_core_words = node_words - negations
            
            # If one has negation and the other does not, but they share significant core topic overlap (> 50%)
            if has_negation != node_has_negation:
                overlap = len(core_words & node_core_words)
                min_len = min(len(core_words), len(node_core_words))
                if min_len > 0 and (overlap / min_len) >= 0.5:
                    return node
        return None

    def _find_matching_claim(self, claim: str) -> Optional[EpistemicProvenanceNode]:
        claim_lower = claim.lower().strip()
        for node in self.nodes.values():
            if node.claim.lower().strip() == claim_lower:
                return node
        return None
