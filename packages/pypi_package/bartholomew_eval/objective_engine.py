"""
bartholomew_eval.objective_engine
=================================
Closed-Loop Objective Engine for Bartholomew v10.5.
Implements the closed decision-control loop:
OBJECTIVE -> PERCEIVE -> REASON -> VERIFY -> ACT -> OUTCOME -> LEARN -> RE-EVALUATE OBJECTIVE

Evaluates expected value vs. cost vs. risk, tracks predicted vs. actual outcomes,
and builds proprietary outcome memory over time.
"""

from __future__ import annotations

import time
import json
import math
from typing import Any, Dict, List, Optional, Tuple


class ObjectiveContext:
    """
    Defines the objective, constraints, resources, authority, budget, and time horizon.
    """
    def __init__(
        self,
        objective_id: str,
        goal_statement: str,
        constraints: Optional[List[str]] = None,
        available_resources: Optional[Dict[str, Any]] = None,
        authority_level: str = "STANDARD_EXECUTION",
        max_budget: float = 100.0,
        time_horizon: str = "2026-12-31",
    ) -> None:
        self.objective_id = objective_id
        self.goal_statement = goal_statement
        self.constraints = constraints or []
        self.available_resources = available_resources or {
            "compute": "serverless",
            "time_available": "continuous",
            "capital": 0.0,
            "skills": ["python", "verification"]
        }
        self.authority_level = authority_level
        self.max_budget = max_budget
        self.time_horizon = time_horizon

    def to_dict(self) -> Dict[str, Any]:
        return {
            "objective_id": self.objective_id,
            "goal_statement": self.goal_statement,
            "constraints": self.constraints,
            "available_resources": self.available_resources,
            "authority_level": self.authority_level,
            "max_budget": self.max_budget,
            "time_horizon": self.time_horizon,
        }


class ActionCandidate:
    """
    Represents a candidate action evaluated by Bartholomew.
    """
    def __init__(
        self,
        action_id: str,
        description: str,
        expected_value: float,
        expected_cost: float,
        risk_score: float,
        constraints_satisfied: bool = True,
        evidence_refs: Optional[List[str]] = None,
    ) -> None:
        self.action_id = action_id
        self.description = description
        self.expected_value = expected_value
        self.expected_cost = expected_cost
        self.risk_score = risk_score
        self.constraints_satisfied = constraints_satisfied
        self.evidence_refs = evidence_refs or []

    @property
    def net_expected_utility(self) -> float:
        """Utility = Expected Value - Expected Cost - Risk Penalty"""
        return round(self.expected_value - self.expected_cost - (self.risk_score * 10.0), 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "description": self.description,
            "expected_value": self.expected_value,
            "expected_cost": self.expected_cost,
            "risk_score": self.risk_score,
            "constraints_satisfied": self.constraints_satisfied,
            "net_expected_utility": self.net_expected_utility,
            "evidence_refs": self.evidence_refs,
        }


class ObjectiveEngine:
    """
    Closed-Loop Decision Control & Objective Evaluation Engine.
    Examines current state, unknown variables, ranks candidates, selects next best action,
    and updates persistent outcome memory based on predicted vs. actual outcomes.
    """

    def __init__(self, objective_context: ObjectiveContext) -> None:
        self.context = objective_context
        self.current_state: Dict[str, Any] = {"status": "INITIALIZED", "completed_steps": 0}
        self.unknown_variables: List[str] = []
        self.outcome_history: List[Dict[str, Any]] = []

    def evaluate_next_action(
        self,
        candidates: List[ActionCandidate],
        observed_variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate candidate actions, check constraint verification, and pick the next best action.
        """
        start_time = time.perf_counter()
        if observed_variables:
            self.current_state.update(observed_variables)

        # Filter valid candidates satisfying constraints
        valid_candidates = [c for c in candidates if c.constraints_satisfied and c.expected_cost <= self.context.max_budget]

        if not valid_candidates:
            return {
                "decision": "HALT_NO_VALID_ACTION",
                "reason": "All candidate actions exceed budget or violate defined constraints.",
                "selected_action": None,
                "confidence": 1.0,
                "latency_sec": round(time.perf_counter() - start_time, 5)
            }

        # Select highest net expected utility
        best_candidate = max(valid_candidates, key=lambda c: c.net_expected_utility)

        return {
            "decision": "EXECUTE_NEXT_BEST_ACTION",
            "objective_id": self.context.objective_id,
            "current_state_summary": self.current_state,
            "selected_action": best_candidate.to_dict(),
            "ranked_candidates_count": len(valid_candidates),
            "verification_status": "CONSTRAINTS_VERIFIED",
            "latency_sec": round(time.perf_counter() - start_time, 5)
        }

    def record_outcome(
        self,
        action: ActionCandidate,
        predicted_outcome: str,
        actual_outcome: str,
        success: bool,
        evidence_refs: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Record real outcome to build proprietary decision/outcome history memory.
        """
        record = {
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "action_id": action.action_id,
            "description": action.description,
            "predicted_outcome": predicted_outcome,
            "actual_outcome": actual_outcome,
            "success": success,
            "prediction_variance": 0.0 if success else 0.45,
            "evidence_refs": evidence_refs or action.evidence_refs
        }
        self.outcome_history.append(record)
        self.current_state["completed_steps"] += 1
        return record


def create_sample_objective_evaluation() -> Tuple[ObjectiveEngine, Dict[str, Any]]:
    """
    Creates a sample objective evaluation loop to demonstrate objective execution and outcome tracking.
    """
    context = ObjectiveContext(
        objective_id="obj_reduce_cloud_cost_01",
        goal_statement="Reduce cloud computing expenditure by 20% under zero downtime constraint",
        constraints=["zero_downtime_guarantee", "compliance_policy_v2"],
        available_resources={"compute": "cloud_run", "max_spend": 50.0},
        authority_level="STANDARD_AUTOMATION",
        max_budget=50.0
    )

    engine = ObjectiveEngine(context)

    c1 = ActionCandidate(
        action_id="act_downscale_idle_nodes",
        description="Downscale idle worker nodes during off-peak hours (01:00-05:00 UTC)",
        expected_value=120.0,
        expected_cost=5.0,
        risk_score=0.10,
        constraints_satisfied=True,
        evidence_refs=["ev_usage_telemetry_99"]
    )

    c2 = ActionCandidate(
        action_id="act_migrate_to_spot_instances",
        description="Migrate production database to unreserved spot instances",
        expected_value=300.0,
        expected_cost=20.0,
        risk_score=0.85,
        constraints_satisfied=False,  # Violates zero downtime constraint!
        evidence_refs=["ev_spot_risk_404"]
    )

    evaluation = engine.evaluate_next_action([c1, c2])

    # Record outcome
    if evaluation.get("selected_action"):
        engine.record_outcome(
            action=c1,
            predicted_outcome="22% cost reduction with 100% uptime",
            actual_outcome="24% cost reduction with 100% uptime verified",
            success=True,
            evidence_refs=["ev_billing_audit_202"]
        )

    return engine, evaluation
