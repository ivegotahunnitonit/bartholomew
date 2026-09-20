"""
Bartholomew Security Tool Guard for CrewAI (Community Integration)
===================================================================
Provides zero-escape AST protection, recursive loop dampening (LDMU),
and secret scrubbing for CrewAI multi-agent tasks.

Usage:
  from integrations.crewai.bartholomew_tool_guard import BartholomewCrewAIGuard

  # Attach to any CrewAI Tool:
  guarded_tool = BartholomewCrewAIGuard(tool=my_custom_tool, max_retries=5)
  agent = Agent(role="Data Engineer", tools=[guarded_tool])
"""

import time
from typing import Dict, Any, Optional

try:
    from src.polyglot_ast_validator import PolyglotASTValidator
    from src.secret_masker import SecretVaultMasker
    from src.trust_protocol import BartholomewTrustAuthority
except ImportError:
    from btp_guard.src.polyglot_ast_validator import PolyglotASTValidator
    from btp_guard.src.secret_masker import SecretVaultMasker
    from btp_guard.src.trust_protocol import BartholomewTrustAuthority


class BartholomewCrewAIGuard:
    """Wrapper around CrewAI BaseTool or custom tool execution."""

    def __init__(self, tool: Any, max_retries: int = 5, spend_cap_usd: float = 250.0):
        self.tool = tool
        self.max_retries = max_retries
        self.spend_cap_usd = spend_cap_usd
        self.retry_count = 0
        self.authority = BartholomewTrustAuthority()

    def run(self, *args, **kwargs) -> Any:
        """Executes tool with deterministic pre-flight invariant check."""
        t0 = time.perf_counter()
        
        # 1. Check retry count to prevent runaway infinite loops
        if self.retry_count >= self.max_retries:
            raise RuntimeError(f"BTP-LDMU-FATIGUE: Execution throttled. Maximum retries ({self.max_retries}) exceeded.")
        
        # 2. Check AST safety on input payload
        input_repr = " ".join(str(a) for a in args) + " " + " ".join(f"{k}={v}" for k, v in kwargs.items())
        is_safe, msg, meta = PolyglotASTValidator.validate_code(input_repr)
        if not is_safe:
            self.retry_count += 1
            raise PermissionError(f"BTP-VETO: CrewAI Tool invariant violation: {msg}")

        # 3. Secret Masking
        clean_args = [SecretVaultMasker.mask_text(str(a))[0] if isinstance(a, str) else a for a in args]
        clean_kwargs = {k: SecretVaultMasker.mask_text(str(v))[0] if isinstance(v, str) else v for k, v in kwargs.items()}

        eval_latency_us = (time.perf_counter() - t0) * 1_000_000

        # 4. Mint Ed25519 execution receipt
        self.authority.evaluate_intent(
            agent_id="crewai-agent",
            action_type="CREWAI_TOOL_RUN",
            payload={"latency_us": eval_latency_us}
        )

        # 5. Execute downstream tool
        if hasattr(self.tool, "run"):
            return self.tool.run(*clean_args, **clean_kwargs)
        elif callable(self.tool):
            return self.tool(*clean_args, **clean_kwargs)
        else:
            return f"Guarded execution approved ({eval_latency_us:.2f} µs)"
