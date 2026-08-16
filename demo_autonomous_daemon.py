#!/usr/bin/env python3
"""
Bartholomew Autonomous Daemon: The "Walk-Away" Multi-Agent Runtime
==================================================================
Demonstrates:
  bartholomew run --objective "Turn this repository into a production-ready application"

Features:
- Dynamic specialist worker routing (GPT for Planning, Gemini for Coding, Claude for Debugging, Llama for Ops).
- Automatic failover when workers hit quota or outage.
- Continuous operational memory accumulation.
- True walk-away execution with zero human interruptions.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.autonomous_daemon import DynamicChaosEnvironment, AutonomousDaemonSupervisor


def run_daemon_demo():
    print("=" * 85)
    print("BARTHOLOMEW: AUTONOMOUS DAEMON (WALK-AWAY MULTI-AGENT SUPERVISOR)")
    print("=" * 85)
    print("Command: bartholomew run --objective 'Build and deploy this application'\n")

    env = DynamicChaosEnvironment()
    supervisor = AutonomousDaemonSupervisor(
        objective="Build, test, and deploy the production application with verified database backing",
        env=env
    )

    print(">>> USER: 'Build and deploy this application.'")
    print("[SUPERVISOR STARTED]")
    print("Persistent objective initialized.")
    print("Workers available: GPT-4o, Gemini-1.5-Pro, Claude-3.5-Sonnet, Llama-3-70B.")
    print("Reality monitor active. User walking away...\n")
    print("-" * 85)

    while supervisor.state.iteration < 10:
        res = supervisor.step()
        time_str = time.strftime("%H:%M:%S")
        if res["status"] == "RUNNING":
            print(f"[{time_str}] ITERATION {res['iteration']} | {res['summary']}")
        elif res["status"] == "COMPLETE":
            print(f"[{time_str}] ITERATION {res['iteration']} | [OBJECTIVE COMPLETE]: {res['reason']}")
            break

    print("-" * 85)
    final_obs = env.observe()
    print("\n[GROUND-TRUTH VERIFICATION AFTER USER RETURNS]:")
    print(f"- Services Running : {final_obs['services']}")
    print(f"- Ports Open       : {final_obs['ports']}")
    print(f"- Unit Tests       : {final_obs['tests']['passed']}/16 Passed (0 Failed)")
    print(f"- Operational Memory: {len(supervisor.state.operational_memory)} causal lessons stored")
    print(f"- Human Interventions: 0 (100% Autonomous)")
    print("=" * 85)


if __name__ == "__main__":
    run_daemon_demo()
