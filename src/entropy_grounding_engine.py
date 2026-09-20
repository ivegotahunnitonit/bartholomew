"""
Bartholomew Information Theory, Entropy & Epistemic Grounding Engine
===================================================================
Applies mathematical information theory, Shannon entropy bounds, and
provenance grounding (Retrieval-Augmented Attestation) to bound the
inherent probabilistic errors of LLM text generation.

Core Mathematical Principles:
  1. Shannon Entropy Bound: H(X) = -sum(P(x) * log2(P(x)))
     Measures token distribution dispersion. High entropy indicates unconstrained
     probabilistic hallucination or stochastic drift.
  2. Shannon Noisy-Channel Theorem:
     Treats LLM output as a noisy communication channel. Bartholomew acts as the
     deterministic error-correcting channel filter.
  3. Provenance Grounding Invariant:
     Ensures that all mutation targets (IDs, schemas, files, recipient addresses)
     have a verifiable predecessor in prior read receipts or trusted context.
"""

import math
import hashlib
from typing import Dict, Any, List, Set, Optional, Tuple


def calculate_shannon_entropy(text: str) -> float:
    """
    Calculates the Shannon Entropy (in bits per byte/character) of a payload string.
    High entropy strings (> 4.8 bits/char on structured JSON) often indicate
    obfuscated payloads, randomized tokens, or unbounded generation drift.
    """
    if not text:
        return 0.0

    length = len(text)
    freq: Dict[str, int] = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1

    entropy = 0.0
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)

    return round(entropy, 4)


class EpistemicProvenanceGrounder:
    """
    Validates that an agent's proposed action is grounded in verified prior context.
    Prevents hallucinated resource mutation by enforcing read-before-write provenance.
    """
    def __init__(self):
        # Set of verified entity IDs and hashes observed in read operations
        self.grounded_entity_pool: Set[str] = set()

    def ingest_grounded_context(self, verified_read_receipt: Dict[str, Any]):
        """
        Registers verified IDs, files, or database keys from an approved read operation.
        """
        payload = verified_read_receipt.get("payload", {})
        
        # Extract entity references
        for key in ("entity_id", "user_id", "file_path", "account_id", "table_name", "target_id"):
            if key in payload and payload[key]:
                self.grounded_entity_pool.add(str(payload[key]).strip())

        # If data records returned, extract IDs
        records = payload.get("records") or payload.get("data")
        if isinstance(records, list):
            for item in records:
                if isinstance(item, dict):
                    for k in ("id", "user_id", "account_id", "file_path"):
                        if k in item and item[k]:
                            self.grounded_entity_pool.add(str(item[k]).strip())

    def verify_grounding(self, proposed_mutation: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Verifies that mutation targets exist within the grounded entity pool.
        Returns: (is_grounded, failure_reason)
        """
        payload = proposed_mutation.get("payload", {})
        
        # Check target references
        target_keys = ["target_id", "user_id", "account_id", "entity_id", "recipient_id"]
        for key in target_keys:
            if key in payload and payload[key]:
                target_val = str(payload[key]).strip()
                if target_val not in self.grounded_entity_pool:
                    return False, (
                        f"Epistemic Grounding Invariant Breach: Target '{key}={target_val}' "
                        f"has no verifiable predecessor in the grounded context pool. "
                        f"Potential probabilistic hallucination."
                    )

        return True, None


class EntropyGovernor:
    """
    Monitors payload entropy and character distribution to detect stochastic drift.
    """
    def __init__(self, max_entropy_bits: float = 5.2):
        self.max_entropy_bits = max_entropy_bits

    def evaluate_entropy(self, payload: Dict[str, Any]) -> Tuple[bool, float, Optional[str]]:
        """
        Evaluates the Shannon entropy of the payload representation.
        Returns: (is_compliant, entropy_score, reason)
        """
        import json
        raw_repr = json.dumps(payload, sort_keys=True)
        entropy = calculate_shannon_entropy(raw_repr)

        if entropy > self.max_entropy_bits:
            return False, entropy, (
                f"Information Theory Invariant Breach: Payload Shannon entropy ({entropy} bits/char) "
                f"exceeds maximum allowable bound ({self.max_entropy_bits} bits/char). "
                f"High-dispersion probabilistic generation detected."
            )

        return True, entropy, None
