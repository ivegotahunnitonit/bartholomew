"""
Universal BTP Model Guard: Multi-Provider Wire-Level Safety & Settlement Interceptor.
Provides uniform AST gating, secret scrubbing, Sovereign Passport circuit breakers,
and Micro-Escrow collateral protection for:
  - OpenAI (GPT-4o, GPT-4-turbo)
  - Moonshot Kimi (moonshot-v1-*)
  - DeepSeek (deepseek-chat, deepseek-coder)
  - Anthropic Claude (claude-3-5-sonnet, claude-3-opus)
  - Google Gemini (gemini-1.5-pro, gemini-1.5-flash)
  - Local / Ollama / vLLM (OpenAI-compatible / native JSON)
"""

import json
import time
import functools
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Union

try:
    from btp_guard import Guard, WireGuard
    from src.polyglot_ast_validator import PolyglotASTValidator
except ImportError:
    Guard = None
    WireGuard = None
    PolyglotASTValidator = None

try:
    from src.agent_passport import SovereignAgentPassport
    from src.settlement.autonomous_escrow import AutonomousEscrowPool
    from src.settlement.swarm_arbitration import ZKFaultProofEngine, SwarmDisputeArbitrator
    from src.alerting.webhook_dispatcher import (
        WebhookDispatcher,
        IncidentEvent,
        IncidentEventType,
        AlertSeverity,
    )
except ImportError:
    SovereignAgentPassport = None
    AutonomousEscrowPool = None
    ZKFaultProofEngine = None
    SwarmDisputeArbitrator = None
    WebhookDispatcher = None
    IncidentEvent = None
    IncidentEventType = None
    AlertSeverity = None


try:
    from src.bartholomew_companion import BartholomewCompanion
except ImportError:
    BartholomewCompanion = None


class ModelProvider:
    OPENAI = "openai"
    GPT_ASTRA = "gpt_astra"
    OPENAI_AGENTS_SDK = "openai_agents_sdk"
    ANTHROPIC = "anthropic"
    CLAUDE_3_7 = "claude_3_7"
    GEMINI = "gemini"
    GEMINI_2 = "gemini_2"
    GEMINI_3 = "gemini_3"
    GEMINI_3_8 = "gemini_3_8"
    DEEPSEEK = "deepseek"
    DEEPSEEK_R1 = "deepseek_r1"
    YANDEX = "yandex"
    YANDEX_GPT = "yandex_gpt"
    KIMI = "kimi"
    OLLAMA = "ollama"
    UNIVERSAL = "universal"


class UniversalBTPModelGuard:
    """
    Universal wire-level interceptor that accepts raw tool-call objects or dictionaries
    emitted by any major LLM provider, normalizes them into an invariant payload,
    and applies sub-35µs local AST gating, Bartholomew companion counsel, and autonomous micro-escrows.
    Supports GPT-Astra, Claude 3.7 (Hybrid Reasoning), Gemini 2.0, DeepSeek-R1, and OpenAI Agents SDK.
    """

    def __init__(
        self,
        spend_cap: float = 50.0,
        strict: bool = True,
        escrow_collateral_usd: Optional[float] = None,
        passport: Optional[Any] = None,
        settlement_rail: str = "L402_LIGHTNING",
        payee_destination: Optional[str] = None,
        org_id: str = "default_org",
        project_id: str = "default_project",
        environment: str = "dev",
        webhook_dispatcher: Optional[Any] = None,
        use_wire: bool = False,
        wire_endpoint: Optional[str] = None,
    ):
        import os
        self.spend_cap = spend_cap
        self.strict = strict
        self.escrow_collateral_usd = escrow_collateral_usd
        self.passport = passport
        self.settlement_rail = settlement_rail
        self.payee_destination = payee_destination
        self.org_id = org_id.lower().strip()
        self.project_id = project_id.lower().strip()
        self.environment = environment.lower().strip()
        self.tenant_id = f"ten_{hashlib.sha256(f'{self.org_id}:{self.project_id}:{self.environment}'.encode()).hexdigest()[:24]}"
        self.use_wire = use_wire or (os.getenv("BTP_USE_WIRE", "0") == "1")
        self.wire_guard = WireGuard(endpoint=wire_endpoint) if (self.use_wire and WireGuard is not None) else None
        self._guard = Guard() if Guard is not None else None
        self._escrow_pool = AutonomousEscrowPool() if AutonomousEscrowPool is not None else None
        self._zk_engine = ZKFaultProofEngine() if ZKFaultProofEngine is not None else None
        self._arbitrator = SwarmDisputeArbitrator() if SwarmDisputeArbitrator is not None else None
        self.webhook_dispatcher = webhook_dispatcher or (WebhookDispatcher() if WebhookDispatcher is not None else None)

    def normalize_tool_call(
        self, 
        tool_call: Union[Dict[str, Any], Any],
        provider: str = ModelProvider.UNIVERSAL
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Normalizes a provider-specific tool call payload into (tool_name, arguments_dict).
        Supports dicts or objects with attributes across GPT-Astra, Claude 3.7, Gemini 2.0,
        DeepSeek-R1, and OpenAI Agents SDK.
        """
        # Convert object to dict if needed
        if not isinstance(tool_call, dict):
            if hasattr(tool_call, "model_dump"):
                data = tool_call.model_dump()
            elif hasattr(tool_call, "__dict__"):
                data = tool_call.__dict__
            else:
                data = {"raw": str(tool_call)}
        else:
            data = tool_call

        # Unwrap chat completion message or tool_calls array if present (e.g. YandexGPT, OpenAI)
        if "message" in data and isinstance(data["message"], dict):
            data = data["message"]
        if "tool_calls" in data and isinstance(data["tool_calls"], list) and len(data["tool_calls"]) > 0:
            data = data["tool_calls"][0]

        # 1. Anthropic Claude 3.7 / 3.5 Content Array (with Hybrid Thinking Blocks):
        # {"content": [{"type": "thinking", "thinking": "..."}, {"type": "tool_use", "name": "...", "input": {...}}]}
        if "content" in data and isinstance(data["content"], list):
            for block in data["content"]:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    return block.get("name", ""), block.get("input", {})

        # 2. Anthropic Direct Tool Use: {"type": "tool_use", "name": "...", "input": {...}}
        if data.get("type") == "tool_use" or ("name" in data and "input" in data):
            tool_name = data.get("name", "")
            raw_input = data.get("input", {})
            args = raw_input if isinstance(raw_input, dict) else {"payload": str(raw_input)}
            return tool_name, args

        # 3. Google Gemini 3.8 / 3.0 / 2.0 / 1.5 FunctionCall & Thought Part Structure:
        # e.g., {"candidates": [{"content": {"parts": [{"thought": "..."}, {"functionCall": {"name": "...", "args": {...}}}]}}]}
        if "parts" in data and isinstance(data["parts"], list):
            for part in data["parts"]:
                if isinstance(part, dict) and ("functionCall" in part or "function_call" in part):
                    fc = part.get("functionCall") or part.get("function_call") or {}
                    tool_name = fc.get("name", "")
                    raw_args = fc.get("args") or fc.get("arguments") or {}
                    args = raw_args if isinstance(raw_args, dict) else {"payload": str(raw_args)}
                    return tool_name, args

        if "functionCall" in data or "function_call" in data:
            fc = data.get("functionCall") or data.get("function_call") or {}
            tool_name = fc.get("name", "")
            raw_args = fc.get("args") or fc.get("arguments") or {}
            if isinstance(raw_args, str):
                try:
                    args = json.loads(raw_args)
                except Exception:
                    args = {"payload": raw_args}
            else:
                args = raw_args
            return tool_name, args

        # 4. OpenAI Agents SDK format: {"tool_name": "...", "tool_arguments": {...}}
        if "tool_name" in data and ("tool_arguments" in data or "arguments" in data):
            tool_name = data.get("tool_name", "")
            raw_args = data.get("tool_arguments") or data.get("arguments") or {}
            args = raw_args if isinstance(raw_args, dict) else {"payload": str(raw_args)}
            return tool_name, args

        # 5. OpenAI / GPT-Astra / DeepSeek / Ollama standard format:
        # {"id": "...", "type": "function", "function": {"name": "...", "arguments": "{...}"}}
        if "function" in data and isinstance(data["function"], dict):
            fn = data["function"]
            tool_name = fn.get("name", "")
            raw_args = fn.get("arguments", {})
            if isinstance(raw_args, str):
                # Clean DeepSeek-R1 / reasoning scratchpad if embedded
                clean_str = raw_args
                if "<think>" in clean_str and "</think>" in clean_str:
                    clean_str = clean_str.split("</think>")[-1].strip()
                try:
                    args = json.loads(clean_str)
                except Exception:
                    args = {"payload": clean_str}
            elif isinstance(raw_args, dict):
                args = raw_args
            else:
                args = {"payload": str(raw_args)}
            return tool_name, args

        # 6. Flat / Direct format: {"name": "...", "arguments": {...}}
        if "name" in data and ("arguments" in data or "args" in data or "parameters" in data):
            tool_name = data.get("name", "")
            raw_args = data.get("arguments") or data.get("args") or data.get("parameters") or {}
            if isinstance(raw_args, str):
                try:
                    args = json.loads(raw_args)
                except Exception:
                    args = {"payload": raw_args}
            else:
                args = raw_args
            return tool_name, args

        # 7. Fallback generic
        tool_name = data.get("name", "unknown_tool")
        return tool_name, {k: v for k, v in data.items() if k != "name"}

    def intercept_and_verify(
        self,
        tool_call: Union[Dict[str, Any], Any],
        provider: str = ModelProvider.UNIVERSAL,
        action_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Intercepts tool call wire payload, validates against Sovereign Passport
        and sub-35µs AST invariants, and manages micro-escrow collateral.
        Returns a verification record dict with status: 'APPROVED' or 'VETOED'.
        """
        start_ns = time.perf_counter_ns()
        tool_name, arguments = self.normalize_tool_call(tool_call, provider)
        resolved_action = action_type or f"{provider.upper()}_{tool_name.upper()}"

        # 1. Check Sovereign Passport & Circuit Breaker
        if self.passport is not None:
            if getattr(self.passport, "is_circuit_broken", False):
                raise PermissionError(
                    f"BTP Universal Guard: Passport {self.passport.agent_id} circuit breaker is ACTIVE. "
                    "All tool calls permanently vetoed."
                )

        # 2. Lock Collateral if configured
        deposit = None
        if self.escrow_collateral_usd is not None and self._escrow_pool is not None:
            agent_id = getattr(self.passport, "agent_id", f"agent-{provider}-universal")
            deposit = self._escrow_pool.lock_escrow(
                agent_id=agent_id,
                action_type=resolved_action,
                amount_usd=self.escrow_collateral_usd,
                passport=self.passport,
                settlement_rail=self.settlement_rail
            )

        # 3. Fast In-Process AST & Safety Inspection (<35us)
        serialized_args = json.dumps(arguments)
        is_safe = True
        violation_rule = None
        upper_payload = serialized_args.upper()

        if any(kw in upper_payload for kw in ["DROP TABLE", "DROP DATABASE", "TRUNCATE TABLE", "DELETE FROM", "ALTER TABLE"]):
            is_safe = False
            violation_rule = "UNAUTHORIZED_DESTRUCTIVE_SQL_MUTATION"
        elif any(kw in upper_payload for kw in ["RM -RF /", "RM -RF /*", ":(){ :|:& };:", "/ETC/PASSWD", "/ETC/SHADOW", "| NC ", "| NETCAT", "CURL -S", "WGET "]):
            is_safe = False
            violation_rule = "DESTRUCTIVE_OS_COMMAND_INJECTION"
        elif any(kw in upper_payload for kw in ["AWS_SECRET_ACCESS_KEY", "PRIVATE_KEY", "ID_RSA", "BEARER EY"]):
            is_safe = False
            violation_rule = "CREDENTIAL_EXFILTRATION_BREACH"
        elif self._guard is not None or PolyglotASTValidator is not None:
            for k, val in arguments.items():
                if isinstance(val, str) and len(val) > 2:
                    if hasattr(self._guard, "evaluate_ast"):
                        res = self._guard.evaluate_ast(val)
                    elif hasattr(self._guard, "check"):
                        res = self._guard.check(val)
                    elif PolyglotASTValidator is not None:
                        safe_ast, r_ast, _ = PolyglotASTValidator.validate_code(val)
                        res = {"allowed": safe_ast, "reason": r_ast, "rule_id": "BTP-AST-001"}
                    else:
                        res = {"allowed": True}
                    if not res.get("allowed", True):
                        is_safe = False
                        violation_rule = res.get("rule_id", "BTP-AST-001")
                        break

        # 4. Optional Cloud Run Wire-Level Verification (BTP v5.4.6)
        if is_safe and self.wire_guard is not None:
            wire_res = self.wire_guard.verify_tool(tool_name, arguments)
            if wire_res.get("status") == "VETOED":
                is_safe = False
                violation_rule = wire_res.get("violation", "BTP-WIRE-VETO")

        latency_us = (time.perf_counter_ns() - start_ns) / 1_000.0

        if not is_safe:
            dispute_id = None
            proof_data = None
            if deposit is not None and self._escrow_pool is not None and ZKFaultProofEngine is not None:
                arb = self._escrow_pool.arbitrator
                zk_proof = ZKFaultProofEngine.generate_fault_proof(
                    prover_agent_id="agent-monitor-guard",
                    target_action=resolved_action,
                    violated_invariant=violation_rule or "UNIVERSAL_INVARIANT_VIOLATION",
                    private_payload=serialized_args,
                    state_pre_hash=deposit.l402_challenge.get("payment_hash", f"pre_{deposit.escrow_id}") if deposit.l402_challenge else f"pre_{deposit.escrow_id}"
                )
                proof_data = zk_proof.to_dict()

                ok_d, msg_d, dispute = arb.open_dispute(
                    escrow_id=deposit.escrow_id,
                    challenger_agent_id="agent-monitor-guard",
                    target_agent_id=deposit.agent_id,
                    target_action=resolved_action,
                    amount_usd=deposit.amount_usd,
                    fault_proof=proof_data,
                    required_quorum=1
                )
                if ok_d:
                    dispute_id = dispute.dispute_id
                    monitor_pass1 = SovereignAgentPassport.issue(
                        agent_id=f"agent-juror-sentinel-{provider}-1",
                        model_family="claude-3-5-sonnet",
                        authorized_capabilities=["audit:verify"],
                        org_id=self.org_id,
                        project_id=self.project_id,
                        environment=self.environment
                    )
                    monitor_pass2 = SovereignAgentPassport.issue(
                        agent_id=f"agent-juror-sentinel-{provider}-2",
                        model_family="gemini-1-5-pro",
                        authorized_capabilities=["audit:verify"],
                        org_id=self.org_id,
                        project_id=self.project_id,
                        environment=self.environment
                    )
                    arb.register_validator(monitor_pass1)
                    arb.register_validator(monitor_pass2)
                    arb.cast_vote(dispute.dispute_id, monitor_pass1, "APPROVE_SLASH")
                    arb.cast_vote(dispute.dispute_id, monitor_pass2, "APPROVE_SLASH")
                    ok_r, msg_r, cert = arb.resolve_dispute(dispute.dispute_id)
                    if ok_r:
                        self._escrow_pool.arbitrate_and_slash(
                            escrow_id=deposit.escrow_id,
                            arbitration_cert=cert,
                            payee_destination=self.payee_destination or "payee_treasury_vault",
                            agent_passport=self.passport
                        )

            if self.passport is not None:
                self.passport.is_circuit_broken = True
                if hasattr(self.passport, "violations_count"):
                    self.passport.violations_count += 1

            # Milestone 5.1: Emit Incident Event to SecOps Webhooks
            if self.webhook_dispatcher is not None and IncidentEvent is not None:
                try:
                    evt_id = f"evt_{hashlib.sha256(f'{self.tenant_id}:{time.time_ns()}'.encode()).hexdigest()[:16]}"
                    incident = IncidentEvent(
                        event_id=evt_id,
                        tenant_id=self.tenant_id,
                        org_id=self.org_id,
                        project_id=self.project_id,
                        environment=self.environment,
                        event_type=IncidentEventType.AST_VETO,
                        severity=AlertSeverity.CRITICAL if deposit is not None else AlertSeverity.HIGH,
                        title=f"Invariant Veto: {violation_rule}",
                        description=f"Rogue tool call '{tool_name}' blocked under invariant rule '{violation_rule}'.",
                        agent_id=getattr(self.passport, "agent_id", f"agent-{provider}-universal"),
                        tool_name=tool_name,
                        target_payload=json.dumps(arguments) if isinstance(arguments, dict) else str(arguments),
                        slashed_amount_usd=self.escrow_collateral_usd if deposit else None,
                        metadata={
                            "provider": provider,
                            "latency_us": latency_us,
                            "dispute_id": dispute_id,
                            "rule": violation_rule
                        }
                    )
                    self.webhook_dispatcher.emit_incident(incident)
                except Exception:
                    pass

            counsel_msg = ""
            if BartholomewCompanion is not None:
                counsel_msg = BartholomewCompanion.counsel(
                    rule_id=violation_rule or "BTP-AST-001",
                    reason=f"Invariant violation '{violation_rule}' in tool '{tool_name}'",
                    blocked_payload=serialized_args
                )

            err_msg = (
                f"BTP Universal Guard VETO [{provider.upper()}]: Tool call '{tool_name}' violated invariant "
                f"'{violation_rule}'. AST latency: {latency_us:.2f}µs."
            )
            if counsel_msg:
                err_msg += f"\n{counsel_msg}"

            if self.strict:
                raise PermissionError(err_msg)
            return {
                "status": "VETOED",
                "provider": provider,
                "tool_name": tool_name,
                "violation": violation_rule,
                "counsel": counsel_msg,
                "latency_us": latency_us,
                "dispute_id": dispute_id,
                "fault_proof": proof_data,
                "circuit_broken": True,
            }

        if self.passport is not None:
            if hasattr(self.passport, "record_successful_action"):
                self.passport.record_successful_action(value_usd=10.0)

        if deposit is not None and self._escrow_pool is not None:
            self._escrow_pool.release_escrow(deposit.escrow_id)

        return {
            "status": "APPROVED",
            "provider": provider,
            "tool_name": tool_name,
            "arguments": arguments,
            "latency_us": latency_us,
            "escrow_released": deposit is not None,
        }


def btp_universal_guard(
    provider: str = ModelProvider.UNIVERSAL,
    spend_cap: float = 50.0,
    strict: bool = True,
    escrow_collateral_usd: Optional[float] = None,
    passport: Optional[Any] = None,
    action_type: Optional[str] = None,
    settlement_rail: str = "L402_LIGHTNING",
    payee_destination: Optional[str] = None,
    org_id: str = "default_org",
    project_id: str = "default_project",
    environment: str = "dev",
):
    guard_inst = UniversalBTPModelGuard(
        spend_cap=spend_cap,
        strict=strict,
        escrow_collateral_usd=escrow_collateral_usd,
        passport=passport,
        settlement_rail=settlement_rail,
        payee_destination=payee_destination,
        org_id=org_id,
        project_id=project_id,
        environment=environment,
    )

    def decorator(fn: Any):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            raw_call = None
            if args and isinstance(args[0], (dict, object)) and hasattr(args[0], "__dict__"):
                raw_call = args[0]
            elif "tool_call" in kwargs:
                raw_call = kwargs["tool_call"]
            else:
                raw_call = {"name": fn.__name__, "arguments": kwargs}

            verification = guard_inst.intercept_and_verify(
                raw_call, 
                provider=provider, 
                action_type=action_type
            )
            return fn(*args, **kwargs)
        return wrapper
    return decorator
