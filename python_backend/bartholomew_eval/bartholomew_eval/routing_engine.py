import time
from typing import Dict, Any, List, Optional

class EmpiricalRoutingEngine:
    """
    Bartholomew Empirical Routing Engine & Model Reliability Matrix.
    Tracks historical accuracy per (Model, Method, Task) triplet based on real-world outcomes.
    Routes requests asymmetrically: Primary -> Challenger (on low conf/conflict) -> Verifier.
    """

    def __init__(self):
        # Reliability matrix: key = "Model::Method::Task" -> {successes, attempts, rate}
        self.reliability_matrix: Dict[str, Dict[str, Any]] = {}
        # Pre-seed defaults
        self._seed_default_matrix()

    def _seed_default_matrix(self):
        defaults = [
            ("gpt-4o", "test_first", "code_generation", 47, 50),
            ("gpt-4o", "direct_impl", "code_generation", 32, 50),
            ("claude-3-5-sonnet", "ast_scrub", "security_analysis", 49, 50),
            ("gemini-1-5-pro", "chain_of_thought", "swarm_consensus", 45, 50),
        ]
        for model, method, task, succ, att in defaults:
            key = f"{model}::{method}::{task}"
            self.reliability_matrix[key] = {
                "model": model,
                "method": method,
                "task": task,
                "successes": succ,
                "attempts": att,
                "reliability_score": round(succ / att, 3)
            }

    def get_best_route(self, task: str, preferred_method: str = "test_first") -> Dict[str, Any]:
        """
        Determines the optimal model + method route for a given task based on historical evidence.
        """
        candidates = []
        for key, entry in self.reliability_matrix.items():
            if entry["task"] == task:
                candidates.append(entry)

        if not candidates:
            # Fallback default
            return {
                "primary_model": "gpt-4o",
                "recommended_method": preferred_method,
                "expected_reliability": 0.85,
                "strategy": "DEFAULT_FALLBACK"
            }

        best = max(candidates, key=lambda x: x["reliability_score"])
        return {
            "primary_model": best["model"],
            "recommended_method": best["method"],
            "expected_reliability": best["reliability_score"],
            "historical_attempts": best["attempts"],
            "strategy": "EMPIRICAL_OPTIMAL_PATH"
        }

    def record_outcome(self, model: str, method: str, task: str, success: bool):
        """
        Outcome-Based Reliability Updater:
        Updates empirical success rates based on real-world verification results.
        """
        key = f"{model}::{method}::{task}"
        if key not in self.reliability_matrix:
            self.reliability_matrix[key] = {
                "model": model,
                "method": method,
                "task": task,
                "successes": 0,
                "attempts": 0,
                "reliability_score": 0.0
            }

        entry = self.reliability_matrix[key]
        entry["attempts"] += 1
        if success:
            entry["successes"] += 1
        entry["reliability_score"] = round(entry["successes"] / entry["attempts"], 3)

    def route_request(
        self,
        task: str,
        risk_level: str = "LOW",
        primary_confidence: float = 0.9,
        has_contradiction: bool = False
    ) -> Dict[str, Any]:
        """
        Asymmetric Tiered Routing Decision:
        Determines if Challenger or Verifier model must be invoked.
        """
        route_info = self.get_best_route(task)
        primary_model = route_info["primary_model"]
        
        needs_challenger = False
        challenger_reason = None
        
        if primary_confidence < 0.75:
            needs_challenger = True
            challenger_reason = "Primary model confidence below 0.75 threshold"
        elif has_contradiction:
            needs_challenger = True
            challenger_reason = "Existing DERG evidence contradiction detected"
        elif risk_level in ["HIGH", "CRITICAL"]:
            needs_challenger = True
            challenger_reason = "High-risk action requires red-team challenger confirmation"

        return {
            "task": task,
            "primary_model": primary_model,
            "method": route_info["recommended_method"],
            "expected_reliability": route_info["expected_reliability"],
            "invoke_challenger": needs_challenger,
            "challenger_model": "claude-3-5-sonnet" if needs_challenger else None,
            "challenger_reason": challenger_reason,
            "verifier_required": True if (needs_challenger or risk_level != "LOW") else False
        }
