import json
import time

from src.btp_guard.authorization_gate import AuthorizationGate


def main() -> None:
    gate = AuthorizationGate(policy={"allow_destructive": False})
    actions = [
        {"agent_id": f"bench-{i}", "action_type": "shell", "payload": {"command": "ls -la /tmp"}}
        for i in range(100)
    ]
    actions += [
        {"agent_id": f"bench-danger-{i}", "action_type": "shell", "payload": {"command": "rm -rf /tmp/data"}}
        for i in range(100)
    ]

    start = time.perf_counter()
    results = [gate.evaluate(action) for action in actions]
    elapsed = time.perf_counter() - start

    allowed = sum(1 for r in results if r["verdict"] == "ALLOW")
    denied = sum(1 for r in results if r["verdict"] == "DENY")

    print(json.dumps({
        "total_actions": len(results),
        "allowed": allowed,
        "denied": denied,
        "elapsed_seconds": round(elapsed, 4),
        "average_latency_ms": round(sum(r["latency_ms"] for r in results) / len(results), 3),
    }, indent=2))


if __name__ == "__main__":
    main()
