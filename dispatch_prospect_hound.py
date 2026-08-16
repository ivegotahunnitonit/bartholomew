#!/usr/bin/env python3
"""
Opportunity Hound: Real Demand Ingestion & Ready-to-Send Proposal Generator
==========================================================================
Scans live channels for concrete pain signatures:
  - Discovers real technical problems (failing CI, flaky pytest suites, patch rewards)
  - Diagnoses technical root cause
  - Calculates market pricing
  - Generates ready-to-copy proposals for human approval & dispatch
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.opportunity_hound import OpportunityHoundEngine


def run_hound():
    print("=" * 105)
    print("BARTHOLOMEW: OPPORTUNITY HOUND (COMMERCIAL DEMAND & PROPOSAL GENERATOR)")
    print("=" * 105)
    print("Mandate: 'Find people with broken code, qualify them, and generate high-conversion proposals for the owner.'\n")

    ledger_path = "qualified_prospects_ledger.jsonl"
    if os.path.exists(ledger_path):
        os.remove(ledger_path)

    hound = OpportunityHoundEngine(ledger_file=ledger_path)
    prospects = hound.qualify_and_generate_proposals()

    for idx, p in enumerate(prospects, 1):
        print(f"[{idx}] {p.prospect_id} | Channel: {p.channel_source:<18} | Quote: ${p.market_price_quote_usd:>6.2f} | Win Prob: {p.probability_of_winning*100:.0f}%")
        print(f"    - Prospect Client   : {p.poster_identity}")
        print(f"    - Public Listing URL: {p.post_url}")
        print(f"    - Stated Pain       : \"{p.raw_problem_statement}\"")
        print(f"    - Diagnosed Root    : {p.technical_root_cause_hypothesis}")
        print(f"    - Ready Proposal    :\n---\n{p.personalized_proposal_pitch}\n---")
        print()

    total_pipeline_value = sum(p.market_price_quote_usd for p in prospects)
    expected_yield = sum(p.market_price_quote_usd * p.probability_of_winning for p in prospects)

    print("=" * 105)
    print("QUALIFIED DEMAND PIPELINE SUMMARY:")
    print("=" * 105)
    print(f"- Total Qualified Prospects Ready for Dispatch : {len(prospects)}")
    print(f"- Total Gross Pipeline Value                   : ${total_pipeline_value:.2f}")
    print(f"- Expected Probability-Weighted Owner Yield     : ${expected_yield:.2f}")
    print(f"- Human Authorization Status                   : REQUIRED BEFORE SENDING (100% Owner Controlled)")
    print(f"- Persistent Prospect Ledger                   : {hound.ledger_file}")
    print("=" * 105)


if __name__ == "__main__":
    run_hound()
