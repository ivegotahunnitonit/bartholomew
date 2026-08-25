"""
Bartholomew (btp_guard) Drop-In SDK
====================================
Sub-millisecond cryptographic invariant and safety guardrail engine for autonomous AI agents.

Usage:
  from btp_guard import Guard, wrap_client
  guard = Guard(spend_cap=100.0, max_retries=5)
  result = guard.check("rm -rf /var/data")
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import Guard, wrap_client, BartholomewTrustAuthority, IndependentTrustVerifier
from src.ast_validator import ASTSecurityValidator
from src.hermetic_sandbox import HermeticCommandSandbox, HermeticFileSandbox
from src.declarative_policy_engine import DeclarativePolicyEngine
from src.marginal_utility_engine import MarginalUtilityTracker

__version__ = "2.2.0"
__all__ = [
    "Guard",
    "wrap_client",
    "BartholomewTrustAuthority",
    "IndependentTrustVerifier",
    "ASTSecurityValidator",
    "HermeticCommandSandbox",
    "HermeticFileSandbox",
    "DeclarativePolicyEngine",
    "MarginalUtilityTracker"
]
