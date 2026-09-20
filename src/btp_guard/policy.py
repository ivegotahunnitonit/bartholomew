from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Policy:
    """Minimal policy for agent authorization decisions."""

    allow_destructive: bool = False
    max_spend_usd: float = 5.0
    allowed_action_types: Optional[List[str]] = None
    require_receipt: bool = True
    blocked_rules: List[str] = field(default_factory=lambda: [
        "BTP-SHELL-001",
        "BTP-SQL-001",
        "BTP-SECRET-001",
        "BTP-INJECT-001",
    ])
    policy_version: str = "v5.4.12"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allow_destructive": self.allow_destructive,
            "max_spend_usd": self.max_spend_usd,
            "allowed_action_types": self.allowed_action_types or [],
            "require_receipt": self.require_receipt,
            "blocked_rules": self.blocked_rules,
            "policy_version": self.policy_version,
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Policy":
        if not data:
            return cls()
        return cls(
            allow_destructive=data.get("allow_destructive", False),
            max_spend_usd=float(data.get("max_spend_usd", 5.0)),
            allowed_action_types=data.get("allowed_action_types"),
            require_receipt=data.get("require_receipt", True),
            blocked_rules=data.get("blocked_rules", [
                "BTP-SHELL-001",
                "BTP-SQL-001",
                "BTP-SECRET-001",
                "BTP-INJECT-001",
            ]),
            policy_version=data.get("policy_version", "v5.4.12"),
        )
