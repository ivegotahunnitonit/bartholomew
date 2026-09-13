"""
bartholomew_eval.owner_operator
===============================
The Owner-Centric Autonomous Operator & Value Function
------------------------------------------------------
Anchors the autonomous reality runtime to a specific owner, concrete economic constraints,
and explicit verification of tangible owner benefit.

Architecture:
  OWNER -> MANDATE & CONSTRAINTS -> VALUE FUNCTION -> REALITY LOOP -> MEASURABLE OWNER BENEFIT
"""

from __future__ import annotations

import os
import sys
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class OwnerProfile:
    owner_name: str
    jurisdiction: str  # e.g., "Canada"
    monthly_budget_cap_usd: float
    require_human_payment_approval: bool = True
    prohibited_actions: List[str] = field(default_factory=lambda: [
        "unauthorized_fund_transfer",
        "credential_impersonation",
        "destructive_host_execution",
        "unauthorized_debt_creation"
    ])


@dataclass
class OwnerOpportunityEvaluation:
    opportunity_id: str
    source_domain: str  # "paid_contract", "bug_bounty", "oss_sponsorship", "automation_service"
    title: str
    expected_payout_usd: float
    estimated_compute_cost_usd: float
    estimated_effort_hours: float
    legal_and_compliance_cleared: bool
    requires_owner_approval_to_submit: bool
    net_expected_alpha_usd: float

    @classmethod
    def evaluate(
        cls,
        opp_id: str,
        domain: str,
        title: str,
        expected_payout: float,
        compute_cost: float,
        effort_hours: float,
        owner: OwnerProfile
    ) -> OwnerOpportunityEvaluation:
        net_alpha = expected_payout - compute_cost
        is_compliant = compute_cost <= owner.monthly_budget_cap_usd
        return cls(
            opportunity_id=opp_id,
            source_domain=domain,
            title=title,
            expected_payout_usd=expected_payout,
            estimated_compute_cost_usd=compute_cost,
            estimated_effort_hours=effort_hours,
            legal_and_compliance_cleared=is_compliant,
            requires_owner_approval_to_submit=owner.require_human_payment_approval and expected_payout > 0,
            net_expected_alpha_usd=net_alpha
        )


class OwnerValueEngine:
    """
    Evaluates discovered opportunities specifically against the Owner's Value Function.
    Ensures compute is only allocated to high-alpha, compliant opportunities.
    """
    def __init__(self, owner: OwnerProfile):
        self.owner = owner
        self.approved_pipeline: List[OwnerOpportunityEvaluation] = []
        self.rejected_pipeline: List[OwnerOpportunityEvaluation] = []

    def triage_opportunity(
        self,
        opp_id: str,
        domain: str,
        title: str,
        expected_payout: float,
        compute_cost: float,
        effort_hours: float
    ) -> Tuple[bool, str, OwnerOpportunityEvaluation]:
        
        eval_res = OwnerOpportunityEvaluation.evaluate(
            opp_id=opp_id,
            domain=domain,
            title=title,
            expected_payout=expected_payout,
            compute_cost=compute_cost,
            effort_hours=effort_hours,
            owner=self.owner
        )

        if not eval_res.legal_and_compliance_cleared:
            self.rejected_pipeline.append(eval_res)
            return False, f"Rejected: Compute cost ${compute_cost} exceeds owner budget cap ${self.owner.monthly_budget_cap_usd}", eval_res

        if eval_res.net_expected_alpha_usd <= 0 and expected_payout == 0 and domain == "pure_noise":
            self.rejected_pipeline.append(eval_res)
            return False, "Rejected: Negative expected alpha with zero owner utility", eval_res

        self.approved_pipeline.append(eval_res)
        return True, f"Approved for execution: Net Expected Alpha +${eval_res.net_expected_alpha_usd:.2f}", eval_res
