#!/usr/bin/env python3
"""
Bartholomew Autonomous Opportunity Loop Demo
============================================
Demonstrates the complete self-directed operating loop:
- User gives no specific task beyond: "Operate and be useful."
- System scans real environment, discovers high-value opportunities.
- Formulates its own objectives, executes, verifies, and advances to the next task.
- 0 human prompts required across all cycles.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.opportunity_engine import (
    RealWorldOpportunityScanner,
    AutonomousOpportunityEngine
)


def run_opportunity_loop_demo():
    print("=" * 85)
    print("BARTHOLOMEW: SELF-DIRECTED OPPORTUNITY & OBJECTIVE GENERATION ENGINE")
    print("=" * 85)
    print("Command: bartholomew run --mode autonomous-opportunity-engine\n")

    scanner = RealWorldOpportunityScanner(workspace_root="/workspace/app")
    engine = AutonomousOpportunityEngine(scanner=scanner)

    print(">>> USER DISPATCHES SYSTEM: 'Scan repository, discover highest-value work, and execute.'")
    print("[AUTONOMOUS OPERATING LOOP ACTIVE]")
    print("User walking away...\n")
    print("-" * 85)

    while True:
        cycle_res = engine.run_cycle()
        if cycle_res["status"] == "ALL_OPPORTUNITIES_SATISFIED":
            print(f"[{time.strftime('%H:%M:%S')}] [ALL WORK SATISFIED]: No further high-value defects or gaps found.")
            break
        
        r = cycle_res["result"]
        print(f"[{time.strftime('%H:%M:%S')}] CYCLE {r['cycle']} [{r['category']}] (Priority: {r['priority_score']})")
        print(f"    -> Self-Formulated Objective: {r['opportunity_selected']}")
        print(f"    -> Target Artifact          : {r['target']}")
        print(f"    -> Execution & Verification : {r['status']}")
        print()

    print("-" * 85)
    print("\n[GROUND-TRUTH SUMMARY AFTER USER RETURNS]:")
    print(f"- Total Self-Formulated Cycles Completed : {len(engine.execution_history)}")
    for item in engine.execution_history:
        print(f"  * Cycle {item['cycle']}: {item['opportunity_selected']} [{item['status']}]")
    print(f"- Human Prompts or Instructions Required : 0 (100% Autonomous)")
    print("=" * 85)


if __name__ == "__main__":
    run_opportunity_loop_demo()
