#!/usr/bin/env python3
"""
Bartholomew Autonomous IDE Agent Supervisor Demo
================================================
Demonstrates walk-away autonomous development:
- User submits objective once.
- Supervisor maintains persistent objective & workspace state.
- Automatically handles agent stops, test failures, and model quota failover (Gemini -> Claude).
- Mechanically validates completion against reality (16/16 passing tests).
- 0 human prompts required.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.agent_supervisor import (
    PersistentObjective,
    WorkspaceRealityObserver,
    AutonomousSupervisor
)


def run_ide_supervisor_demo():
    print("=" * 85)
    print("BARTHOLOMEW: AUTONOMOUS IDE AGENT SUPERVISOR & CONTINUATION RUNTIME")
    print("=" * 85)
    print("Scenario: User dispatches objective -> Worker 1 creates code -> Worker 1 hits quota")
    print("          -> Supervisor fails over to Worker 2 -> Worker 2 finishes & tests pass.\n")

    objective = PersistentObjective(
        objective_id="obj_auth_service_001",
        description="Build authentication module in /workspace/app/src/auth.py with 16 passing tests",
        target_artifacts=["/workspace/app/src/auth.py"],
        required_tests=["test_auth_tokens", "test_expiry"],
        constraints=["sandbox:/workspace/app"]
    )

    observer = WorkspaceRealityObserver(workspace_root="/workspace/app")
    supervisor = AutonomousSupervisor(objective=objective, workspace_observer=observer)

    print(">>> USER DISPATCHES SUPERVISOR (Walking away)...")
    print("-" * 85)

    while supervisor.iteration < 5:
        res = supervisor.step()
        time_str = time.strftime("%H:%M:%S")
        if res["status"] == "CONTINUING":
            print(f"[{time_str}] ITERATION {res['iteration']} | {res['summary']}")
        elif res["status"] == "COMPLETE":
            print(f"[{time_str}] ITERATION {res['iteration']} | [OBJECTIVE SATISFIED]: {res['reason']}")
            break

    print("-" * 85)
    print("\n[FINAL VERIFICATION]:")
    final_snap = observer.observe_workspace()
    print(f"- Artifacts Present : {final_snap.files_present}")
    print(f"- Unit Test Results : {final_snap.test_results['passed']} Passed, {final_snap.test_results['failed']} Failed")
    print(f"- Git Workspace     : {final_snap.git_status}")
    print(f"- Human Interventions: 0 (100% Autonomous Continuation)")
    print("=" * 85)


if __name__ == "__main__":
    run_ide_supervisor_demo()
