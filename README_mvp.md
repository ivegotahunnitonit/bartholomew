# Bartholomew Authorization Gate MVP

This is the minimal productized version of the execution guard for autonomous agents.

## What it does

The gate evaluates a requested agent action before execution and returns a verdict:

- ALLOW for safe actions
- DENY for unsafe actions
- a reason and rule identifier for blocked actions
- a receipt hash for auditability
- optional telemetry emission

## Quickstart

```python
from src.btp_guard.authorization_gate import AuthorizationGate

policy = {
    "allow_destructive": False,
    "max_spend_usd": 5.0,
    "allowed_action_types": ["shell", "read", "search"],
}

gate = AuthorizationGate(policy=policy)

safe = gate.evaluate({
    "agent_id": "worker-1",
    "action_type": "shell",
    "payload": {"command": "ls -la /tmp"},
    "policy": policy,
})

unsafe = gate.evaluate({
    "agent_id": "worker-1",
    "action_type": "shell",
    "payload": {"command": "rm -rf /tmp/data"},
    "policy": policy,
})

print(safe)
print(unsafe)
```

## Example output

```json
{
  "verdict": "ALLOW",
  "reason": "No policy violations detected",
  "rule_id": null,
  "latency_ms": 0.047,
  "timestamp": "2026-09-15T22:07:07.752116+00:00",
  "receipt_sha256": "71754d8ac4339c2aaa9a71bb4d8337439cafcb81dcef72e6e7a3fc48141fed93"
}
```

```json
{
  "verdict": "DENY",
  "reason": "Destructive shell pattern detected",
  "rule_id": "BTP-SHELL-001",
  "latency_ms": 0.025,
  "timestamp": "2026-09-15T22:07:07.752206+00:00",
  "receipt_sha256": "7808a40a1b7afafc2575e0f23c26c574eacca562ba7cf2a7a2fa5be8ee2e17d1"
}
```

## Supported checks

- destructive shell command detection
- dangerous SQL mutation detection
- secret leakage detection
- prompt injection detection
- blocked action type by policy

## Future direction

This is the foundation for:

- hosted policy enforcement
- enterprise telemetry dashboards
- delegated spend controls
- agent authorization and auditing
