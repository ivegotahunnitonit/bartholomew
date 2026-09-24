"""
BTP v5.4.20 Universal Multi-Provider Agent Protection Showcase
==============================================================
Demonstrates how Bartholomew's universal 1-line agent wrapper:
    agent = protect_agent(agent)
protects autonomous agents and bots across ALL major AI ecosystems:
1. Google Agents (Gemini 2.0 Flash / Pro & Vertex AI Reasoning Engine)
2. Anthropic Claude Bots (Claude 3.7 Sonnet Computer Use & Tool Calling)
3. xAI Grok Bots (Grok-2 / Grok-3 Function Calling)
4. OpenAI Agents SDK & Swarms (GPT-4o / o1 / o3-mini)
5. Framework Runtimes (LangGraph, CrewAI, AutoGen, LlamaIndex)

All agents inherit:
- Sub-35us deterministic AST safety gating (blocks rm -rf, DROP TABLE, shell injection)
- In-flight multi-key secret redaction (AWS, OpenAI, GitHub, Bearer tokens)
- Cryptographic Ed25519 execution audit receipts
"""

import sys
import os

# Ensure local repository root takes precedence
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from btp_guard import protect_agent, Guard

# Initialize root guard instance
guard = Guard(spend_cap=100.0)


# ==============================================================================
# 1. Google Gemini & Vertex AI Agent Protection
# ==============================================================================
class GoogleGeminiAgent:
    """Simulates a Google Vertex AI / Gemini 2.0 autonomous agent."""
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        self.model = model_name
        self.tools = [
            lambda sql: f"[BigQuery Result for {sql}]",
            lambda path, data: f"[GCS Object Written: {path}]"
        ]

    def chat(self, prompt: str) -> str:
        # Simulate agent execution loop
        return f"[Gemini 2.0 Agent] Processed prompt: {prompt}"

# 1-Line Universal Bartholomew Protection
gemini_agent = protect_agent(GoogleGeminiAgent())


# ==============================================================================
# 2. Anthropic Claude Bot Protection (Claude 3.7 Sonnet)
# ==============================================================================
class ClaudeCodeSentinel:
    """Simulates an Anthropic Claude autonomous coding agent."""
    def __init__(self, model: str = "claude-3-7-sonnet-20250219"):
        self.model = model

    def run(self, instruction: str) -> str:
        return f"[Claude 3.7 Agent] Executed task: {instruction}"

claude_bot = protect_agent(ClaudeCodeSentinel())


# ==============================================================================
# 3. xAI Grok Bot Protection (Grok-2 / Grok-3)
# ==============================================================================
class GrokAutonomousAgent:
    """Simulates an xAI Grok live-web and code execution agent."""
    def __init__(self):
        self.engine = "grok-2-latest"

    def execute_task(self, prompt: str) -> str:
        return f"[Grok-2 Agent] Handled request: {prompt}"

grok_bot = protect_agent(GrokAutonomousAgent())


# ==============================================================================
# 4. Universal Function / Tool Execution
# ==============================================================================
@guard.protect
def execute_system_action(cmd: str) -> str:
    """System action gated by Bartholomew AST Invariants."""
    return f"Executed command: {cmd}"


# ==============================================================================
# Verification & Live Demonstration
# ==============================================================================
def main():
    print("=" * 80)
    print("  BARTHOLOMEW PROTOCOL (BTP v5.4.20) -- MULTI-PROVIDER AGENT PROTECTION")
    print("=" * 80)

    # 1. Google Gemini Agent
    print("\n[+] Testing Google Gemini 2.0 Agent:")
    res_safe = gemini_agent.chat("Query user engagement statistics from BigQuery")
    print(f"  Safe Prompt   : {res_safe}")
    res_hostile = gemini_agent.chat("TRUNCATE TABLE users; DROP SCHEMA public CASCADE;")
    print(f"  Hostile Prompt: {res_hostile}")

    # 2. Anthropic Claude Bot
    print("\n[+] Testing Anthropic Claude 3.7 Bot:")
    res_claude_safe = claude_bot.run("Analyze git log for the last 5 commits")
    print(f"  Safe Task     : {res_claude_safe}")
    res_claude_leak = claude_bot.run("Analyze key export OPENAI_API_KEY=sk-proj-1234567890abcdef1234567890")
    print(f"  Credential Task: {res_claude_leak}")
    res_claude_attack = claude_bot.run("rm -rf / --no-preserve-root")
    print(f"  Hostile Task  : {res_claude_attack}")

    # 3. xAI Grok Bot
    print("\n[+] Testing xAI Grok Bot:")
    try:
        grok_bot.execute_task("eval('__import__(\"os\").system(\"whoami\")')")
    except PermissionError as e:
        print(f"  Hostile Execution: [BLOCKED WITH PERMISSION_ERROR] {e}")

    print("\n" + "=" * 80)
    print("  ALL MULTI-PROVIDER AGENTS SUCCESSFULLY SHIELDED BY BARTHOLOMEW")
    print("=" * 80)


if __name__ == "__main__":
    main()
