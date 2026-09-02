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

from src import (
    Guard,
    wrap_client,
    BartholomewTrustAuthority,
    IndependentTrustVerifier,
    DeclarativePolicyEngine,
    MarginalUtilityTracker,
    secure_tool,
    SecurityVetoException,
    guard
)
from src.ast_validator import ASTSecurityValidator
from src.hermetic_sandbox import HermeticCommandSandbox, HermeticFileSandbox
from src.polyglot_ast_validator import PolyglotASTValidator
from src.secret_masker import SecretVaultMasker
from src.snapshot_engine import WorkspaceSnapshotEngine
from src.mcp_gateway import MCPProxyGateway
from src.a2a_protocol import AgentToAgentProtocol
from src.cloud_identity import CloudKMSProvider, LocalEd25519Provider, OIDCPolicyEvaluator

__version__ = "2.3.0"
__all__ = [
    "Guard",
    "wrap_client",
    "secure_tool",
    "SecurityVetoException",
    "guard",
    "BartholomewTrustAuthority",
    "IndependentTrustVerifier",
    "ASTSecurityValidator",
    "PolyglotASTValidator",
    "SecretVaultMasker",
    "WorkspaceSnapshotEngine",
    "MCPProxyGateway",
    "AgentToAgentProtocol",
    "CloudKMSProvider",
    "LocalEd25519Provider",
    "OIDCPolicyEvaluator",
    "HermeticCommandSandbox",
    "HermeticFileSandbox",
    "DeclarativePolicyEngine",
    "MarginalUtilityTracker"
]
