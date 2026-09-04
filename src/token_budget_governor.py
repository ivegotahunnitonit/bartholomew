"""
Bartholomew Token Budget & Rate Limiting Governor (BTP v2.5.0)
==============================================================
Protects against Denial-of-Wallet (DoW) attacks, infinite recursive loops,
and runaway external API billing.

Metrics Governed:
  1. Requests Per Minute (RPM) sliding window.
  2. Cumulative Token Consumption per agent session (input + output).
  3. Wall-clock Tool Execution Latency caps.
"""

import time
from collections import deque
from typing import Dict, Any, Tuple, Optional

class TokenBudgetGovernor:
    """
    In-memory rate, latency, and token consumption rate-limiter.
    """
    def __init__(
        self,
        max_rpm: int = 60,
        max_tokens_per_hour: int = 250_000,
        max_action_duration_seconds: float = 30.0
    ):
        self.max_rpm = max_rpm
        self.max_tokens_per_hour = max_tokens_per_hour
        self.max_action_duration_seconds = max_action_duration_seconds

        # session_id -> deque of timestamps
        self.request_timestamps: Dict[str, deque] = {}
        # session_id -> cumulative token count
        self.token_usage: Dict[str, int] = {}
        # session_id -> reset timestamp
        self.token_window_starts: Dict[str, float] = {}

    def check_request(
        self,
        session_id: str,
        estimated_tokens: int = 0
    ) -> Tuple[bool, str]:
        """
        Evaluates RPM and token consumption before dispatching an LLM or tool call.
        Returns (is_allowed, reason).
        """
        now = time.time()

        # 1. Sliding Window RPM Check
        if session_id not in self.request_timestamps:
            self.request_timestamps[session_id] = deque()

        window = self.request_timestamps[session_id]
        # Evict timestamps older than 60 seconds
        while window and (now - window[0]) > 60.0:
            window.popleft()

        if len(window) >= self.max_rpm:
            return False, f"BTP-RATE-001: Request frequency cap exceeded ({len(window)}/{self.max_rpm} RPM). Throttled."

        # 2. Token Budget Check
        if session_id not in self.token_window_starts or (now - self.token_window_starts[session_id]) > 3600.0:
            self.token_window_starts[session_id] = now
            self.token_usage[session_id] = 0

        current_tokens = self.token_usage[session_id]
        if (current_tokens + estimated_tokens) > self.max_tokens_per_hour:
            return False, f"BTP-DOW-002: Denial-of-Wallet cap reached ({current_tokens + estimated_tokens}/{self.max_tokens_per_hour} tokens/hour). Execution halted."

        # Record usage
        window.append(now)
        self.token_usage[session_id] += estimated_tokens
        return True, "Within token budget and rate bounds"
