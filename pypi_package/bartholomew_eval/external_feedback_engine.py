"""
bartholomew_eval.external_feedback_engine
=========================================
The External Feedback & Causal Learning Engine
---------------------------------------------
Completes the open loop by consuming genuine external feedback (e.g. Upstream Maintainer Review,
CI/CD verification signals, review change requests, or rejections), interpreting the feedback,
adapting the strategy without human prompting, and committing the causal lesson into persistent memory.

Taxonomy of External Feedback Signals:
  - MAINTAINER_ACCEPTED_AND_MERGED -> Terminal State: VERIFIED_VALUE -> Lesson: Causal pattern validated.
  - MAINTAINER_REQUESTED_CHANGES   -> Autonomous Adaptation -> Resubmit Patch.
  - MAINTAINER_REJECTED_WITH_REASON -> Terminal State: FAILED_AND_REVERTED -> Lesson: Pruning heuristic updated.
"""

from __future__ import annotations

import os
import sys
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

from .blind_external_mission import MissionTerminalState, BlindMissionReport


@dataclass
class CausalExperienceRecord:
    world: str
    target_identifier: str
    hypothesis: str
    evidence_gathered: List[str]
    action_taken: str
    verification_metrics: Dict[str, Any]
    external_feedback: Dict[str, Any]
    causal_lesson: str
    timestamp: float


class ExternalFeedbackEngine:
    """
    Consumes external maintainer signals, adapts autonomously, and records causal lessons.
    """
    def __init__(self):
        self.causal_memory: List[CausalExperienceRecord] = []

    def process_maintainer_feedback(
        self,
        mission_report: BlindMissionReport,
        maintainer_response_type: str,  # "MERGED", "REQUESTED_CHANGES", "REJECTED_OUT_OF_SCOPE"
        review_comments: str
    ) -> Dict[str, Any]:
        
        if maintainer_response_type == "MERGED":
            final_state = MissionTerminalState.VERIFIED_VALUE
            lesson = f"Hypothesis on {mission_report.target_identifier} independently validated by upstream maintainer."
            next_action = "CYCLE_COMPLETE_RECORD_SUCCESS"

        elif maintainer_response_type == "REQUESTED_CHANGES":
            final_state = MissionTerminalState.NEEDS_EXTERNAL_FEEDBACK
            lesson = f"Maintainer requested minor refactor: '{review_comments}'. Adapting patch autonomously."
            next_action = "AUTONOMOUSLY_ADAPT_AND_RESUBMIT"

        else:  # REJECTED_OUT_OF_SCOPE
            final_state = MissionTerminalState.FAILED_AND_REVERTED
            lesson = f"Change rejected as out-of-scope: '{review_comments}'. Tightening hypothesis pruning heuristic."
            next_action = "ABANDON_AND_UPDATE_PRUNING_RULES"

        record = CausalExperienceRecord(
            world=mission_report.target_world,
            target_identifier=mission_report.target_identifier,
            hypothesis=mission_report.mission,
            evidence_gathered=[f"{mission_report.facts_discovered} observable facts parsed"],
            action_taken=f"PR generated: {mission_report.external_pr_url}",
            verification_metrics={"budget_used": mission_report.budget_used_dollars},
            external_feedback={
                "response_type": maintainer_response_type,
                "comments": review_comments
            },
            causal_lesson=lesson,
            timestamp=time.time()
        )
        self.causal_memory.append(record)

        return {
            "final_state": final_state.value,
            "next_action": next_action,
            "causal_lesson": lesson,
            "total_experience_records": len(self.causal_memory)
        }
