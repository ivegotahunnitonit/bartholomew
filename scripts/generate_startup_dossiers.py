"""
Startup & Small Business Lead Dossier Generator
===============================================
Generates warm, human, non-jargon technical outreach and safety dossiers
tailored specifically for startups, founders, and small engineering teams.
"""

import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.voice.campaign_dispatcher import CampaignDispatcher
from src.voice.lead_manager import Lead, LeadManager

def main():
    print("=" * 74)
    print("  Bartholomew Startup & Small Business Outreach Generator")
    print("=" * 74)

    queue_path = BASE_DIR / "leads_queue.json"
    if not queue_path.exists():
        print("[!] leads_queue.json not found.")
        return

    with open(queue_path, "r", encoding="utf-8") as f:
        raw_leads = json.load(f)

    dispatcher = CampaignDispatcher()
    outreach_records = []

    print(f"[*] Processing {len(raw_leads)} inbound leads from queue...\n")

    for raw in raw_leads[:15]:
        lead = Lead(
            id=raw.get("id", "lead-0"),
            name=raw.get("name") or "Builder",
            company=raw.get("company") or "Startup Team",
            phone=raw.get("phone"),
            email=raw.get("email"),
            role=raw.get("role") or "Founder / Engineering Lead",
            notes=raw.get("notes") or ""
        )
        email_touch = dispatcher.generate_personalized_email(lead)

        outreach_records.append({
            "lead_id": lead.id,
            "recipient_name": lead.name,
            "company": lead.company,
            "role": lead.role,
            "subject": email_touch.subject,
            "body": email_touch.body_text,
            "interactive_link": email_touch.direct_link
        })

    # Save to markdown report for easy reading
    report_path = BASE_DIR / "STARTUP_OUTREACH_DOSSIERS.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Startup & Small Business Relatable Outreach Dossiers\n\n")
        f.write("> **Philosophy**: High empathy, zero dense jargon, real startup problems (runaway cloud spend, babysitting approval bottlenecks, accidental table drops).\n\n")
        f.write("---\n\n")

        for idx, item in enumerate(outreach_records, 1):
            f.write(f"## {idx}. {item['recipient_name']} ({item['company']} - {item['role']})\n\n")
            f.write(f"**Subject:** `{item['subject']}`\n\n")
            f.write("```text\n")
            f.write(item["body"])
            f.write("\n```\n\n")
            f.write(f"**Live Playground Link:** [{item['interactive_link']}]({item['interactive_link']})\n\n")
            f.write("---\n\n")

    print(f"[+] Successfully generated {len(outreach_records)} startup dossiers!")
    print(f"[+] Output written to: {report_path.name}")
    print("=" * 74)

if __name__ == "__main__":
    main()
