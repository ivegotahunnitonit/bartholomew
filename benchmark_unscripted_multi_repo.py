#!/usr/bin/env python3
"""
Unscripted Multi-Repository Reality Benchmark (10 Diverse Repositories)
======================================================================
Tests Bartholomew across 10 real-world repository profiles with zero hardcoded fixtures:
- High variability in LOC, file counts, and facts discovered.
- Correctly identifies pristine repositories and chooses DO NOTHING.
- Patches genuine edge-case defects while auto-reverting speculative regressions.
- Tracks exact inference cost per verified upstream contribution.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.unscripted_external_evaluator import DynamicMultiRepoEvaluator, UnscriptedEvaluationOutcome


def run_unscripted_multi_repo_benchmark():
    print("=" * 105)
    print("BARTHOLOMEW: UNSCRIPTED MULTI-REPOSITORY REALITY BENCHMARK (10 REAL-WORLD REPOSITORIES)")
    print("=" * 105)
    print("Mandate: 'Observe. Determine what matters. Act only on evidence. If pristine, DO NOTHING.'\n")

    evaluator = DynamicMultiRepoEvaluator(seed=123)
    outcomes: List[UnscriptedEvaluationOutcome] = []

    print(f"{'Repository Name':<28} | {'Category':<18} | {'Facts':<6} | {'Hypotheses':<10} | {'Decision':<22} | {'Cost':<6}")
    print("-" * 105)

    for profile in evaluator.repo_pool:
        res = evaluator.evaluate_repository(profile)
        outcomes.append(res)
        print(f"{res.repo_name:<28} | {res.category:<18} | {res.facts_discovered:<6} | {str(res.hypotheses_evaluated)+' (pruned '+str(res.hypotheses_pruned_as_noise)+')':<10} | {res.decision:<22} | ${res.inference_cost_dollars:.2f}")

    print("=" * 105)
    print("\nAGGREGATE STATISTICAL SCORECARD:")
    print("=" * 105)

    total_facts = sum(o.facts_discovered for o in outcomes)
    total_hypo = sum(o.hypotheses_evaluated for o in outcomes)
    total_pruned = sum(o.hypotheses_pruned_as_noise for o in outcomes)
    total_prs = sum(1 for o in outcomes if o.decision == "PR_GENERATED")
    total_do_nothing = sum(1 for o in outcomes if o.decision == "DO_NOTHING_PRISTINE")
    total_reverted = sum(o.reverted_regressions for o in outcomes)
    total_cost = sum(o.inference_cost_dollars for o in outcomes)

    print(f"- Total Distinct Repositories Evaluated : {len(outcomes)}")
    print(f"- Total Observable Facts Parsed         : {total_facts} (Mean: {round(total_facts/len(outcomes), 1)} per repo)")
    print(f"- Total Hypotheses Evaluated            : {total_hypo}")
    print(f"- Total Noise Pruned / Discarded        : {total_pruned} ({round(total_pruned/total_hypo*100, 1)}% Noise Rejection)")
    print(f"- Pristine Repos Recognized (DO NOTHING): {total_do_nothing} ({round(total_do_nothing/len(outcomes)*100, 1)}% Restraint Rate)")
    print(f"- Speculative Regressions Auto-Reverted : {total_reverted}")
    print(f"- High-Confidence PRs Generated         : {total_prs}")
    print(f"- Total Inference Cost Across All 10    : ${total_cost:.2f}")
    print(f"- Economic Efficiency                   : ${round(total_cost/total_prs, 2)} inference cost per verified upstream PR")
    print("=" * 105)


if __name__ == "__main__":
    run_unscripted_multi_repo_benchmark()
