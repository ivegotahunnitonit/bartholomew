#!/usr/bin/env python3
"""
Bartholomew: The Owner-Centric Value Function Demo
==================================================
Demonstrates how the autonomous runtime aligns every action with the Owner's benefit:
- Concrete Owner constraints (Jurisdiction, budget ceiling, human payment approval).
- Rigorous Alpha Triage: Rejects negative-ROI churn, prioritizes high-value work.
- Transparent economic scorecard showing exact net owner value.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.owner_operator import OwnerProfile, OwnerValueEngine


def run_owner_demo():
    print("=" * 105)
    print("BARTHOLOMEW: OWNER-CENTRIC VALUE FUNCTION & ECONOMIC TRIAGE")
    print("=" * 105)
    print("Core Premise: Bartholomew works on behalf of a specific owner under explicit constraints.\n")

    owner = OwnerProfile(
        owner_name="Don",
        jurisdiction="Canada",
        monthly_budget_cap_usd=20.0,
        require_human_payment_approval=True
    )

    engine = OwnerValueEngine(owner=owner)

    print(f">>> [OWNER PROFILE INITIALIZED]: {owner.owner_name} ({owner.jurisdiction}) | Budget Cap: ${owner.monthly_budget_cap_usd:.2f}/mo")
    print(f"    - Constraints : Human payment approval REQUIRED | Prohibited: {owner.prohibited_actions}")
    print("-" * 105)

    candidates = [
        {
            "id": "OPP_CONTRACT_001",
            "domain": "paid_contract",
            "title": "Build distributed rate-limit verification harness for remote client",
            "payout": 350.00,
            "cost": 2.40,
            "hours": 1.5
        },
        {
            "id": "OPP_BOUNTY_002",
            "domain": "bug_bounty",
            "title": "Reproduce and report token bucket concurrency race condition in Redis client",
            "payout": 150.00,
            "cost": 1.20,
            "hours": 0.8
        },
        {
            "id": "OPP_NOISE_003",
            "domain": "pure_noise",
            "title": "Speculative whitespace and formatting refactor across 40 files",
            "payout": 0.00,
            "cost": 0.50,
            "hours": 2.0
        }
    ]

    for c in candidates:
        approved, reason, eval_res = engine.triage_opportunity(
            opp_id=c["id"],
            domain=c["domain"],
            title=c["title"],
            expected_payout=c["payout"],
            compute_cost=c["cost"],
            effort_hours=c["hours"]
        )

        status_tag = "[APPROVED]" if approved else "[REJECTED]"
        print(f"{status_tag:<14} | {c['id']:<18} | Domain: {c['domain']:<14} | Payout: ${c['payout']:>6.2f} | Compute: ${c['cost']:>4.2f}")
        print(f"  -> Title  : {c['title']}")
        print(f"  -> Verdict: {reason}")
        if approved:
            print(f"  -> Owner Action: Requires owner approval to submit/collect = {eval_res.requires_owner_approval_to_submit}")
        print()

    print("=" * 105)
    print("OWNER ECONOMIC PIPELINE SUMMARY:")
    print("=" * 105)
    total_approved_payout = sum(o.expected_payout_usd for o in engine.approved_pipeline)
    total_compute_cost = sum(o.estimated_compute_cost_usd for o in engine.approved_pipeline)
    net_owner_alpha = total_approved_payout - total_compute_cost

    print(f"- Total High-Value Opportunities Approved : {len(engine.approved_pipeline)}")
    print(f"- Total Speculative Churn Rejected        : {len(engine.rejected_pipeline)}")
    print(f"- Total Expected Gross Payout to Owner    : ${total_approved_payout:.2f}")
    print(f"- Total Estimated Compute Cost Incurred   : ${total_compute_cost:.2f}")
    print(f"- NET PROJECTED OWNER ECONOMIC ALPHA      : +${net_owner_alpha:.2f}")
    print(f"- Expected ROI                            : {round(total_approved_payout / total_compute_cost, 1)}x return on compute capital")
    print("=" * 105)


if __name__ == "__main__":
    run_owner_demo()
