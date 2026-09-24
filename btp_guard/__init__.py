"""
Bartholomew Trust Protocol (BTP v5.4.19) - Agentic Runtime Protection (ARP)
=============================================================================
High-performance execution guardrails, AST validation, and cryptographic audit receipts
for autonomous AI agents (LangChain, CrewAI, AutoGen, Claude Code, Cursor, Windsurf).

Usage:
    from btp_guard import Guard, secure_tool

    # 1-line function decorator:
    @secure_tool
    def execute_query(sql: str):
        ...

    # Direct safety gate:
    guard = Guard(spend_cap=50.0)
    verdict = guard.check("rm -rf /")
    if not verdict["allowed"]:
        print("Blocked:", verdict["reason"])
"""

import sys
import os

# Ensure repo root and src are accessible
_pkg_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.dirname(_pkg_dir)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

# Core imports
from src.agent_protector import protect_agent
from src import (
    Guard,
    wrap_client,
    BartholomewTrustAuthority,
    IndependentTrustVerifier,
    DeclarativePolicyEngine,
    MarginalUtilityTracker,
    secure_tool,
    SecurityVetoException,
    SecurityVetoException as BTPViolationError,
    guard
)
from src.polyglot_ast_validator import PolyglotASTValidator
from src.ast_validator import ASTSecurityValidator
from src.secret_masker import SecretVaultMasker
from src.usage_tracker import load_license, save_license, record_evaluation, STRIPE_PRO_URL, STRIPE_ENTERPRISE_URL
from src.btp_guard.authorization_gate import AuthorizationGate
from src.btp_guard.ledger import BillableLedger
from src.btp_guard.policy import Policy
from src.btp_guard.stripe_bridge import StripeMeterBridge
from src.btp_guard.telemetry import TelemetryEmitter
from src.btp_guard.btp_guard import WireGuard
import btp_guard.integrations as integrations

__version__ = "5.4.20"

__all__ = [
    "Guard",
    "protect_agent",
    "secure_tool",
    "SecurityVetoException",
    "BTPViolationError",
    "wrap_client",
    "guard",
    "BartholomewTrustAuthority",
    "IndependentTrustVerifier",
    "DeclarativePolicyEngine",
    "MarginalUtilityTracker",
    "PolyglotASTValidator",
    "ASTSecurityValidator",
    "SecretVaultMasker",
    "load_license",
    "save_license",
    "record_evaluation",
    "STRIPE_PRO_URL",
    "STRIPE_ENTERPRISE_URL",
    "AuthorizationGate",
    "BillableLedger",
    "Policy",
    "StripeMeterBridge",
    "TelemetryEmitter",
    "WireGuard",
    "integrations",
    "__version__",
]
