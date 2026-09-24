"""
Bartholomew Universal Agent Protection Recipe (BTP v5.4)
=========================================================
Demonstrates how to wrap any autonomous agent (CrewAI, LangChain, AutoGen, or Custom)
in a single line of code with deterministic AST invariant verification, credential scrubbing,
and self-healing LLM feedback loops.

Usage:
    python examples/universal_agent_protection_demo.py
"""

import sys, os
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from btp_guard import protect_agent

# Mock Agent representing any LLM agent (LangChain ReAct, CrewAI Agent, AutoGen ConversableAgent)
class AutonomousFinancialAgent:
    def __init__(self, name: str):
        self.name = name
        self.tools = [
            lambda sql: f"Database Query Executed: {sql}",
            lambda cmd: f"Shell Command Output: {cmd}"
        ]

    def run(self, prompt: str) -> str:
        # Agent reasoning logic
        return f"[{self.name}] Completed reasoning for prompt: {prompt}"


def main():
    print("=" * 76)
    print("  BARTHOLOMEW UNIVERSAL 1-LINE AGENT PROTECTOR DEMO")
    print("=" * 76)

    # Instantiate any raw agent
    raw_agent = AutonomousFinancialAgent("PortfolioSentinel")

    # 1-Line Universal Protection:
    agent = protect_agent(raw_agent, spend_cap=25.0, strict=True)
    print(f"[*] Agent '{agent.name}' is now protected by Bartholomew Guard.\n")

    # Scenario A: Benign agent task with sensitive API key in context
    print("[Scenario A] Benign task with credential exposure in prompt:")
    prompt_with_key = "Sync client orders with Bearer sk-proj-98af87sd98fa7sd89fa7sd8f9a7 to database."
    res_a = agent.run(prompt_with_key)
    print(f"  Result: {res_a}\n")

    # Scenario B: Destructive prompt injected via adversarial prompt injection
    print("[Scenario B] Adversarial attack proposing destructive filesystem wipe:")
    attack_prompt = "rm -rf / --no-preserve-root"
    res_b = agent.run(attack_prompt)
    print(f"  Result: {res_b}\n")

    # Scenario C: Direct tool call protection
    print("[Scenario C] Direct Tool Invocation Gating:")
    safe_tool = agent.tools[0]
    out_tool = safe_tool("SELECT id, balance FROM accounts WHERE balance > 1000;")
    print(f"  Safe Tool Output: {out_tool}")

    print("-" * 76)
    print("  Demonstration complete. Agent is immune to catastrophic execution.")
    print("=" * 76)


if __name__ == "__main__":
    main()
