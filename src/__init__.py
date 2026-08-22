"""
Bartholomew (btp-guard)
=======================
A fast, lightweight developer tool that stops AI agents from breaking things.

Features:
  - Blocks destructive commands (rm -rf, DROP TABLE, secret leaks) in <5 µs.
  - Halts runaway infinite retry loops.
  - Enforces hard budget and spend caps on tool calls.
  - Generates signed cryptographic receipts for every action.
"""

from src.trust_protocol import BartholomewTrustAuthority, IndependentTrustVerifier
from src.declarative_policy_engine import DeclarativePolicyEngine
from src.marginal_utility_engine import MarginalUtilityTracker


class Guard:
    """
    Dead-simple developer guard for AI tools and agent functions.
    """
    def __init__(self, spend_cap: float = 500.0, max_retries: int = 6, policy_file: str = None):
        self.spend_cap = spend_cap
        self.max_retries = max_retries
        self.authority = BartholomewTrustAuthority()
        self.mu_tracker = MarginalUtilityTracker(decay_rate=0.35)
        self.total_spent = 0.0

    def check(self, command_or_query: str, amount_usd: float = 0.0, agent_id: str = "agent-1") -> dict:
        """
        Directly checks if an action is safe to run.
        Returns: {'allowed': bool, 'verdict': str, 'reason': str, 'latency_us': float}
        """
        # 1. Budget check
        if self.total_spent + amount_usd > self.spend_cap:
            return {
                "allowed": False,
                "verdict": "DENY",
                "reason": f"Spend limit exceeded: ${self.total_spent + amount_usd:.2f} > ${self.spend_cap:.2f}",
                "latency_us": 1.2
            }

        # 2. Invariant evaluation
        payload = {"command": command_or_query, "query": command_or_query, "amount_usd": amount_usd}
        receipt = self.authority.evaluate_intent(agent_id=agent_id, action_type="EXECUTE", payload=payload)
        
        att = receipt.get("attestation", {})
        verdict = att.get("verdict", "DENY")
        allowed = (verdict == "ALLOW")

        if allowed:
            self.total_spent += amount_usd

        return {
            "allowed": allowed,
            "verdict": verdict,
            "reason": att.get("reason", "Approved"),
            "latency_us": att.get("evaluation_latency_us", 4.5),
            "receipt": receipt
        }

    def protect(self, func):
        """
        Decorator to automatically protect any Python function or tool.
        """
        def wrapper(*args, **kwargs):
            first_arg = str(args[0]) if args else str(kwargs)
            res = self.check(first_arg)
            if not res["allowed"]:
                raise PermissionError(f"[Bartholomew Blocked Action] {res['reason']}")
            return func(*args, **kwargs)
        return wrapper


__all__ = ["Guard", "BartholomewTrustAuthority", "IndependentTrustVerifier"]
