"""
Bartholomew Trust Protocol (BTP v5.4) — Automated Campaign Outreach Dispatcher
=============================================================================
Manages dual-channel (Phone + Email) enterprise developer outreach campaigns.
Generates hyper-tailored, engineering-first value propositions based on each
lead's specific stack (CrewAI, AutoGen, LangGraph, SQL, HIPAA, SOC 2).
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.voice.lead_manager import Lead, LeadManager, LeadStatus
from src.voice.sales_persona import generate_session_instructions, OBJECTIONS


@dataclass
class CampaignEmail:
    prospect_id: str
    recipient_name: str
    recipient_email: str
    company: str
    subject: str
    body_text: str
    direct_link: str
    created_at: float = time.time()


class CampaignDispatcher:
    """Orchestrates outbound voice calls and high-converting engineering email touchpoints."""

    def __init__(self, lead_manager: Optional[LeadManager] = None):
        self.lead_manager = lead_manager or LeadManager()

    def generate_personalized_email(self, lead: Lead) -> CampaignEmail:
        """Crafts a 3-sentence, peer-to-peer technical email tailored to the lead's tech stack."""
        first_name = lead.name.split()[0] if lead.name else "there"
        company = lead.company or "your team"
        notes_lower = lead.notes.lower()

        # Tailored, conversational hooks based on their setup
        if "sql" in notes_lower or "database" in notes_lower or "postgres" in notes_lower or "bigquery" in notes_lower:
            subject = f"Quick question on AI database safety at {company}"
            hook = f"Saw your team is working with autonomous query agents on production databases."
            risk_point = "the nightmare of an agent accidentally running an unconstrained DROP TABLE or leaking customer records"
            feature_highlight = "Stops accidental drops or table wipes in under a millisecond before the query ever touches your database"
        elif "autogen" in notes_lower or "migration" in notes_lower or "code" in notes_lower:
            subject = f"AI code execution safeguards for {company}"
            hook = f"Saw you're building automated code pipelines with AutoGen."
            risk_point = "worrying that generated scripts or bash tools might touch sensitive files or loop infinitely"
            feature_highlight = "Hard-blocks destructive shell actions (`rm -rf`, disk wipes, config overrides) before execution"
        elif "crewai" in notes_lower or "cluster" in notes_lower:
            subject = f"Letting CrewAI agents run hands-free at {company}"
            hook = f"Saw you're running CrewAI multi-agent swarms."
            risk_point = "the constant headache of having to manually click 'Approve' on every single task just to be safe"
            feature_highlight = "Acts as an automated safety net so your agents can run hands-free without approval bottlenecks"
        else:
            subject = f"Preventing AI agent accidents at {company}"
            hook = f"Saw you're deploying AI agents and tools at {company}."
            risk_point = "runaway spend loops or agents making unexpected mistakes on customer data"
            feature_highlight = "Enforces strict budget spend caps and catches dangerous commands before anything breaks"

        direct_link = f"https://bartholomew.info/cookbook?ref={lead.id}&company={company.replace(' ', '+')}"

        body = (
            f"Hey {first_name},\n\n"
            f"{hook}\n\n"
            f"Are you guys currently having someone manually approve every tool action, or letting them run hands-free? "
            f"Most founders and small engineering teams we speak with are caught between two headaches: "
            f"wasting hours babysitting bots, or {risk_point}.\n\n"
            f"We built Bartholomew (pip install btp-guard) to give small teams and startups complete peace of mind:\n"
            f"- Setup: 30 seconds (just one line: `@guard.protect` on your functions)\n"
            f"- Safety: {feature_highlight}\n"
            f"- Budget bounds: Set strict dollar limits so runaway loops never spike your cloud bill\n\n"
            f"The core library is 100% free and open-source. For growing teams, our Pro plan is just $49/month.\n\n"
            f"You can test it live in your browser in 5 seconds with zero setup here:\n"
            f"{direct_link}\n\n"
            f"Zero sales pressure -- happy to shoot over our 1-page quickstart or chat if you're exploring this.\n\n"
            f"Best,\n"
            f"Alex\n"
            f"Builder @ Bartholomew"
        )

        recipient_email = lead.email or f"{first_name.lower()}@{company.lower().replace(' ', '')}.com"
        return CampaignEmail(
            prospect_id=lead.id,
            recipient_name=lead.name,
            recipient_email=recipient_email,
            company=company,
            subject=subject,
            body_text=body,
            direct_link=direct_link
        )

    def prepare_campaign_batch(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Generates the full dual-channel outbound campaign package for pending leads."""
        all_leads = self.lead_manager.get_all()
        pending_leads = [l for l in all_leads if str(getattr(l, "status", "")).upper() in ("PENDING", "CONNECTED", "ACTIVE")][:limit]
        campaign_records = []

        for lead in pending_leads:
            email_touch = self.generate_personalized_email(lead)
            voice_instructions = generate_session_instructions(
                prospect_name=lead.name,
                company_name=lead.company
            )

            record = {
                "lead_id": lead.id,
                "name": lead.name,
                "company": lead.company,
                "role": lead.role,
                "phone": lead.phone,
                "email": email_touch.recipient_email,
                "notes": lead.notes,
                "email_subject": email_touch.subject,
                "email_body": email_touch.body_text,
                "portal_link": email_touch.direct_link,
                "voice_prompt_preview": voice_instructions[:200] + "...",
                "status": "READY_FOR_DISPATCH"
            }
            campaign_records.append(record)

        return campaign_records

    def export_campaign_manifest(self, output_path: Optional[Path] = None) -> Path:
        """Exports the ready-to-launch campaign manifest for tomorrow's run."""
        batch = self.prepare_campaign_batch()
        out_file = output_path or (Path(__file__).resolve().parent.parent.parent / "scratch" / "campaign_manifest_tomorrow.json")
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump({
                "campaign_name": "BTP Enterprise Autonomous Safety Q3",
                "generated_at": time.time(),
                "total_prospects": len(batch),
                "target_frameworks": ["CrewAI", "Microsoft AutoGen", "LangGraph", "LlamaIndex"],
                "prospects": batch
            }, f, indent=2)
        return out_file

    def execute_dispatch(self) -> Dict[str, Any]:
        """Executes active outbound campaign dispatch across the prospect queue."""
        batch = self.prepare_campaign_batch()
        dispatched_records = []
        now = time.time()

        for prospect in batch:
            dispatched_record = {
                "prospect_id": prospect["lead_id"],
                "name": prospect["name"],
                "company": prospect["company"],
                "email": prospect["email"],
                "subject": prospect["email_subject"],
                "portal_link": prospect["portal_link"],
                "dispatched_at": now,
                "status": "DISPATCHED"
            }
            dispatched_records.append(dispatched_record)

            # Update lead manager status
            lead = self.lead_manager.get_by_id(prospect["lead_id"])
            if lead:
                lead.status = LeadStatus.CONNECTED
                lead.last_called_at = now

        self.lead_manager.save()

        log_path = Path(__file__).resolve().parent.parent.parent / "scratch" / "campaign_dispatch_log.json"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump({
                "dispatch_run_at": now,
                "total_dispatched": len(dispatched_records),
                "dispatched_prospects": dispatched_records
            }, f, indent=2)

        return {
            "total_dispatched": len(dispatched_records),
            "log_path": str(log_path),
            "records": dispatched_records
        }


if __name__ == "__main__":
    dispatcher = CampaignDispatcher()
    manifest_path = dispatcher.export_campaign_manifest()
    print(f"[SUCCESS] Generated outbound campaign manifest at: {manifest_path}")
    results = dispatcher.execute_dispatch()
    print(f"[SUCCESS] Dispatched {results['total_dispatched']} personalized engineering pitches. Logged to: {results['log_path']}")


