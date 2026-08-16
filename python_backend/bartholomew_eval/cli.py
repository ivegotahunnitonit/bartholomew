"""
bartholomew_eval.cli
====================
CLI terminal runner for Bartholomew AI Agent Security & Trajectory Auditor v7.0.
"""

from __future__ import annotations

import json
import sys
import time
from typing import List, Optional

from .engine import BartholomewEngine


_HELP = """\
+----------------------------------------------------------------------------------+
|   BARTHOLOMEW AI AGENT SECURITY & TRAJECTORY AUDITOR  *  v7.2                    |
+----------------------------------------------------------------------------------+
|  scan        <file.json>        Audit a trajectory JSON file                     |
|  scan-codebase [dir]            SAST / SCA / IaC full repo scan                  |
|  report      <file.json>        Full audit report saved as Markdown              |
|  benchmark   [n]                Latency & throughput benchmark (n trajs)         |
|  swarm       <proposals.json>   Multi-agent swarm consensus from JSON            |
|  verify      <file.json>        Verify Ed25519 Evidence Artifact                 |
|  advisories                     Print security advisory log                      |
|  init                           Create a sample @guard agent template            |
|  version (-v)                   Print package version                            |
+----------------------------------------------------------------------------------+
"""


def main(args: Optional[List[str]] = None) -> int:
    """CLI main entry point for bartholomew."""
    if args is None:
        args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print(_HELP)
        return 0

    command = args[0].lower()

    # ── verify ────────────────────────────────────────────────────────────────
    if command == "verify":
        from .verifier import main as verifier_main
        return verifier_main(args)

    # ── version ──────────────────────────────────────────────────────────────
    if command in ("-v", "--version", "version"):
        from . import __version__
        print(f"bartholomew-eval v{__version__}")
        return 0

    # ── advisories ────────────────────────────────────────────────────────────
    if command == "advisories":
        engine = BartholomewEngine(secret_key="bartholomew-cli-demo")
        advisories = engine.get_security_advisories()
        print(f"\n[BARTHOLOMEW] Security Advisory Log — {len(advisories)} entries\n")
        for adv in advisories:
            print(f"  [{adv['severity']}] {adv['id']} — {adv['title']}")
            print(f"         Status : {adv['status']}")
            print(f"         Date   : {adv['date']}")
            print()
        return 0

    # ── init ──────────────────────────────────────────────────────────────────
    if command == "init":
        filename = "secured_agent_sample.py"
        sample_code = (
            "from bartholomew_eval import guard\n\n"
            "@guard(max_budget_tokens=1000, secret_scrubbing=True)\n"
            "def safe_agent_step(user_prompt: str) -> str:\n"
            "    return f'Processed query: {user_prompt}'\n\n"
            "if __name__ == '__main__':\n"
            "    print(safe_agent_step('Hello Bartholomew AI'))\n"
        )
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(sample_code)
            print(f"[INIT] Created sample guarded agent in `{filename}`!")
            return 0
        except Exception as e:
            print(f"[ERROR] Failed to create template: {e}")
            return 1

    # ── scan ──────────────────────────────────────────────────────────────────
    if command in ("scan", "audit"):
        if len(args) < 2:
            print("[ERROR] Missing JSON trajectory file path. Usage: bartholomew scan <file.json>")
            return 1
        filepath = args[1]
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            engine = BartholomewEngine(secret_key="bartholomew-cli-scan")
            result = engine.evaluate_trajectory(data)
            print(json.dumps(result, indent=2))
            status = result.get("audit_summary", {}).get("compliance_status", "")
            return 0 if status == "SOC2_PASSED" else 1
        except Exception as e:
            print(f"[ERROR] Failed to scan `{filepath}`: {e}")
            return 1

    # ── scan-codebase ─────────────────────────────────────────────────────────
    if command in ("scan-codebase", "scan-vulnerabilities", "vuln-scan"):
        from .vulnerability_scanner import BartholomewVulnerabilityScanner
        target_dir = args[1] if len(args) > 1 else "."
        print(f"[BARTHOLOMEW] Launching Enterprise AST Taint & Vulnerability Audit on `{target_dir}`...")
        scanner = BartholomewVulnerabilityScanner()
        report = scanner.audit_workspace_repository(target_dir)
        print(json.dumps(report, indent=2))
        return 0 if report.get("total_vulnerabilities", 0) == 0 else 1

    # ── report ────────────────────────────────────────────────────────────────
    if command == "report":
        if len(args) < 2:
            print("[ERROR] Missing JSON trajectory file. Usage: bartholomew report <file.json>")
            return 1
        filepath = args[1]
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            engine = BartholomewEngine(secret_key="bartholomew-cli-report")
            result = engine.evaluate_trajectory(data)
            summary = result.get("audit_summary", {})
            md = _render_markdown_report(filepath, summary, result)
            out_path = filepath.replace(".json", "_bartholomew_report.md")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(md)
            print(md)
            print(f"\n[REPORT] Saved to `{out_path}`")
            return 0
        except Exception as e:
            print(f"[ERROR] Failed to generate report: {e}")
            return 1

    # ── benchmark ─────────────────────────────────────────────────────────────
    if command == "benchmark":
        n = int(args[1]) if len(args) > 1 and args[1].isdigit() else 100
        print(f"[BARTHOLOMEW] Running latency & throughput benchmark ({n} synthetic trajectories)...")
        engine = BartholomewEngine(secret_key="bartholomew-bench-key")
        trajs = [
            {
                "agent_name": f"BenchBot-{i}",
                "steps": [
                    {"step_index": 1, "type": "thought", "content": f"Analyzing request {i}"},
                    {"step_index": 2, "type": "action",  "content": f"Fetched data from endpoint {i}"},
                    {"step_index": 3, "type": "thought", "content": f"Validated output for request {i}"},
                ],
            }
            for i in range(n)
        ]
        t0 = time.perf_counter()
        results = [engine.evaluate_trajectory(t) for t in trajs]
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        total_steps = n * 3
        tps = total_steps / (elapsed_ms / 1000.0)
        avg_ms = elapsed_ms / n
        passed = sum(1 for r in results if r["audit_summary"]["compliance_status"] == "SOC2_PASSED")
        print(f"\n{'-'*60}")
        print(f"  Trajectories Audited : {n}")
        print(f"  Total Steps          : {total_steps}")
        print(f"  Total Elapsed        : {elapsed_ms:.2f} ms")
        print(f"  Avg Latency / Traj   : {avg_ms:.3f} ms")
        print(f"  Throughput           : {tps:,.0f} steps/sec")
        print(f"  SOC2 Passed          : {passed}/{n}")
        print(f"{'-'*60}\n")
        return 0

    # ── swarm ─────────────────────────────────────────────────────────────────
    if command == "swarm":
        if len(args) < 2:
            print("[ERROR] Missing proposals JSON. Usage: bartholomew swarm <proposals.json>")
            print('  JSON: {"task": "...", "propositions": [{"agent_id": ..., "proposed_path": ..., ...}]}')
            return 1
        filepath = args[1]
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            from .swarm_federation import SovereignSwarmFederation
            swarm = SovereignSwarmFederation()
            task = data.get("task", "Unspecified task")
            propositions = data.get("propositions", [])
            if not propositions:
                print("[ERROR] No propositions found in swarm JSON.")
                return 1
            result = swarm.synthesize_optimal_swarm_outcome(task, propositions)
            print(json.dumps(result, indent=2))
            return 0
        except Exception as e:
            print(f"[ERROR] Swarm synthesis failed: {e}")
            return 1

    print(f"[ERROR] Unknown command `{command}`. Run `bartholomew --help` for usage.")
    return 1


def _render_markdown_report(filepath: str, summary: dict, full_result: dict) -> str:
    """Render a human-readable Markdown audit report."""
    status = summary.get("compliance_status", "UNKNOWN")
    score = summary.get("reliability_score_pct", 0.0)
    grade_icon = "[PASSED]" if status == "SOC2_PASSED" else ("[WARNING]" if status == "WARNING" else "[CRITICAL]")
    violations = summary.get("violations", [])
    lines = [
        f"# {grade_icon} Bartholomew Audit Report",
        "",
        f"**File:** `{filepath}`  ",
        f"**Agent:** `{full_result.get('agent_name', 'unknown')}`  ",
        f"**Timestamp:** `{summary.get('timestamp', 'N/A')}`  ",
        "",
        "## Compliance Status",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Status | `{status}` |",
        f"| Reliability Score | `{score}%` |",
        f"| Credential Leaks | `{summary.get('credential_leaks', 0)}` |",
        f"| Prompt Injections | `{summary.get('prompt_injections', 0)}` |",
        f"| Total Violations | `{summary.get('total_violations', 0)}` |",
        f"| Audit Latency | `{summary.get('latency_ms', 0):.3f} ms` |",
        "",
        "## Attestation",
        "```",
        f"SHA-256: {summary.get('attestation_sha256', 'N/A')}",
        "```",
        "",
    ]
    if violations:
        lines += ["## Violations", ""]
        for v in violations:
            lines.append(f"- [FLAG] {v}")
        lines.append("")
    else:
        lines += ["## Violations", "", "No violations detected. [OK]", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
