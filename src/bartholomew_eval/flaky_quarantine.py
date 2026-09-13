# Bartholomew Autonomous Flaky Test Quarantine & Auto-Fix Engine
# Detects non-deterministic test suites, statistical variance, and applies automated isolation.

import math
import time
from typing import Dict, List, Any, Optional

class FlakyTestQuarantineEngine:
    """
    Automated statistical flaky test detection & quarantine governor.
    Evaluates failure distributions across N runs to isolate non-deterministic tests.
    """

    def __init__(self, runs_threshold: int = 10, significance_alpha: float = 0.05):
        self.runs_threshold = runs_threshold
        self.significance_alpha = significance_alpha
        self.quarantined_tests: Dict[str, Dict[str, Any]] = {}

    def analyze_test_run_history(self, test_name: str, execution_results: List[bool]) -> Dict[str, Any]:
        """
        Calculates pass/fail variance. If passes > 0 and failures > 0 across repeated runs,
        categorizes test as FLAKY and recommends AST quarantine.
        """
        n = len(execution_results)
        if n < 2:
            return {"test": test_name, "status": "INSUFFICIENT_DATA", "flaky": False}

        passes = sum(1 for r in execution_results if r is True)
        failures = n - passes
        failure_rate = failures / n

        # A deterministic test has failure_rate = 0.0 or 1.0. A flaky test has 0 < failure_rate < 1.0.
        is_flaky = (passes > 0 and failures > 0)
        
        # Calculate standard deviation
        p = failure_rate
        variance = p * (1 - p)
        std_dev = math.sqrt(variance)

        result = {
            "test": test_name,
            "total_runs": n,
            "passes": passes,
            "failures": failures,
            "failure_rate": round(failure_rate, 4),
            "std_dev": round(std_dev, 4),
            "flaky": is_flaky,
            "recommended_action": "QUARANTINE_AND_REPAIR" if is_flaky else ("PASS" if failure_rate == 0 else "CONSISTENT_FAILURE")
        }

        if is_flaky:
            self.quarantined_tests[test_name] = {
                "isolated_at": time.time(),
                "metrics": result,
                "quarantine_decorator": f"@pytest.mark.quarantine(reason='Flaky failure rate: {round(failure_rate*100, 1)}%')"
            }

        return result

    def generate_quarantine_patch(self, test_file_content: str, test_name: str) -> str:
        """
        Applies non-destructive AST quarantine decorator to prevent breaking main CI pipeline.
        """
        decorator = "@pytest.mark.quarantine\n"
        target_def = f"def {test_name}"
        if target_def in test_file_content:
            return test_file_content.replace(target_def, f"{decorator}{target_def}")
        return test_file_content

    def get_quarantined_report(self) -> Dict[str, Any]:
        return {
            "total_quarantined": len(self.quarantined_tests),
            "quarantined_suite": self.quarantined_tests
        }
