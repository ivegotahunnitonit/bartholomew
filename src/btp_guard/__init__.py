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
from src.usage_tracker import load_license, record_evaluation


class Guard:
    """Public compatibility wrapper for the execution gate."""

    def __init__(self, policy=None, telemetry_path=None, ledger_path=None):
        self.policy = policy or {}
        self.gate = AuthorizationGate(policy=self.policy, telemetry_path=telemetry_path, ledger_path=ledger_path)

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
        return result

    def is_allowed(self, command: str, **kwargs):
        result = self.check(command, **kwargs)
        return result.get("verdict") == "ALLOW"

    def protect(self, func):
        def wrapper(*args, **kwargs):
            payload = {"command": " ".join(str(arg) for arg in args if isinstance(arg, str))}
            result = self.check(payload["command"], **kwargs)
            if result["verdict"] == "DENY":
                raise ValueError(f"Action blocked by Bartholomew Guard: {result['reason']}")
            return func(*args, **kwargs)
        return wrapper


__version__ = "0.1.0-mvp"

__all__ = ["AuthorizationGate", "Guard", "Policy", "TelemetryEmitter", "BillableLedger", "StripeMeterBridge", "WireGuard", "__version__"]
