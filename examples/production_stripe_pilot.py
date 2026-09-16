from __future__ import annotations

import json
import os
from pathlib import Path

from src.btp_guard import AuthorizationGate, StripeMeterBridge


def load_local_env() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(name, value)


def load_customer_map() -> dict:
    raw = os.getenv("BTP_STRIPE_CUSTOMER_MAP", "{}")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def run_pilot() -> dict:
    load_local_env()
    api_key = os.getenv("BTP_STRIPE_API_KEY") or os.getenv("STRIPE_SECRET_KEY", "")
    meter_name = os.getenv("BTP_STRIPE_METER_NAME", "autonomous_action_allowed")
    customer_map = load_customer_map()

    if not api_key:
        raise RuntimeError(
            "BTP_STRIPE_API_KEY is missing. Set it in the environment or create a local .env file."
        )

    gate = AuthorizationGate(
        policy={"allow_destructive": False},
        ledger_path="btp_guard_ledger.db",
    )

    action = {
        "agent_id": "production-agent",
        "tenant_id": "tenant-demo",
        "action_type": "tool_call",
        "payload": {"command": "echo hello"},
    }

    result = gate.evaluate(action)
    events = gate.ledger.list_events(limit=1)
    if not events:
        raise RuntimeError("No allowed-action ledger event was recorded.")

    bridge = StripeMeterBridge(
        api_key=api_key,
        meter_name=meter_name,
        customer_map=customer_map,
    )
    config_check = bridge.validate_configuration(action["tenant_id"])
    if config_check["status"] != "ok":
        raise RuntimeError(json.dumps({"stripe_configuration": config_check}, sort_keys=True))
    payload = bridge.build_usage_payload(events[0])
    stripe_result = bridge.report_usage(events[0])

    return {
        "result": result,
        "ledger_event": events[0],
        "configuration_check": config_check,
        "usage_payload": payload,
        "stripe_result": stripe_result,
    }


if __name__ == "__main__":
    print(json.dumps(run_pilot(), indent=2, sort_keys=True))
