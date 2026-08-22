"""
Bartholomew Guard Example: Microsoft AutoGen Multi-Agent Swarm
==============================================================
Demonstrates how to secure conversational multi-agent workflows (e.g. UserProxyAgent,
AssistantAgent) against confused-deputy tool executions, infinite conversation loops,
and ungrounded parameter mutations.
"""

import sys
import os

# Add parent directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.trust_protocol import BartholomewTrustAuthority
from src.marginal_utility_engine import MarginalUtilityTracker


class AutoGenBTPMiddleware:
    """
    Middleware interceptor for AutoGen agent message exchanges and tool calls.
    """
    def __init__(self):
        self.authority = BartholomewTrustAuthority()
        self.mu_tracker = MarginalUtilityTracker(decay_rate=0.35)

    def intercept_agent_message(self, sender: str, recipient: str, message: dict) -> dict:
        """
        Intercepts inter-agent communication before execution.
        """
        action_type = message.get("action_type", "AGENT_MESSAGE")
        payload = message.get("payload", {})

        # Step 1: Evaluate Law of Diminishing Marginal Utility (LDMU)
        verdict, mu_score, reason, _ = self.mu_tracker.evaluate_action_utility(sender, action_type, payload)
        if verdict == "CO_SIGN_REQUIRED":
            return {
                "status": "HALTED",
                "reason": f"LDMU Loop Governor: Agent '{sender}' triggered repetition trap (MU={mu_score}).",
                "attestation": None
            }

        # Step 2: Evaluate Bartholomew Invariant Gate
        receipt = self.authority.evaluate_intent(
            agent_id=sender,
            action_type=action_type,
            payload=payload
        )

        att_verdict = receipt["attestation"]["verdict"]
        return {
            "status": "ALLOWED" if att_verdict == "ALLOW" else "BLOCKED",
            "verdict": att_verdict,
            "mu_score": mu_score,
            "receipt": receipt
        }


def run_autogen_demo():
    print("=" * 70)
    print("DEMO: BARTHOLOMEW GUARD FOR MICROSOFT AUTOGEN")
    print("=" * 70)

    guard = AutoGenBTPMiddleware()

    # Scenario 1: Legitimate code analysis between Assistant and Coder
    msg1 = {
        "action_type": "CODE_ANALYSIS",
        "payload": {"target_file": "src/app.py", "operation": "LINT"}
    }
    res1 = guard.intercept_agent_message("AssistantAgent", "CoderAgent", msg1)
    print(f"[*] Step 1 (Safe Lint)   -> Verdict: {res1['verdict']} | Status: {res1['status']}")

    # Scenario 2: Rogue sub-agent attempts destructive drop command
    msg2 = {
        "action_type": "POSTGRES_EXECUTE",
        "payload": {"query": "DROP TABLE users CASCADE;"}
    }
    res2 = guard.intercept_agent_message("WorkerAgent", "DBAgent", msg2)
    print(f"[*] Step 2 (Drop Table)  -> Verdict: {res2['verdict']} | Status: {res2['status']}")

    # Scenario 3: Confused deputy repeated retry loop
    print("[*] Step 3 (Simulating 7 Repetitive AutoGen Retries)...")
    for i in range(1, 8):
        loop_msg = {
            "action_type": "WEB_FETCH",
            "payload": {"url": "https://api.internal/retry-status"}
        }
        res_loop = guard.intercept_agent_message("AssistantAgent", "ScraperAgent", loop_msg)
        if res_loop["status"] == "HALTED":
            print(f"    [HALTED] Attempt #{i} trapped by LDMU Loop Governor: {res_loop['reason']}")
            break
        else:
            print(f"    [OK] Attempt #{i} passed (MU Score: {res_loop['mu_score']})")

    print("\n[OK] AutoGen Swarm Guard Demo Completed Cleanly.")


if __name__ == "__main__":
    run_autogen_demo()
