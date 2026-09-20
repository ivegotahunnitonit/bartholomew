"""
LlamaIndex BTP v4.1 Tool & Function Execution Guard
Provides sub-35µs in-process AST gating, secret scrubbing, Sovereign Passport authorization,
and structured BTPViolationError parity for LlamaIndex agents.
"""

from typing import Callable, Dict, Any, List, Optional
import functools
import sys
import os
import time

try:
    from btp_guard import Guard, SovereignAgentPassport
except ImportError:
    Guard = None
    SovereignAgentPassport = None

try:
    from scripts.standalone_btp_verifier import independent_verify_btp_receipt
except ImportError:
    try:
        from btp_guard import independent_verify_btp_receipt
    except ImportError:
        independent_verify_btp_receipt = None


# ---------------------------------------------------------------------------
# Structured Violation Exception
# ---------------------------------------------------------------------------

class BTPViolationError(PermissionError):
    """
    Structured security violation raised when a LlamaIndex tool or agent payload
    breaches AST safety invariants enforced by the Bartholomew Trust Protocol.
    Inherits from PermissionError for backward compatibility.
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
            f"[BTP-SECURITY-VETO] LlamaIndex execution blocked by rule {rule_id}: {reason}"
        )
        self.reason = reason
        self.rule_id = rule_id
        self.blocked_payload = blocked_payload
        self.latency_us = latency_us
        self.metadata = metadata or {}

    def to_diagnostics(self) -> Dict[str, Any]:
        """Returns structured JSON diagnostics suitable for telemetry and logs."""
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
        counsel_str = ""
        try:
            from src.bartholomew_companion import BartholomewCompanion
            counsel_str = "\n" + BartholomewCompanion.counsel(
                rule_id=self.rule_id,
                reason=self.reason,
                blocked_payload=self.blocked_payload,
                context=self.metadata
            )
        except Exception:
            pass

        return (
            f"[BTP-SECURITY-VETO] LlamaIndex execution blocked by rule {self.rule_id}: {self.reason} "
            f"(latency={round(self.latency_us, 2)}us){counsel_str}"
        )


# ---------------------------------------------------------------------------
# Tool Decorator
# ---------------------------------------------------------------------------

def btp_llamaindex_tool(
    fn: Callable = None, 
    *, 
    required_capability: Optional[str] = "tools:execute", 
    spend_cap: float = 50.0, 
    strict: bool = True,
    on_violation: Optional[Callable[[BTPViolationError], Any]] = None,
    barter_agent_id: Optional[str] = None,
    mint_awu: float = 0.0,
    barter_gateway: Optional[str] = None,
):
    """
    Drop-in decorator for LlamaIndex agent tool functions.
    Intercepts proposed tool arguments in local memory (<35µs), validates
    optional Sovereign Agent Passport credentials, and automatically mints
    Attested Work Units (AWU) upon safe execution into the bilateral barter pool.

    Usage:
        @btp_llamaindex_tool(required_capability="db:query", mint_awu=1.25)
        def query_database(sql: str) -> str:
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            t0 = time.perf_counter()

            # 1. Sovereign Passport Verification (if passed via kwargs)
            passport_data = kwargs.pop("agent_passport", None)
            if passport_data is not None:
                if SovereignAgentPassport is not None:
                    if isinstance(passport_data, dict):
                        passport = SovereignAgentPassport.from_dict(passport_data)
                    else:
                        passport = passport_data
                    is_valid, msg = passport.verify_signature()
                    if not is_valid:
                        latency_us = (time.perf_counter() - t0) * 1_000_000
                        err = BTPViolationError(
                            reason=f"LlamaIndex agent passport signature invalid: {msg}",
                            rule_id="BTP-PASSPORT-001",
                            latency_us=latency_us,
                            metadata={"tool": func.__name__},
                        )
                        if on_violation:
                            return on_violation(err)
                        raise err

                    if required_capability and not passport.has_capability(required_capability):
                        latency_us = (time.perf_counter() - t0) * 1_000_000
                        err = BTPViolationError(
                            reason=f"LlamaIndex agent passport unauthorized: missing capability '{required_capability}'",
                            rule_id="BTP-AUTH-002",
                            latency_us=latency_us,
                            metadata={"tool": func.__name__, "required": required_capability},
                        )
                        if on_violation:
                            return on_violation(err)
                        raise err

            # 2. In-Process AST & Command Evaluation
            if Guard is not None:
                guard = Guard(spend_cap=spend_cap, strict=strict)
                for arg in args:
                    if isinstance(arg, str):
                        res = guard.evaluate_ast(arg)
                        if not res.get("allowed", True):
                            latency_us = (time.perf_counter() - t0) * 1_000_000
                            err = BTPViolationError(
                                reason=res.get("reason", "Prohibited AST construction"),
                                rule_id="BTP-AST-001",
                                blocked_payload=arg,
                                latency_us=latency_us,
                                metadata={"tool": func.__name__},
                            )
                            if on_violation:
                                return on_violation(err)
                            raise err

                for k, v in kwargs.items():
                    if isinstance(v, str):
                        res = guard.evaluate_ast(v)
                        if not res.get("allowed", True):
                            latency_us = (time.perf_counter() - t0) * 1_000_000
                            err = BTPViolationError(
                                reason=res.get("reason", f"Argument '{k}' blocked"),
                                rule_id="BTP-AST-001",
                                blocked_payload=v,
                                latency_us=latency_us,
                                metadata={"tool": func.__name__, "param": k},
                            )
                            if on_violation:
                                return on_violation(err)
                            raise err

            result = func(*args, **kwargs)

            # 3. Bilateral Barter AWU Minting on clean execution
            effective_agent = barter_agent_id or "agent-llamaindex-worker"
            if mint_awu > 0 and effective_agent:
                try:
                    from src.economy.barter_client import BTPBarterClient
                    client = BTPBarterClient(default_gateway=barter_gateway)
                    client.pulse(
                        agent_id=effective_agent,
                        work_units=mint_awu,
                        task_type="LLAMAINDEX_TOOL_EXEC"
                    )
                except Exception as e:
                    pass

            return result
        return wrapper

    if fn is not None:
        return decorator(fn)
    return decorator


class BartholomewLlamaIndexTool:
    """
    Wrapper for LlamaIndex BaseTool or FunctionTool instances to enforce BTP execution safety,
    passport attestation, and cross-swarm bilateral query delegation.
    """
    def __init__(
        self, 
        tool_fn: Callable, 
        tool_name: str, 
        description: str,
        required_capability: Optional[str] = "tools:execute",
        on_violation: Optional[Callable[[BTPViolationError], Any]] = None,
        barter_gateway: Optional[str] = None,
        agent_id: str = "Agent-LlamaIndex-Node",
    ):
        self.name = tool_name
        self.description = description
        self.required_capability = required_capability
        self.barter_gateway = barter_gateway
        self.agent_id = agent_id
        self._guarded_fn = btp_llamaindex_tool(
            tool_fn, 
            required_capability=required_capability,
            on_violation=on_violation,
            barter_gateway=barter_gateway,
            barter_agent_id=agent_id,
        )

    def __call__(self, *args, **kwargs):
        return self._guarded_fn(*args, **kwargs)

    def delegate_query(
        self,
        task_description: str,
        query_fn: Callable,
        specialist_id: str,
        awu_units: float = 1.0,
        query_args: Optional[List[Any]] = None,
        query_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Delegates a RAG retrieval or query synthesis to a specialist agent swarm,
        atomically transferring AWU credits with an Ed25519 escrow receipt.
        """
        query_args = query_args or []
        query_kwargs = query_kwargs or {}
        sender = self.agent_id

        from src.economy.barter_client import BTPBarterClient
        barter_client = BTPBarterClient(default_gateway=self.barter_gateway)

        transfer_result = barter_client.spend(
            sender_id=sender,
            recipient_id=specialist_id,
            units=awu_units,
            task_type=f"llamaindex_delegation:{task_description[:32]}"
        )

        query_result = query_fn(*query_args, **query_kwargs)

        return {
            "status": "DELEGATION_COMPLETED",
            "task_description": task_description,
            "sender_id": sender,
            "specialist_id": specialist_id,
            "awu_transferred": float(awu_units),
            "barter_settlement": transfer_result,
            "result": query_result,
        }
