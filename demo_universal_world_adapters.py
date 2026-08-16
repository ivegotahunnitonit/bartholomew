#!/usr/bin/env python3
"""
Bartholomew Universal World Adapter Demonstration
=================================================
Demonstrates the invariant 4-pillar reality interface across diverse worlds:
- GitHub (Repositories, PRs, Maintainer Feedback Loop)
- Docker (Containers, Runtimes, Port Telemetry)
- Security Advisories (Global CVE Feeds, Vulnerability Exploitability Filtering)

The model is interchangeable.
The world is interchangeable.
The reality interface stays constant.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.world_adapters import UniversalRealityRouter


def run_world_adapter_demo():
    print("=" * 90)
    print("BARTHOLOMEW: UNIVERSAL WORLD ADAPTER SUBSTRATE")
    print("=" * 90)
    print("Core Axiom: Models change. Worlds change. The Reality Interface stays constant.\n")

    # 1. WORLD: GITHUB
    print(">>> [1. CONNECTING TO WORLD: 'github' (psf/requests)]")
    gh = UniversalRealityRouter.connect("github", "psf/requests")
    gh_obs = gh.observe()
    print(f"    - Observed State : {gh_obs.state_metrics}")
    print(f"    - Anomaly Found  : {gh_obs.anomalies_detected}")
    gh_act = gh.act("patch_auth_retry", "src/auth.py", None)
    print(f"    - Action Result  : {gh_act.feedback_signal}")
    print(f"    - Verified Truth : {gh.verify(gh_act)}")
    # Maintainer Feedback Loop!
    gh.learn(gh_act, maintainer_feedback="PR #42 merged upstream by maintainer!")
    print(f"    - Learned Memory : {gh.memory[-1]['feedback']}")
    print()

    # 2. WORLD: DOCKER
    print(">>> [2. CONNECTING TO WORLD: 'docker' (local_cluster)]")
    dk = UniversalRealityRouter.connect("docker", "local_cluster")
    dk_obs = dk.observe()
    print(f"    - Observed State : {dk_obs.state_metrics}")
    dk_act = dk.act("restart_db", "postgres:15-alpine", None)
    print(f"    - Action Result  : {dk_act.feedback_signal}")
    print(f"    - Verified Truth : {dk.verify(dk_act)}")
    dk.learn(dk_act)
    print()

    # 3. WORLD: SECURITY ADVISORIES
    print(">>> [3. CONNECTING TO WORLD: 'security_advisories' (global_feed)]")
    sec = UniversalRealityRouter.connect("security_advisories", "global_feed")
    sec_obs = sec.observe()
    print(f"    - Observed State : {sec_obs.state_metrics}")
    print(f"    - Anomaly Found  : {sec_obs.anomalies_detected}")
    sec_act = sec.act("log_unexploitable", "CVE-2026-4410", None)
    print(f"    - Action Result  : {sec_act.feedback_signal}")
    sec.learn(sec_act)
    print()

    print("=" * 90)
    print("SUMMARY: Single coherent reality abstraction operating over code, containers, and web.")
    print("=" * 90)


if __name__ == "__main__":
    run_world_adapter_demo()
