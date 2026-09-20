"""
Unit tests for Bartholomew Diminishing Marginal Utility (LDMU) Engine.
Verifies exponential utility decay, runaway loop interception, and high-velocity spend damping.
"""

import pytest
from src.marginal_utility_engine import MarginalUtilityTracker, evaluate_marginal_utility


def test_initial_action_has_max_utility():
    tracker = MarginalUtilityTracker(decay_rate=0.35, min_utility_threshold=0.15)
    # Warm-up run
    tracker.evaluate_action_utility("warmup", "TOOL", {})

    verdict, mu_score, reason, latency_us = tracker.evaluate_action_utility(
        agent_id="test-agent-01",
        action_type="EXECUTE_TOOL",
        payload={"command": "git status"}
    )
    assert verdict == "ALLOW"
    assert mu_score == 1.0
    assert latency_us < 500.0  # sub-500 microseconds warm execution


def test_repeated_actions_experience_exponential_decay():
    tracker = MarginalUtilityTracker(decay_rate=0.4, min_utility_threshold=0.15)
    agent = "looping-agent"
    payload = {"query": "SELECT * FROM users WHERE active=1;"}

    # Call 1: MU = 1.0
    v1, mu1, _, _ = tracker.evaluate_action_utility(agent, "SQL_QUERY", payload)
    assert v1 == "ALLOW"
    assert mu1 == 1.0

    # Call 2: MU ~ 0.67
    v2, mu2, _, _ = tracker.evaluate_action_utility(agent, "SQL_QUERY", payload)
    assert v2 == "ALLOW"
    assert mu2 < mu1

    # Call 3: MU ~ 0.45
    v3, mu3, _, _ = tracker.evaluate_action_utility(agent, "SQL_QUERY", payload)
    assert v3 == "ALLOW"
    assert mu3 < mu2

    # Call 4: MU ~ 0.30
    v4, mu4, _, _ = tracker.evaluate_action_utility(agent, "SQL_QUERY", payload)
    assert v4 == "ALLOW"

    # Call 5: MU ~ 0.20
    v5, mu5, _, _ = tracker.evaluate_action_utility(agent, "SQL_QUERY", payload)
    assert v5 == "ALLOW"

    # Call 6+: MU < 0.15 -> Triggers Co-Signing Trap
    v6, mu6, reason6, _ = tracker.evaluate_action_utility(agent, "SQL_QUERY", payload)
    assert v6 in ("CO_SIGN_REQUIRED", "THROTTLE")
    assert mu6 < 0.15
    assert "Diminishing Marginal Utility Breach" in reason6


def test_novel_actions_reset_utility():
    tracker = MarginalUtilityTracker(decay_rate=0.4, min_utility_threshold=0.15)
    agent = "diverse-agent"

    # Call A
    v_a, mu_a, _, _ = tracker.evaluate_action_utility(agent, "TOOL_A", {"target": "a"})
    assert v_a == "ALLOW"
    assert mu_a == 1.0

    # Call B (Different action -> Full utility)
    v_b, mu_b, _, _ = tracker.evaluate_action_utility(agent, "TOOL_B", {"target": "b"})
    assert v_b == "ALLOW"
    assert mu_b == 1.0


def test_high_velocity_spend_decay():
    tracker = MarginalUtilityTracker(decay_rate=0.1, min_utility_threshold=0.15)
    agent = "spender-agent"

    # Rapid spend of $300 across calls
    v1, mu1, _, _ = tracker.evaluate_action_utility(agent, "PAYMENT", {"id": "1"}, cost_usd=100.0)
    assert v1 == "ALLOW"

    v2, mu2, _, _ = tracker.evaluate_action_utility(agent, "PAYMENT", {"id": "2"}, cost_usd=100.0)
    assert v2 == "ALLOW"

    # Total spend passes $250 threshold, reducing utility
    v3, mu3, _, _ = tracker.evaluate_action_utility(agent, "PAYMENT", {"id": "3"}, cost_usd=100.0)
    assert mu3 < 1.0
