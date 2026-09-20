import math
import time
from typing import Dict, Any, List, Optional

class InternalEngineCalculator:
    """
    Bartholomew Proprietary Internal Engine Calculator.
    Owned outright under Bartholomew IP specification.
    
    Calculates exact epistemic and resource metrics:
    - Epistemic Calibration Error (ECE)
    - Expected Goal Efficiency Score (xG)
    - Token Compression & Savings Ratio
    - Latency Compression Factor (microseconds)
    - System Reliability Calibration Index
    """

    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def calculate_calibration_error(self, predictions: List[float], outcomes: List[int]) -> float:
        """
        Calculates Epistemic Calibration Error (ECE):
        ECE = (1/N) * sum(|confidence_i - actual_outcome_i|)
        """
        if not predictions or len(predictions) != len(outcomes):
            return 0.0

        n = len(predictions)
        total_error = sum(abs(p - o) for p, o in zip(predictions, outcomes))
        return round(total_error / n, 4)

    def calculate_xg_efficiency(
        self,
        expected_information_gain: float,
        success_rate: float,
        cost_tokens: int,
        latency_ms: float
    ) -> float:
        """
        Calculates Expected Goal Efficiency (xG Score):
        xG = (EIG * SuccessRate * 1000) / (CostTokens + (LatencyMS * 2.0))
        """
        if cost_tokens <= 0 and latency_ms <= 0:
            return 100.0

        cost_factor = (cost_tokens * 1.0) + (latency_ms * 2.0)
        if cost_factor <= 0:
            cost_factor = 1.0

        raw_xg = (expected_information_gain * success_rate * 1000.0) / cost_factor
        return round(raw_xg, 4)

    def calculate_resource_compression(
        self,
        unoptimized_tokens: int,
        actual_tokens: int,
        unoptimized_latency_ms: float,
        actual_latency_ms: float
    ) -> Dict[str, Any]:
        """
        Calculates exact token reduction % and latency compression factor.
        """
        token_savings_pct = 0.0
        if unoptimized_tokens > 0:
            token_savings_pct = round(((unoptimized_tokens - actual_tokens) / unoptimized_tokens) * 100.0, 2)

        latency_compression_factor = 1.0
        if actual_latency_ms > 0:
            latency_compression_factor = round(unoptimized_latency_ms / actual_latency_ms, 2)

        return {
            "token_savings_pct": token_savings_pct,
            "tokens_saved": max(0, unoptimized_tokens - actual_tokens),
            "latency_compression_factor": f"{latency_compression_factor}x",
            "latency_saved_ms": round(max(0.0, unoptimized_latency_ms - actual_latency_ms), 2)
        }

    def evaluate_system_assessment(
        self,
        predictions: List[float],
        outcomes: List[int],
        unoptimized_tokens: int = 5000,
        actual_tokens: int = 420,
        unoptimized_latency_ms: float = 1200.0,
        actual_latency_ms: float = 0.0076
    ) -> Dict[str, Any]:
        """
        Generates full proprietary system assessment report.
        """
        ece = self.calculate_calibration_error(predictions, outcomes)
        
        # Mean success rate and EIG
        avg_pred = sum(predictions) / len(predictions) if predictions else 0.5
        avg_outcome = sum(outcomes) / len(outcomes) if outcomes else 0.5
        
        xg = self.calculate_xg_efficiency(
            expected_information_gain=avg_pred,
            success_rate=avg_outcome,
            cost_tokens=actual_tokens,
            latency_ms=actual_latency_ms
        )

        compression = self.calculate_resource_compression(
            unoptimized_tokens=unoptimized_tokens,
            actual_tokens=actual_tokens,
            unoptimized_latency_ms=unoptimized_latency_ms,
            actual_latency_ms=actual_latency_ms
        )

        assessment = {
            "timestamp": time.time(),
            "epistemic_calibration_error": ece,
            "calibration_grade": "OPTIMAL" if ece < 0.1 else ("ACCEPTABLE" if ece < 0.2 else "POOR"),
            "xg_efficiency_score": xg,
            "token_compression": compression,
            "ownership_status": "OWNED_OUTRIGHT_PROPRIETARY_IP"
        }
        self.history.append(assessment)
        return assessment
