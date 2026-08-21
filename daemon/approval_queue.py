"""
Bartholomew Local Daemon: Human Co-Signing Approval Queue
Manages high-stakes agent actions requiring operator confirmation.
"""

import time
import uuid
from typing import Dict, Optional, Any, Callable


class PendingApproval:
    def __init__(self, request_id: str, agent_id: str, action_type: str, payload: Dict[str, Any], reason: str, timeout_seconds: float = 60.0, risk_level: str = "MEDIUM"):
        self.request_id = request_id
        self.agent_id = agent_id
        self.action_type = action_type
        self.payload = payload
        self.reason = reason
        self.risk_level = risk_level
        self.created_at = time.time()
        self.expires_at = self.created_at + timeout_seconds
        self.status: str = "PENDING"  # PENDING, APPROVED, REJECTED, EXPIRED
        self.decided_by: Optional[str] = None
        self.decided_at: Optional[float] = None

    def is_expired(self) -> bool:
        return time.time() > self.expires_at and self.status == "PENDING"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "agent_id": self.agent_id,
            "action_type": self.action_type,
            "payload": self.payload,
            "reason": self.reason,
            "risk_level": self.risk_level,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "time_remaining_sec": max(0.0, round(self.expires_at - time.time(), 1)),
            "status": "EXPIRED" if self.is_expired() else self.status,
            "decided_by": self.decided_by,
            "decided_at": self.decided_at
        }


class ApprovalQueue:
    def __init__(self):
        self._pending: Dict[str, PendingApproval] = {}
        self._listeners: list[Callable[[PendingApproval], None]] = []

    def add_listener(self, listener: Callable[[PendingApproval], None]):
        self._listeners.append(listener)

    def submit_for_approval(self, agent_id: str, action_type: str, payload: Dict[str, Any], reason: str, timeout_seconds: float = 60.0, risk_level: str = "MEDIUM") -> PendingApproval:
        req_id = f"req-{uuid.uuid4().hex[:8]}"
        approval = PendingApproval(req_id, agent_id, action_type, payload, reason, timeout_seconds, risk_level=risk_level)
        self._pending[req_id] = approval

        for listener in self._listeners:
            try:
                listener(approval)
            except Exception:
                pass

        return approval

    enqueue = submit_for_approval

    def get(self, request_id: str) -> Optional[PendingApproval]:
        return self._pending.get(request_id)

    def list_active(self) -> list[Dict[str, Any]]:
        now = time.time()
        active = []
        for req in self._pending.values():
            if req.status == "PENDING" and now <= req.expires_at:
                active.append(req.to_dict())
            elif req.status == "PENDING" and now > req.expires_at:
                req.status = "EXPIRED"
        return active

    def decide(self, request_id: str, approve: bool, operator_name: str = "Local Operator") -> Optional[PendingApproval]:
        req = self._pending.get(request_id)
        if not req:
            return None
        if req.is_expired():
            req.status = "EXPIRED"
            return req

        req.status = "APPROVED" if approve else "REJECTED"
        req.decided_by = operator_name
        req.decided_at = time.time()
        return req
