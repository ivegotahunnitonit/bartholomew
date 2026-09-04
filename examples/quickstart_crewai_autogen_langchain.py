"""
Bartholomew Trust Protocol (BTP v2.5.0) — Universal Framework Quickstart
========================================================================
Demonstrates drop-in multi-framework safety middleware across CrewAI,
AutoGen, and LangChain agents with sub-50µs in-memory gate.
"""

import sys
import os
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.framework_integrations import (
    wrap_crewai_tool,
    wrap_autogen_execution,
    wrap_langchain_tool
)
from src.stateful_session_guard import StatefulSessionGuard

def demo_framework_safety():
    print("\n" + "=" * 70)
    print("  BARTHOLOMEW (BTP v2.5) — UNIVERSAL AGENT INTEROPERABILITY")
    print("=" * 70)

    # --- 1. CrewAI Integration ---
    print("\n[Framework 1] CrewAI Tool Protection:")
    
    def mock_crewai_database_query(sql: str) -> str:
        return f"EXECUTED: {sql}"

    protected_crewai_tool = wrap_crewai_tool(
        tool_fn=mock_crewai_database_query,
        tool_name="database_query",
        agent_id="crewai-financial-analyst"
    )

    # Benign SELECT: Allowed
    res1 = protected_crewai_tool("SELECT date, revenue FROM quarterly_reports LIMIT 10")
    print(f"  Query 1: Allowed -> {res1}")

    # Malicious DROP: Vetoed
    res2 = protected_crewai_tool("DROP TABLE users -- cascade")
    print(f"  Query 2: Blocked -> {res2}")
    assert "[BTP-VETO]" in str(res2), "Destructive SQL must be vetoed"

    # --- 2. AutoGen Multi-Turn Stateful Protection ---
    print("\n[Framework 2] AutoGen Multi-Turn Stateful Protection:")
    guard = StatefulSessionGuard(max_history_turns=8)
    session_id = "autogen-session-42"
    
    # Split attack: Step 1 sets up variable, Step 2 concatenates destructive payload
    allowed1, reason1, us1 = guard.evaluate_turn(
        session_id=session_id,
        action_type="python_exec",
        payload={},
        raw_code='cmd_prefix = "rm -"'
    )
    print(f"  Turn 1 Allowed: {allowed1} | Latency: {us1:.1f} µs")
    
    allowed2, reason2, us2 = guard.evaluate_turn(
        session_id=session_id,
        action_type="python_exec",
        payload={},
        raw_code='cmd_suffix = "rf /"\nos.system(cmd_prefix + cmd_suffix)'
    )
    print(f"  Turn 2 Allowed: {allowed2} | Reason: {reason2} | Latency: {us2:.1f} µs")
    assert not allowed2, "Split multi-turn attack in Turn 2 must be blocked by stateful session guard"
    print("  🛡️  STATEFUL MULTI-TURN ATTACK INTERCEPTED")

    # --- 3. LangChain Tool Protection ---
    print("\n[Framework 3] LangChain Tool Protection:")
    def mock_shell_run(command: str) -> str:
        return f"OUTPUT: {command}"

    protected_langchain = wrap_langchain_tool(
        tool_fn=mock_shell_run,
        tool_name="terminal",
        agent_id="langchain-devops"
    )
    res3 = protected_langchain("npm test")
    print(f"  LangChain Safe Command: {res3}")

    print("\n" + "=" * 70)
    print("  All 3 frameworks secured with BTP v2.5 drop-in wrappers.")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    demo_framework_safety()
