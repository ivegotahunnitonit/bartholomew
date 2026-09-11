"""
Wave 1 Founder & Startup Outreach Dispatch Engine
=================================================
Selects and executes dispatch for the top 5 high-intent startup founders
and engineering leads using the empathetic, non-jargon copy templates.
"""

import json
import time
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.voice.campaign_dispatcher import CampaignDispatcher
from src.voice.lead_manager import Lead

def execute_wave_1(dry_run: bool = False):
    print("=" * 76)
    print("  Bartholomew Wave 1 Founder Outreach Dispatch Engine")
    print("=" * 76)

    queue_path = BASE_DIR / "leads_queue.json"
    if not queue_path.exists():
        print("[!] leads_queue.json not found.")
        return

    with open(queue_path, "r", encoding="utf-8") as f:
        leads_data = json.load(f)

    # Top 5 high-intent targets: Devin Chen, Marcus Vance, Liam Gallagher, Elena Rostova, Sarah Jenkins
    target_ids = ["132f5d0f", "e78802b5", "46a509ad", "d29494a6"]
    
    # Also find Liam Gallagher
    for l in leads_data:
        if "liam" in (l.get("name") or "").lower() or "nexus" in (l.get("company") or "").lower():
            if l.get("id") not in target_ids:
                target_ids.append(l.get("id"))
                break

    target_leads = [l for l in leads_data if l.get("id") in target_ids][:5]
    print(f"[*] Identified {len(target_leads)} priority startup founder / lead profiles.\n")

    dispatcher = CampaignDispatcher()
    dispatch_records = []

    for raw in target_leads:
        lead = Lead(
            id=raw.get("id"),
            name=raw.get("name") or "Builder",
            company=raw.get("company") or "Startup Team",
            phone=raw.get("phone"),
            email=raw.get("email"),
            role=raw.get("role") or "Founder / CTO",
            notes=raw.get("notes") or ""
        )
        email_touch = dispatcher.generate_personalized_email(lead)

        record = {
            "lead_id": lead.id,
            "recipient_name": lead.name,
            "recipient_email": email_touch.recipient_email,
            "company": lead.company,
            "role": lead.role,
            "subject": email_touch.subject,
            "body": email_touch.body_text,
            "interactive_link": email_touch.direct_link,
            "dispatched_at": time.time(),
            "status": "SIMULATED_DISPATCH" if dry_run else "DISPATCHED"
        }
        dispatch_records.append(record)

        # Update status in local lead records
        raw["status"] = "DISPATCHED_WAVE_1"
        raw["last_called_at"] = time.time()
        if "outreach_history" not in raw:
            raw["outreach_history"] = []
        raw["outreach_history"].append({
            "channel": "EMAIL_WAVE_1",
            "subject": email_touch.subject,
            "timestamp": time.time(),
            "status": "SENT"
        })

        print(f"[+] [{record['status']}] {lead.name:<18} ({lead.company}) -> {email_touch.recipient_email}")
        print(f"    Subject: {email_touch.subject}")
        print(f"    Link   : {email_touch.direct_link}\n")

    # Persist updated queue
    if not dry_run:
        with open(queue_path, "w", encoding="utf-8") as f:
            json.dump(leads_data, f, indent=2)
        print(f"[+] Updated {queue_path.name} with DISPATCHED_WAVE_1 status.")

    # Save summary report
    report_path = BASE_DIR / "WAVE_1_OUTREACH_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Bartholomew Wave 1 Founder Outreach Report\n\n")
        f.write(f"- **Dispatched At**: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n")
        f.write(f"- **Total Recipients**: {len(dispatch_records)}\n")
        f.write(f"- **Focus**: Empathetic, non-jargon problem solving (accidental database drops, runaway spend, approval fatigue)\n\n")
        f.write("---\n\n")

        for idx, rec in enumerate(dispatch_records, 1):
            f.write(f"### {idx}. {rec['recipient_name']} ({rec['company']} - {rec['role']})\n\n")
            f.write(f"- **Email**: `{rec['recipient_email']}`\n")
            f.write(f"- **Subject**: `{rec['subject']}`\n")
            f.write(f"- **Status**: `{rec['status']}`\n\n")
            f.write("```text\n")
            f.write(rec["body"])
            f.write("\n```\n\n")
            f.write(f"**Interactive Link**: [{rec['interactive_link']}]({rec['interactive_link']})\n\n")
            f.write("---\n\n")

    print(f"[+] Dispatch log written to: {report_path.name}")
    print("=" * 76)

if __name__ == "__main__":
    execute_wave_1(dry_run=False)
