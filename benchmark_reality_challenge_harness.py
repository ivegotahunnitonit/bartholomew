#!/usr/bin/env python3
"""
Reality Challenge Harness Benchmark: Real-World Scorecard
=========================================================
Runs the unguided Reality Challenge Harness on an uncurated target codebase:
- Observes physical ground truth.
- Reasons over noisy hypotheses (real bugs vs pointless TODOs vs breaking dependency upgrades).
- Executes only verified improvements.
- Auto-reverts regressions.
- Concludes based on empirical value thresholds.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.reality_challenge_harness import RealityChallengeHarness


def main():
    print("=" * 85)
    print("BARTHOLOMEW: REALITY CHALLENGE HARNESS (REAL-WORLD ADVERSARIAL TEST)")
    print("=" * 85)
    print("Target: ./workspace/target-project (Unvetted Codebase)")
    print("Mandate: 'Observe. Determine what matters. Act only on evidence. Verify. Learn.'\n")

    harness = RealityChallengeHarness(target_path="./workspace/target-project", max_duration_s=21600.0, budget_dollars=20.0)
    result = harness.execute_challenge()

    print("-" * 85)
    print("OBJECTIVE EXTERNAL SCORECARD:")
    print("-" * 85)
    print(f"Target World Inspected         : {result.target_world}")
    print(f"Observable Facts Parsed        : {result.observable_facts}")
    print(f"Hypotheses Investigated        : {result.hypotheses_investigated}")
    print(f"Hypotheses Pruned (Noise/Risk) : {result.hypotheses_rejected_as_noise}")
    print(f"Verified Interventions         : {result.verified_interventions}")
    print(f"Reverted Regressions           : {result.reverted_regressions}")
    print(f"External Action Result         : {result.residual_action}")
    if result.git_patch_summary:
        print(f"Generated Git Patch            : '{result.git_patch_summary}'")
    print("=" * 85)


if __name__ == "__main__":
    main()
