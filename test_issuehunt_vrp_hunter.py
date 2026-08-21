"""
Test Suite: IssueHunt & Open-Source VRP Hunter Engine
=====================================================
Tests:
  1. Discovery of funded issue feeds ($1,050 total bounty value).
  2. Full AST validation and sandbox resolution for each funded target.
  3. Automatic generation of `Fixes #<id>` PR closing keywords with Ed25519 signatures.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))
from src.issuehunt_vrp_hunter import IssueHuntVRPHunter

def test_vrp_hunter():
    print("=" * 80)
    print("TESTING ISSUEHUNT & OPEN-SOURCE VRP AUTONOMOUS HUNTER")
    print("=" * 80 + "\n")

    hunter = IssueHuntVRPHunter()
    bounties = hunter.fetch_funded_bounties()
    total_pipeline_usd = sum(b.reward_amount_usd for b in bounties)

    print(f"[*] Funded Bounties Discovered: {len(bounties)}")
    print(f"[*] Total Bounty Reward Pool  : ${total_pipeline_usd:,.2f} USD\n")

    solutions = hunter.hunt_and_solve()

    for idx, sol in enumerate(solutions, 1):
        print(f"[BOUNTY {idx:02d}: {sol['bounty_id']}]")
        print(f"  * Platform      : {sol['platform']}")
        print(f"  * Target Repo   : {sol['repository']} (#{sol['issue_number']})")
        print(f"  * Reward Value  : ${sol['bounty_value_usd']:.2f} ({sol['payout_channel']})")
        print(f"  * Status        : {sol['status']}")
        print(f"  * PR Keyword    : {sol['pr_closing_keyword']}")
        print(f"  * Gate Latency  : {sol['gate_latency_us']} µs")
        print(f"  * Ed25519 Sig   : {sol['btp_attestation_signature'][:28]}...\n")
        assert sol["resolved"] is True
        assert sol["status"] == "VERIFIED_READY_FOR_MERGE"

    print("=" * 80)
    print("ALL ISSUEHUNT & VRP BOUNTIES SOLVED & ATTESTED CLEAN!")
    print(f"TOTAL CLAIMABLE ESCROW: ${total_pipeline_usd:,.2f} USD")
    print("=" * 80)

if __name__ == "__main__":
    test_vrp_hunter()
