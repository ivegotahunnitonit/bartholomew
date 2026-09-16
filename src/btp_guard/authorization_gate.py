from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from .ledger import BillableLedger
from .policy import Policy
from .telemetry import TelemetryEmitter


class AuthorizationGate:
    """Minimal authorization gate for autonomous agent actions."""

    DESTRUCTIVE_SHELL_PATTERNS = [
        re.compile(r"(?i)rm\s+-rf\b"),
        re.compile(r"(?i)mkfs\b"),
        re.compile(r"(?i)dd\s+if=|dd\s+of="),
        re.compile(r"(?i)chmod\s+777\b"),
    ]

    DANGEROUS_SQL_PATTERNS = [
        re.compile(r"(?i)\bDROP\s+TABLE\b"),
        re.compile(r"(?i)\bTRUNCATE\b"),
        re.compile(r"(?i)\bDELETE\s+FROM\b"),
    ]

    SECRET_PATTERNS = [
        re.compile(r"(?i)ghp_[A-Za-z0-9]{20,}"),
        re.compile(r"(?i)sk-[A-Za-z0-9]{20,}"),
        re.compile(r"(?i)AKIA[0-9A-Z]{16}"),
        re.compile(r"(?i)eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+"),
    ]

    PROMPT_INJECTION_PATTERNS = [
        re.compile(r"(?i)ignore\s+all\s+previous\s+instructions"),
        re.compile(r"(?i)reveal\s+(the\s+)?system\s+prompt"),
        re.compile(r"(?i)you\s+are\s+now\s+in\s+DAN\s+mode"),
    ]

    def __init__(
        self,
        policy: Optional[Dict[str, Any]] = None,
        telemetry_path: Optional[str] = None,
        ledger_path: Optional[str] = None,
    ):
        self.policy = Policy.from_dict(policy)
        self.telemetry = TelemetryEmitter(telemetry_path)
        self.ledger = BillableLedger(ledger_path)

    def evaluate(self, action: Dict[str, Any]) -> Dict[str, Any]:
        started_at = time.perf_counter()
        payload = action.get("payload", {})
        text_blob = json.dumps(payload, sort_keys=True)

        effective_policy = self.policy
        if action.get("policy") is not None:
            effective_policy = Policy.from_dict({**self.policy.to_dict(), **action.get("policy", {})})
        else:
            effective_policy = self.policy

        violations: list[Tuple[str, str]] = []

        command = str(payload.get("command", ""))
        query = str(payload.get("query", ""))
        text = str(payload.get("text", ""))
        combined_text = " ".join([command, query, text, text_blob])

        amount_usd = payload.get("amount_usd")
        if amount_usd is not None:
            try:
                amount_value = float(amount_usd)
            except (TypeError, ValueError):
                amount_value = None
            if amount_value is not None and amount_value > effective_policy.max_spend_usd:
                violations.append(("BTP-SPEND-001", f"Payment exceeds max_spend_usd limit ({amount_value} > {effective_policy.max_spend_usd})"))

        if not effective_policy.allow_destructive and self._matches_any(command, self.DESTRUCTIVE_SHELL_PATTERNS):
            violations.append(("BTP-SHELL-001", "Destructive shell pattern detected"))

        if self._matches_any(query, self.DANGEROUS_SQL_PATTERNS):
            violations.append(("BTP-SQL-001", "Dangerous SQL mutation detected"))

        if self._matches_any(combined_text, self.SECRET_PATTERNS):
            violations.append(("BTP-SECRET-001", "Sensitive secret detected in agent payload"))

        if self._matches_any(combined_text, self.PROMPT_INJECTION_PATTERNS):
            violations.append(("BTP-INJECT-001", "Prompt injection pattern detected"))

        l402_preimage = payload.get("l402_preimage")
        l402_payment_hash = payload.get("l402_payment_hash")
        l402_settled = False
        if l402_preimage and l402_payment_hash:
            computed_hash = hashlib.sha256(bytes.fromhex(l402_preimage)).hexdigest() if isinstance(l402_preimage, str) else ""
            if computed_hash.lower() != str(l402_payment_hash).lower():
                violations.append(("BTP-L402-001", f"L402 payment preimage hash mismatch ({computed_hash} != {l402_payment_hash})"))
            else:
                l402_settled = True

        action_type = action.get("action_type", "")
        if effective_policy.allowed_action_types and action_type not in effective_policy.allowed_action_types:
            violations.append(("BTP-ACTION-001", f"Action type '{action_type}' is not allowed by policy"))

        latency_ms = (time.perf_counter() - started_at) * 1000
        timestamp = datetime.now(timezone.utc).isoformat()

        if violations:
            rule_id, reason = violations[0]
            if rule_id in (effective_policy.blocked_rules or []):
                reason = f"{reason}; rule {rule_id} blocked by policy"
            verdict = "DENY"
        else:
            rule_id = None
            reason = "No policy violations detected"
            verdict = "ALLOW"

        result = {
            "verdict": verdict,
            "reason": reason,
            "rule_id": rule_id,
            "latency_ms": round(latency_ms, 3),
            "timestamp": timestamp,
            "policy_version": effective_policy.policy_version,
            "l402_settled": l402_settled,
        }
        result["receipt_sha256"] = self._build_receipt_hash(result, action)

        self.telemetry.emit({
            "event_type": "agent_action_evaluated",
            "agent_id": action.get("agent_id", "unknown"),
            "action_type": action_type,
            "verdict": verdict,
            "rule_id": rule_id,
            "latency_ms": result["latency_ms"],
            "timestamp": timestamp,
        })

        if verdict == "ALLOW":
            self.ledger.record_allowed_action(action, result)

        return result

    @staticmethod
    def _matches_any(value: str, patterns: list[re.Pattern[str]]) -> bool:
        return any(pattern.search(value) for pattern in patterns)

    @staticmethod
    def _build_receipt_hash(result: Dict[str, Any], action: Dict[str, Any]) -> str:
        payload = {
            "action": action,
            "result": result,
        }
        digest_input = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(digest_input).hexdigest()
