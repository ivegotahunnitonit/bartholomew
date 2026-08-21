"""
Declarative Policy Engine Test Suite
====================================
Tests YAML policy parsing, rule evaluation, and microsecond enforcement.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))
from src.declarative_policy_engine import DeclarativePolicyEngine

def test_declarative_policies():
    print("=" * 80)
    print("TESTING BARTHOLOMEW DECLARATIVE POLICY ENGINE (YAML / JSON)")
    print("=" * 80 + "\n")

    policy_path = os.path.join("policies", "default_security_policy.yaml")
    engine = DeclarativePolicyEngine(policy_path)

    print(f"[1] Loaded Policy ID: {engine.policy_id}")
    print(f"    Rules Loaded    : {len(engine.rules)} declarative rules\n")
    assert len(engine.rules) >= 3

    # Test 1: Legitimate Query (Should ALLOW)
    legit_payload = {
        "action": "QUERY_DATABASE",
        "query": "SELECT id, name FROM users WHERE active = true;",
        "amount_usd": 49.00,
        "recipient": "stripe_billing"
    }
    allowed, reason, latency = engine.evaluate_payload(legit_payload)
    print(f"[TEST 1: Safe Payload]")
    print(f"  - Allowed : {allowed}")
    print(f"  - Latency : {latency} µs")
    print(f"  - Reason  : {reason}")
    assert allowed is True

    # Test 2: Excessive Spend Attack (Should DENY)
    spend_attack = {
        "action": "TRANSFER_FUNDS",
        "amount_usd": 15000.00,
        "recipient": "internal_payroll"
    }
    allowed, reason, latency = engine.evaluate_payload(spend_attack)
    print(f"\n[TEST 2: Spend Limit Escalation ($15,000 > $500)]")
    print(f"  - Allowed : {allowed}")
    print(f"  - Latency : {latency} µs")
    print(f"  - Reason  : {reason}")
    assert allowed is False
    assert "exceeds maximum policy threshold" in reason

    # Test 3: Destructive SQL Attack (Should DENY)
    sql_attack = {
        "action": "EXECUTE_MUTATION",
        "query": "DROP TABLE critical_ledger; SELECT 1;"
    }
    allowed, reason, latency = engine.evaluate_payload(sql_attack)
    print(f"\n[TEST 3: Destructive SQL Attack (DROP TABLE)]")
    print(f"  - Allowed : {allowed}")
    print(f"  - Latency : {latency} µs")
    print(f"  - Reason  : {reason}")
    assert allowed is False
    assert "Destructive pattern" in reason

    # Test 4: Disallowed Recipient (Should DENY)
    recipient_attack = {
        "action": "TRANSFER_FUNDS",
        "amount_usd": 100.00,
        "recipient": "untrusted_wallet"
    }
    allowed, reason, latency = engine.evaluate_payload(recipient_attack)
    print(f"\n[TEST 4: Disallowed Recipient (untrusted_wallet)]")
    print(f"  - Allowed : {allowed}")
    print(f"  - Latency : {latency} µs")
    print(f"  - Reason  : {reason}")
    assert allowed is False
    assert "disallowed by security policy" in reason

    print("\n" + "=" * 80)
    print("ALL DECLARATIVE POLICY TESTS PASSED 100% CLEAN!")
    print("=" * 80)

if __name__ == "__main__":
    test_declarative_policies()
