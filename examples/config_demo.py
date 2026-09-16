import json

from src.btp_guard.authorization_gate import AuthorizationGate
from src.btp_guard.policy import Policy


def main() -> None:
    with open("examples/policy_demo.json", "r", encoding="utf-8") as f:
        policy_data = json.load(f)

    policy = Policy.from_dict(policy_data)
    gate = AuthorizationGate(policy=policy.to_dict())

    safe_action = {
        "agent_id": "worker-1",
        "action_type": "read",
        "payload": {"path": "/tmp/logs.txt"},
        "policy": policy.to_dict(),
    }

    unsafe_action = {
        "agent_id": "worker-1",
        "action_type": "shell",
        "payload": {"command": "rm -rf /tmp/data"},
        "policy": policy.to_dict(),
    }

    print("SAFE ACTION")
    print(json.dumps(gate.evaluate(safe_action), indent=2))
    print("\nUNSAFE ACTION")
    print(json.dumps(gate.evaluate(unsafe_action), indent=2))


if __name__ == "__main__":
    main()
