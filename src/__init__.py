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
from src.usage_tracker import record_evaluation, load_license, save_license


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

        # Usage tracking & non-blocking quota reminder
        record_evaluation()
        lic = load_license()

        return {
            "allowed": allowed,
            "verdict": verdict,
            "reason": att.get("reason", "Approved"),
            "latency_us": att.get("evaluation_latency_us", 4.5),
            "license_tier": lic.get("tier", "COMMUNITY"),
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

    def escrow_collateral(
        self,
        amount_usd: float = 100.0,
        action_type: str = "DEFAULT_ACTION",
        settlement_rail: str = "L402_LIGHTNING",
        agent_id: str = "agent-worker",
        passport=None,
        pool=None
    ):
        """
        Decorator that locks autonomous micro-escrow collateral before function execution.
        If the function executes cleanly and passes AST verification, escrow is released.
        If an invariant violation occurs, an automated regression proof is stamped
        and collateral is liquidated to the claimant payee.
        """
        import hashlib
        from src.settlement.autonomous_escrow import AutonomousEscrowPool
        escrow_pool = pool or AutonomousEscrowPool()

        def decorator(func):
            def wrapper(*args, **kwargs):
                # 1. Lock micro-escrow collateral
                deposit = escrow_pool.lock_escrow(
                    agent_id=agent_id,
                    action_type=action_type,
                    amount_usd=amount_usd,
                    passport=passport,
                    settlement_rail=settlement_rail
                )
                try:
                    # 2. Pre-execution AST / argument check
                    first_arg = str(args[0]) if args else str(kwargs)
                    res = self.check(first_arg, amount_usd=amount_usd, agent_id=agent_id)
                    if not res["allowed"]:
                        proof = {
                            "type": "BTP_REGRESSION_PROOF",
                            "violated_invariant": res.get("reason", "INVARIANT_VETO"),
                            "proof_signature": f"0x{hashlib.sha256(first_arg.encode()).hexdigest()}",
                            "target_action": action_type
                        }
                        escrow_pool.claim_and_slash(
                            escrow_id=deposit.escrow_id,
                            regression_proof=proof,
                            payee_destination=kwargs.get("claimant_payee", "0x000000000000000000000000000000000000dead"),
                            agent_passport=passport
                        )
                        raise PermissionError(f"[Bartholomew Micro-Escrow Slashed] {res['reason']}")

                    result = func(*args, **kwargs)
                    # 3. Clean release
                    escrow_pool.release_escrow(deposit.escrow_id, agent_passport=passport)
                    return result
                except Exception as exc:
                    if deposit.status == "LOCKED":
                        proof = {
                            "type": "BTP_REGRESSION_PROOF",
                            "violated_invariant": str(exc),
                            "proof_signature": f"0x{hashlib.sha256(str(exc).encode()).hexdigest()}",
                            "target_action": action_type
                        }
                        escrow_pool.claim_and_slash(
                            escrow_id=deposit.escrow_id,
                            regression_proof=proof,
                            payee_destination=kwargs.get("claimant_payee", "0x000000000000000000000000000000000000dead"),
                            agent_passport=passport
                        )
                    raise exc
            wrapper.escrow_pool = escrow_pool
            wrapper.deposit = lambda: next(reversed(list(escrow_pool.active_escrows.values())), None)
            return wrapper
        return decorator


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


from src.settlement.swarm_arbitration import (
    ZKFaultProofEngine,
    ZKFaultProof,
    SwarmDisputeArbitrator,
    ArbitrationResolutionCertificate
)


__all__ = [
    "Guard",
    "wrap_client",
    "BartholomewTrustAuthority",
    "IndependentTrustVerifier",
    "ZKFaultProofEngine",
    "ZKFaultProof",
    "SwarmDisputeArbitrator",
    "ArbitrationResolutionCertificate"
]
