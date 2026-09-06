"""
AutoGen + BTP Guard: Multi-Agent GroupChat with Dynamic Consensus Rebalancing
=============================================================================
Demonstrates how AutoGen multi-agent group chats use AutoGenBTPInterceptor
and DynamicThresholdRebalancer to protect against Byzantine peer agents.

Run:
    python examples/autogen_multiagent_defense/run_groupchat.py
"""

import sys
import os
import time

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from framework_adapters.autogen.autogen_btp_interceptor import AutoGenBTPInterceptor
from src.ebpf_kernel_guard import DynamicThresholdRebalancer, KernelSyscallEvent
from src.trust_protocol import BartholomewTrustAuthority


def main():
    print("=" * 70)
    print("  AutoGen + BTP Guard: GroupChat Defense & Threshold Rebalancing")
    print("=" * 70)

    auth = BartholomewTrustAuthority(ttl_seconds=300)
    root_pubkey = auth.public_key_hex
    rebalancer = DynamicThresholdRebalancer(baseline_threshold=2, baseline_total=3)

    print(f"[+] Initial Quorum Policy: {rebalancer.current_k}-of-{rebalancer.current_n}")

    # Initialize interceptor for GroupChat Manager
    interceptor = AutoGenBTPInterceptor(
        trusted_authorities=[root_pubkey],
        recipient_id="GroupChat-Manager-01"
    )

    # 1. Normal Multi-Agent Message Exchange
    print("\n--- [1] Processing Verified Peer Message ---")
    valid_payload = {"file": "app.py", "action": "code_review"}
    envelope = auth.evaluate_intent(
        "Developer-Agent",
        "CODE_REVIEW",
        valid_payload,
        target_recipient="GroupChat-Manager-01"
    )

    inbound_message = {
        "role": "user",
        "sender": "Developer-Agent",
        "action_type": "CODE_REVIEW",
        "content": valid_payload,
        "btp_envelope": envelope
    }

    verified_msg = interceptor.intercept_message(inbound_message)
    print(f"Outcome: {verified_msg.get('status', 'ACCEPTED')} (Signature & Invariants Valid)")

    # 2. Threat Spikes & Consensus Elevation
    print("\n--- [2] Simulating Attack Spikes & Automatic Quorum Elevation ---")
    attack_events = [
        KernelSyscallEvent(
            pid=4001,
            uid=1000,
            syscall_nr=59,
            action="BLOCK" if i % 2 == 0 else "ALLOW",
            comm="python",
            target="exfiltrate_secrets",
            timestamp_ns=time.time_ns()
        )
        for i in range(50)
    ]

    entropy, k, n, status = rebalancer.evaluate_threat_entropy(attack_events)
    print(f"[!] Threat Entropy Detected: {entropy * 100:.1f}%")
    print(f"[!] Consensus Quorum Dynamically Elevated: {k}-of-{n} ({status})")

    print("\n" + "=" * 70)
    print("  AutoGen GroupChat Demo Complete: Byzantine Attacks Thwarted")
    print("=" * 70)
    return True


if __name__ == "__main__":
    main()
