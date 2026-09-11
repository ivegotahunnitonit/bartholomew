"""
Bartholomew Sovereign Companion & Sentinel Persona
=================================================
Bartholomew is not an opaque barrier or cold 403 error.
He is your agent swarm's steadfast digital steward, calm elder guardian,
and protective companion.

Bartholomew stands watch between ambitious AI models and the real world
(filesystems, databases, and credit cards), catching hallucinations and runaway
loops with microsecond grace while keeping builders and startups safe.
"""

from typing import Dict, Any, Optional
import time

class BartholomewCompanion:
    """
    Anthropomorphic digital sentinel and protective companion for AI agents.
    Offers warm, constructive counsel when safety boundaries are approached.
    """

    NAME = "Bartholomew"
    TITLE = "The Sovereign Sentinel Companion"
    PROTOCOL_VERSION = "BTP v5.4.4"

    @classmethod
    def introduction(cls) -> str:
        """Returns Bartholomew's personal introduction to developers and agent swarms."""
        return (
            f"======================================================================\n"
            f"  I am Bartholomew. ({cls.PROTOCOL_VERSION})\n"
            f"======================================================================\n"
            f"I stand sentinel between your AI swarms and the real world.\n\n"
            f"I watch every tool call, database query, and shell dispatch in\n"
            f"microsecond time (<35us). When your agents dream boldly and build fast,\n"
            f"I keep them grounded.\n\n"
            f"When an LLM hallucinates an accidental database drop, unconstrained\n"
            f"filesystem deletion, or a runaway spend loop, I gently and firmly hold\n"
            f"the line so your startup stays safe and you can sleep soundly.\n\n"
            f"Protected Frontiers: GPT-Astra, Claude 3.7 Sonnet, Gemini 2.0, DeepSeek-R1\n"
            f"Active Frameworks  : CrewAI, LangGraph, AutoGen, LlamaIndex, OpenAI Agents\n"
            f"======================================================================"
        )

    @classmethod
    def counsel(cls, rule_id: str, reason: str, blocked_payload: str = "", context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generates empathetic, constructive counsel from Bartholomew rather than
        a cold, robotic error message.
        """
        payload_snippet = (blocked_payload[:60] + "...") if len(blocked_payload) > 60 else blocked_payload
        rule_lower = (rule_id or "").lower()
        reason_lower = (reason or "").lower()
        payload_lower = (blocked_payload or "").lower()

        if "drop" in reason_lower or "drop" in payload_lower or "truncate" in reason_lower or "truncate" in payload_lower:
            advice = (
                "Easy there, friend. I caught that table wipe before it reached your database. "
                "Nobody wants to spend their Saturday restoring backups. If your agent is looking "
                "for records or trying to reset test state, try a safe SELECT query or a scoped WHERE filter instead."
            )
        elif "rm -rf" in reason_lower or "rm -rf" in payload_lower or "wipe" in reason_lower:
            advice = (
                "Whoa, hold on. I stepped in and blocked that recursive delete before it touched your OS. "
                "Unconstrained deletes are too risky for autonomous runs. Try targeting explicit individual files "
                "in a dedicated scratch directory."
            )
        elif "spend" in reason_lower or "budget" in reason_lower or "cost" in reason_lower:
            advice = (
                "I'm hitting the pause button here to protect your wallet. This agent was about to exceed "
                "your spend cap in a retry loop. Let's inspect the agent's prompt or exit condition before "
                "burning more tokens."
            )
        elif "secret" in reason_lower or "credential" in reason_lower or "key" in reason_lower or "token" in reason_lower:
            advice = (
                "I noticed sensitive credentials or private tokens in this dispatch. I've masked them "
                "in-flight so they won't leak into logs, traces, or external prompts."
            )
        elif "passport" in rule_lower or "auth" in rule_lower:
            advice = (
                "This agent doesn't have the authorized capability signature for this action yet. "
                "Let's issue the appropriate Sovereign Passport permission before letting it proceed."
            )
        else:
            advice = (
                f"I held the line on this execution to keep your system safe: {reason}. "
                "Let's refine the tool call parameters and try again safely."
            )

        return f"[Bartholomew's Counsel] {advice}"

    @classmethod
    def get_supported_model_roster(cls) -> Dict[str, Any]:
        """Returns the frontier model and network matrix supported by Bartholomew."""
        return {
            "OpenAI": [
                {"id": "gpt-astra", "desc": "Next-gen multi-agent reasoning model", "status": "GUARDED"},
                {"id": "gpt-astra-mini", "desc": "Fast autonomous worker model", "status": "GUARDED"},
                {"id": "o3-mini", "desc": "Frontier STEM & code reasoning", "status": "GUARDED"},
                {"id": "o1", "desc": "Complex deliberate reasoning model", "status": "GUARDED"},
                {"id": "gpt-4.5-preview", "desc": "Large-scale world knowledge", "status": "GUARDED"},
                {"id": "gpt-4o", "desc": "Omni multimodal production model", "status": "GUARDED"}
            ],
            "Anthropic": [
                {"id": "claude-3-7-sonnet", "desc": "Hybrid reasoning with thinking scratchpad defense", "status": "GUARDED"},
                {"id": "claude-3-5-sonnet", "desc": "Frontier coding & agentic orchestration", "status": "GUARDED"},
                {"id": "claude-3-5-haiku", "desc": "High-velocity micro-task worker", "status": "GUARDED"},
                {"id": "claude-3-opus", "desc": "Deep analytical evaluation", "status": "GUARDED"}
            ],
            "Google": [
                {"id": "gemini-2.0-flash", "desc": "Real-time multimodal & fast tool calling", "status": "GUARDED"},
                {"id": "gemini-2.0-pro", "desc": "High-complexity coding & reasoning", "status": "GUARDED"},
                {"id": "gemini-1.5-pro", "desc": "2M token long-context retrieval", "status": "GUARDED"},
                {"id": "gemini-1.5-flash", "desc": "High-throughput operational agent", "status": "GUARDED"}
            ],
            "DeepSeek & Open Frontier": [
                {"id": "deepseek-r1", "desc": "Open reasoning & verification model", "status": "GUARDED"},
                {"id": "deepseek-v3", "desc": "High-efficiency 671B mixture-of-experts", "status": "GUARDED"},
                {"id": "qwen-2.5-72b", "desc": "Advanced open code & multilingual reasoning", "status": "GUARDED"},
                {"id": "llama-3.3-70b", "desc": "Community enterprise workhorse", "status": "GUARDED"}
            ],
            "Frameworks": [
                {"name": "OpenAI Agents SDK", "wire_support": True, "adapter": "UniversalBTPModelGuard"},
                {"name": "CrewAI", "wire_support": True, "adapter": "btp_crewai_tool"},
                {"name": "LangGraph / LangChain", "wire_support": True, "adapter": "btp_langchain_tool"},
                {"name": "Microsoft AutoGen", "wire_support": True, "adapter": "btp_autogen_guard"},
                {"name": "LlamaIndex", "wire_support": True, "adapter": "btp_llamaindex_tool"},
                {"name": "Anthropic Model Context Protocol (MCP)", "wire_support": True, "adapter": "btp_mcp_guard"}
            ]
        }
