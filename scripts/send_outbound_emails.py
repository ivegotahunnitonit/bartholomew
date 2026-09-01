"""
Bartholomew Outbound SES Batch Dispatcher (50 Fast-Moving AI Startups)
======================================================================
Sends personalized, human, AI-proof developer-to-developer outreach
from itsub@bartholomew.info to technical leads and founders.

Usage:
  python scripts/send_outbound_emails.py --dry-run
  python scripts/send_outbound_emails.py --send-id 1
  python scripts/send_outbound_emails.py --send-all
"""

import boto3
import json
import os
import sys
import time
import argparse

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
SENDER = "Itsub Alemayehu <itsub@bartholomew.info>"

ses_client = boto3.client("ses", region_name=AWS_REGION)

def load_leads():
    path = os.path.join(os.path.dirname(__file__), "startup_leads_50.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_email_content(lead):
    first_name = lead["contact"].split()[0]
    company = lead["company"]
    focus = lead["focus"]

    subject = f"quick technical note on {company} agent execution latency"

    body = f"""Hi {first_name},

Big fan of what you guys are building with {company} around {focus}.

I'm reaching out because we kept hitting a frustrating bottleneck with autonomous agent tool execution: cloud guardrails add 1.2 to 2.0 seconds of latency on every tool call and rack up token bills fast.

We built Bartholomew (`btp-guard`) to fix that.

Instead of making cloud roundtrips, it evaluates tool commands directly inside local memory at the AST level in 38 microseconds (about 30,000x faster than cloud filters) for $0.00. It catches things like accidental database drops, destructive file writes, and leaked API keys before the computer ever executes them.

We already published drop-in Python and Node adapters on PyPI and npm (`pip install btp-guard`).

We put together an interactive sandbox where you can test real tool calls live in the browser without installing anything:
👉 https://bartholomew.info

No sales pitch here—just thought this might save your team a ton of latency. Would love your candid feedback on the approach if you have 2 minutes to check it out.

Cheers,

Itsub Alemayehu
Founder, ACN
itsub@bartholomew.info | https://bartholomew.info"""

    return subject, body

def send_single_email(lead, dry_run=False):
    subject, body = generate_email_content(lead)
    to_email = lead["email"]

    if dry_run:
        print(f"[DRY-RUN] Would send to: {lead['contact']} <{to_email}> ({lead['company']})")
        print(f"          Subject: {subject}")
        return True

    try:
        response = ses_client.send_email(
            Destination={"ToAddresses": [to_email]},
            Message={
                "Body": {"Text": {"Charset": "UTF-8", "Data": body}},
                "Subject": {"Charset": "UTF-8", "Data": subject},
            },
            Source=SENDER,
        )
        print(f"[OK] Sent to {lead['company']} ({to_email}) | MessageId: {response['MessageId']}")
        return True
    except Exception as e:
        print(f"[!] Error sending to {lead['company']} ({to_email}): {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="50 Startup Outbound Email Dispatcher")
    parser.add_argument("--dry-run", action="store_true", help="Preview all 50 emails without sending")
    parser.add_argument("--send-id", type=int, help="Send email to specific lead ID (1-50)")
    parser.add_argument("--send-all", action="store_true", help="Send to all 50 startups")
    args = parser.parse_args()

    leads = load_leads()

    if args.send_id:
        match = next((l for l in leads if l["id"] == args.send_id), None)
        if match:
            print(f"Dispatching to #{match['id']} - {match['company']}...")
            send_single_email(match, dry_run=args.dry_run)
        else:
            print(f"[!] Lead ID {args.send_id} not found.")
        return

    if args.dry_run or args.send_all:
        print("=" * 75)
        print(f"  BARTHOLOMEW 50-STARTUP OUTBOUND DISPATCH {'(DRY RUN)' if args.dry_run else '(LIVE SEND)'}")
        print("=" * 75)
        success_count = 0
        for l in leads:
            res = send_single_email(l, dry_run=args.dry_run)
            if res:
                success_count += 1
            if not args.dry_run:
                time.sleep(1.0) # Rate limit pacing
        print("=" * 75)
        print(f"Completed {success_count}/{len(leads)} leads.")
    else:
        print("Run with `--dry-run` to preview all 50 emails, or `--send-id <id>` to send to a specific lead.")

if __name__ == "__main__":
    main()
