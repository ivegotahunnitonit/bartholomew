"""
CrewAI BTP v4.1 Task & Tool Execution Guard
============================================
Provides pre-flight in-process AST gating, secret scrubbing, Sovereign Passport
verification, and Autonomous Micro-Escrow collateral protection for CrewAI
agent swarms.

Usage:
    from framework_adapters.crewai import btp_crewai_tool, CrewAIBTPTaskGuard, BTPViolationError

    @btp_crewai_tool(spend_cap=50.0, passport=agent_passport)
    def execute_code(code: str) -> str:
        ...
"""

import functools
import logging
from typing import Callable, Dict, Any, List, Optional

logger = logging.getLogger("btp.adapters.crewai")

try:
    from btp_guard import Guard
except ImportError:
    try:
        from src.polyglot_ast_validator import PolyglotASTValidator as Guard
    except ImportError:
        Guard = None

try:
    from standalone_btp_verifier import independent_verify_btp_receipt
except ImportError:
    try:
        from btp_guard import independent_verify_btp_receipt
    except ImportError:
        independent_verify_btp_receipt = None

try:
    from src.agent_passport import SovereignAgentPassport
    from src.settlement.autonomous_escrow import AutonomousEscrowPool
    from src.settlement.swarm_arbitration import ZKFaultProofEngine
except ImportError:
    SovereignAgentPassport = None
    AutonomousEscrowPool = None
    ZKFaultProofEngine = None


# ---------------------------------------------------------------------------
# Structured Violation Exception
# ---------------------------------------------------------------------------

class BTPViolationError(PermissionError):
    """
    Structured security violation raised when a CrewAI tool or task payload
    breaches AST safety invariants enforced by the Bartholomew Trust Protocol.
    """

    def __init__(
        self,
        reason: str,
        rule_id: str = "BTP-AST-001",
        blocked_payload: str = "",
        latency_us: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            f"[BTP-SECURITY-VETO] CrewAI execution blocked by rule {rule_id}: {reason}"
        )
        self.reason = reason
        self.rule_id = rule_id
        self.blocked_payload = blocked_payload
        self.latency_us = latency_us
        self.metadata = metadata or {}

    def to_diagnostics(self) -> Dict[str, Any]:
        """Returns structured JSON diagnostics suitable for logs or telemetry."""
        return {
            "status": "BLOCKED",
            "rule_id": self.rule_id,
            "reason": self.reason,
            "blocked_payload": (
                self.blocked_payload[:120] + "..."
                if len(self.blocked_payload) > 120
                else self.blocked_payload
            ),
            "latency_us": round(self.latency_us, 2),
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        return (
            f"[BTP-VETO] CrewAI Tool Execution Blocked!\n"
            f"  - Rule ID:   {self.rule_id}\n"
            f"  - Reason:    {self.reason}\n"
            f"  - Latency:   {self.latency_us:.1f} µs\n"
            f"  - Payload:   {self.blocked_payload[:80] + ('...' if len(self.blocked_payload) > 80 else '')}"
        )


# ---------------------------------------------------------------------------
# Internal helper: escrow lock + ZK slash on AST breach
# ---------------------------------------------------------------------------

def _lock_and_slash_escrow(
    passport: Any,
    action_type: str,
    escrow_collateral_usd: float,
    settlement_rail: str,
    payee_destination: str,
    ast_result: Dict[str, Any],
) -> None:
    """
    Locks micro-escrow collateral and triggers autonomous ZK-fault slashing
    when an AST invariant is violated.  Called internally before raising
    BTPViolationError.
    """
    if AutonomousEscrowPool is None or ZKFaultProofEngine is None:
        return

    pool = AutonomousEscrowPool()
    agent_id = getattr(passport, "agent_id", "Agent-CrewAI-Worker")
    deposit = pool.lock_escrow(
        agent_id=agent_id,
        action_type=action_type,
        amount_usd=escrow_collateral_usd,
        passport=passport,
        settlement_rail=settlement_rail,
    )
    if deposit is None:
        return

    try:
        pre_hash = (
            deposit.l402_challenge.get("payment_hash", f"pre_{deposit.escrow_id}")
            if deposit.l402_challenge
            else f"pre_{deposit.escrow_id}"
        )
        zk_proof = ZKFaultProofEngine.generate_fault_proof(
            prover_agent_id="agent-crewai-sentinel",
            target_action=action_type,
            violated_invariant=ast_result.get("rule_id", "BTP-AST-001"),
            private_payload=ast_result.get("blocked_payload", ""),
            state_pre_hash=pre_hash,
        )
        arb = pool.arbitrator
        ok_d, _, dispute = arb.open_dispute(
            escrow_id=deposit.escrow_id,
            challenger_agent_id="agent-crewai-sentinel",
            target_agent_id=deposit.agent_id,
            target_action=action_type,
            amount_usd=deposit.amount_usd,
            fault_proof=zk_proof.to_dict(),
            required_quorum=1,
        )
        if ok_d and SovereignAgentPassport is not None:
            j1 = SovereignAgentPassport.issue(
                agent_id="agent-juror-crewai-1",
                model_family="claude-3-5-sonnet",
                authorized_capabilities=["audit:verify"],
            )
            j2 = SovereignAgentPassport.issue(
                agent_id="agent-juror-crewai-2",
                model_family="gemini-1-5-pro",
                authorized_capabilities=["audit:verify"],
            )
            arb.register_validator(j1)
            arb.register_validator(j2)
            arb.cast_vote(dispute.dispute_id, j1, "APPROVE_SLASH")
            arb.cast_vote(dispute.dispute_id, j2, "APPROVE_SLASH")
            ok_r, _, cert = arb.resolve_dispute(dispute.dispute_id)
            if ok_r:
                pool.arbitrate_and_slash(
                    escrow_id=deposit.escrow_id,
                    arbitration_cert=cert,
                    payee_destination=payee_destination or "payee_treasury_vault",
                    agent_passport=passport,
                )
    except Exception:
        # Escrow slash is best-effort; violation is still raised.
        logger.exception("BTP escrow slash failed for CrewAI tool")


# ---------------------------------------------------------------------------
# @btp_crewai_tool decorator
# ---------------------------------------------------------------------------

def btp_crewai_tool(
    fn: Callable = None,
    *,
    spend_cap: float = 50.0,
    strict: bool = True,
    custom_patterns: Optional[List[str]] = None,
    escrow_collateral_usd: Optional[float] = None,
    passport: Optional[Any] = None,
    action_type: str = "CREWAI_TOOL_EXEC",
    settlement_rail: str = "L402_LIGHTNING",
    payee_destination: Optional[str] = None,
    on_violation: Optional[Callable[["BTPViolationError"], Any]] = None,
):
    """
    Drop-in decorator for CrewAI tools.  Inspects every string argument
    for malicious payloads, destructive commands, or prompt injections in
    sub-35 microseconds before the underlying system receives the call.

    Usage:
        @btp_crewai_tool(spend_cap=50.0, passport=agent_passport)
        def execute_code(code: str) -> str:
            ...

        # With optional violation callback instead of raise:
        @btp_crewai_tool(on_violation=lambda e: {"error": str(e)})
        def risky_tool(payload: str) -> dict:
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Sovereign Passport gate
            if passport is not None and getattr(passport, "is_circuit_broken", False):
                err = BTPViolationError(
                    reason=f"Agent passport '{passport.agent_id}' is CIRCUIT-BROKEN (Reputation revoked)",
                    rule_id="BTP-PASSPORT-REVOKED",
                )
                if on_violation:
                    return on_violation(err)
                raise err

            guard_instance = Guard(spend_cap=spend_cap, strict=strict) if Guard else None

            def _check(value: str, label: str) -> None:
                if not guard_instance:
                    return
                res = guard_instance.evaluate_ast(value)
                if not res.get("allowed", True):
                    if escrow_collateral_usd and passport is not None:
                        _lock_and_slash_escrow(
                            passport=passport,
                            action_type=action_type,
                            escrow_collateral_usd=escrow_collateral_usd,
                            settlement_rail=settlement_rail,
                            payee_destination=payee_destination or "payee_treasury_vault",
                            ast_result=res,
                        )
                    rule = (
                        res.get("violations", ["BTP-AST-001"])[0].split(":")[0]
                        if res.get("violations")
                        else "BTP-AST-001"
                    )
                    err = BTPViolationError(
                        reason=f"{label}: {res.get('reason', 'Destructive pattern detected')}",
                        rule_id=rule,
                        blocked_payload=value,
                        latency_us=res.get("latency_us", 0.0),
                        metadata=res.get("metadata", {}),
                    )
                    logger.warning("BTP CrewAI violation: %s", err.to_diagnostics())
                    if on_violation:
                        return on_violation(err)
                    raise err

            # 2. Inspect positional arguments
            for i, arg in enumerate(args):
                if isinstance(arg, str):
                    result = _check(arg, f"arg[{i}]")
                    if result is not None:
                        return result

            # 3. Inspect keyword arguments
            for k, v in kwargs.items():
                if isinstance(v, str):
                    result = _check(v, f"kwarg '{k}'")
                    if result is not None:
                        return result

            # 4. Safe execution — escrow collateral is locked only on clean path
            pool = None
            deposit = None
            if escrow_collateral_usd and escrow_collateral_usd > 0 and AutonomousEscrowPool is not None and passport is not None:
                pool = AutonomousEscrowPool()
                deposit = pool.lock_escrow(
                    agent_id=getattr(passport, "agent_id", "Agent-CrewAI-Worker"),
                    action_type=action_type,
                    amount_usd=escrow_collateral_usd,
                    passport=passport,
                    settlement_rail=settlement_rail,
                )

            try:
                result = func(*args, **kwargs)
                if pool and deposit:
                    pool.release_escrow(deposit.escrow_id)
                    if passport is not None:
                        passport.record_action(volume_usd=escrow_collateral_usd)
                return result
            except Exception as exc:
                if pool and deposit and getattr(deposit, "status", None) == "LOCKED":
                    pool.release_escrow(deposit.escrow_id)
                raise exc

        return wrapper

    if fn is not None:
        return decorator(fn)
    return decorator


# ---------------------------------------------------------------------------
# CrewAIBTPTaskGuard class (receipt + passport attestation)
# ---------------------------------------------------------------------------

class CrewAIBTPTaskGuard:
    """
    Guards CrewAI task execution with offline Ed25519 BTP receipt attestation,
    capability bounds, and sovereign passport reputation gating.

    Usage:
        guard = CrewAIBTPTaskGuard(trusted_authorities=[ROOT_KEY], passport=my_passport)
        safe_deploy = guard.wrap_task("Deploy Production Patch", deploy_fn)
        safe_deploy(..., btp_receipt=receipt_json)
    """

    def __init__(
        self,
        trusted_authorities: List[str] = None,
        recipient_id: str = "Agent-CrewAI-Worker",
        allowed_capabilities: Optional[List[str]] = None,
        enforce_strict: bool = True,
        passport: Optional[Any] = None,
        escrow_collateral_usd: Optional[float] = None,
    ):
        self.trusted_authorities = trusted_authorities or []
        self.recipient_id = recipient_id
        self.allowed_capabilities = allowed_capabilities or ["FS_WRITE_RESTRICTED", "NO_NET_EGRESS"]
        self.enforce_strict = enforce_strict
        self.passport = passport
        self.escrow_collateral_usd = escrow_collateral_usd
        self.seen_nonces: set = set()

    def wrap_task(self, task_description: str, task_fn: Callable) -> Callable:
        """Wraps a task function with BTP receipt verification and passport checks."""

        @functools.wraps(task_fn)
        def guarded_task_exec(*args, **kwargs):
            # Passport circuit-breaker gate
            if self.passport is not None and getattr(self.passport, "is_circuit_broken", False):
                raise BTPViolationError(
                    reason=f"Agent passport '{self.passport.agent_id}' is revoked",
                    rule_id="BTP-PASSPORT-REVOKED",
                )

            receipt = kwargs.pop("btp_receipt", None)

            if self.enforce_strict and not receipt and self.trusted_authorities:
                raise BTPViolationError(
                    reason=f"Missing required BTP trust receipt for task '{task_description}'",
                    rule_id="BTP-RECEIPT-MISSING",
                )

            if receipt and independent_verify_btp_receipt is not None:
                payload = {"task": task_description, "args": args, "kwargs": kwargs}
                ok, msg = independent_verify_btp_receipt(
                    receipt_json_str=receipt,
                    candidate_payload=payload,
                    trusted_root_pubkeys=self.trusted_authorities,
                    expected_recipient_context=self.recipient_id,
                    seen_nonces=self.seen_nonces,
                    allowed_capabilities=self.allowed_capabilities,
                )
                if not ok:
                    raise BTPViolationError(
                        reason=f"Task attestation rejected: {msg}",
                        rule_id="BTP-RECEIPT-INVALID",
                    )

            return task_fn(*args, **kwargs)

        return guarded_task_exec
