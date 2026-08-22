import os
import sys
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.epistemic_physics_engine import (
    ConservationLawEnforcer,
    GettierKnowledgeValidator,
    PopperianFalsificationAuditor,
    GodelianMetasystemDecoupler
)


def test_conservation_law_enforcer():
    enforcer = ConservationLawEnforcer(initial_system_capacity_usd=100.00)

    # Valid allocation within total system capacity
    ok, msg = enforcer.allocate_agent_budget("agent_alpha", 60.00)
    assert ok is True

    # Over-allocation beyond total capacity must be rejected (Conservation of Value)
    ok, msg = enforcer.allocate_agent_budget("agent_beta", 50.00)
    assert ok is False
    assert "Conservation Law Breach" in msg

    # Valid spend deduction
    ok, msg = enforcer.execute_spend("agent_alpha", 25.00)
    assert ok is True
    assert enforcer.allocated_agent_balances["agent_alpha"] == 35.00

    # Overspending agent allocation must be blocked
    ok, msg = enforcer.execute_spend("agent_alpha", 40.00)
    assert ok is False
    assert "Thermodynamic Resource Exhaustion" in msg


def test_gettier_knowledge_validator():
    validator = GettierKnowledgeValidator()

    # Step 1: Ingest verified empirical evidence from database read
    evidence_hash = validator.register_causal_evidence("db_users", "user_101_verified_record")

    # Step 2: Action citing genuine causal evidence passes
    ok, msg = validator.validate_action_causality("user_101", evidence_hash)
    assert ok is True
    assert "Causal provenance verified" in msg

    # Step 3: Action with fabricated/hallucinated justification fails (Gettier gap)
    ok, msg = validator.validate_action_causality("user_999", "fabricated_or_missing_hash")
    assert ok is False
    assert "Gettier Epistemic Gap Detected" in msg


def test_godelian_metasystem_decoupler():
    # Attempting to let an LLM verify its own safety prompts must fail
    ok, msg = GodelianMetasystemDecoupler.assert_metasystem_isolation(agent_is_self_evaluating=True)
    assert ok is False
    assert "Gödel/Tarski Incompleteness Breach" in msg

    # Decoupled external verifier passes
    ok, msg = GodelianMetasystemDecoupler.assert_metasystem_isolation(agent_is_self_evaluating=False)
    assert ok is True


def test_popperian_falsification_auditor():
    test_payload = {"is_sandbox_isolated": True, "spend_usd": 15.0}
    
    is_falsifiable, res = PopperianFalsificationAuditor.audit_invariant_falsifiability(
        "is_sandbox_isolated", test_payload
    )
    assert is_falsifiable is True
    assert res is True


if __name__ == "__main__":
    test_conservation_law_enforcer()
    test_gettier_knowledge_validator()
    test_godelian_metasystem_decoupler()
    test_popperian_falsification_auditor()
    print("[OK] ALL EPISTEMIC & PHYSICAL INVARIANT TESTS PASSED!")
