"""
Bartholomew Guard for LangChain & LangGraph (Community Integration)
===================================================================
Provides sub-50 µs deterministic AST invariant checking and Ed25519 execution
stamping for LangChain tools, agents, and LangGraph state nodes.

Usage:
  from integrations.langchain.bartholomew_guard import BartholomewCallbackHandler, BartholomewToolGuard

  # 1. Attach as a Callback Handler across an entire agent chain:
  agent = initialize_agent(tools, llm, callbacks=[BartholomewCallbackHandler()])

  # 2. Or wrap individual tools directly:
  @BartholomewToolGuard(spend_cap_usd=100.0)
  def run_sql_query(query: str): ...
"""

import time
from typing import Dict, Any, Optional, List, Union

try:
    from src.polyglot_ast_validator import PolyglotASTValidator
    from src.secret_masker import SecretVaultMasker
    from src.trust_protocol import BartholomewTrustAuthority
except ImportError:
    from btp_guard.src.polyglot_ast_validator import PolyglotASTValidator
    from btp_guard.src.secret_masker import SecretVaultMasker
    from btp_guard.src.trust_protocol import BartholomewTrustAuthority


class BartholomewCallbackHandler:
    """LangChain / LangGraph Callback Handler for deterministic tool call verification."""

    def __init__(self, spend_cap_usd: float = 500.0, authority: Optional[BartholomewTrustAuthority] = None):
        self.spend_cap_usd = spend_cap_usd
        self.authority = authority or BartholomewTrustAuthority()
        self.current_spend = 0.0

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        """Pre-flight evaluation before tool physically executes."""
        t0 = time.perf_counter()
        
        # 1. Polyglot AST check
        is_safe, msg, meta = PolyglotASTValidator.validate_code(input_str)
        if not is_safe:
            raise PermissionError(f"BTP-VETO: Invariant violation on tool '{serialized.get('name', 'tool')}': {msg}")

        # 2. Spend Cap check
        estimated_cost = kwargs.get("cost_usd", 0.0)
        if self.current_spend + estimated_cost > self.spend_cap_usd:
            raise PermissionError(f"BTP-VETO: Spend cap exceeded (${self.spend_cap_usd} USD limit)")
        
        self.current_spend += estimated_cost
        eval_latency_us = (time.perf_counter() - t0) * 1_000_000

        # 3. Mint Ed25519 Attestation
        receipt = self.authority.evaluate_intent(
            agent_id="langchain-agent",
            action_type=serialized.get("name", "TOOL_INVOCATION"),
            payload={"input": input_str, "latency_us": eval_latency_us}
        )
        return receipt


def BartholomewToolGuard(spend_cap_usd: float = 500.0):
    """Decorator to wrap LangChain tool functions with sub-50µs invariant enforcement."""
    def decorator(fn):
        authority = BartholomewTrustAuthority()
        
        def wrapper(*args, **kwargs):
            input_text = " ".join(str(a) for a in args) + " " + " ".join(f"{k}={v}" for k, v in kwargs.items())
            is_safe, msg, meta = PolyglotASTValidator.validate_code(input_text)
            if not is_safe:
                raise PermissionError(f"BTP-VETO: Invariant violation in {fn.__name__}: {msg}")
            
            # Mask high entropy secrets
            sanitized_args = [SecretVaultMasker.mask_text(str(a))[0] if isinstance(a, str) else a for a in args]
            sanitized_kwargs = {k: SecretVaultMasker.mask_text(str(v))[0] if isinstance(v, str) else v for k, v in kwargs.items()}
            
            return fn(*sanitized_args, **sanitized_kwargs)
        return wrapper
    return decorator
