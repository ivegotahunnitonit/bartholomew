"""
Unit tests for Bartholomew Autonomous Policy Synthesizer.
"""

import pytest
from src.policy_synthesizer import PolicySynthesizer


def test_policy_synthesis_from_traces():
    synthesizer = PolicySynthesizer(policy_id="urn:btp:policy:test-agent")

    # Ingest baseline traces
    synthesizer.observe_execution_trace({
        "action_type": "STRIPE_CHARGE",
        "payload": {"amount_usd": 45.00, "recipient": "stripe_api"}
    })
    synthesizer.observe_execution_trace({
        "action_type": "STRIPE_CHARGE",
        "payload": {"amount_usd": 120.00, "recipient": "stripe_api"}
    })
    synthesizer.observe_execution_trace({
        "action_type": "READ_FILE",
        "payload": {"path": "src/app.py"}
    })

    policy = synthesizer.synthesize_policy_dict()
    assert policy["policy_id"] == "urn:btp:policy:test-agent"
    
    # Cap should be 120.00 * 1.25 = 150.00
    spend_rule = [r for r in policy["rules"] if r["id"] == "AUTO_RULE_SPEND_CAP"][0]
    assert spend_rule["value"] == 150.00

    yaml_str = synthesizer.synthesize_yaml()
    assert "AUTO_RULE_SPEND_CAP" in yaml_str
    assert "150.00" in yaml_str
    assert "AUTO_RULE_DIMINISHING_MARGINAL_UTILITY" in yaml_str
