"""
Bartholomew Trust Protocol (BTP v5.4) -- Round-The-Clock Global Outreach & Dialing Engine
========================================================================================
Autonomous timezone-aware dialer that operates 24/7 across global markets:
  - Americas (UTC-8 to UTC-3): 14:00 - 23:00 UTC (US, Canada, LATAM)
  - Asia-Pacific (UTC+5.5 to UTC+10): 00:00 - 08:00 UTC (Tokyo, Singapore, Sydney, Bangalore)
  - Europe & Middle East (UTC+0 to UTC+4): 07:00 - 16:00 UTC (London, Berlin, Paris, Dublin, Dubai)

Enforces strict local business-hour windows (9:00 AM - 5:30 PM local time),
smart redial cadences (max 3 attempts, 4-hour cooldown), and automated SMS follow-ups.
"""

import os
import sys
import time
import json
import logging
import asyncio
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from .voice_config import config, VoiceConfig
from .lead_manager import Lead, LeadManager, LeadStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("btp.voice.global_runner")


# ---------------------------------------------------------------------------
# Global Timezone Mapping Table
# ---------------------------------------------------------------------------

AREA_CODE_TIMEZONES_US_CA: Dict[str, float] = {
    # US Pacific Time (UTC -7 DST)
    "415": -7.0, "650": -7.0, "408": -7.0, "510": -7.0, "206": -7.0,
    "503": -7.0, "310": -7.0, "818": -7.0, "949": -7.0, "858": -7.0,
    # Canada Pacific (Vancouver / BC)
    "604": -7.0, "778": -7.0, "250": -7.0,
    # US Mountain Time (UTC -6 DST)
    "303": -6.0, "720": -6.0, "801": -6.0, "602": -7.0, "480": -7.0, "505": -6.0,
    # Canada Mountain (Calgary / Edmonton)
    "403": -6.0, "587": -6.0,
    # US Central Time (UTC -5 DST)
    "312": -5.0, "773": -5.0, "512": -5.0, "214": -5.0, "713": -5.0, "612": -5.0, "615": -5.0,
    # US Eastern Time (UTC -4 DST)
    "212": -4.0, "646": -4.0, "718": -4.0, "617": -4.0, "305": -4.0, "404": -4.0, "202": -4.0,
    # Canada Eastern (Toronto / Montreal / Ottawa)
    "416": -4.0, "647": -4.0, "905": -4.0, "514": -4.0, "613": -4.0,
}

COUNTRY_TIMEZONES: Dict[str, Tuple[float, str]] = {
    # Europe
    "+44": (1.0, "Europe/London (BST/GMT)"),
    "+353": (1.0, "Europe/Dublin (IST/GMT)"),
    "+49": (2.0, "Europe/Berlin (CEST/CET)"),
    "+33": (2.0, "Europe/Paris (CEST/CET)"),
    "+31": (2.0, "Europe/Amsterdam (CEST/CET)"),
    "+41": (2.0, "Europe/Zurich (CEST/CET)"),
    "+46": (2.0, "Europe/Stockholm (CEST/CET)"),
    # Middle East
    "+971": (4.0, "Asia/Dubai (GST)"),
    "+972": (3.0, "Asia/Jerusalem (IDT)"),
    # Asia & Pacific
    "+91": (5.5, "Asia/Kolkata (IST)"),
    "+65": (8.0, "Asia/Singapore (SGT)"),
    "+852": (8.0, "Asia/Hong_Kong (HKT)"),
    "+81": (9.0, "Asia/Tokyo (JST)"),
    "+82": (9.0, "Asia/Seoul (KST)"),
    "+61": (10.0, "Australia/Sydney (AEST)"),
    # Latin America
    "+55": (-3.0, "America/Sao_Paulo (BRT)"),
    "+52": (-6.0, "America/Mexico_City (CST)")
}


def resolve_prospect_timezone(phone: str) -> Tuple[float, str]:
    """
    Infers UTC offset and region description from international phone prefix or area code.
    """
    clean_phone = phone.strip().replace(" ", "").replace("-", "")

    # Check non-US/CA country codes first
    for prefix, (offset, name) in COUNTRY_TIMEZONES.items():
        if clean_phone.startswith(prefix):
            return offset, name

    # Check US / Canada (+1)
    if clean_phone.startswith("+1") and len(clean_phone) >= 5:
        area_code = clean_phone[2:5]
        if area_code in AREA_CODE_TIMEZONES_US_CA:
            offset = AREA_CODE_TIMEZONES_US_CA[area_code]
            if offset == -7.0:
                tz_label = "US/Canada Pacific"
            elif offset == -6.0:
                tz_label = "US/Canada Mountain"
            elif offset == -5.0:
                tz_label = "US Central"
            else:
                tz_label = "US/Canada Eastern"
            return offset, f"{tz_label} (Area {area_code})"

    # Default fallback to US Eastern (primary business hub)
    return -4.0, "US/Eastern (Default)"


def is_in_business_hours(
    utc_offset: float,
    target_time_utc: Optional[datetime] = None,
    allow_weekends: bool = False
) -> Tuple[bool, str]:
    """
    Determines if current local time at target offset is within calling hours.
    - Weekdays: 9:00 AM - 5:30 PM local time.
    - Weekends (if allowed): 10:00 AM - 6:00 PM local time.
    """
    now_utc = target_time_utc or datetime.now(timezone.utc)
    # Compute decimal local hour
    utc_hours = now_utc.hour + (now_utc.minute / 60.0)
    local_hour = (utc_hours + utc_offset) % 24.0

    # Local day of week (accounting for day wrap)
    local_day = now_utc.weekday()
    if (utc_hours + utc_offset) < 0:
        local_day = (local_day - 1) % 7
    elif (utc_hours + utc_offset) >= 24:
        local_day = (local_day + 1) % 7

    status_str = f"{int(local_hour):02d}:{int((local_hour % 1) * 60):02d} local time"

    # Weekend check (5 = Saturday, 6 = Sunday)
    if local_day >= 5:
        if not allow_weekends:
            return False, f"Weekend ({status_str})"
        in_hours = 10.0 <= local_hour <= 18.0
        return in_hours, f"Weekend Daytime ({status_str})" if in_hours else f"Weekend Off-Hours ({status_str})"

    # Weekday business hours: 9:00 to 17:30
    in_hours = 9.0 <= local_hour <= 17.5
    return in_hours, status_str


# ---------------------------------------------------------------------------
# Global Campaign Runner Class
# ---------------------------------------------------------------------------

class GlobalCampaignRunner:
    """
    Orchestrates round-the-clock, continuous calling across global markets.
    """

    def __init__(self, lead_manager: Optional[LeadManager] = None):
        self.lead_mgr = lead_manager or LeadManager()

    def get_callable_leads_now(
        self,
        allow_weekends: bool = False,
        cooldown_hours: float = 4.0,
        max_attempts: int = 3
    ) -> List[Tuple[Lead, float, str, str]]:
        """
        Scans all leads and returns those whose local time is currently in active business hours.
        Enforces polite redial cadences (max attempts and cooldown).
        """
        now_ts = time.time()
        callable_list = []
        eligible_statuses = (
            LeadStatus.PENDING,
            LeadStatus.DISPATCHED_EXECUTIVE_DOSSIER,
            LeadStatus.VOICEMAIL
        )

        for lead in self.lead_mgr.get_all():
            if lead.status in eligible_statuses:
                # Check attempt count
                attempts = lead.extra.get("call_attempts", 0)
                if attempts >= max_attempts:
                    continue

                # Check cooldown
                last_called = lead.last_called_at or 0.0
                if (now_ts - last_called) < (cooldown_hours * 3600):
                    continue

                offset, tz_name = resolve_prospect_timezone(lead.phone)
                in_hours, local_str = is_in_business_hours(offset, allow_weekends=allow_weekends)
                if in_hours:
                    callable_list.append((lead, offset, tz_name, local_str))

        return callable_list

    def get_global_schedule_status(self, allow_weekends: bool = False) -> Dict[str, Any]:
        """
        Summarizes global calling readiness across Americas, EMEA, and APAC.
        """
        now_utc = datetime.now(timezone.utc)
        leads = self.lead_mgr.get_all()
        callable_now = self.get_callable_leads_now(allow_weekends=allow_weekends)

        # Regional breakdowns
        regions = {
            "APAC (Tokyo, Singapore, Sydney, Bangalore)": is_in_business_hours(8.0, now_utc, allow_weekends=allow_weekends)[0],
            "Middle East (Dubai, Tel Aviv)": is_in_business_hours(4.0, now_utc, allow_weekends=allow_weekends)[0],
            "EMEA (London, Berlin, Paris, Dublin, Zurich)": is_in_business_hours(1.0, now_utc, allow_weekends=allow_weekends)[0],
            "Americas (New York, Austin, SF, Toronto)": is_in_business_hours(-5.0, now_utc, allow_weekends=allow_weekends)[0],
        }

        active_region = [r for r, active in regions.items() if active]

        # Calculate total pipeline revenue
        total_pipeline = sum(getattr(l, "contract_value_usd", 25000.0) or 25000.0 for l in leads)

        return {
            "current_utc": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "active_business_regions": active_region or ["Global Transition Window"],
            "total_leads_in_queue": len(leads),
            "total_pipeline_value_usd": total_pipeline,
            "callable_leads_right_now": len(callable_now),
            "callable_sample": [
                {
                    "name": l[0].name,
                    "company": l[0].company,
                    "phone": l[0].phone,
                    "region": l[2],
                    "local_time": l[3]
                }
                for l in callable_now[:6]
            ]
        }

    def dial_prospect(self, lead: Lead, simulate: bool = False, send_sms: bool = True) -> Dict[str, Any]:
        """
        Executes a real or simulated phone consultation call.
        """
        logger.info(f"Initiating consultation with {lead.name} at {lead.company} ({lead.phone})...")

        # Track attempt
        attempts = lead.extra.get("call_attempts", 0) + 1
        lead.extra["call_attempts"] = attempts
        lead.last_called_at = time.time()

        if simulate or "555" in lead.phone or not config.is_twilio_ready():
            logger.info(f"[SIMULATION] Simulating conversational phone session for {lead.name}...")
            lead.status = LeadStatus.CONNECTED
            lead.call_duration_seconds = 52
            first_name = lead.name.split()[0]
            lead.transcript = [
                {"role": "assistant", "content": f"Hey {first_name}! Alex here. Caught you randomly -- do you have 30 seconds, or are you in the middle of a deployment fire over at {lead.company}?"},
                {"role": "user", "content": "Haha yeah, what's this regarding?"},
                {"role": "assistant", "content": "Quick question from one builder to another: are you guys letting your AI agents run tools hands-free yet, or still stuck babysitting every single action?"},
                {"role": "user", "content": "We manually approve everything right now because we're terrified of accidental database table drops or runaway spend."},
                {"role": "assistant", "content": "Haha yeah, the classic approval bottleneck! That exact headache is why we built Bartholomew -- 100% open source on npm and PyPI, blocks bad commands in under 35 microseconds."},
                {"role": "user", "content": "35 microseconds in-memory? That's actually pretty clean. Can you send over the docs and quickstart?"},
                {"role": "assistant", "content": "100%! Can check out bartholomew.info or I can shoot the 1-page guide to your email. What's the best address?"}
            ]
            self.lead_mgr.qualify_lead(lead.id, notes="Interested in execution firewall; requested quickstart guide.")
            proposal = self.lead_mgr.send_proposal(lead.id, tier="pro")

            sms_result = None
            if send_sms:
                from .twilio_server import send_followup_sms
                sms_result = send_followup_sms(lead.phone, lead.name, checkout_url=proposal.get("checkout_url"))

            return {
                "status": "simulated_success",
                "lead_id": lead.id,
                "company": lead.company,
                "outcome": "QUALIFIED",
                "proposal_sent": True,
                "sms_dispatched": bool(sms_result)
            }

        # Real Twilio Outbound Call Execution with AMD
        try:
            from twilio.rest import Client
            client = Client(config.twilio_account_sid, config.twilio_auth_token)
            stream_entrypoint = f"{config.public_base_url.rstrip('/')}/voice/live_stream?lead_id={lead.id}"
            amd_callback = f"{config.public_base_url.rstrip('/')}/voice/amd_callback?lead_id={lead.id}"

            call = client.calls.create(
                to=lead.phone,
                from_=config.twilio_phone_number,
                url=stream_entrypoint,
                machine_detection="DetectMessageEnd",
                async_amd="true",
                async_amd_status_callback=amd_callback
            )
            lead.status = LeadStatus.CALLING
            self.lead_mgr.save()
            return {
                "status": "dialing_active",
                "call_sid": call.sid,
                "target_phone": lead.phone,
                "company": lead.company
            }
        except Exception as e:
            logger.error(f"Twilio dialing error for {lead.phone}: {e}")
            return {"status": "error", "error": str(e)}

    def run_continuous_campaign(
        self,
        interval_seconds: int = 45,
        max_calls: int = 50,
        dry_run: bool = False,
        allow_weekends: bool = False,
        send_sms: bool = True
    ):
        """
        Continuous round-the-clock campaign loop.
        Dials eligible leads as their local timezone opens, sleeping when none are active.
        """
        calls_made = 0
        logger.info("Starting Bartholomew 24/7 Global Autonomous Dialing Engine...")

        while calls_made < max_calls:
            callable_leads = self.get_callable_leads_now(allow_weekends=allow_weekends)
            if not callable_leads:
                sched = self.get_global_schedule_status(allow_weekends=allow_weekends)
                logger.info(f"No leads currently in active business hours. Active regions: {sched['active_business_regions']}. Pausing 60s...")
                time.sleep(min(interval_seconds, 60))
                continue

            target_lead, offset, tz_name, local_time = callable_leads[0]
            logger.info(f"Selected Lead: {target_lead.name} ({target_lead.company}) in {tz_name} [{local_time}]")

            result = self.dial_prospect(target_lead, simulate=dry_run, send_sms=send_sms)
            calls_made += 1
            logger.info(f"Call #{calls_made}/{max_calls} completed: {result.get('status')} -> {result.get('outcome', 'IN_PROGRESS')}")

            if calls_made < max_calls:
                logger.info(f"Pacing pause: sleeping {interval_seconds} seconds before next consultation...")
                time.sleep(interval_seconds)

        logger.info(f"Campaign cycle finished. Total consultations conducted: {calls_made}.")


# ---------------------------------------------------------------------------
# CLI Command Entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Bartholomew Round-the-Clock Global Dialing Engine")
    parser.add_argument("--status", action="store_true", help="Display global timezone status and callable queue")
    parser.add_argument("--dial-next", action="store_true", help="Dial the single highest-priority callable prospect")
    parser.add_argument("--continuous", "--daemon", action="store_true", help="Run 24/7 continuous autonomous dialing loop")
    parser.add_argument("--interval", type=int, default=45, help="Pacing interval between calls in seconds")
    parser.add_argument("--max-calls", type=int, default=25, help="Maximum calls to execute in this run")
    parser.add_argument("--dry-run", action="store_true", help="Run in simulation mode without carrier charges")
    parser.add_argument("--allow-weekends", action="store_true", help="Allow daytime calling on weekends (10:00 - 18:00 local)")
    parser.add_argument("--no-sms", action="store_true", help="Disable automated follow-up SMS dispatch")

    args = parser.parse_args()
    runner = GlobalCampaignRunner()

    if args.status:
        st = runner.get_global_schedule_status(allow_weekends=args.allow_weekends)
        print("======================================================================")
        print("  Bartholomew Round-The-Clock Global Calling Readiness")
        print(f"  Current UTC Time:          {st['current_utc']}")
        print(f"  Active Business Regions:   {', '.join(st['active_business_regions'])}")
        print(f"  Total Leads in Queue:      {st['total_leads_in_queue']}")
        print(f"  Total Pipeline Value:      USD {st['total_pipeline_value_usd']:,.2f}")
        print(f"  Callable Right Now:        {st['callable_leads_right_now']}")
        print("======================================================================")
        if st["callable_sample"]:
            print("\nSample Callable Prospects:")
            for p in st["callable_sample"]:
                print(f"  - {p['name']:<18} | {p['company']:<28} | {p['region']:<28} | {p['local_time']}")
        print()

    elif args.dial_next:
        callable_leads = runner.get_callable_leads_now(allow_weekends=args.allow_weekends)
        if not callable_leads:
            print("No prospects currently in local business hours. Check back as the next region opens.")
            return
        target = callable_leads[0][0]
        res = runner.dial_prospect(target, simulate=args.dry_run, send_sms=not args.no_sms)
        print("Dial Result:", json.dumps(res, indent=2))

    elif args.continuous:
        runner.run_continuous_campaign(
            interval_seconds=args.interval,
            max_calls=args.max_calls,
            dry_run=args.dry_run,
            allow_weekends=args.allow_weekends,
            send_sms=not args.no_sms
        )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
