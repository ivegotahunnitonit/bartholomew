"""
Bartholomew Guard for CrewAI (BTP v5.4.14)
=========================================
Wraps CrewAI Tools and Agent Tasks with sub-35µs in-process AST gating,
infinite retry loop dampening, and cryptographic Merkle execution receipts.

Usage:
    from btp_guard.integrations.crewai import BtpCrewAIGuard

    # Wrap any CrewAI custom tool:
    guarded_search = BtpCrewAIGuard(tool=web_search_tool, spend_cap=15.0)
    agent = Agent(role="Researcher", tools=[guarded_search])
"""

import time
from typing import Any, Dict, Optional
from ..authorization_gate import AuthorizationGate


class BtpCrewAIGuard:
    """Wrapper around CrewAI BaseTool or custom tool execution."""

    def __init__(
        self,
        tool: Any,
        spend_cap: float = 50.0,
        max_retries: int = 5,
        strict: bool = True,
        agent_id: str = "crewai-agent",
    ):
        self.tool = tool
        self.spend_cap = float(spend_cap)
        self.max_retries = int(max_retries)
        self.agent_id = str(agent_id)
        self.retry_count = 0
        self.gate = AuthorizationGate(policy={
            "max_spend_usd": self.spend_cap,
            "strict": strict,
            "allow_destructive": False,
        })

    def run(self, *args, **kwargs) -> Any:
        """Executes tool with deterministic pre-flight invariant check."""
        # 1. Loop Fatigue Guard
        if self.retry_count >= self.max_retries:
            raise RuntimeError(
                f"[BTP-LOOP-001] CrewAI execution throttled: Maximum retries ({self.max_retries}) exceeded."
            )

        # 2. Extract payload representation
        cmd_str = " ".join(str(a) for a in args) + " " + " ".join(f"{k}={v}" for k, v in kwargs.items())
        
        # 3. Pre-flight AST Safety & Spend Evaluation (<35µs)
        action = {
            "agent_id": self.agent_id,
            "action_type": getattr(self.tool, "name", "crewai_tool"),
            "payload": {
                "command": cmd_str,
                "amount_usd": kwargs.get("amount_usd", 0.0),
            }
        }
        verdict_res = self.gate.evaluate(action)

        if verdict_res.get("verdict") == "DENY":
            self.retry_count += 1
            reason = verdict_res.get("reason", "Security policy violation")
            rule_id = verdict_res.get("rule_id", "BTP-AST-001")
            raise PermissionError(f"[{rule_id}] CrewAI Tool Action BLOCKED by Bartholomew: {reason}")

        # 4. Execute tool
        self.retry_count = 0  # Reset upon allowed action
        if hasattr(self.tool, "run") and callable(self.tool.run):
            return self.tool.run(*args, **kwargs)
        elif callable(self.tool):
            return self.tool(*args, **kwargs)
        else:
            return verdict_res

    def __call__(self, *args, **kwargs) -> Any:
        return self.run(*args, **kwargs)
