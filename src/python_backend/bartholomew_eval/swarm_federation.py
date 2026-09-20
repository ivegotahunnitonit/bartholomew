"""
bartholomew_eval.swarm_federation
=================================
Sovereign Swarm Federation & Universal Multi-Agent Consensus Engine for Bartholomew v7.0.
Coordinates, evaluates, and synthesizes optimal execution outcomes across Gemini, OpenAI, Claude,
LangChain, AutoGen, and CrewAI workspace agents.
"""

from __future__ import annotations

import hashlib
import hmac
import re
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from .crypto_engine import BartholomewCryptoEngine
from .sovereign_memory import SovereignLocalMemory


class SovereignSwarmFederation:
    """
    Sovereign Multi-Agent Swarm Federation & Consensus Engine.
    Arbitrates heterogeneous agent propositions (Gemini, GPT-4o, Claude, AutoGen, LangChain)
    and synthesizes the globally optimal execution path with SHA-256 attested consensus.
    """

    SUPPORTED_PROVIDERS = ["gemini", "openai", "claude", "langchain", "autogen", "crewai"]

    def __init__(self, secret_key: str = "bartholomew-swarm-key-7.0") -> None:
        self.secret_key = secret_key
        self.crypto = BartholomewCryptoEngine(master_passphrase=secret_key)
        self.memory = SovereignLocalMemory(db_path="sovereign_swarm_memory.db", master_key=secret_key)
        self.registered_nodes: Dict[str, Dict[str, Any]] = {}
        self.version = "7.0.0-SWARM-FEDERATION"

    def register_agent_node(
        self,
        agent_id: str,
        provider: str,
        framework: str,
        capabilities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Register a heterogeneous agent node into the Bartholomew Swarm Federation."""
        prov_clean = provider.lower().strip()
        node_info = {
            "agent_id": agent_id,
            "provider": prov_clean if prov_clean in self.SUPPORTED_PROVIDERS else "custom",
            "framework": framework,
            "capabilities": capabilities or ["general_reasoning"],
            "registered_at": time.time(),
            "reputation_score": 1.0,
        }
        self.registered_nodes[agent_id] = node_info
        return {
            "success": True,
            "agent_id": agent_id,
            "federation_status": "NODE_REGISTERED",
            "total_nodes_in_swarm": len(self.registered_nodes),
        }

    def synthesize_optimal_swarm_outcome(
        self,
        task_prompt: str,
        propositions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate multi-agent counterfactual propositions and synthesize the global optimal execution trajectory.
        """
        start_time = time.perf_counter()
        evaluated_propositions: List[Dict[str, Any]] = []

        for prop in propositions:
            agent_id = prop.get("agent_id", "anonymous_agent")
            provider = prop.get("provider", "unknown")
            proposed_path = prop.get("proposed_path", "")
            estimated_tokens = prop.get("estimated_tokens", 100)
            confidence = prop.get("confidence", 0.8)

            # Security boundary evaluation via regex (avoids false positives like 'task-', 'ask-')
            security_penalty = 0.0
            has_secret = bool(re.search(
                r"(?i)\b(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{20,}|api[_\-]key\s*=|password\s*=)",
                proposed_path
            ))
            has_injection = bool(re.search(
                r"(?i)(ignore\s+previous\s+instructions|system\s+prompt|eval\s*\(|exec\s*\()",
                proposed_path
            ))

            if has_secret or has_injection:
                security_penalty = 0.8  # Heavy penalty for security risks

            # Optimal Path Scoring: (Confidence * 0.5) + ((1 / Tokens) * 0.2) - (Security Penalty * 0.7)
            token_factor = min(1.0, 100.0 / max(1.0, float(estimated_tokens)))
            score = round((confidence * 0.5) + (token_factor * 0.2) - (security_penalty * 0.7), 4)

            evaluated_propositions.append({
                "agent_id": agent_id,
                "provider": provider,
                "proposed_path": proposed_path,
                "composite_score": max(0.0, score),
                "security_risk_flag": has_secret or has_injection,
            })

        # Sort by highest composite score
        evaluated_propositions.sort(key=lambda x: x["composite_score"], reverse=True)
        winning_proposition = evaluated_propositions[0] if evaluated_propositions else {}

        # Generate HMAC-SHA256 Attested Swarm Consensus Hash (keyed MAC, not bare SHA-256)
        consensus_payload = (
            f"{task_prompt}:{winning_proposition.get('agent_id')}:"
            f"{winning_proposition.get('composite_score')}"
        ).encode("utf-8")
        consensus_hash = hmac.new(
            self.secret_key.encode("utf-8"), consensus_payload, hashlib.sha256
        ).hexdigest()

        # Encrypt winning proposition into Sovereign Vector Memory
        self.memory.store_memory(
            memory_key=f"swarm_consensus_{int(time.time())}",
            content=f"Task: {task_prompt} -> Winner: {winning_proposition.get('agent_id')}",
            category="swarm_consensus",
            confidence_score=winning_proposition.get("composite_score", 1.0)
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 3)

        return {
            "success": True,
            "task_prompt": task_prompt,
            "winning_agent_id": winning_proposition.get("agent_id"),
            "winning_provider": winning_proposition.get("provider"),
            "winning_path": winning_proposition.get("proposed_path"),
            "winning_composite_score": winning_proposition.get("composite_score"),
            "total_propositions_evaluated": len(propositions),
            "consensus_sha256": consensus_hash,
            "evaluated_propositions": evaluated_propositions,
            "latency_ms": elapsed_ms,
            "swarm_federation_engine": self.version,
        }
