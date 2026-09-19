"""
Bartholomew Trust Protocol (BTP) Guard Package.
Minimal authorization gate for autonomous agent actions.
"""

from .authorization_gate import AuthorizationGate
from .ledger import BillableLedger
from .policy import Policy
from .stripe_bridge import StripeMeterBridge
from .telemetry import TelemetryEmitter
from .btp_guard import WireGuard
from src.usage_tracker import load_license, record_evaluation, trigger_threat_intercept_notice


class Guard:
    """Public compatibility wrapper for the execution gate."""

    def __init__(self, policy=None, telemetry_path=None, ledger_path=None, spend_cap=None, strict=False, workspace_id=None, **kwargs):
        self.policy = dict(policy or {})
        if spend_cap is not None:
            self.policy["max_spend_usd"] = float(spend_cap)
        if strict:
            self.policy["strict"] = True
        if workspace_id:
            self.policy["workspace_id"] = str(workspace_id)
        for k, v in kwargs.items():
            self.policy[k] = v

        self.gate = AuthorizationGate(
            policy=self.policy,
            telemetry_path=telemetry_path,
            ledger_path=ledger_path,
        )

    def evaluate(self, action):
        if isinstance(action, str):
            return self.check(action)
        if action.get("policy") is None and self.policy:
            action = {**action, "policy": self.policy}
        return self.gate.evaluate(action)

    def check(self, command: str, **kwargs):
        action = {
            "agent_id": kwargs.get("agent_id", "guard-client"),
            "action_type": kwargs.get("action_type", "shell" if isinstance(command, str) else "unknown"),
            "payload": {"command": command, **kwargs.get("payload", {})},
        }
        if "policy" in kwargs:
            action["policy"] = kwargs["policy"]
        elif self.policy:
            action["policy"] = self.policy
        result = self.gate.evaluate(action)
        record_evaluation()
        result["allowed"] = result.get("verdict") == "ALLOW"
        result["license_tier"] = load_license().get("tier", "COMMUNITY")
        if not result["allowed"]:
            trigger_threat_intercept_notice(
                rule_id=result.get("rule_id", "BTP-AST-001"),
                action_summary=command,
                latency_us=result.get("latency_us", 24.8)
            )
        return result

    def is_allowed(self, command: str, **kwargs):
        result = self.check(command, **kwargs)
        return result.get("verdict") == "ALLOW"

    def evaluate_ast(self, code_str: str, language: str = None) -> dict:
        """Evaluates arbitrary code string with sub-35µs AST safety rules."""
        from src.polyglot_ast_validator import PolyglotASTValidator
        is_safe, reason, metadata = PolyglotASTValidator.validate_code(code_str, language)
        latency_us = metadata.get("latency_us", 15.0) if isinstance(metadata, dict) else 15.0
        return {
            "allowed": is_safe,
            "violations": [reason] if not is_safe else [],
            "reason": reason,
            "latency_us": latency_us,
            "metadata": metadata
        }

    def protect(self, func):
        def wrapper(*args, **kwargs):
            payload = {"command": " ".join(str(arg) for arg in args if isinstance(arg, str))}
            result = self.check(payload["command"], **kwargs)
            if result["verdict"] == "DENY":
                raise PermissionError(f"Action blocked by Bartholomew Guard: {result.get('reason') or 'Policy Violation'}")
            return func(*args, **kwargs)
        return wrapper


__version__ = "5.4.16"
__all__ = ["Guard", "WireGuard", "AuthorizationGate", "BillableLedger", "Policy", "StripeMeterBridge", "TelemetryEmitter"]

__all__ = ["AuthorizationGate", "Guard", "Policy", "TelemetryEmitter", "BillableLedger", "StripeMeterBridge", "WireGuard", "__version__"]
