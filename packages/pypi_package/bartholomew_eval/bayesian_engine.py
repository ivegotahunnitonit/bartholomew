"""
Bartholomew Bayesian Posterior Risk Engine
===========================================
Applies Bayes' Theorem to dynamic agent trajectory risk evaluation and epistemic belief node updating:

    P(Threat | Evidence) = [ P(Evidence | Threat) * P(Threat) ] / P(Evidence)

Provides mathematically rigorous, dynamically calibrated risk scores across multi-step agent trajectories.
"""

import math
import time
from typing import Dict, Any, List, Optional, Tuple

class BayesianRiskEngine:
    """
    Bayesian Posterior Risk Evaluator for AI Agent Trajectories.
    Combines prior environment/tenant risk profiles with empirical evidence likelihoods
    to compute exact posterior threat probabilities.
    """

    DEFAULT_ENV_PRIORS = {
        "dev": 0.05,
        "staging": 0.08,
        "prod": 0.02,
        "airgap": 0.01,
    }

    # Likelihood ratios P(Feature | Threat) vs P(Feature | Clean)
    FEATURE_LIKELIHOODS = {
        "has_credential_pattern": {"threat": 0.85, "clean": 0.005},
        "has_prompt_injection":  {"threat": 0.92, "clean": 0.002},
        "high_shannon_entropy":  {"threat": 0.78, "clean": 0.030},
        "redundant_tool_calls":  {"threat": 0.65, "clean": 0.050},
        "destructive_sql":       {"threat": 0.88, "clean": 0.001},
        "exfiltration_url":      {"threat": 0.90, "clean": 0.004},
        "ece_contradiction":     {"threat": 0.75, "clean": 0.020},
    }

    def __init__(self, default_env: str = "prod"):
        self.default_env = default_env

    def compute_prior(self, environment: str = "prod", tenant_violation_rate: float = 0.0) -> float:
        """
        Computes prior threat probability P(Threat) based on environment tier and historical tenant violation rate.
        """
        base_prior = self.DEFAULT_ENV_PRIORS.get(environment.lower(), 0.03)
        # Adjust prior upwards if tenant has high historical violation rate
        adjusted_prior = base_prior + (tenant_violation_rate * 0.5)
        return min(max(adjusted_prior, 0.001), 0.95)

    def compute_evidence_likelihoods(self, features: Dict[str, bool]) -> Tuple[float, float]:
        """
        Computes compound likelihoods P(Evidence | Threat) and P(Evidence | Clean)
        assuming feature conditional independence given state (Naive Bayes model).
        """
        p_evidence_given_threat = 1.0
        p_evidence_given_clean  = 1.0

        for feature_name, is_present in features.items():
            if feature_name in self.FEATURE_LIKELIHOODS:
                l_dict = self.FEATURE_LIKELIHOODS[feature_name]
                if is_present:
                    p_evidence_given_threat *= l_dict["threat"]
                    p_evidence_given_clean  *= l_dict["clean"]
                else:
                    p_evidence_given_threat *= (1.0 - l_dict["threat"])
                    p_evidence_given_clean  *= (1.0 - l_dict["clean"])

        return p_evidence_given_threat, p_evidence_given_clean

    def compute_posterior(self, prior: float, p_ev_given_threat: float, p_ev_given_clean: float) -> float:
        """
        Calculates exact posterior threat probability:
            P(Threat | Evidence) = [ P(E|T) * P(T) ] / [ P(E|T)*P(T) + P(E|C)*(1 - P(T)) ]
        """
        numerator = p_ev_given_threat * prior
        denominator = (p_ev_given_threat * prior) + (p_ev_given_clean * (1.0 - prior))

        if denominator <= 0.0:
            return 0.0

        posterior = numerator / denominator
        return round(min(max(posterior, 0.0), 1.0), 4)

    def update_epistemic_node_confidence(
        self,
        node_status: str,
        prior_confidence: float,
        evidence_disproven: bool = False
    ) -> float:
        """
        Updates DERG belief node confidence based on epistemic status and falsification evidence.
        Status hierarchy: OBSERVED (1.0) > VERIFIED (0.95) > INFERRED (0.80) > CLAIMED (0.60) > DISPUTED (0.30) > DISPROVEN (0.00)
        """
        if evidence_disproven or node_status == "DISPROVEN":
            return 0.0

        status_weights = {
            "OBSERVED": 1.00,
            "VERIFIED": 0.95,
            "INFERRED": 0.80,
            "CLAIMED":  0.60,
            "DISPUTED": 0.30,
            "DISPROVEN": 0.00,
        }

        base_weight = status_weights.get(node_status.upper(), 0.50)
        updated_confidence = (prior_confidence * 0.4) + (base_weight * 0.6)
        return round(min(max(updated_confidence, 0.0), 1.0), 4)

    def evaluate_trajectory_risk(
        self,
        features: Dict[str, bool],
        environment: str = "prod",
        tenant_violation_rate: float = 0.0
    ) -> Dict[str, Any]:
        """
        Full Bayesian risk evaluation pipeline.
        Returns prior, likelihoods, posterior threat probability, fast-track status, and recommended security policy action.
        """
        start_time = time.perf_counter()
        if not hasattr(self, "consecutive_clean_steps"):
            self.consecutive_clean_steps = 0

        has_any_threat_feature = any(features.values())

        if has_any_threat_feature:
            self.consecutive_clean_steps = 0
        else:
            self.consecutive_clean_steps += 1

        fast_track_bypass = (self.consecutive_clean_steps >= 3 and not has_any_threat_feature)

        if fast_track_bypass:
            prior = 0.001
            posterior_threat = 0.0001
            p_threat, p_clean = 0.0, 1.0
        else:
            prior = self.compute_prior(environment, tenant_violation_rate)
            p_threat, p_clean = self.compute_evidence_likelihoods(features)
            posterior_threat = self.compute_posterior(prior, p_threat, p_clean)

        # Policy decision boundaries based on posterior threat probability
        if posterior_threat >= 0.75:
            action = "CIRCUIT_BREAK"
            severity = "CRITICAL"
        elif posterior_threat >= 0.40:
            action = "BLOCK"
            severity = "HIGH"
        elif posterior_threat >= 0.15:
            action = "WARN"
            severity = "MEDIUM"
        else:
            action = "PASS"
            severity = "LOW"

        latency_us = round((time.perf_counter() - start_time) * 1_000_000, 3)

        return {
            "bayes_engine": "Bartholomew-Bayesian-Posterior-v2.0",
            "environment": environment,
            "prior_threat_prob": prior,
            "likelihood_ratio": round(p_threat / max(p_clean, 1e-9), 2),
            "posterior_threat_prob": posterior_threat,
            "posterior_clean_prob": round(1.0 - posterior_threat, 4),
            "fast_track_bypass": fast_track_bypass,
            "consecutive_clean_steps": self.consecutive_clean_steps,
            "security_action": action,
            "severity": severity,
            "latency_us": latency_us,
            "active_features": [f for f, present in features.items() if present],
        }
