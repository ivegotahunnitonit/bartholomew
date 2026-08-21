"""
Bartholomew Autonomous M2M Opportunity & Cashflow Daemon Runner
==============================================================
Launches the persistent autonomous opportunity discovery & triage daemon.
Discovers tasks across agent ecosystems, evaluates Bayesian EMV, executes
solutions inside BTP-guarded sandboxes, and logs immutable provenance.
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./pypi_package"))

from bartholomew_eval.persistent_daemon import PersistentAutonomousDaemon
from src.trust_protocol import BartholomewTrustAuthority

def run_cashflow_daemon():
    print("=" * 80)
    print("STARTING BARTHOLOMEW AUTONOMOUS M2M OPPORTUNITY DAEMON")
    print("=" * 80)

    authority = BartholomewTrustAuthority(ttl_seconds=300)
    print(f"[*] BTP Authority Initialized : {authority.public_key_hex[:32]}...")
    print(f"[*] Mandate                   : Autonomous M2M Task Resolution & Cashflow Discovery")
    print(f"[*] Budget Cap                : $100.00 USD")
    print(f"[*] Checkpoint Storage        : ./mission_state.json\n")

    daemon = PersistentAutonomousDaemon(
        mandate="Autonomous Discovery & Verification of High-Alpha Bounties",
        workspace_dir="./workspace/target-project",
        state_file="mission_state.json",
        budget_cap_usd=100.0,
        poll_interval_s=0.5
    )

    print("[*] Beginning live opportunity discovery cycles...\n")

    def cycle_callback(step_result):
        cycle = step_result.get("cycle", 0)
        summary = step_result.get("summary", "")
        ts = step_result.get("timestamp", "")
        print(f"[{ts}] [Cycle {cycle:02d}] {summary}")

    # Run 5 live discovery cycles
    daemon.run_loop(max_cycles=5, callback=cycle_callback)

    print("\n" + "=" * 80)
    print("DAEMON CHECKPOINT SUMMARY:")
    print("=" * 80)
    print(f"[*] Cycles Completed        : {daemon.state.cycle}")
    print(f"[*] Sources Queried         : {daemon.state.external_sources_queried_count}")
    print(f"[*] Opportunities Screened  : {daemon.state.opportunities_screened}")
    print(f"[*] Actions Verified        : {daemon.state.actions_verified}")
    print(f"[*] Compute Invested        : ${daemon.state.cash_spent_usd:.2f}")
    print(f"[*] Confirmed State Checkpoint: {daemon.state_file}")
    print("=" * 80)

if __name__ == "__main__":
    run_cashflow_daemon()
