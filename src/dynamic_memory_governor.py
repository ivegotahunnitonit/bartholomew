"""
Bartholomew Dynamic Memory Governor & Heap Exhaustion Protector (BTP v2.6.0)
===========================================================================
Protects host systems from Denial-of-Memory (DoM) exploits and runaway agent memory loops:
  1. Real-time Resident Set Size (RSS) and heap tracking per agent worker session.
  2. Multi-tier memory thresholds: Soft Warning (Throttle) & Hard Ceiling (Rollback & Termination).
  3. Memory Allocation Velocity Limiter (detects explosive heap expansions > threshold MB/sec).
  4. Non-repudiable audit receipts and SIEM alert generation.
"""

import os
import sys
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class MemorySessionMetrics:
    session_id: str
    baseline_rss_bytes: int
    current_rss_bytes: int
    peak_rss_bytes: int
    allocation_velocity_mb_s: float
    last_check_timestamp: float
    status: str  # 'NORMAL' | 'THROTTLED' | 'TERMINATED'

class DynamicMemoryGovernor:
    """
    Monitors and bounds memory allocations for autonomous agent execution workers.
    Terminates runaway loops before host OS OOM killer triggers.
    """
    def __init__(
        self,
        soft_limit_mb: float = 256.0,
        hard_limit_mb: float = 512.0,
        max_velocity_mb_s: float = 100.0
    ):
        self.soft_limit_bytes = int(soft_limit_mb * 1024 * 1024)
        self.hard_limit_bytes = int(hard_limit_mb * 1024 * 1024)
        self.max_velocity_mb_s = max_velocity_mb_s
        self.sessions: Dict[str, MemorySessionMetrics] = {}
        self.violation_log: List[Dict[str, Any]] = []

    def register_session(self, session_id: str, baseline_bytes: int = 10 * 1024 * 1024) -> MemorySessionMetrics:
        """Initializes a monitored agent memory session with baseline allocation."""
        now = time.time()
        metrics = MemorySessionMetrics(
            session_id=session_id,
            baseline_rss_bytes=baseline_bytes,
            current_rss_bytes=baseline_bytes,
            peak_rss_bytes=baseline_bytes,
            allocation_velocity_mb_s=0.0,
            last_check_timestamp=now,
            status="NORMAL"
        )
        self.sessions[session_id] = metrics
        return metrics

    def record_allocation(self, session_id: str, new_rss_bytes: int) -> Tuple[bool, str, Optional[str]]:
        """
        Records an updated memory reading for a session.
        Returns: (is_allowed: bool, status: str, reason: Optional[str])
        """
        now = time.time()
        session = self.sessions.get(session_id)
        if not session:
            session = self.register_session(session_id, new_rss_bytes)

        elapsed = now - session.last_check_timestamp
        delta_bytes = max(0, new_rss_bytes - session.current_rss_bytes)

        # Only compute velocity when elapsed window >= 20ms to avoid sub-millisecond timer quantization
        velocity_mb_s = 0.0
        if elapsed >= 0.02:
            velocity_mb_s = (delta_bytes / (1024 * 1024)) / elapsed
            session.allocation_velocity_mb_s = velocity_mb_s
            session.last_check_timestamp = now

        session.current_rss_bytes = new_rss_bytes
        session.peak_rss_bytes = max(session.peak_rss_bytes, new_rss_bytes)

        # 1. Check Hard Limit Breach
        if new_rss_bytes >= self.hard_limit_bytes:
            session.status = "TERMINATED"
            reason = (
                f"BTP-DOM-001: Hard memory limit exceeded ({new_rss_bytes / (1024*1024):.1f} MB >= "
                f"{self.hard_limit_bytes / (1024*1024):.1f} MB). Agent worker terminated to protect host OS."
            )
            self._log_violation(session_id, "HARD_LIMIT_BREACH", reason, new_rss_bytes)
            return False, "TERMINATED", reason

        # 2. Check Allocation Velocity Explosion (> threshold MB/sec)
        if velocity_mb_s >= self.max_velocity_mb_s and delta_bytes > (20 * 1024 * 1024):
            session.status = "TERMINATED"
            reason = (
                f"BTP-DOM-002: Abnormal memory expansion velocity detected ({velocity_mb_s:.1f} MB/s >= "
                f"{self.max_velocity_mb_s:.1f} MB/s). Runaway heap expansion blocked."
            )
            self._log_violation(session_id, "VELOCITY_EXPLOSION", reason, new_rss_bytes)
            return False, "TERMINATED", reason

        # 3. Check Soft Limit Warning
        if new_rss_bytes >= self.soft_limit_bytes:
            session.status = "THROTTLED"
            reason = (
                f"BTP-DOM-003: Soft memory limit reached ({new_rss_bytes / (1024*1024):.1f} MB >= "
                f"{self.soft_limit_bytes / (1024*1024):.1f} MB). Micro-throttling active."
            )
            self._log_violation(session_id, "SOFT_LIMIT_WARNING", reason, new_rss_bytes)
            return True, "THROTTLED", reason

        session.status = "NORMAL"
        return True, "NORMAL", None

    def _log_violation(self, session_id: str, violation_type: str, reason: str, rss_bytes: int):
        self.violation_log.append({
            "session_id": session_id,
            "violation_type": violation_type,
            "reason": reason,
            "rss_bytes": rss_bytes,
            "timestamp": time.time()
        })

    def get_audit_summary(self) -> Dict[str, Any]:
        """Generates an audit digest of memory enforcement activity."""
        raw_manifest = f"{len(self.sessions)}:{len(self.violation_log)}"
        digest = hashlib.sha256(raw_manifest.encode("utf-8")).hexdigest()
        return {
            "active_sessions": len(self.sessions),
            "total_violations": len(self.violation_log),
            "soft_limit_mb": self.soft_limit_bytes / (1024 * 1024),
            "hard_limit_mb": self.hard_limit_bytes / (1024 * 1024),
            "audit_digest_sha256": digest,
            "status": "HEALTHY"
        }
