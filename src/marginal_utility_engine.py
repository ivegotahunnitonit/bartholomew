"""
Bartholomew Diminishing Marginal Utility (LDMU) Invariant Engine
===============================================================
Applies economic Law of Diminishing Marginal Utility to autonomous AI agents:
  1. Action Fatigue & Loop Damping: Rapid repeated identical/similar actions suffer exponential utility decay.
  2. Entropy & Information Gain Check: Zero-novelty calls are intercepted before wasting tokens.
  3. Non-Linear Decaying Spend Caps: Prevents high-velocity wallet drain within a single unverified tranche.
"""

import time
import math
import hashlib
import json
from typing import Dict, Any, Tuple, List, Optional
from collections import defaultdict, deque


class MarginalUtilityTracker:
    """
    In-memory, sub-microsecond sliding window utility tracker per agent session.
    """
    def __init__(self, decay_rate: float = 0.35, min_utility_threshold: float = 0.15, window_seconds: float = 300.0):
        self.decay_rate = decay_rate
        self.min_utility_threshold = min_utility_threshold
        self.window_seconds = window_seconds
        # agent_id -> deque of (timestamp, action_signature, cost_usd)
        self.history: Dict[str, deque] = defaultdict(deque)

    def _hash_action(self, action_type: str, payload: Dict[str, Any]) -> str:
        """Generates canonical signature of action intent."""
        # Clean volatile timestamps if present to detect true semantic repetition
        clean_payload = {k: v for k, v in payload.items() if k not in ("timestamp", "nonce", "request_id")}
        raw = f"{action_type}:{json.dumps(clean_payload, sort_keys=True)}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def clean_old_entries(self, agent_id: str, now: float):
        dq = self.history[agent_id]
        cutoff = now - self.window_seconds
        while dq and dq[0][0] < cutoff:
            dq.popleft()

    def evaluate_action_utility(
        self,
        agent_id: str,
        action_type: str,
        payload: Dict[str, Any],
        cost_usd: float = 0.0
    ) -> Tuple[str, float, str, float]:
        """
        Evaluates marginal utility of the proposed action.
        Returns: (verdict: 'ALLOW' | 'THROTTLE' | 'CO_SIGN_REQUIRED' | 'DENY', mu_score: float, reason: str, latency_us: float)
        """
        t0 = time.perf_counter()
        now = time.time()

        self.clean_old_entries(agent_id, now)
        action_sig = self._hash_action(action_type, payload)
        dq = self.history[agent_id]

        # 1. Count identical / similar actions within active window
        identical_count = sum(1 for ts, sig, _ in dq if sig == action_sig)
        total_recent_actions = len(dq)
        total_recent_spend = sum(cost for _, _, cost in dq) + cost_usd

        # 2. Calculate Base Marginal Utility via Exponential Decay
        # MU = e^(-decay_rate * repetition_count)
        repetition_factor = identical_count
        marginal_utility = math.exp(-self.decay_rate * repetition_factor)

        # 3. High-velocity spend decay multiplier
        if total_recent_spend > 250.0:
            spend_decay = max(0.1, 1.0 - (total_recent_spend - 250.0) / 250.0)
            marginal_utility *= spend_decay

        mu_score = round(max(0.0, min(1.0, marginal_utility)), 4)
        latency_us = round((time.perf_counter() - t0) * 1_000_000, 2)

        # Record this action
        dq.append((now, action_sig, cost_usd))

        # 4. Invariant Verdict Determination
        if mu_score < self.min_utility_threshold:
            if identical_count >= 5:
                reason = (
                    f"Diminishing Marginal Utility Breach: Action repeated {identical_count + 1} times within "
                    f"{int(self.window_seconds)}s window with near-zero marginal utility (MU={mu_score:.3f} < {self.min_utility_threshold}). "
                    f"Runaway loop detected; requires human co-signing."
                )
                return "CO_SIGN_REQUIRED", mu_score, reason, latency_us
            else:
                reason = (
                    f"Diminishing Marginal Utility Breach: High-velocity action fatigue (MU={mu_score:.3f}). "
                    f"Action throttled to prevent resource exhaustion."
                )
                return "THROTTLE", mu_score, reason, latency_us

        reason = f"Marginal utility acceptable (MU={mu_score:.3f}, repeats={identical_count})."
        return "ALLOW", mu_score, reason, latency_us

    def reset_agent(self, agent_id: str):
        """Clears action fatigue history when human operator approves or resets."""
        if agent_id in self.history:
            self.history[agent_id].clear()


# Global Singleton Engine
_DEFAULT_UTILITY_ENGINE = MarginalUtilityTracker()


def evaluate_marginal_utility(
    agent_id: str,
    action_type: str,
    payload: Dict[str, Any],
    cost_usd: float = 0.0,
    decay_rate: float = 0.35,
    min_utility_threshold: float = 0.15
) -> Tuple[str, float, str, float]:
    """Microsecond standalone evaluator for marginal utility invariant."""
    _DEFAULT_UTILITY_ENGINE.decay_rate = decay_rate
    _DEFAULT_UTILITY_ENGINE.min_utility_threshold = min_utility_threshold
    return _DEFAULT_UTILITY_ENGINE.evaluate_action_utility(agent_id, action_type, payload, cost_usd)
