from __future__ import annotations

import json
import os

from src.btp_guard import AuthorizationGate, StripeMeterBridge


def run_demo(ledger_path: str = "btp_guard_ledger.db", meter_name: str = "autonomous_action_allowed") -> dict:
    gate = AuthorizationGate(policy={"allow_destructive": False}, ledger_path=ledger_path)

    action = {
        "agent_id": "pilot-agent",
        "tenant_id": "tenant-demo",
        "action_type": "tool_call",
        "payload": {"command": "echo 'safe action'"},
    }

    result = gate.evaluate(action)
    ledger_events = gate.ledger.list_events(limit=1)
    if not ledger_events:
        raise RuntimeError("No allowed-action ledger event was recorded.")

    bridge = StripeMeterBridge(
        api_key=os.getenv("STRIPE_API_KEY", ""),
        meter_name=meter_name,
    )
    usage_payload = bridge.build_usage_payload(ledger_events[0])
    stripe_usage = bridge.report_usage(ledger_events[0])

    payload = {
        "result": result,
        "ledger_event": ledger_events[0],
        "usage_payload": usage_payload,
        "stripe_usage": stripe_usage,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return payload


if __name__ == "__main__":
    run_demo()
