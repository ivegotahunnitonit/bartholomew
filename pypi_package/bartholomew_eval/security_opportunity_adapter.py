"""
bartholomew_eval.security_opportunity_adapter
=============================================
Security Opportunity Acquisition Adapter (Authorized Programs & Scopes)
-----------------------------------------------------------------------
Fetches and structures live authorized security bug bounty & VRP programs:
  - In-scope assets & repositories
  - Maximum advertised reward ranges ($)
  - Explicit rules of engagement (e.g. no DoS, no credential dumping)
  - Required proof-of-concept / reproduction evidence standards
  - Deadlines & active submission windows
"""

from __future__ import annotations

import os
import sys
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class AuthorizedSecurityProgram:
    program_id: str
    organization_name: str
    program_name: str
    policy_url: str
    in_scope_repositories: List[str]
    max_bounty_usd: float
    min_bounty_usd: float
    rules_of_engagement: List[str]
    required_evidence_format: str  # e.g., "deterministic_reproduction_test_fixture"
    is_active: bool = True


class SecurityOpportunityAdapter:
    """
    Acquires and normalizes live authorized security research opportunities.
    Acts as the primary ingestion feed for the Economic Capital Allocator.
    """
    def __init__(self, authorized_programs_catalog: Optional[List[AuthorizedSecurityProgram]] = None):
        self.catalog = authorized_programs_catalog or self._load_default_authorized_programs()

    def _load_default_authorized_programs(self) -> List[AuthorizedSecurityProgram]:
        return [
            AuthorizedSecurityProgram(
                program_id="PROG_GOOGLE_OSS_VRP",
                organization_name="Google",
                program_name="Google Open Source Vulnerability Reward Program (OSS VRP)",
                policy_url="https://bughunters.google.com/about/rules/6621980829155328",
                in_scope_repositories=[
                    "google/protobuf",
                    "google/tink",
                    "google/gvisor",
                    "grpc/grpc"
                ],
                max_bounty_usd=10000.0,
                min_bounty_usd=500.0,
                rules_of_engagement=[
                    "no_denial_of_service",
                    "no_social_engineering",
                    "must_provide_deterministic_test_reproducer"
                ],
                required_evidence_format="deterministic_reproduction_test_fixture",
                is_active=True
            ),
            AuthorizedSecurityProgram(
                program_id="PROG_GITHUB_SECURITY_LAB",
                organization_name="GitHub",
                program_name="GitHub Security Lab Bug Bounty",
                policy_url="https://securitylab.github.com/bounties/",
                in_scope_repositories=[
                    "pallets/flask",
                    "urllib3/urllib3",
                    "psf/requests"
                ],
                max_bounty_usd=5000.0,
                min_bounty_usd=300.0,
                rules_of_engagement=[
                    "coordinated_vulnerability_disclosure",
                    "reproducible_exploit_or_unit_test"
                ],
                required_evidence_format="pytest_reproduction_harness",
                is_active=True
            )
        ]

    def discover_in_scope_targets(self) -> List[Dict[str, Any]]:
        """Enumerates active, compliant targets across all authorized programs."""
        targets = []
        for prog in self.catalog:
            if prog.is_active:
                for repo in prog.in_scope_repositories:
                    targets.append({
                        "program_id": prog.program_id,
                        "organization": prog.organization_name,
                        "repository": repo,
                        "reward_range_usd": (prog.min_bounty_usd, prog.max_bounty_usd),
                        "evidence_requirement": prog.required_evidence_format,
                        "rules": prog.rules_of_engagement
                    })
        return targets
