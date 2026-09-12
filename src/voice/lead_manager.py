"""
Bartholomew Trust Protocol (BTP v5.4) — Lead & Campaign Queue Manager
Loads, manages, and tracks outbound cold call prospects, status transitions,
and auditable call outcome transcripts.
"""

import json
import csv
import time
import uuid
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any


class LeadStatus(str, Enum):
    PENDING = "PENDING"
    CALLING = "CALLING"
    CONNECTED = "CONNECTED"
    QUALIFIED = "QUALIFIED"                           # Agreed to demo / requested docs
    DISPATCHED_EXECUTIVE_DOSSIER = "DISPATCHED_EXECUTIVE_DOSSIER"  # Executive dossier dispatched
    PROPOSAL_SENT = "PROPOSAL_SENT"                   # Pricing / checkout link / dossier sent
    CLOSED_WON = "CLOSED_WON"                         # Closed deal / active paid account
    NOT_INTERESTED = "NOT_INTERESTED"
    VOICEMAIL = "VOICEMAIL"
    FAILED = "FAILED"
    DO_NOT_CALL = "DO_NOT_CALL"


@dataclass
class Lead:
    """Individual prospect contact record."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = "Lead"
    company: str = "AI Labs"
    phone: str = "+15551234567"
    email: Optional[str] = None
    role: str = "AI Engineer"
    status: LeadStatus = LeadStatus.PENDING
    notes: str = ""
    call_duration_seconds: int = 0
    transcript: List[Dict[str, str]] = field(default_factory=list)
    deal_value_usd: float = 0.0
    checkout_url: Optional[str] = None
    invoice_id: Optional[str] = None
    last_called_at: Optional[float] = None
    created_at: float = field(default_factory=time.time)
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = dict(self.extra)
        base = asdict(self)
        base.pop("extra", None)
        base["status"] = self.status.value
        d.update(base)
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Lead":
        status_val = data.get("status", LeadStatus.PENDING.value)
        try:
            status = LeadStatus(status_val)
        except ValueError:
            status = LeadStatus.PENDING

        known_keys = {
            "id", "name", "company", "phone", "email", "role", "status",
            "notes", "call_duration_seconds", "transcript", "deal_value_usd",
            "contract_value_usd", "checkout_url", "invoice_id", "last_called_at", "created_at"
        }
        extra_fields = {k: v for k, v in data.items() if k not in known_keys}

        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", "Lead"),
            company=data.get("company", "AI Labs"),
            phone=data.get("phone", ""),
            email=data.get("email"),
            role=data.get("role", "AI Engineer"),
            status=status,
            notes=data.get("notes", ""),
            call_duration_seconds=data.get("call_duration_seconds", 0),
            transcript=data.get("transcript", []),
            deal_value_usd=float(data.get("deal_value_usd", data.get("contract_value_usd", 0.0))),
            checkout_url=data.get("checkout_url"),
            invoice_id=data.get("invoice_id"),
            last_called_at=data.get("last_called_at"),
            created_at=data.get("created_at", time.time()),
            extra=extra_fields
        )


class LeadManager:
    """Manages the outbound dialing queue and outcome persistent storage."""

    def __init__(self, storage_file: Optional[Path] = None):
        self.storage_file = storage_file or (Path(__file__).resolve().parent.parent.parent / "leads_queue.json")
        self.leads: List[Lead] = []
        self._load_or_seed()

    def _load_or_seed(self) -> None:
        """Load leads from persistent disk or seed sample AI startup leads."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.leads = [Lead.from_dict(item) for item in data]
                    return
            except Exception:
                pass

        # Seed realistic target engineering leads for instant demonstration
        self.leads = [
            Lead(
                name="Marcus Vance",
                company="Synthetix AI",
                phone="+14155552671",
                role="Head of AI Platform",
                notes="Deploys multi-agent CrewAI clusters with code execution tools.",
            ),
            Lead(
                name="Elena Rostova",
                company="VectorFlow Dynamics",
                phone="+12065558914",
                role="Lead ML Infrastructure Engineer",
                notes="Scaling LangGraph pipelines for enterprise financial clients.",
            ),
            Lead(
                name="Devin Chen",
                company="HyperScale Agents",
                phone="+16505553190",
                role="CTO",
                notes="Building autonomous database query agents with Postgres & BigQuery.",
            ),
            Lead(
                name="Sarah Jenkins",
                company="Cognitive Corp",
                phone="+13125557732",
                role="VP of Engineering",
                notes="Needs SOC 2 Type II audit compliance for LLM tool executions.",
            ),
        ]
        self.save()

    def save(self) -> None:
        """Persist current leads queue to JSON."""
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump([lead.to_dict() for lead in self.leads], f, indent=2)

    def get_all(self) -> List[Lead]:
        return self.leads

    def get_by_id(self, lead_id: str) -> Optional[Lead]:
        for l in self.leads:
            if l.id == lead_id:
                return l
        return None

    def get_next_pending(self) -> Optional[Lead]:
        """Fetch the next pending lead from queue."""
        for lead in self.leads:
            if lead.status == LeadStatus.PENDING:
                return lead
        return None

    def update_lead_outcome(
        self,
        lead_id: str,
        status: LeadStatus,
        duration: int,
        transcript: List[Dict[str, str]],
        notes: Optional[str] = None
    ) -> Optional[Lead]:
        """Update contact record after a call completes."""
        lead = self.get_by_id(lead_id)
        if not lead:
            return None
        
        lead.status = status
        lead.call_duration_seconds = duration
        lead.transcript = transcript
        lead.last_called_at = time.time()
        if notes:
            lead.notes = f"{lead.notes} | {notes}".strip(" |")
        
        self.save()
        return lead

    def add_lead(self, name: str, company: str, phone: str, email: Optional[str] = None, role: str = "Engineer") -> Lead:
        lead = Lead(name=name, company=company, phone=phone, email=email, role=role)
        self.leads.append(lead)
        self.save()
        return lead

    def import_from_csv(self, csv_filepath: Path) -> int:
        """Import leads from an uploaded CSV file."""
        added = 0
        with open(csv_filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("name") or row.get("Name") or "Lead"
                company = row.get("company") or row.get("Company") or "Tech Inc"
                phone = row.get("phone") or row.get("Phone") or ""
                email = row.get("email") or row.get("Email")
                role = row.get("role") or row.get("Role") or "AI Engineer"
                if phone:
                    self.add_lead(name=name, company=company, phone=phone, email=email, role=role)
                    added += 1
        return added

    def qualify_lead(self, lead_id: str, notes: str = "", email: Optional[str] = None) -> Optional[Lead]:
        """Mark a lead as qualified and ready for proposal/closing."""
        lead = self.get_by_id(lead_id)
        if not lead:
            return None
        lead.status = LeadStatus.QUALIFIED
        if email:
            lead.email = email
        if notes:
            lead.notes = f"{lead.notes} | {notes}".strip(" |")
        self.save()
        return lead

    def send_proposal(self, lead_id: str, tier: str = "pro", notes: str = "") -> Optional[Dict[str, Any]]:
        """Transition lead to PROPOSAL_SENT with direct Stripe checkout URL."""
        lead = self.get_by_id(lead_id)
        if not lead:
            return None
        tier_normalized = tier.lower()
        if "ent" in tier_normalized:
            deal_val = 199.0
            checkout = "https://buy.stripe.com/fZu14ng3PgyC9ao2z69R601"
            tier_name = "Enterprise Fleet ($199/mo)"
        else:
            deal_val = 49.0
            checkout = "https://buy.stripe.com/fZu28rbNz5TYcmAddK9R600"
            tier_name = "Pro Startup ($49/mo)"

        lead.status = LeadStatus.PROPOSAL_SENT
        lead.deal_value_usd = deal_val
        lead.checkout_url = checkout
        lead.invoice_id = f"INV-BTP-{uuid.uuid4().hex[:8].upper()}"
        if notes:
            lead.notes = f"{lead.notes} | Proposal: {tier_name} ({notes})".strip(" |")
        self.save()
        return {
            "lead_id": lead.id,
            "company": lead.company,
            "tier": tier_name,
            "deal_value_usd": deal_val,
            "checkout_url": checkout,
            "invoice_id": lead.invoice_id
        }

    def close_deal(
        self,
        lead_id: str,
        tier: str = "pro",
        deal_value_usd: Optional[float] = None,
        notes: str = ""
    ) -> Optional[Lead]:
        """Mark lead as CLOSED_WON with recorded deal value."""
        lead = self.get_by_id(lead_id)
        if not lead:
            return None
        tier_normalized = tier.lower()
        if deal_value_usd is not None:
            val = deal_value_usd
        elif "ent" in tier_normalized:
            val = 199.0
        else:
            val = 49.0

        lead.status = LeadStatus.CLOSED_WON
        lead.deal_value_usd = val
        if notes:
            lead.notes = f"{lead.notes} | Closed Won: {notes}".strip(" |")
        self.save()
        return lead
