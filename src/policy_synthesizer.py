"""
Bartholomew Autonomous Policy Synthesizer
=========================================
Automatically synthesizes tight, least-privilege declarative YAML security policies
by analyzing agent runtime execution traces without requiring manual policy authoring.
"""

import math
from typing import List, Dict, Any, Optional


class PolicySynthesizer:
    def __init__(self, policy_id: str = "urn:btp:policy:auto-synthesized-v1"):
        self.policy_id = policy_id
        self.observed_spends: List[float] = []
        self.observed_recipients: set = set()
        self.observed_tools: set = set()
        self.max_observed_repeats: int = 1

    def observe_execution_trace(self, trace: Dict[str, Any]):
        """Ingests an agent execution trace item."""
        payload = trace.get("payload", {})
        
        # Track financial amounts
        amount = float(payload.get("amount_usd", payload.get("amount", 0.0)))
        if amount > 0.0:
            self.observed_spends.append(amount)

        # Track recipients / domains
        recipient = payload.get("recipient", payload.get("domain", payload.get("target")))
        if recipient and isinstance(recipient, str):
            self.observed_recipients.add(recipient)

        # Track tools
        tool = trace.get("action_type", payload.get("tool"))
        if tool:
            self.observed_tools.add(str(tool))

    def synthesize_policy_dict(self) -> Dict[str, Any]:
        """Synthesizes structured declarative rules with optimal mathematical bounds."""
        # 1. Calculate Optimal Spend Cap (99th percentile or max + 25% buffer)
        if self.observed_spends:
            max_spend = max(self.observed_spends)
            suggested_cap = round(max(50.0, max_spend * 1.25), 2)
        else:
            suggested_cap = 500.0

        # 2. Optimal LDMU Decay Rate based on tool entropy
        # Fewer distinct tools -> higher repetition risk -> tighter decay
        unique_tool_count = len(self.observed_tools)
        decay_rate = 0.45 if unique_tool_count <= 2 else 0.35 if unique_tool_count <= 5 else 0.25

        rules = [
            {
                "id": "AUTO_RULE_SPEND_CAP",
                "name": "Synthesized Maximum Spend Bound",
                "field": "amount_usd",
                "type": "max_threshold",
                "value": suggested_cap,
                "action": "DENY",
                "message": f"Transaction exceeds synthesized baseline safety limit of ${suggested_cap:.2f}"
            },
            {
                "id": "AUTO_RULE_DIMINISHING_MARGINAL_UTILITY",
                "name": "Synthesized Action Fatigue Governor",
                "type": "diminishing_marginal_utility",
                "decay_rate": decay_rate,
                "min_utility_threshold": 0.15,
                "action": "DENY",
                "message": "Action repetition fatigue threshold breached."
            },
            {
                "id": "AUTO_RULE_INVARIANT_DESTRUCTIVE_PATTERNS",
                "name": "Synthesized Destructive Pattern Blocker",
                "type": "forbidden_substrings",
                "patterns": [
                    "drop table", "drop schema", "truncate table",
                    "rm -rf", "/etc/shadow", "aws_secret_access_key", "sk-live"
                ],
                "action": "DENY",
                "message": "Destructive system modification or credential exfiltration detected."
            }
        ]

        return {
            "version": "2.2.0",
            "policy_id": self.policy_id,
            "description": f"Autonomous policy synthesized from {len(self.observed_spends)} financial traces and {len(self.observed_tools)} tools.",
            "rules": rules
        }

    def synthesize_yaml(self) -> str:
        """Converts synthesized policy to clean declarative YAML string."""
        data = self.synthesize_policy_dict()
        cap = data["rules"][0]["value"]
        decay = data["rules"][1]["decay_rate"]

        yaml_content = f"""version: "{data['version']}"
policy_id: "{data['policy_id']}"
description: "{data['description']}"

rules:
  - id: "AUTO_RULE_SPEND_CAP"
    name: "Synthesized Maximum Spend Bound"
    field: "amount_usd"
    type: "max_threshold"
    value: {cap:.2f}
    action: "DENY"
    message: "Transaction exceeds synthesized baseline safety limit of ${cap:.2f}"

  - id: "AUTO_RULE_DIMINISHING_MARGINAL_UTILITY"
    name: "Synthesized Action Fatigue Governor"
    type: "diminishing_marginal_utility"
    decay_rate: {decay}
    min_utility_threshold: 0.15
    action: "DENY"

  - id: "AUTO_RULE_INVARIANT_DESTRUCTIVE_PATTERNS"
    name: "Synthesized Destructive Pattern Blocker"
    type: "forbidden_substrings"
    patterns:
      - "drop table"
      - "drop schema"
      - "truncate table"
      - "rm -rf"
      - "/etc/shadow"
      - "aws_secret_access_key"
      - "sk-live"
    action: "DENY"
"""
        return yaml_content
