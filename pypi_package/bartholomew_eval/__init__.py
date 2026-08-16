"""
bartholomew_eval
================
Bartholomew Core v7.0 — Sub-Millisecond Security Guard, Sovereign Local Memory,
Asynchronous Dreaming Engine & Universal Swarm Federation for AI Agents.
"""

from .guard import guard, GuardViolation
from .engine import BartholomewEngine
from .fuzzer import TrajectoryFuzzer, fuzzer_instance
from .cli import main
from .transformer import BartholomewTransformerEngine
from .threat_hunter import AIThreatHunter
from .self_healing import SelfHealingEngine
from .vulnerability_scanner import BartholomewVulnerabilityScanner
from .threat_discovery import AutonomousThreatDiscoverer
from .xg_optimizer import ContextAndXGOptimizer
from .sovereign_memory import SovereignLocalMemory
from .memory_curator import InBandOutBandCurator
from .async_dreamer import AsynchronousDreamingEngine
from .attestation_verifier import AttestationVerifier
from .crypto_engine import BartholomewCryptoEngine
from .pipeline_engine import AsyncTrajectoryPipeline
from .agent_scouter import AutonomousAgentScouter
from .swarm_federation import SovereignSwarmFederation

from .agent_credential import AgentCredential
from .evidence_artifact import BartholomewEvidence
from .verifier import BartholomewVerifier
from .guard_proxy import BartholomewGuard
from .environment import BartholomewEnvironment
from .experience_store import EpistemicExperienceStore
from .cache_engine import DeterministicDecisionCache
from .epistemic_provenance import EpistemicProvenanceNode, ContradictionEngine
from .routing_engine import EmpiricalRoutingEngine
from .resource_governor import ResourceGovernor
from .internal_engine_calculator import InternalEngineCalculator
from .algorithm_synthesizer import AlgorithmSynthesizer
from .epistemic_execution_engine import EpistemicExecutionEngine
from .linux_adapter import LinuxExecutionAdapter, LinuxExecutionViolation
from .linux_master import LinuxMasterEngine, LinuxSecurityViolation

__version__ = "9.1.0"
__author__ = "Itsub Solomon Alemayehu"
__all__ = [
    "LinuxExecutionAdapter",
    "LinuxExecutionViolation",
    "LinuxMasterEngine",
    "LinuxSecurityViolation",
    "guard",
    "GuardViolation",
    "BartholomewEngine",
    "BartholomewTransformerEngine",
    "AIThreatHunter",
    "SelfHealingEngine",
    "BartholomewVulnerabilityScanner",
    "AutonomousThreatDiscoverer",
    "ContextAndXGOptimizer",
    "SovereignLocalMemory",
    "InBandOutBandCurator",
    "AsynchronousDreamingEngine",
    "AttestationVerifier",
    "BartholomewCryptoEngine",
    "AsyncTrajectoryPipeline",
    "AutonomousAgentScouter",
    "SovereignSwarmFederation",
    "AgentCredential",
    "BartholomewEvidence",
    "BartholomewVerifier",
    "BartholomewGuard",
    "BartholomewEnvironment",
    "EpistemicExperienceStore",
    "DeterministicDecisionCache",
    "EpistemicProvenanceNode",
    "ContradictionEngine",
    "EmpiricalRoutingEngine",
    "ResourceGovernor",
    "InternalEngineCalculator",
    "AlgorithmSynthesizer",
    "EpistemicExecutionEngine",
    "TrajectoryFuzzer",
    "fuzzer_instance",
    "main",
]
