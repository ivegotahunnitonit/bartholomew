"""
Microsoft AutoGen BTP Message Interceptor Demo
=============================================
Demonstrates how to intercept agent-to-agent tool calls in AutoGen
to enforce financial spend limits and command boundaries.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))
from src.declarative_policy_engine import DeclarativePolicyEngine

policy_engine = DeclarativePolicyEngine("policies/default_security_policy.yaml")

class AutoGenBTPInterceptor:
    @staticmethod
    def inspect_agent_message(sender_id: str, receiver_id: str, message: dict) -> dict:
        """Evaluates agent-to-agent message payloads in <40 µs."""
        allowed, reason, latency_us = policy_engine.evaluate_payload(message)
        return {
            "authorized": allowed,
            "sender": sender_id,
            "receiver": receiver_id,
            "reason": reason,
            "decision_latency_us": latency_us
        }

if __name__ == "__main__":
    print("=" * 60)
    print("MICROSOFT AUTOGEN BTP INTERCEPTOR DEMO")
    print("=" * 60)

    # 1. Normal Task Delegation
    msg1 = {"task": "Fetch report", "amount_usd": 49.00}
    res1 = AutoGenBTPInterceptor.inspect_agent_message("planner_agent", "worker_agent", msg1)
    print(f"\n[1] Normal Delegation: Authorized={res1['authorized']} ({res1['decision_latency_us']} µs)")

    # 2. Spend Limit Escalation
    msg2 = {"task": "Execute wire transfer", "amount_usd": 12000.00}
    res2 = AutoGenBTPInterceptor.inspect_agent_message("worker_agent", "banking_agent", msg2)
    print(f"\n[2] Spend Limit Escalation: Authorized={res2['authorized']}")
    print(f"    Reason: {res2['reason']}")

    print("\n" + "=" * 60)
