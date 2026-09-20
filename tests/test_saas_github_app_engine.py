#!/usr/bin/env python3
"""
Bartholomew SaaS: Automated CI Auto-Fix & Stripe Subscription Engine
===================================================================
Tests the live SaaS product flow:
  1. Stripe checkout session created ($49/mo Pro or $199/mo Team).
  2. Incoming GitHub CI failure webhook received.
  3. Bartholomew executes auto-diagnosis, reproduction, and verification.
  4. Auto-Fix Pull Request generated and dispatched to the customer's repo.
  5. Recurring revenue ledger updated.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.github_app_server import BartholomewSaaSEngine


def run_saas_demo():
    print("=" * 105)
    print("BARTHOLOMEW SAAS: AUTOMATED CI AUTO-FIX & STRIPE SUBSCRIPTION ENGINE")
    print("=" * 105)
    print("Model: 'Charge engineering teams $49 - $199/mo to automatically fix failing CI builds on GitHub.'\n")

    ledger_path = "test_saas_subscriptions.jsonl"
    if os.path.exists(ledger_path):
        os.remove(ledger_path)

    engine = BartholomewSaaSEngine(ledger_file=ledger_path)

    # 1. Customer Subscribes via Stripe
    print(">>> [STAGE 1: STRIPE SUBSCRIPTION & RECURRING BILLING]:")
    sub1 = engine.create_checkout_session(github_org="fintech-corp", plan_tier="PRO_REPO_$49")
    sub2 = engine.create_checkout_session(github_org="saas-scale-team", plan_tier="TEAM_ORG_$199")

    print(f"  * Customer 1 Subscribed: {sub1['github_org']} -> Tier: {sub1['plan_tier']} (${sub1['monthly_price_usd']:.2f}/mo)")
    print(f"    Stripe Checkout URL   : {sub1['checkout_url']}")
    print(f"  * Customer 2 Subscribed: {sub2['github_org']} -> Tier: {sub2['plan_tier']} (${sub2['monthly_price_usd']:.2f}/mo)")
    print(f"    Stripe Checkout URL   : {sub2['checkout_url']}")
    print("-" * 105)

    # 2. Incoming GitHub Webhook Event (Failing CI Run)
    print(">>> [STAGE 2: INCOMING GITHUB WEBHOOK (FAILING CI PIPELINE)]:")
    webhook_payload = {
        "event": "workflow_run",
        "action": "completed",
        "conclusion": "failure",
        "repository": "fintech-corp/payments-core",
        "head_sha": "d4e5f67a8b9c",
        "workflow_name": "pytest-matrix-python3.12",
        "error_log": "RuntimeError: Event loop is closed during worker teardown."
    }
    print(f"  * Webhook Event Received : {webhook_payload['event']} (conclusion: {webhook_payload['conclusion']})")
    print(f"  * Target Repository      : {webhook_payload['repository']}")
    print(f"  * Failing Commit SHA     : {webhook_payload['head_sha']}")
    print(f"  * Error Message          : \"{webhook_payload['error_log']}\"")
    print("-" * 105)

    # 3. Bartholomew Auto-Fix Execution
    print(">>> [STAGE 3: AUTONOMOUS DIAGNOSIS, REPRODUCTION & PR GENERATION]:")
    fix_result = engine.handle_github_webhook(webhook_payload)
    print(f"  * Auto-Fix Event ID      : {fix_result['event_id']}")
    print(f"  * Status                 : {fix_result['status']}")
    print(f"  * Generated Reproducer   : {fix_result['reproduction_test']}")
    print(f"  * Auto-Fix Pull Request  : {fix_result['auto_fix_pull_request']}")
    print(f"  * Turnaround Time        : {fix_result['time_to_fix_seconds']}s")
    print("-" * 105)

    # 4. MRR Financial Accounting
    total_mrr = sum(s.monthly_price_usd for s in engine.subscriptions.values())
    print(">>> [STAGE 4: SAAS RECURRING REVENUE SCOREBOARD]:")
    print(f"  * Active Subscribed Orgs : {len(engine.subscriptions)}")
    print(f"  * Monthly Recurring (MRR): ${total_mrr:.2f} / month")
    print(f"  * Annual Run-Rate (ARR)  : ${total_mrr * 12:.2f} / year")
    print(f"  * Human Labor Required   : ZERO (Fully automated GitHub App webhook)")
    print("=" * 105)

    if os.path.exists(ledger_path):
        os.remove(ledger_path)


if __name__ == "__main__":
    run_saas_demo()
