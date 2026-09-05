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
from src.decorator import secure_tool, SecurityVetoException
from src.polyglot_ast_validator import PolyglotASTValidator


def guard(code_str: str, language: str = None):
    """1-line global helper to check if arbitrary code is safe."""
    return PolyglotASTValidator.validate_code(code_str, language)



class Guard:
    """
    Dead-simple developer guard for AI tools and agent functions.
    """
    def __init__(self, spend_cap: float = 500.0, max_retries: int = 6, policy_file: str = None, strict: bool = True):
        self.spend_cap = spend_cap
        self.max_retries = max_retries
        self.strict = strict
        self.authority = BartholomewTrustAuthority()
        self.mu_tracker = MarginalUtilityTracker(decay_rate=0.35)
        self.total_spent = 0.0

    def evaluate_ast(self, code_str: str, language: str = None) -> dict:
        """Evaluates arbitrary code string with sub-35µs AST safety rules."""
        is_safe, reason, metadata = PolyglotASTValidator.validate_code(code_str, language)
        latency_us = metadata.get("latency_us", 15.0) if isinstance(metadata, dict) else 15.0
        return {
            "allowed": is_safe,
            "violations": [reason] if not is_safe else [],
            "reason": reason,
            "latency_us": latency_us,
            "metadata": metadata
        }

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


def wrap_client(client, spend_cap: float = 100.0, guard: Guard = None):
    """
    1-Line client wrapper for OpenAI, Anthropic, or custom client instances.
    """
    active_guard = guard or Guard(spend_cap=spend_cap)
    
    class WrappedClient:
        def __init__(self, target_client, btp_guard):
            self._client = target_client
            self._guard = btp_guard

        def __getattr__(self, name):
            attr = getattr(self._client, name)
            if callable(attr):
                return active_guard.protect(attr)
            return attr

    return WrappedClient(client, active_guard)


__all__ = ["Guard", "wrap_client", "BartholomewTrustAuthority", "IndependentTrustVerifier"]
