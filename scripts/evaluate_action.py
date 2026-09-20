#!/usr/bin/env python3
"""Evaluate one autonomous action through the Bartholomew authorization gate."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from src.btp_guard.authorization_gate import AuthorizationGate


def load_policy(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    policy_path = Path(path)
    if not policy_path.exists():
        raise FileNotFoundError(f"Policy file not found: {policy_path}")
    text = policy_path.read_text(encoding="utf-8")
    if policy_path.suffix.lower() == ".json":
        return json.loads(text)
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to read YAML policy files") from exc
    return yaml.safe_load(text) or {}


def evaluate(command: str, action_type: str, agent_id: str, policy_file: str | None) -> dict[str, Any]:
    policy = load_policy(policy_file)
    gate = AuthorizationGate(policy=policy)
    return gate.evaluate({
        "agent_id": agent_id,
        "action_type": action_type,
        "payload": {"command": command},
    })


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", required=True)
    parser.add_argument("--action-type", default="shell")
    parser.add_argument("--agent-id", default="bartholomew-runner")
    parser.add_argument("--policy-file")
    args = parser.parse_args()

    result = evaluate(args.command, args.action_type, args.agent_id, args.policy_file)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["verdict"] == "ALLOW" else 1


if __name__ == "__main__":
    raise SystemExit(main())
