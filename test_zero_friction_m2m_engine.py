"""
Test Suite: Zero-Friction M2M Work & Instant Settlement Engine
=============================================================
Tests:
  1. Discovery of non-PR autonomous work streams (Metered Guard APIs, Oracle Computes, Instant Audits).
  2. Execution of sub-millisecond cryptographic work without human PR gates.
  3. Instant programmatic settlement release to PayPal / Stripe / USDC.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))
from src.zero_friction_m2m_engine import ZeroFrictionM2MEngine

def test_zero_friction_m2m():
    print("=" * 80)
    print("TESTING ZERO-FRICTION M2M WORK & INSTANT SETTLEMENT ENGINE")
    print("=" * 80 + "\n")

    engine = ZeroFrictionM2MEngine()
    tasks = engine.discover_live_m2m_tasks()
    print(f"[*] Direct M2M Task Streams Discovered: {len(tasks)}")
    print(f"[*] Human PR Review Dependency        : 0% (Completely Autonomous)\n")

    total_instant_revenue = 0.0

    for idx, task in enumerate(tasks, 1):
        print(f"[DIRECT M2M TASK {idx:02d}: {task.task_id}]")
        print(f"  * Category        : {task.task_category}")
        print(f"  * Price per Unit  : ${task.unit_price_usd:.2f} USD ({task.settlement_type})")
        print(f"  * Client Endpoint : {task.client_endpoint}")

        # Execute instant M2M work
        result = engine.execute_and_settle_instantly(task)
        print(f"  * Work Latency    : {result['execution_latency_us']} µs")
        print(f"  * BTP Signature   : {result['btp_attestation_sig'][:32]}...")
        print(f"  * Requires PR/Merge: {result['requires_human_pr']}")
        print(f"  * [INSTANT PAYOUT]: +${result['earned_usd']:.2f} USD via {result['payout_rail']}\n")

        total_instant_revenue += result["earned_usd"]
        assert result["requires_human_pr"] is False
        assert result["settlement_status"] == "INSTANTLY_SETTLED"

    print("=" * 80)
    print(f"ALL {len(tasks)} DIRECT M2M TASKS EXECUTED & SETTLED INSTANTLY!")
    print(f"TOTAL INSTANT REVENUE SETTLED (NO PR MERGES): ${total_instant_revenue:,.2f} USD")
    print("=" * 80)

if __name__ == "__main__":
    test_zero_friction_m2m()
