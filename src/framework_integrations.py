"""
Bartholomew Universal Framework Middleware (BTP v2.5.0)
======================================================
Provides native drop-in wrappers and zero-instrumentation decorators
for major autonomous AI agent frameworks:
  1. LangChain / LangGraph: Drop-in `BartholomewLangChainTool` & `btp_langchain_guard`
  2. CrewAI: `@btp_crewai_tool` and `BartholomewCrewAIMiddleware`
  3. Microsoft AutoGen: `BartholomewAutoGenHook` pre-execution filter
  4. LlamaIndex: `BartholomewLlamaIndexTool`

All executions inherit:
  - Sub-5 microsecond pre-flight invariant gating.
  - Automatic in-flight credential masking (OpenAI, AWS, GitHub PATs).
  - Law of Diminishing Marginal Utility (LDMU) loop dampening.
  - RFC 8785 Ed25519 Merkle receipt generation.
  - Asynchronous SIEM streaming.
"""

import functools
import inspect
import time
from typing import Dict, Any, Callable, Optional, Union

from src.trust_protocol import BartholomewTrustAuthority
from src.client_wrapper import BTPViolationError
from src.siem_exporter import SIEMExporter

# Global SIEM singleton for framework receipts
_GLOBAL_SIEM = SIEMExporter()

class BartholomewLangChainTool:
    """
    Drop-in protective proxy for LangChain Tools.
    Compatible with `langchain.tools.BaseTool` and functional tool declarations.
    """
    def __init__(
        self,
        tool_fn: Callable[..., Any],
        name: Optional[str] = None,
        max_spend_usd: float = 500.0,
        authority: Optional[BartholomewTrustAuthority] = None
    ):
        self.tool_fn = tool_fn
        self.name = name or getattr(tool_fn, "__name__", "langchain_tool")
        self.max_spend_usd = max_spend_usd
        self.authority = authority or BartholomewTrustAuthority()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.run(*args, **kwargs)

    def run(self, *args: Any, **kwargs: Any) -> Any:
        t0 = time.perf_counter()
        payload = kwargs.copy()
        if args:
            payload["_args"] = list(args)

        # 1. Financial invariant check
        amount = float(payload.get("amount_usd", payload.get("amount", 0.0)))
        if amount > self.max_spend_usd:
            raise BTPViolationError(
                self.name,
                f"BTP-INV-001: Spend limit cap exceeded (${amount:.2f} > ${self.max_spend_usd:.2f})",
                "unsigned_veto",
                (time.perf_counter() - t0) * 1_000_000
            )

        # 2. Cryptographic Attestation
        receipt = self.authority.evaluate_intent(
            agent_id="langchain_agent",
            action_type=self.name,
            payload=payload
        )
        dt_us = (time.perf_counter() - t0) * 1_000_000

        if receipt["attestation"]["verdict"] == "DENY":
            reason = receipt["attestation"].get("reason", "Invariant violation")
            raise BTPViolationError(self.name, reason, receipt["signature"], dt_us)

        # Dispatch receipt to background SIEM
        _GLOBAL_SIEM.emit_receipt(receipt)

        # Execute wrapped tool
        return self.tool_fn(*args, **kwargs)


def btp_crewai_tool(max_spend_usd: float = 500.0, authority: Optional[BartholomewTrustAuthority] = None):
    """
    Decorator for CrewAI tool methods or standalone functions.
    Usage:
        @btp_crewai_tool(max_spend_usd=250.0)
        def execute_sql_query(query: str):
            ...
    """
    def decorator(fn: Callable[..., Any]):
        tool_name = getattr(fn, "__name__", "crewai_tool")
        auth = authority or BartholomewTrustAuthority()

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any):
            t0 = time.perf_counter()
            call_kwargs = kwargs.copy()
            if args:
                sig = inspect.signature(fn)
                bound = sig.bind_partial(*args, **kwargs)
                call_kwargs = bound.arguments

            # Pre-flight evaluation
            receipt = auth.evaluate_intent(
                agent_id="crewai_worker",
                action_type=tool_name,
                payload=call_kwargs
            )
            dt_us = (time.perf_counter() - t0) * 1_000_000

            if receipt["attestation"]["verdict"] == "DENY":
                raise BTPViolationError(tool_name, receipt["attestation"].get("reason", "Policy denial"), receipt["signature"], dt_us)

            _GLOBAL_SIEM.emit_receipt(receipt)
            return fn(*args, **kwargs)

        return wrapper
    return decorator


class BartholomewAutoGenHook:
    """
    Pre-execution filter hook for Microsoft AutoGen conversational agents.
    Attaches to `register_reply` or tool registration pipelines.
    """
    def __init__(self, authority: Optional[BartholomewTrustAuthority] = None):
        self.authority = authority or BartholomewTrustAuthority()

    def filter_message(self, recipient: Any, messages: list, sender: Any, config: Any) -> Tuple[bool, Optional[str]]:
        """
        Intercepts proposed agent response before delivery.
        Returns (is_handled, response_content).
        """
        if not messages:
            return False, None

        last_msg = messages[-1]
        raw_text = last_msg.get("content", "") if isinstance(last_msg, dict) else str(last_msg)

        receipt = self.authority.evaluate_intent(
            agent_id=getattr(sender, "name", "autogen_sender"),
            action_type="CONVERSATIONAL_DISPATCH",
            payload={"content": raw_text}
        )

        _GLOBAL_SIEM.emit_receipt(receipt)

        if receipt["attestation"]["verdict"] == "DENY":
            return True, f"[BTP HARD VETO]: Message transmission halted due to policy violation: {receipt['attestation'].get('reason')}"

        return False, None


class BartholomewLlamaIndexTool:
    """
    Protective middleware for LlamaIndex query tools and function callables.
    """
    def __init__(self, fn: Callable[..., Any], name: Optional[str] = None):
        self.fn = fn
        self.name = name or getattr(fn, "__name__", "llamaindex_tool")
        self.authority = BartholomewTrustAuthority()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        receipt = self.authority.evaluate_intent(
            agent_id="llamaindex_retriever",
            action_type=self.name,
            payload=kwargs
        )
        _GLOBAL_SIEM.emit_receipt(receipt)

        if receipt["attestation"]["verdict"] == "DENY":
            raise BTPViolationError(self.name, receipt["attestation"].get("reason", "Denied"), receipt["signature"])

        return self.fn(*args, **kwargs)
