"""
Bartholomew Multi-Agent Consensus & Hierarchical Approval Gate (BTP v2.5.0)
===========================================================================
Supports tri-state governance decisions: `ALLOW`, `DENY`, and `REQUIRE_APPROVAL`.

Use Cases:
  1. High-Value Financial Operations (e.g. spend > $1,000 USD).
  2. Irreversible Infrastructure Changes (e.g. database schema migrations, IAM policy edits).
  3. M-of-N Multi-Agent Quorum: Requires M distinct agent/auditor signatures before release.
  4. Human-in-the-Loop (HITL) Gateways: Pauses execution until authorized operator approves.
"""

import time
import hashlib
from typing import Dict, Any, List, Optional, Set, Tuple
from src.trust_protocol import BartholomewTrustAuthority, rfc8785_canonicalize

class PendingApprovalRequest:
    """Represents an elevated-risk tool execution paused for approval."""
    def __init__(
        self,
        request_id: str,
        originating_agent_id: str,
        action_type: str,
        payload: Dict[str, Any],
        required_signatures: int = 2,
        authorized_approver_pubkeys: Optional[Set[str]] = None,
        ttl_seconds: float = 600.0
    ):
        self.request_id = request_id
        self.originating_agent_id = originating_agent_id
        self.action_type = action_type
        self.payload = payload
        self.required_signatures = required_signatures
        self.authorized_approver_pubkeys = authorized_approver_pubkeys or set()
        self.ttl_seconds = ttl_seconds
        self.created_at = time.time()
        self.signatures: Dict[str, str] = {}  # pubkey -> signature
        self.status = "PENDING"  # "PENDING", "APPROVED", "REJECTED", "EXPIRED"
        self.final_attestation: Optional[Dict[str, Any]] = None

    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl_seconds

    def to_canonical_dict(self) -> Dict[str, Any]:
        return {
            "protocol": "BTP/2.5.0",
            "request_id": self.request_id,
            "originating_agent_id": self.originating_agent_id,
            "action_type": self.action_type,
            "payload_hash": hashlib.sha256(rfc8785_canonicalize(self.payload)).hexdigest(),
            "created_at": self.created_at,
            "required_signatures": self.required_signatures
        }


class QuorumApprovalGate:
    """
    Manages M-of-N threshold quorum verification and approval workflows.
    """
    def __init__(self, authority: Optional[BartholomewTrustAuthority] = None, high_risk_spend_threshold_usd: float = 1000.0):
        self.authority = authority or BartholomewTrustAuthority()
        self.high_risk_spend_threshold_usd = high_risk_spend_threshold_usd
        self.pending_requests: Dict[str, PendingApprovalRequest] = {}

    def assess_risk(self, action_type: str, payload: Dict[str, Any]) -> str:
        """
        Determines whether an action can execute immediately or requires consensus approval.
        Returns: 'ALLOW' | 'REQUIRE_APPROVAL' | 'DENY'
        """
        # 1. Catastrophic destruction is unconditionally DENIED
        cmd = str(payload.get("command", "") or payload.get("query", "")).lower()
        if "rm -rf /" in cmd or "drop database" in cmd:
            return "DENY"

        # 2. Financial spend check
        amount = float(payload.get("amount_usd", payload.get("amount", 0.0)))
        if amount >= self.high_risk_spend_threshold_usd:
            return "REQUIRE_APPROVAL"

        # 3. High-risk operational actions
        if action_type in ("DATABASE_MIGRATE", "IAM_POLICY_MUTATE", "REVOKE_CREDENTIALS", "CLUSTER_FAILOVER"):
            return "REQUIRE_APPROVAL"

        return "ALLOW"

    def create_approval_request(
        self,
        agent_id: str,
        action_type: str,
        payload: Dict[str, Any],
        required_signatures: int = 2,
        authorized_approver_pubkeys: Optional[Set[str]] = None
    ) -> PendingApprovalRequest:
        """Enqueues an action into the cryptographic approval queue."""
        req_hash = hashlib.sha256(f"{agent_id}:{action_type}:{time.time()}".encode()).hexdigest()[:16]
        req_id = f"btp-req-{req_hash}"

        req = PendingApprovalRequest(
            request_id=req_id,
            originating_agent_id=agent_id,
            action_type=action_type,
            payload=payload,
            required_signatures=required_signatures,
            authorized_approver_pubkeys=authorized_approver_pubkeys
        )
        self.pending_requests[req_id] = req
        return req

    def submit_approval_signature(
        self,
        request_id: str,
        approver_pubkey: str,
        signature_hex: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Submits an Ed25519 co-signature to satisfy the M-of-N threshold.
        Returns (is_approved, status_message, final_attestation_if_ready).
        """
        req = self.pending_requests.get(request_id)
        if not req:
            return False, f"Request '{request_id}' not found.", None

        if req.is_expired():
            req.status = "EXPIRED"
            return False, f"Request '{request_id}' has expired.", None

        if req.status != "PENDING":
            return False, f"Request is already in status '{req.status}'.", None

        if req.authorized_approver_pubkeys and approver_pubkey not in req.authorized_approver_pubkeys:
            return False, f"Approver '{approver_pubkey[:12]}...' is not authorized for this request.", None

        req.signatures[approver_pubkey] = signature_hex

        # Check if threshold reached
        if len(req.signatures) >= req.required_signatures:
            req.status = "APPROVED"
            
            # Mint final release receipt
            receipt = self.authority.evaluate_intent(
                agent_id=req.originating_agent_id,
                action_type=req.action_type,
                payload=req.payload
            )
            receipt["quorum_attestation"] = {
                "request_id": req.request_id,
                "approved_at": time.time(),
                "signatures_collected": len(req.signatures),
                "approvers": list(req.signatures.keys())
            }
            req.final_attestation = receipt
            return True, f"Quorum reached ({len(req.signatures)}/{req.required_signatures} signatures). Action RELEASED.", receipt

        return False, f"Signature recorded ({len(req.signatures)}/{req.required_signatures} required). Pending remaining approvals.", None
