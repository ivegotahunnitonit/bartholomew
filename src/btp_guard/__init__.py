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
                raise PermissionError(f"Action blocked by Bartholomew Guard: {result.get('reason') or 'Policy Violation'}")
            return func(*args, **kwargs)
        return wrapper


__version__ = "5.4.15"
__all__ = ["Guard", "WireGuard", "AuthorizationGate", "BillableLedger", "Policy", "StripeMeterBridge", "TelemetryEmitter"]

__all__ = ["AuthorizationGate", "Guard", "Policy", "TelemetryEmitter", "BillableLedger", "StripeMeterBridge", "WireGuard", "__version__"]
