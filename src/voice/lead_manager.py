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
    QUALIFIED = "QUALIFIED"           # Agreed to demo / requested docs
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
    last_called_at: Optional[float] = None
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Lead":
        status_val = data.get("status", LeadStatus.PENDING.value)
        try:
            status = LeadStatus(status_val)
        except ValueError:
            status = LeadStatus.PENDING
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
            last_called_at=data.get("last_called_at"),
            created_at=data.get("created_at", time.time())
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
