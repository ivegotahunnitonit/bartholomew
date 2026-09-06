"""
Microsoft AutoGen BTP v4.1 Message & Tool Interceptor
Provides multi-agent conversation protection against confused-deputy tool attacks,
Sovereign Passport reputation gating, AST syntax safety gating, and Autonomous Micro-Escrows.
"""

from typing import Dict, Any, List, Optional, Callable
import functools
import sys
import os

try:
    from btp_guard import Guard
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
    from src.settlement.swarm_arbitration import ZKFaultProofEngine, SwarmDisputeArbitrator
except ImportError:
    SovereignAgentPassport = None
    AutonomousEscrowPool = None
    ZKFaultProofEngine = None
    SwarmDisputeArbitrator = None


def btp_autogen_guard(
    fn: Callable = None, 
    *, 
    spend_cap: float = 50.0, 
    strict: bool = True,
    escrow_collateral_usd: Optional[float] = None,
    passport: Optional[Any] = None,
    action_type: str = "AUTOGEN_TOOL_EXEC",
    settlement_rail: str = "L402_LIGHTNING",
    payee_destination: Optional[str] = None
):
    """
    Decorator for AutoGen agent tool calls or register_for_execution functions.
    Inspects tool inputs for malicious payload / command injection prior to dispatch,
    with automated micro-escrow collateral staking and Byzantine swarm slashing.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Sovereign Passport Check
            if passport is not None:
                if getattr(passport, "is_circuit_broken", False):
                    raise PermissionError(
                        f"[BTP-VETO] AutoGen agent passport '{passport.agent_id}' is CIRCUIT-BROKEN (Revoked)."
                    )

            # 2. Autonomous Escrow Collateral Lock
            pool = None
            deposit = None
            if escrow_collateral_usd and escrow_collateral_usd > 0 and AutonomousEscrowPool is not None:
                pool = AutonomousEscrowPool()
                agent_id = getattr(passport, "agent_id", "Agent-AutoGen-Worker")
                deposit = pool.lock_escrow(
                    agent_id=agent_id,
                    action_type=action_type,
                    amount_usd=escrow_collateral_usd,
                    passport=passport,
                    settlement_rail=settlement_rail
                )

            # 3. Local AST Invariant Evaluation
            if Guard is not None:
                guard = Guard(spend_cap=spend_cap, strict=strict)
                for arg in args:
                    if isinstance(arg, str):
                        res = guard.evaluate_ast(arg)
                        if not res.get("allowed", True):
                            if pool and deposit and ZKFaultProofEngine is not None:
                                zk_proof = ZKFaultProofEngine.generate_fault_proof(
                                    prover_agent_id="agent-autogen-sentinel",
                                    target_action=action_type,
                                    violated_invariant=res.get("rule_id", "BTP-AST-001"),
                                    private_payload=arg,
                                    state_pre_hash=deposit.l402_challenge.get("payment_hash", f"pre_{deposit.escrow_id}") if deposit.l402_challenge else f"pre_{deposit.escrow_id}"
                                )
                                arb = pool.arbitrator
                                ok_d, msg_d, dispute = arb.open_dispute(
                                    escrow_id=deposit.escrow_id,
                                    challenger_agent_id="agent-autogen-sentinel",
                                    target_agent_id=deposit.agent_id,
                                    target_action=action_type,
                                    amount_usd=deposit.amount_usd,
                                    fault_proof=zk_proof.to_dict(),
                                    required_quorum=1
                                )
                                if ok_d:
                                    from src.agent_passport import SovereignAgentPassport
                                    monitor_pass1 = SovereignAgentPassport.issue(
                                        agent_id="agent-juror-autogen-1",
                                        model_family="claude-3-5-sonnet",
                                        authorized_capabilities=["audit:verify"]
                                    )
                                    monitor_pass2 = SovereignAgentPassport.issue(
                                        agent_id="agent-juror-autogen-2",
                                        model_family="gemini-1-5-pro",
                                        authorized_capabilities=["audit:verify"]
                                    )
                                    arb.register_validator(monitor_pass1)
                                    arb.register_validator(monitor_pass2)
                                    arb.cast_vote(dispute.dispute_id, monitor_pass1, "APPROVE_SLASH")
                                    arb.cast_vote(dispute.dispute_id, monitor_pass2, "APPROVE_SLASH")
                                    ok_r, msg_r, cert = arb.resolve_dispute(dispute.dispute_id)
                                    if ok_r:
                                        pool.arbitrate_and_slash(
                                            escrow_id=deposit.escrow_id,
                                            arbitration_cert=cert,
                                            payee_destination=payee_destination or "payee_treasury_vault",
                                            agent_passport=passport
                                        )

                            raise PermissionError(f"[BTP-VETO] AutoGen tool '{func.__name__}' execution blocked: {res.get('reason')}")

                for k, v in kwargs.items():
                    if isinstance(v, str):
                        res = guard.evaluate_ast(v)
                        if not res.get("allowed", True):
                            raise PermissionError(f"[BTP-VETO] AutoGen tool '{func.__name__}' argument '{k}' blocked: {res.get('reason')}")

            # 4. Safe Execution
            try:
                result = func(*args, **kwargs)
                if pool and deposit:
                    pool.release_escrow(deposit.escrow_id)
                    if passport is not None:
                        passport.record_action(volume_usd=escrow_collateral_usd)
                return result
            except Exception as exc:
                if pool and deposit and deposit.status == "LOCKED":
                    pool.release_escrow(deposit.escrow_id)
                raise exc

        return wrapper

    if fn is not None:
        return decorator(fn)
    return decorator


class AutoGenBTPInterceptor:
    """
    Intercepts and validates incoming AutoGen agent messages before tool execution,
    evaluating sovereign passport reputation and invariant compliance.
    
    Usage:
        interceptor = AutoGenBTPInterceptor(trusted_authorities=[ROOT_KEY], passport=my_passport)
        safe_msg = interceptor.intercept_message(inbound_message)
    """
    def __init__(self, 
                 trusted_authorities: List[str] = None, 
                 recipient_id: str = "Agent-AutoGen-Worker",
                 enforce_strict: bool = True,
                 passport: Optional[Any] = None):
        self.trusted_authorities = trusted_authorities or []
        self.recipient_id = recipient_id
        self.enforce_strict = enforce_strict
        self.passport = passport
        self.seen_nonces = set()
        self.guard = Guard() if Guard else None

    def intercept_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Validates incoming message envelope 100% offline."""
        if self.passport is not None and getattr(self.passport, "is_circuit_broken", False):
            return {
                "role": "system",
                "content": f"[BTP_SECURITY_ALERT] Message rejected: Passport '{self.passport.agent_id}' is CIRCUIT-BROKEN.",
                "status": "DENIED"
            }

        content = message.get("content", "")
        
        # 1. AST Invariant Check on raw content if text command
        if self.guard and isinstance(content, str):
            res = self.guard.evaluate_ast(content)
            if not res.get("allowed", True):
                return {
                    "role": "system",
                    "content": f"[BTP_SECURITY_ALERT] Blocked destructive agent payload: {res.get('reason')}",
                    "status": "DENIED"
                }

        # 2. Offline cryptographic receipt verification if envelope present
        if "btp_envelope" in message:
            envelope = message["btp_envelope"]
            payload = message.get("content", {})
            if independent_verify_btp_receipt is not None and self.trusted_authorities:
                ok, msg = independent_verify_btp_receipt(
                    receipt_json_str=envelope,
                    candidate_payload=payload,
                    trusted_root_pubkeys=self.trusted_authorities,
                    expected_recipient_context=self.recipient_id,
                    seen_nonces=self.seen_nonces
                )
                if not ok:
                    return {
                        "role": "system",
                        "content": f"[BTP_SECURITY_ALERT] Inbound message attestation failed: {msg}. Execution halted.",
                        "status": "DENIED"
                    }
        elif self.enforce_strict and message.get("action_type") in ["EXEC_COMMAND", "DEPLOY_PATCH", "SQL_EXEC"]:
            return {
                "role": "system",
                "content": "[BTP_SECURITY_ALERT] Unattested high-privilege action rejected.",
                "status": "DENIED"
            }
        return message
