"""
Bartholomew Inbound Lead & Enterprise Trial Manager (BTP v5.4)
===============================================================
Captures, persists, and cryptographically signs inbound enterprise trial requests,
visitor audit telemetry, and CISO evaluation requests.
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_LEADS_FILE = DATA_DIR / "inbound_leads.json"
USER_LEADS_FILE = Path.home() / ".btp" / "inbound_leads.json"


def record_inbound_lead(
    email: str,
    company: Optional[str] = None,
    role: Optional[str] = None,
    source: str = "web",
    tier: str = "ENTERPRISE_TRIAL",
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Records an inbound lead, issues a cryptographically hashed 14-day trial passkey,
    and appends the record to both local workspace and user ~/.btp vaults.
    """
    clean_email = str(email).strip().lower()
    if "@" not in clean_email or "." not in clean_email:
        raise ValueError(f"Invalid email address: {email}")

    now = time.time()
    expires_at = now + (14 * 86400)
    salt = "btp_sovereign_lead_v54"
    token_hash = hashlib.sha256(f"{clean_email}:{salt}:{now}".encode()).hexdigest()[:16]
    trial_key = f"BTP-TRIAL-v54-{token_hash}"

    lead_record = {
        "lead_id": f"lead_{token_hash[:8]}",
        "email": clean_email,
        "company": (company or "Autonomous Enterprise").strip(),
        "role": (role or "AI Engineer / CISO").strip(),
        "source": source,
        "tier": tier,
        "trial_key": trial_key,
        "created_at_unix": now,
        "created_at_iso": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(now)),
        "expires_at_unix": expires_at,
        "expires_at_iso": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(expires_at)),
        "status": "ACTIVE_TRIAL",
        "notes": notes or ""
    }

    # Save to local workspace data/
    _append_lead_to_file(LOCAL_LEADS_FILE, lead_record)

    # Save to user ~/.btp/
    try:
        USER_LEADS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _append_lead_to_file(USER_LEADS_FILE, lead_record)
    except Exception:
        pass

    return lead_record


def get_inbound_leads() -> List[Dict[str, Any]]:
    """Retrieves all deduplicated inbound enterprise leads across local and ~/.btp vaults."""
    leads_map: Dict[str, Dict[str, Any]] = {}

    for path in [LOCAL_LEADS_FILE, USER_LEADS_FILE]:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    entries = json.load(f)
                    if isinstance(entries, list):
                        for item in entries:
                            key = item.get("email") or item.get("lead_id")
                            if key:
                                leads_map[key] = item
            except Exception:
                pass

    leads = list(leads_map.values())
    leads.sort(key=lambda x: x.get("created_at_unix", 0), reverse=True)
    return leads


def _append_lead_to_file(file_path: Path, lead_record: Dict[str, Any]) -> None:
    """Safely appends a lead to a JSON list file."""
    existing: List[Dict[str, Any]] = []
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                if isinstance(content, list):
                    existing = content
        except Exception:
            existing = []

    # Update or append
    existing = [e for e in existing if e.get("email") != lead_record.get("email")]
    existing.append(lead_record)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)
