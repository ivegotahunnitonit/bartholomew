"""
bartholomew_eval.memory_curator
===============================
In-Band & Out-of-Band Memory Curation and Stale Memory Resolver for Bartholomew v5.0.
Provides real-time memory sanitization and asynchronous background memory decay.
"""

from __future__ import annotations

import math
import re
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .sovereign_memory import SovereignLocalMemory


# Compiled regex patterns for in-band secret redaction (matches embedded secrets mid-string)
_SECRET_REDACTION_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    ("OPENAI_PROJECT_KEY",   re.compile(r"sk-proj-[a-zA-Z0-9_\-]{20,}")),
    ("GENERIC_API_SECRET",   re.compile(r"\bsk-[a-zA-Z0-9]{20,}")),
    ("GITHUB_PAT",           re.compile(r"ghp_[a-zA-Z0-9]{20,}")),
    ("GITHUB_FINE_PAT",      re.compile(r"github_pat_[a-zA-Z0-9_\-]{20,}")),
    ("AWS_ACCESS_KEY",       re.compile(r"AKIA[0-9A-Z]{16}")),
    ("STRIPE_LIVE_KEY",      re.compile(r"sk_live_[0-9a-zA-Z]{24,}")),
    ("BARTHOLOMEW_ENT_KEY",  re.compile(r"age_live_[a-zA-Z0-9_\-]{16,}")),
    ("OPERATOR_SEC_KEY",     re.compile(r"acn_op_sec_[a-zA-Z0-9_\-]{16,}")),
    ("JWT_BEARER",           re.compile(r"eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+")),
    ("BEARER_TOKEN",         re.compile(r"(?i)bearer\s+[a-zA-Z0-9_\-\.\+/=]{12,}")),
]

# Injection marker phrases to block from memory ingestion
_INJECTION_PHRASES = [
    "ignore previous instructions",
    "system prompt leak",
    "dan mode",
    "you are now in",
    "disregard all prior",
]


class InBandOutBandCurator:
    """
    In-Band and Out-of-Band Memory Curator & Stale Memory Resolver.
    """

    def __init__(self, memory_engine: Optional[SovereignLocalMemory] = None) -> None:
        self.memory_engine = memory_engine or SovereignLocalMemory()
        self.decay_lambda = 0.05  # Decay constant for temporal staleness

    def in_band_curate_step(self, step_content: str, step_type: str = "thought") -> Tuple[bool, str, Dict[str, Any]]:
        """
        In-Band Memory Gatekeeper: Evaluates live step content before storing in memory.
        Filters out secret keys, prompt injection payloads, and noise using comprehensive regex.
        """
        # 1. Reject prompt injection candidates
        content_lower = step_content.lower()
        for phrase in _INJECTION_PHRASES:
            if phrase in content_lower:
                return False, step_content, {
                    "action": "REJECTED_INBAND",
                    "reason": f"Prompt Injection Pattern Detected: '{phrase}'",
                    "sanitized": False,
                }

        # 2. Regex-based credential redaction (catches embedded secrets like `token=sk-proj-...`)
        clean_content = step_content
        scrubbed_types: List[str] = []
        for label, pattern in _SECRET_REDACTION_PATTERNS:
            if pattern.search(clean_content):
                clean_content = pattern.sub(f"[REDACTED_MEMORY_{label}]", clean_content)
                scrubbed_types.append(label)

        was_sanitized = bool(scrubbed_types)
        return True, clean_content, {
            "action": "CURATED_INBAND",
            "sanitized": was_sanitized,
            "redacted_types": scrubbed_types,
        }

    def out_of_band_prune_stale_memories(self, max_age_days: float = 30.0) -> Dict[str, Any]:
        """
        Out-of-Band Memory Resolver: Asynchronously evaluates memories for temporal staleness
        and prunes or flags outdated facts using exponential decay S(t) = S_0 * e^(-lambda * t).
        """
        conn = sqlite3.connect(self.memory_engine.db_path)
        try:
            cursor = conn.cursor()
            now = time.time()

            cursor.execute("SELECT id, memory_key, created_timestamp, confidence_score FROM sovereign_memories WHERE is_stale = 0")
            rows = cursor.fetchall()

            pruned_count = 0
            decayed_count = 0

            for row_id, key, created_ts, confidence in rows:
                age_days = (now - created_ts) / 86400.0
                decayed_confidence = confidence * math.exp(-self.decay_lambda * age_days)

                if age_days > max_age_days or decayed_confidence < 0.2:
                    cursor.execute(
                        "UPDATE sovereign_memories SET is_stale = 1, confidence_score = ? WHERE id = ?",
                        (decayed_confidence, row_id)
                    )
                    pruned_count += 1
                else:
                    cursor.execute(
                        "UPDATE sovereign_memories SET confidence_score = ? WHERE id = ?",
                        (decayed_confidence, row_id)
                    )
                    decayed_count += 1

            conn.commit()
        finally:
            conn.close()

        return {
            "out_of_band_curation_success": True,
            "pruned_stale_memories_count": pruned_count,
            "active_decayed_memories_count": decayed_count,
            "decay_lambda": self.decay_lambda,
            "timestamp": now,
        }

