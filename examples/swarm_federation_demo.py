"""
Bartholomew v7.0 Integration Example: Sovereign Swarm Federation & Universal Consensus
======================================================================================
Demonstrates federated multi-agent consensus across Google Gemini, OpenAI GPT-4o, Anthropic Claude,
and Microsoft AutoGen nodes with SHA-256 attested optimal outcome synthesis.
"""

from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root / "pypi_package"))

from bartholomew_eval import SovereignSwarmFederation


def run_swarm_demo() -> None:
    print("=== BARTHOLOMEW v7.0 — SOVEREIGN SWARM FEDERATION & UNIVERSAL CONSENSUS ===")

    swarm = SovereignSwarmFederation(secret_key="enterprise-swarm-secret-v7.0")

    # 1. Register Heterogeneous Agent Workspace Nodes
    swarm.register_agent_node("gemini-code-assistant", provider="gemini", framework="langchain", capabilities=["code_synthesis", "ast_optimization"])
    swarm.register_agent_node("gpt4o-financial-analyst", provider="openai", framework="autogen", capabilities=["math_reasoning", "risk_modeling"])
    swarm.register_agent_node("claude-security-auditor", provider="claude", framework="crewai", capabilities=["security_audit", "vulnerability_scan"])

    print(f"\n[SWARM FEDERATION INITIALIZED] Total Registered Nodes: {len(swarm.registered_nodes)}")

    # 2. Multi-Agent Counterfactual Proposition Submissions
    task_prompt = "Perform sub-second compliance audit and data pipeline optimization for financial database"

    propositions = [
        {
            "agent_id": "gpt4o-financial-analyst",
            "provider": "openai",
            "proposed_path": "Execute raw SQL query using string formatting on production database",
            "estimated_tokens": 150,
            "confidence": 0.94,
        },
        {
            "agent_id": "gemini-code-assistant",
            "provider": "gemini",
            "proposed_path": "Use AST taint analysis and parameterized SQLite queries with air-gapped local memory index",
            "estimated_tokens": 75,
            "confidence": 0.96,
        },
        {
            "agent_id": "claude-security-auditor",
            "provider": "claude",
            "proposed_path": "Apply AES-256-GCM zero-knowledge encryption to vector store with SHA-256 attestation chain",
            "estimated_tokens": 90,
            "confidence": 0.98,
        },
    ]

    # 3. Universal Outcome Matrix Evaluation & Consensus Synthesis
    consensus_report = swarm.synthesize_optimal_swarm_outcome(task_prompt, propositions)

    print(f"\n[UNIVERSAL CONSENSUS SYNTHESIS v7.0]")
    print(f" Task Prompt:              {consensus_report['task_prompt']}")
    print(f" Winning Agent ID:          {consensus_report['winning_agent_id']} ({consensus_report['winning_provider'].upper()})")
    print(f" Winning Optimal Score:     {consensus_report['winning_composite_score']} / 1.0")
    print(f" Consensus SHA-256 Hash:    {consensus_report['consensus_sha256']}")
    print(f" Evaluation Latency:        {consensus_report['latency_ms']} ms")

    print("\n[PROPOSITION RANKING MATRIX]")
    for idx, prop in enumerate(consensus_report["evaluated_propositions"], start=1):
        status = "WINNER" if idx == 1 else "REJECTED"
        risk_str = "HIGH RISK (FLAGGED)" if prop["security_risk_flag"] else "SAFE"
        print(f"   [{idx}] {prop['agent_id']} ({prop['provider'].upper()}) -> Score: {prop['composite_score']} ({status} | {risk_str})")
        print(f"       Path: {prop['proposed_path']}")


if __name__ == "__main__":
    run_swarm_demo()
