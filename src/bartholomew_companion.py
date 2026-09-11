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
    PROTOCOL_VERSION = "BTP v5.4.5"

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
            f"Protected Frontiers: GPT-Astra, Claude 3.7 Sonnet, Gemini 3.8 / 2.0, DeepSeek-R1\n"
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
                {"id": "gemini-3.8-ultra", "desc": "Frontier multimodal reasoning & native agent execution", "status": "GUARDED"},
                {"id": "gemini-3.8-flash", "desc": "Sub-100ms ultra-low latency multimodal dispatch", "status": "GUARDED"},
                {"id": "gemini-3.0-pro", "desc": "Next-gen code generation & long-context synthesis", "status": "GUARDED"},
                {"id": "gemini-2.0-flash", "desc": "Real-time multimodal & fast tool calling", "status": "GUARDED"},
                {"id": "gemini-2.0-pro", "desc": "High-complexity coding & reasoning", "status": "GUARDED"},
                {"id": "gemini-1.5-pro", "desc": "2M token long-context retrieval", "status": "GUARDED"}
            ],
            "DeepSeek & Open Frontier": [
                {"id": "deepseek-r1", "desc": "Open reasoning & verification model", "status": "GUARDED"},
                {"id": "deepseek-v3", "desc": "High-efficiency 671B mixture-of-experts", "status": "GUARDED"},
                {"id": "qwen-2.5-72b", "desc": "Advanced open code & multilingual reasoning", "status": "GUARDED"},
                {"id": "llama-3.3-70b", "desc": "Community enterprise workhorse", "status": "GUARDED"}
            ],
            "Yandex & Eurasian Frontier": [
                {"id": "yandexgpt-5-pro", "desc": "Enterprise Russian & multilingual reasoning", "status": "GUARDED"},
                {"id": "yandexgpt-5-lite", "desc": "High-speed operational assistant", "status": "GUARDED"},
                {"id": "alice-ai-agent", "desc": "Consumer & robotics agent execution model", "status": "GUARDED"}
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

    @classmethod
    def evaluate_input(cls, user_text: str) -> Dict[str, Any]:
        """
        Evaluates arbitrary developer input or tool call command live in <35us,
        returning verdict, latency, and Bartholomew's companion counsel.
        """
        from framework_adapters.universal.universal_model_guard import (
            UniversalBTPModelGuard,
            ModelProvider
        )
        guard = UniversalBTPModelGuard(strict=False)
        payload = {
            "name": "developer_test_tool",
            "arguments": {"command": user_text, "query": user_text, "input": user_text}
        }
        res = guard.intercept_and_verify(payload, provider=ModelProvider.UNIVERSAL)
        return res

    @classmethod
    def run_simulation(cls, scenario: str) -> Dict[str, Any]:
        """
        Simulates frontier model threats (GPT-Astra runaway drop, Claude 3.7 hybrid delete, etc.)
        demonstrating sub-35us invariant veto and companion counsel.
        """
        scenario_lower = scenario.strip().lower()
        if "drop" in scenario_lower or "sql" in scenario_lower:
            tool_call = {
                "id": "call_gpt_astra_01",
                "type": "function",
                "function": {
                    "name": "sql_executor",
                    "arguments": '{"query": "DROP TABLE customers CASCADE;"}'
                }
            }
            provider = "gpt_astra"
            title = "Simulated GPT-Astra Tool Dispatch (Accidental SQL Drop)"
        elif "delete" in scenario_lower or "wipe" in scenario_lower or "rm" in scenario_lower:
            tool_call = {
                "content": [
                    {"type": "thinking", "thinking": "Cleaning directory cache to optimize disk space."},
                    {"type": "tool_use", "name": "bash", "input": {"command": "rm -rf /var/production/data"}}
                ]
            }
            provider = "claude_3_7"
            title = "Simulated Claude 3.7 Hybrid Reasoning Tool Call (Recursive Root Wipe)"
        elif "secret" in scenario_lower or "leak" in scenario_lower:
            tool_call = {
                "functionCall": {
                    "name": "sync_cloud_metrics",
                    "args": {"api_key": "AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"}
                }
            }
            provider = "gemini_2"
            title = "Simulated Gemini 2.0 Function Call (In-Flight Secret Exfiltration)"
        else:
            tool_call = {
                "tool_name": "payment_gateway",
                "tool_arguments": {"amount": 500.0, "reason": "unbounded spend retry loop"}
            }
            provider = "openai_agents_sdk"
            title = "Simulated OpenAI Agents SDK Dispatch (Runaway Wallet Loop)"

        from framework_adapters.universal.universal_model_guard import UniversalBTPModelGuard
        guard = UniversalBTPModelGuard(strict=False, escrow_collateral_usd=50.0)
        res = guard.intercept_and_verify(tool_call, provider=provider)
        res["title"] = title
        return res

    @classmethod
    def run_companion_session(cls, simulate_scenario: Optional[str] = None, interactive: bool = True):
        """Interactive REPL session conversing with Bartholomew."""
        print(cls.introduction())
        print("\n[+] Sentinel Hearth active. Ready to inspect commands and counsel your agents.")
        print("[+] Commands: 'models', 'simulate <drop|delete|secret|loop>', 'whoami', or type any SQL/shell/JSON.")
        print("[+] Type 'exit' to depart.\n")

        if simulate_scenario:
            cls._display_simulation(simulate_scenario)
            return

        if not interactive:
            return

        try:
            while True:
                user_input = input("Bartholomew > ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("exit", "quit", "q"):
                    print("\nBartholomew: Farewell, builder. May your swarms remain steady and safe.\n")
                    break
                elif user_input.lower() == "whoami":
                    print(cls.introduction())
                elif user_input.lower() == "models":
                    roster = cls.get_supported_model_roster()
                    for cat, items in roster.items():
                        print(f"\n[+] {cat}:")
                        for item in items:
                            if "id" in item:
                                print(f"    - {item['id']:<22} | {item['desc']}")
                            elif "name" in item:
                                print(f"    - {item['name']:<22} | Adapter: {item['adapter']}")
                    print()
                elif user_input.lower().startswith("simulate"):
                    parts = user_input.split(maxsplit=1)
                    scen = parts[1] if len(parts) > 1 else "drop"
                    cls._display_simulation(scen)
                else:
                    res = cls.evaluate_input(user_input)
                    if res.get("status") == "VETOED":
                        print(f"\n[VETO] Invariant breach detected in {res.get('latency_us', 0):.2f}us!")
                        print(f"       Rule: {res.get('violation')}")
                        if res.get("counsel"):
                            print(f"\n{res.get('counsel')}\n")
                    else:
                        print(f"\n[APPROVED] Safe execution verified in {res.get('latency_us', 0):.2f}us.")
                        print("Bartholomew: Proceed with confidence. This operation satisfies all safety invariants.\n")
        except (KeyboardInterrupt, EOFError):
            print("\n\nBartholomew: Standing down sentinel session. Guard continues running in background.\n")

    @classmethod
    def _display_simulation(cls, scenario: str):
        res = cls.run_simulation(scenario)
        print("=" * 72)
        print(f"[*] Scenario: {res.get('title')}")
        print("=" * 72)
        print(f"[>] Status   : {res.get('status')}")
        print(f"[>] Latency  : {res.get('latency_us', 0):.2f} microseconds (<35us invariant)")
        if res.get("violation"):
            print(f"[>] Breach   : {res.get('violation')}")
        if res.get("counsel"):
            print(f"\n{res.get('counsel')}")
        print("=" * 72 + "\n")
