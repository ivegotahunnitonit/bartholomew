import time
from typing import Dict, Any, List, Optional

class ResourceGovernor:
    """
    Bartholomew Resource Governor & Economic Stopping Function.
    Allocates budgets (tokens, compute, time, risk), calculates Expected Value of Next Action (EV_next),
    builds Adaptive Context Packets (HOT/WARM/COLD), and enforces economic stopping boundaries.
    """

    def __init__(
        self,
        token_budget: int = 10000,
        time_budget_sec: float = 30.0,
        max_tool_calls: int = 10,
        min_ev_threshold: float = 0.15
    ):
        self.max_tokens = token_budget
        self.max_time_sec = time_budget_sec
        self.max_tool_calls = max_tool_calls
        self.min_ev_threshold = min_ev_threshold
        
        self.tokens_used = 0
        self.start_time = time.time()
        self.tool_calls_used = 0
        self.mode = "EXPLOIT"  # "EXPLOIT" or "EXPLORE"

    def check_budget(self) -> Dict[str, Any]:
        """Checks remaining budget limits."""
        elapsed_sec = time.time() - self.start_time
        tokens_remaining = max(0, self.max_tokens - self.tokens_used)
        time_remaining = max(0.0, self.max_time_sec - elapsed_sec)
        tool_calls_remaining = max(0, self.max_tool_calls - self.tool_calls_used)

        is_exhausted = (
            tokens_remaining <= 0 or
            time_remaining <= 0.0 or
            tool_calls_remaining <= 0
        )

        return {
            "tokens_used": self.tokens_used,
            "tokens_remaining": tokens_remaining,
            "time_elapsed_sec": round(elapsed_sec, 2),
            "time_remaining_sec": round(time_remaining, 2),
            "tool_calls_used": self.tool_calls_used,
            "tool_calls_remaining": tool_calls_remaining,
            "is_exhausted": is_exhausted,
            "mode": self.mode
        }

    def consume_resources(self, tokens: int = 0, tool_calls: int = 0):
        """Deducts resource usage from budget."""
        self.tokens_used += tokens
        self.tool_calls_used += tool_calls

    def evaluate_stopping_function(
        self,
        expected_information_gain: float,  # EIG: 0.0 to 1.0
        decision_impact: float,            # Impact: 0.0 to 1.0
        estimated_action_cost_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Economic Stopping Function:
        EV_next = (EIG * Impact) / Cost_Factor
        If EV_next < min_ev_threshold OR Budget Exhausted -> STOP.
        """
        budget_status = self.check_budget()
        if budget_status["is_exhausted"]:
            return {
                "should_continue": False,
                "reason": "RESOURCE_BUDGET_EXHAUSTED",
                "ev_next": 0.0,
                "budget": budget_status
            }

        # Normalize cost factor relative to token budget
        cost_factor = max(0.1, estimated_action_cost_tokens / 1000.0)
        ev_next = (expected_information_gain * decision_impact) / cost_factor

        should_continue = ev_next >= self.min_ev_threshold

        return {
            "should_continue": should_continue,
            "reason": "EV_ABOVE_THRESHOLD" if should_continue else "EV_BELOW_ECONOMIC_THRESHOLD",
            "ev_next": round(ev_next, 4),
            "eig": round(expected_information_gain, 3),
            "impact": round(decision_impact, 3),
            "min_threshold": self.min_ev_threshold,
            "budget": budget_status
        }

    def build_adaptive_context_packet(
        self,
        decision_type: str,  # "OPERATIONAL", "INVESTIGATIVE", "PREDICTIVE"
        hot_memory: List[Dict[str, Any]],
        warm_memory: List[Dict[str, Any]],
        cold_memory: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Builds the minimum required evidence payload per decision type.
        Reduces token footprint by filtering irrelevant historical memories.
        """
        if decision_type == "OPERATIONAL":
            # Minimum context: Recent HOT constraints & active state
            selected = hot_memory[:3]
            tier = "HOT_MINIMAL"
        elif decision_type == "INVESTIGATIVE":
            # Context: Prior failure vectors & disputed evidence
            selected = hot_memory[:2] + [m for m in warm_memory if m.get("outcome") == "FAILED_ATTEMPT"][:3]
            tier = "WARM_FAILURES_AND_DISPUTES"
        elif decision_type == "PREDICTIVE":
            # Context: Historical outcomes & model reliability
            selected = warm_memory[:2] + cold_memory[:3]
            tier = "COLD_HISTORICAL_OUTCOMES"
        else:
            selected = hot_memory[:2]
            tier = "DEFAULT_MINIMAL"

        estimated_packet_tokens = sum(len(str(m)) for m in selected) // 4

        return {
            "decision_type": decision_type,
            "context_tier": tier,
            "selected_items_count": len(selected),
            "estimated_packet_tokens": estimated_packet_tokens,
            "packet_items": selected
        }
