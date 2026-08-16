#!/usr/bin/env python3
"""
Bartholomew Self-Driving Autonomous Runtime Demo
================================================
Demonstrates the continuous, self-driving autonomous execution loop:
- User submits objective once.
- Runtime continuously loops: OBSERVE -> REASON -> ACT -> VERIFY -> REPEAT.
- Zero human input() calls or message interruptions.
- Streams live, machine-grounded telemetry until objective is mechanically satisfied.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.autonomous_runtime import AutonomousRuntime
from bartholomew_eval.reality_substrate import BartholomewRealitySubstrate
from bartholomew_eval.agent_protocol import CryptographicIdentityCredential


def run_self_driving_demo():
    print("=" * 85)
    print("BARTHOLOMEW: SELF-DRIVING AUTONOMOUS RUNTIME")
    print("=" * 85)
    print("Loop: User inputs objective once -> System drives to mechanical completion.\n")

    cred = CryptographicIdentityCredential(
        agent_did="did:bth:autonomous_runner_01",
        issuer_did="did:bth:root_org",
        issuer_pub_key="pubkey_root_org",
        possessed_capabilities=["fs:read", "fs:write", "test:run"],
        constraint_manifest=["sandbox:/workspace/app"]
    )

    env = BartholomewRealitySubstrate(agent_cred=cred, allowed_paths=["/workspace/app"])

    runtime = AutonomousRuntime(
        objective="Build, test, and verify the token authentication service in /workspace/app",
        env=env,
        max_iterations=10
    )

    print(">>> USER DISPATCHES RUNTIME (Walking away)...")
    print("-" * 85)
    
    result = runtime.run()

    print("-" * 85)
    print(f"\n[FINAL STATUS]: {result['status']}")
    print(f"Total Iterations Driven: {result['iterations']}")
    print(f"Total Events Logged   : {result['total_events']}")
    print(f"Human Inputs Required : 0 (100% Autonomous Continuous Loop)")
    print("=" * 85)


if __name__ == "__main__":
    run_self_driving_demo()
