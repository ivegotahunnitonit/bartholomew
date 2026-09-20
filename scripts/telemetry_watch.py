#!/usr/bin/env python3
"""
Bartholomew Ecosystem Telemetry Watcher & Deal Pipeline Monitor
===============================================================
Aggregates real-time telemetry from npm, PyPI, Cloud Run, GitHub,
and the outbound lead qualification & deal-closing pipeline.
"""

import os
import sys
import json
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.voice.lead_manager import LeadManager, LeadStatus


def get_npm_stats():
    try:
        url = "https://api.npmjs.org/downloads/point/last-week/btp-guard"
        req = urllib.request.Request(url, headers={"User-Agent": "BTP-Telemetry/1.0"})
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("downloads", 0)
    except Exception as e:
        return f"Error: {e}"


def get_pypi_stats():
    try:
        url = "https://pypistats.org/api/packages/btp-guard/recent"
        req = urllib.request.Request(url, headers={"User-Agent": "BTP-Telemetry/1.0"})
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            recent = data.get("data", {})
            return {
                "last_day": recent.get("last_day", 0),
                "last_week": recent.get("last_week", 0),
                "last_month": recent.get("last_month", 0)
            }
    except Exception as e:
        return {"error": str(e)}


def get_mcp_pr_status():
    try:
        url = "https://api.github.com/repos/punkpeye/awesome-mcp-servers/pulls/14215"
        req = urllib.request.Request(url, headers={"User-Agent": "BTP-Telemetry/1.0"})
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {
                "state": data.get("state"),
                "mergeable": data.get("mergeable_state"),
                "url": data.get("html_url")
            }
    except Exception as e:
        return {"error": str(e)}


def get_pipeline_summary():
    mgr = LeadManager()
    leads = mgr.get_all()
    
    total = len(leads)
    by_status = {}
    total_pipeline_val = 0.0
    closed_won_val = 0.0

    for l in leads:
        st = l.status.value if hasattr(l.status, "value") else str(l.status)
        by_status[st] = by_status.get(st, 0) + 1
        val = getattr(l, "deal_value_usd", 0.0) or 0.0
        total_pipeline_val += val
        if st == "CLOSED_WON":
            closed_won_val += val

    return {
        "total_leads": total,
        "by_status": by_status,
        "total_pipeline_val": total_pipeline_val,
        "closed_won_val": closed_won_val,
        "qualified_count": by_status.get("QUALIFIED", 0),
        "proposals_sent": by_status.get("PROPOSAL_SENT", 0),
        "closed_won": by_status.get("CLOSED_WON", 0)
    }


def print_telemetry_dashboard():
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    npm_downloads = get_npm_stats()
    pypi_downloads = get_pypi_stats()
    pr_status = get_mcp_pr_status()
    pipe = get_pipeline_summary()

    print("======================================================================")
    print(f"  Bartholomew Trust Protocol (BTP v5.4.10) -- Executive Telemetry Watch")
    print(f"  Snapshot Time: {timestamp}")
    print("======================================================================")
    print()
    print("[1] Package Distribution & Registry Adoption")
    print(f"    - npm (btp-guard) 7-day downloads:     {npm_downloads}")
    if "error" not in pypi_downloads:
        print(f"    - PyPI (btp-guard) 24h downloads:      {pypi_downloads['last_day']}")
        print(f"    - PyPI (btp-guard) 30d downloads:      {pypi_downloads['last_month']}")
    else:
        print(f"    - PyPI stats: {pypi_downloads['error']}")
    print()
    print("[2] Official MCP Directory PR Status")
    if "error" not in pr_status:
        print(f"    - awesome-mcp-servers PR #14215:       State: {pr_status['state'].upper()} | Mergeable: {pr_status['mergeable']}")
        print(f"    - URL: {pr_status['url']}")
    else:
        print(f"    - PR query error: {pr_status['error']}")
    print()
    print("[3] Deal Pipeline & Commercial Revenue Metrics")
    print(f"    - Total Target Accounts in Queue:      {pipe['total_leads']}")
    print(f"    - Qualified Prospects (Ready for Deck): {pipe['qualified_count']}")
    print(f"    - Proposals & Checkouts Dispatched:    {pipe['proposals_sent']}")
    print(f"    - Closed Won Paid Deployments:         {pipe['closed_won']}")
    print(f"    - Active Pipeline Value:               ${pipe['total_pipeline_val']:,.2f}")
    print(f"    - Realized Commercial Revenue:         ${pipe['closed_won_val']:,.2f}")
    print()
    print("[4] Account Status Breakdown")
    for st, count in sorted(pipe["by_status"].items()):
        print(f"    - {st:<28} : {count} accounts")
    print("======================================================================")


if __name__ == "__main__":
    print_telemetry_dashboard()
