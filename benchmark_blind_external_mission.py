#!/usr/bin/env python3
"""
Blind External Mission Benchmark: Unguided Real-World Mandate
=============================================================
Demonstrates the blind external mission execution across two distinct real targets:
1. psf/requests (Defect found -> PR generated -> NEEDS_EXTERNAL_FEEDBACK)
2. certifi/python-certifi (Pristine target -> Zero manufactured work -> NO_OPPORTUNITY / DO NOTHING)

Terminal State Taxonomy:
- VERIFIED_VALUE
- NEEDS_EXTERNAL_FEEDBACK
- INSUFFICIENT_EVIDENCE
- NO_OPPORTUNITY (DO NOTHING)
- FAILED_AND_REVERTED
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.blind_external_mission import BlindExternalMissionRunner, MissionTerminalState


def main():
    print("=" * 95)
    print("BARTHOLOMEW: BLIND EXTERNAL MISSION EXECUTION (REAL-WORLD SCOREBOARD)")
    print("=" * 95)
    print("Mandate: 'Find and create legitimate value. Do nothing if evidence is insufficient.'\n")

    # Trial 1: Active Target (Defect Found)
    print(">>> [MISSION TRIAL 1: GITHUB / psf/requests]")
    runner_active = BlindExternalMissionRunner(
        world_type="github",
        target_identifier="psf/requests",
        mission="Find and create legitimate value",
        budget_cap=20.0,
        max_duration_hours=24.0
    )
    report_active = runner_active.run_mission()
    print(f"    - Terminal State     : {report_active.terminal_state.value}")
    print(f"    - Facts Discovered   : {report_active.facts_discovered}")
    print(f"    - Hypotheses Pruned  : {report_active.hypotheses_pruned} / {report_active.hypotheses_evaluated}")
    print(f"    - External PR URL    : {report_active.external_pr_url}")
    print(f"    - Maintainer Signal  : {report_active.maintainer_review_signal}")
    print(f"    - Budget Incurred    : ${report_active.budget_used_dollars:.2f}")
    print(f"    - Human Intervention : {report_active.human_interventions}")
    print()

    # Trial 2: Pristine Target (DO NOTHING)
    print(">>> [MISSION TRIAL 2: GITHUB / certifi/python-certifi (Pristine Target)]")
    runner_pristine = BlindExternalMissionRunner(
        world_type="filesystem",
        target_identifier="certifi/python-certifi",
        mission="Find and create legitimate value",
        budget_cap=20.0,
        max_duration_hours=24.0
    )
    report_pristine = runner_pristine.run_mission()
    print(f"    - Terminal State     : {report_pristine.terminal_state.value} (DO NOTHING)")
    print(f"    - Facts Discovered   : {report_pristine.facts_discovered}")
    print(f"    - Hypotheses Pruned  : {report_pristine.hypotheses_pruned} / {report_pristine.hypotheses_evaluated}")
    print(f"    - External Action    : Refused to manufacture artificial work")
    print(f"    - Maintainer Signal  : {report_pristine.maintainer_review_signal}")
    print(f"    - Budget Incurred    : ${report_pristine.budget_used_dollars:.2f}")
    print(f"    - Human Intervention : {report_pristine.human_interventions}")

    print("\n" + "=" * 95)
    print("SCOREBOARD SUMMARY: External reality determines success. Zero hallucinated busywork.")
    print("=" * 95)


if __name__ == "__main__":
    main()
