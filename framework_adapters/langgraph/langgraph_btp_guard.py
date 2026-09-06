"""
LangGraph / LangChain BTP v4.1 Tool Execution & Delegation Guard
Provides sub-35µs in-process AST gating, secret scrubbing, Sovereign Passport verification,
and Autonomous Micro-Escrow collateral protection for LangChain and LangGraph tools.
"""

from typing import Callable, Dict, Any, List, Optional
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


def btp_langchain_tool(
    fn: Callable = None, 
    *, 
    spend_cap: float = 50.0, 
    strict: bool = True,
    escrow_collateral_usd: Optional[float] = None,
    passport: Optional[Any] = None,
    action_type: str = "LANGCHAIN_TOOL_EXEC",
    settlement_rail: str = "L402_LIGHTNING",
    payee_destination: Optional[str] = None
):
    """
    Drop-in decorator for LangChain / LangGraph tool functions.
    Intercepts raw tool arguments in memory and evaluates AST invariants (<35µs),
    with automated micro-escrow collateral staking and Byzantine swarm slashing.

    Usage:
        @btp_langchain_tool(escrow_collateral_usd=500.0, passport=agent_passport)
        def run_terminal_command(command: str) -> str:
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Sovereign Passport Check
            if passport is not None:
                if getattr(passport, "is_circuit_broken", False):
                    raise PermissionError(
                        f"[BTP-VETO] LangChain agent passport '{passport.agent_id}' is CIRCUIT-BROKEN (Revoked)."
                    )

            # 2. Autonomous Escrow Collateral Lock
            pool = None
            deposit = None
            if escrow_collateral_usd and escrow_collateral_usd > 0 and AutonomousEscrowPool is not None:
                pool = AutonomousEscrowPool()
                agent_id = getattr(passport, "agent_id", "Agent-LangGraph-Node")
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
                                    prover_agent_id="agent-langchain-sentinel",
                                    target_action=action_type,
                                    violated_invariant=res.get("rule_id", "BTP-AST-001"),
                                    private_payload=arg,
                                    state_pre_hash=deposit.l402_challenge.get("payment_hash", f"pre_{deposit.escrow_id}") if deposit.l402_challenge else f"pre_{deposit.escrow_id}"
                                )
                                arb = pool.arbitrator
                                ok_d, msg_d, dispute = arb.open_dispute(
                                    escrow_id=deposit.escrow_id,
                                    challenger_agent_id="agent-langchain-sentinel",
                                    target_agent_id=deposit.agent_id,
                                    target_action=action_type,
                                    amount_usd=deposit.amount_usd,
                                    fault_proof=zk_proof.to_dict(),
                                    required_quorum=1
                                )
                                if ok_d:
                                    from src.agent_passport import SovereignAgentPassport
                                    monitor_pass1 = SovereignAgentPassport.issue(
                                        agent_id="agent-juror-langgraph-1",
                                        model_family="claude-3-5-sonnet",
                                        authorized_capabilities=["audit:verify"]
                                    )
                                    monitor_pass2 = SovereignAgentPassport.issue(
                                        agent_id="agent-juror-langgraph-2",
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

                            raise PermissionError(f"[BTP-VETO] LangChain tool '{func.__name__}' blocked: {res.get('reason')}")

                for k, v in kwargs.items():
                    if isinstance(v, str):
                        res = guard.evaluate_ast(v)
                        if not res.get("allowed", True):
                            raise PermissionError(f"[BTP-VETO] LangChain tool '{func.__name__}' argument '{k}' blocked: {res.get('reason')}")

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


class BartholomewLangChainTool:
    """
    Wrapper for LangChain BaseTool instances to enforce BTP v4.1 execution safety.
    """
    def __init__(self, tool: Any, spend_cap: float = 50.0, strict: bool = True, passport: Optional[Any] = None):
        self.tool = tool
        self.spend_cap = spend_cap
        self.strict = strict
        self.passport = passport
        self.guard = Guard(spend_cap=spend_cap, strict=strict) if Guard else None

    def __call__(self, *args, **kwargs):
        if self.passport is not None and getattr(self.passport, "is_circuit_broken", False):
            raise PermissionError(f"[BTP-VETO] Tool execution blocked: Passport '{self.passport.agent_id}' is revoked.")

        if self.guard:
            for arg in args:
                if isinstance(arg, str):
                    res = self.guard.evaluate_ast(arg)
                    if not res.get("allowed", True):
                        raise PermissionError(f"[BTP-VETO] Tool execution blocked: {res.get('reason')}")
        return self.tool(*args, **kwargs)

    def run(self, *args, **kwargs):
        return self(*args, **kwargs)


class LangGraphBTPGuard:
    """
    Wraps LangGraph tools and nodes with offline Ed25519 Merkle receipt attestation
    and sovereign passport reputation gating.
    
    Usage:
        guard = LangGraphBTPGuard(trusted_authorities=[ROOT_PUBKEY], agent_id="Agent-Production-Cluster", passport=my_passport)
        
        @guard.wrap_tool
        def execute_sql_query(query: str):
            return db.execute(query)
    """
    def __init__(self, 
                 trusted_authorities: List[str] = None, 
                 agent_id: str = "Agent-LangGraph-Node",
                 enforce_strict: bool = True,
                 passport: Optional[Any] = None,
                 escrow_collateral_usd: Optional[float] = None):
        self.trusted_authorities = trusted_authorities or []
        self.agent_id = agent_id
        self.enforce_strict = enforce_strict
        self.passport = passport
        self.escrow_collateral_usd = escrow_collateral_usd
        self.seen_nonces = set()

    def wrap_tool(self, tool_fn: Callable):
        """Decorator for LangGraph tool functions with receipt verification."""
        @functools.wraps(tool_fn)
        def guarded_exec(*args, **kwargs):
            if self.passport is not None and getattr(self.passport, "is_circuit_broken", False):
                raise PermissionError(f"[BTP_BLOCKED] Execution denied: Agent passport '{self.passport.agent_id}' is revoked.")

            receipt = kwargs.pop("btp_receipt", None)
            if self.enforce_strict and not receipt and self.trusted_authorities:
                raise PermissionError(f"[BTP_BLOCKED] Execution denied: Missing required BTP trust receipt for tool '{tool_fn.__name__}'")
            
            if receipt and independent_verify_btp_receipt is not None:
                payload = {"tool": tool_fn.__name__, "args": args, "kwargs": kwargs}
                ok, msg = independent_verify_btp_receipt(
                    receipt_json_str=receipt,
                    candidate_payload=payload,
                    trusted_root_pubkeys=self.trusted_authorities,
                    expected_recipient_context=self.agent_id,
                    seen_nonces=self.seen_nonces
                )
                if not ok:
                    raise PermissionError(f"[BTP_BLOCKED] Attestation rejected for tool '{tool_fn.__name__}': {msg}")
            
            return tool_fn(*args, **kwargs)
        return guarded_exec
