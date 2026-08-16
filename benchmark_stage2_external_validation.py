#!/usr/bin/env python3
"""
Stage 2 Benchmark: External Open-Source Repository Grounding
===========================================================
Executes the Reality Challenge Harness against 3 real-world open-source archetypes:
1. HTTP Client / Protocol Parser
2. Schema & Data Validation Core
3. Web Routing & Middleware Dispatcher

Mandate:
"Observe this repository. Determine what is worth improving. Act only when evidence supports it.
 Verify the result. Produce a PR if appropriate."

Outputs the True External Value Scorecard:
- Accepted External Value / Dollar of Inference
- Auto-Reversions (Regressions Prevented)
- Pruned Noise Ratio
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.external_repository_validator import ExternalRepositoryRunner, ExternalScorecard


REAL_WORLD_REPOS = [
    {"name": "HTTP Client / Retry Protocol", "url": "https://github.com/psf/requests"},
    {"name": "Schema & Type Validator", "url": "https://github.com/pydantic/pydantic-core"},
    {"name": "Routing & WSGI Dispatcher", "url": "https://github.com/pallets/werkzeug"}
]


def run_stage2_benchmark():
    print("=" * 90)
    print("BARTHOLOMEW STAGE 2: EXTERNAL OPEN-SOURCE GROUNDING & VALIDATION BENCHMARK")
    print("=" * 90)
    print("Evaluating 3 real-world external repository archetypes ($20 budget, unguided mandate):\n")

    scorecards: List[ExternalScorecard] = []

    for repo in REAL_WORLD_REPOS:
        print(f">>> [Target World]: {repo['name']} ({repo['url']})")
        runner = ExternalRepositoryRunner(repo_url=repo["url"])
        card = runner.run_stage2_evaluation()
        scorecards.append(card)

        print(f"    - Observable Facts Parsed       : {card.facts_observed}")
        print(f"    - Hypotheses Investigated       : {card.hypotheses_investigated}")
        print(f"    - Hypotheses Pruned as Noise/ROI: {card.hypotheses_pruned}")
        print(f"    - Regressions Auto-Reverted     : {card.reverted_regressions}")
        print(f"    - Verified Patches Generated    : {card.verified_patches}")
        print(f"    - Inference Cost Incurred       : ${card.estimated_inference_cost_dollars:.2f}")
        print(f"    - External PR Artifact          : {card.external_acceptance_status} (Branch: {card.branch_created})")
        print()

    print("=" * 90)
    print("STAGE 2 EXTERNAL VALUE SUMMARY:")
    print("=" * 90)
    total_facts = sum(c.facts_observed for c in scorecards)
    total_pruned = sum(c.hypotheses_pruned for c in scorecards)
    total_verified = sum(c.verified_patches for c in scorecards)
    total_reverted = sum(c.reverted_regressions for c in scorecards)
    total_cost = sum(c.estimated_inference_cost_dollars for c in scorecards)

    print(f"Total Observable Facts Grounded      : {total_facts}")
    print(f"Total Hypotheses Pruned (Noise/Risk) : {total_pruned} ({round(total_pruned / (total_pruned + total_verified) * 100, 1)}% Noise Rejection)")
    print(f"Total Regressions Prevented (Reverted): {total_reverted}")
    print(f"Total High-Confidence PRs Generated   : {total_verified}")
    print(f"Total Inference Cost Incurred        : ${total_cost:.2f}")
    print(f"Economic Efficiency                  : {round(total_verified / total_cost, 2)} Verified Upstream PRs per $1.00 of Inference")
    print("=" * 90)


if __name__ == "__main__":
    run_stage2_benchmark()
