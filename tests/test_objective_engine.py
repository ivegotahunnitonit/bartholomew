import pytest
from bartholomew_eval.objective_engine import (
    ObjectiveContext,
    ActionCandidate,
    ObjectiveEngine,
    create_sample_objective_evaluation
)


def test_objective_engine_candidate_filtering():
    context = ObjectiveContext(
        objective_id="obj_test_01",
        goal_statement="Test candidate evaluation",
        max_budget=100.0
    )
    engine = ObjectiveEngine(context)

    valid_action = ActionCandidate(
        action_id="act_valid",
        description="Safe valid action",
        expected_value=100.0,
        expected_cost=10.0,
        risk_score=0.10,
        constraints_satisfied=True
    )

    invalid_action = ActionCandidate(
        action_id="act_invalid",
        description="Violates constraint",
        expected_value=500.0,
        expected_cost=10.0,
        risk_score=0.90,
        constraints_satisfied=False
    )

    res = engine.evaluate_next_action([valid_action, invalid_action])
    assert res["decision"] == "EXECUTE_NEXT_BEST_ACTION"
    assert res["selected_action"]["action_id"] == "act_valid"


def test_closed_loop_outcome_recording():
    engine, evaluation = create_sample_objective_evaluation()

    assert evaluation["decision"] == "EXECUTE_NEXT_BEST_ACTION"
    assert len(engine.outcome_history) == 1
    assert engine.outcome_history[0]["success"] is True
    assert engine.current_state["completed_steps"] == 1
