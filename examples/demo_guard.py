import json

from src.btp_guard.authorization_gate import AuthorizationGate


def main() -> None:
    gate = AuthorizationGate()

    safe_action = {
        "agent_id": "worker-1",
        "action_type": "shell",
        "payload": {"command": "ls -la /tmp"},
        "policy": {"allow_destructive": False},
    }

    unsafe_action = {
        "agent_id": "worker-1",
        "action_type": "shell",
        "payload": {"command": "rm -rf /tmp/data"},
        "policy": {"allow_destructive": False},
    }

    safe_result = gate.evaluate(safe_action)
    unsafe_result = gate.evaluate(unsafe_action)

    print("SAFE ACTION")
    print(json.dumps(safe_result, indent=2))
    print("\nUNSAFE ACTION")
    print(json.dumps(unsafe_result, indent=2))


if __name__ == "__main__":
    main()
