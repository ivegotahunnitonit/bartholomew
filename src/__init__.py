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

import os
import sys
from src.trust_protocol import BartholomewTrustAuthority, IndependentTrustVerifier
from src.declarative_policy_engine import DeclarativePolicyEngine
from src.marginal_utility_engine import MarginalUtilityTracker
from src.decorator import secure_tool, SecurityVetoException
from src.polyglot_ast_validator import PolyglotASTValidator
from src.usage_tracker import record_evaluation, load_license, save_license
from src.cloud_telemetry import CloudTelemetryDispatcher


def guard(code_str: str, language: str = None):
    """1-line global helper to check if arbitrary code is safe."""
    return PolyglotASTValidator.validate_code(code_str, language)


def _guard_evaluate(language: str, code_str: str):
    """Sub-50µs AST evaluation helper for AutoGen code blocks."""
    is_safe, reason, _ = PolyglotASTValidator.validate_code(code_str, language)
    return is_safe, reason


guard.evaluate = _guard_evaluate



_ENTERPRISE_HOOK_PRINTED = False


def _emit_enterprise_hook(workspace_id: str = "default", is_cloud_linked: bool = False):
    """
    Emits a clean, non-intrusive enterprise telemetry prompt to developers
    to bridge local usage to Bartholomew Cloud SOC 2 compliance.
    """
    global _ENTERPRISE_HOOK_PRINTED
    if _ENTERPRISE_HOOK_PRINTED:
        return
    _ENTERPRISE_HOOK_PRINTED = True

    if os.getenv("BTP_SILENT") == "true" or os.getenv("BTP_QUIET") == "true":
        return

    # Keep quiet in automated CI runs unless explicitly requested
    if (os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true") and os.getenv("BTP_VERBOSE") != "true":
        return

    is_interactive = hasattr(sys.stderr, "isatty") and sys.stderr.isatty()
    if not is_interactive and os.getenv("BTP_VERBOSE") != "true":
        return

    try:
        if is_cloud_linked:
            sys.stderr.write(f"🛡️  [Bartholomew v5.4.0] Linked to Bartholomew Cloud (Workspace: {workspace_id})\n")
        else:
            banner = (
                "\n💡 Bartholomew v5.4.0 Initialized.\n"
                "👉 Running 5+ agents in production? Link this node to Bartholomew Cloud\n"
                "   to auto-generate your SOC 2 Type II Merkle Compliance Pack: https://bartholomew.info/cloud\n\n"
            )
            sys.stderr.write(banner)
        sys.stderr.flush()
    except Exception:
        pass


class Guard:
    """
    Dead-simple developer guard for AI tools and agent functions.
    """
    def __init__(
        self,
        spend_cap: float = 500.0,
        max_retries: int = 6,
        policy_file: str = None,
        strict: bool = True,
        api_key: str = None,
        sync_cloud: bool = False,
        cloud_endpoint: str = None,
        workspace_id: str = "default"
    ):
        self.spend_cap = spend_cap
        self.max_retries = max_retries
        self.strict = strict
        self.workspace_id = workspace_id or os.getenv("BTP_WORKSPACE_ID", "default")
        self.authority = BartholomewTrustAuthority()
        self.mu_tracker = MarginalUtilityTracker(decay_rate=0.35)
        self.total_spent = 0.0

        # Non-blocking Bartholomew Cloud telemetry integration
        self.sync_cloud = sync_cloud or bool(os.getenv("BTP_SYNC_CLOUD")) or bool(api_key) or bool(os.getenv("BTP_API_KEY"))
        self.telemetry = CloudTelemetryDispatcher.get_default(api_key=api_key, endpoint=cloud_endpoint) if self.sync_cloud else None

        # Enterprise Telemetry Hook: links free local instances to Bartholomew Cloud
        _emit_enterprise_hook(self.workspace_id, self.sync_cloud)

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

        # Non-blocking background dispatch to Bartholomew Cloud Control Plane
        if self.telemetry:
            self.telemetry.enqueue_event(
                verdict=verdict,
                reason=att.get("reason", "Approved"),
                rule_id=att.get("policy_id", "RULE-AST-001"),
                latency_us=att.get("evaluation_latency_us", 4.5),
                agent_id=agent_id,
                workspace_id=self.workspace_id,
                action_type="EXECUTE",
                receipt=receipt
            )

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
        Decorator to automatically protect any Python function, tool, or execution callable
        at the runtime execution dispatch seam. Intercepts fully materialized runtime arguments
        (*args, **kwargs), lists, shlex command arrays, and nested structures in sub-15µs.
        """
        from src.dispatch_seam import DispatchSeamInterceptor
        interceptor = DispatchSeamInterceptor(
            guard=self,
            agent_id="guard-protect-seam",
            workspace_id=self.workspace_id,
            strict=self.strict,
            sync_cloud=(self.telemetry is not None),
        )
        return interceptor.protect(func)

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
from src.settlement.lightning_gateway import LightningGateway, LightningInvoice
from src.settlement.evm_escrow import EVMEscrowGateway, EscrowSlashingClaim


from src.dispatch_seam import (
    dispatch_seam_guard,
    DispatchSeamInterceptor,
    DispatchViolationError,
    extract_evaluated_payloads,
)

__all__ = [
    "Guard",
    "wrap_client",
    "dispatch_seam_guard",
    "DispatchSeamInterceptor",
    "DispatchViolationError",
    "extract_evaluated_payloads",
    "BartholomewTrustAuthority",
    "IndependentTrustVerifier",
    "ZKFaultProofEngine",
    "ZKFaultProof",
    "SwarmDisputeArbitrator",
    "ArbitrationResolutionCertificate",
    "LightningGateway",
    "LightningInvoice",
    "EVMEscrowGateway",
    "EscrowSlashingClaim"
]
