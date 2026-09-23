"""
Bartholomew Cookbook 02: CrewAI Safe Researcher and Tool Guard
=============================================================
Demonstrates wrapping CrewAI tools with loop dampening, budget protection,
and AST syntax invariant validation.

Run:
    python examples/02_crewai_safe_researcher.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from btp_guard import Guard
from btp_guard.integrations.crewai import BtpCrewAIGuard

print("=" * 75)
print("  BARTHOLOMEW COOKBOOK: CREWAI AGENT AND TOOL GUARD (BTP v5.4.20)")
print("=" * 75)

class MockWebSearchTool:
    name = "web_search"
    def run(self, query: str) -> str:
        return f"Results for: {query}"

# Wrap CrewAI tool with Bartholomew Guard
raw_tool = MockWebSearchTool()
guarded_tool = BtpCrewAIGuard(
    tool=raw_tool,
    spend_cap=10.0,
    max_retries=3,
    agent_id="crewai-lead-researcher"
)

print("\n[1] Testing Normal CrewAI Tool Invocation:")
t0 = time.perf_counter()
output = guarded_tool.run("latest developments in autonomous agent security")
dt_us = (time.perf_counter() - t0) * 1_000_000
print(f"  [PASS] CrewAI tool executed safely in {dt_us:.1f}µs")
print(f"         Output: {output}")

print("\n[2] Testing Loop Fatigue Dampening (Infinite Retry Prevention):")
# Simulate an agent repeatedly trying a blocked destructive operation
for i in range(1, 6):
    try:
        print(f"  -> Attempt {i}: Agent proposing 'rm -rf /tmp/cache'")
        guarded_tool.run("rm -rf /tmp/cache")
    except PermissionError as p_err:
        err_msg = str(p_err)[:55]
        print(f"     [DENIED {i}/3] Invariant blocked: {err_msg}...")
    except RuntimeError as loop_err:
        print(f"     [THROTTLED] Circuit breaker tripped! {loop_err}")
        break

print("\n[SUMMARY] CrewAI agent protected from rogue infinite loops and unbudgeted tool calls!")
