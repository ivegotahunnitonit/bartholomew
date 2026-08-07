"""
bartholomew_eval.cli
====================
CLI terminal runner for Bartholomew AI Agent Security & Trajectory Auditor.
"""

from __future__ import annotations

import json
import sys
from typing import List, Optional

from .engine import BartholomewEngine


def main(args: Optional[List[str]] = None) -> int:
    """CLI main entry point for bartholomew."""
    if args is None:
        args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print("======================================================================")
        print(" BARTHOLOMEW AI AGENT SECURITY & TRAJECTORY AUDITOR CLI")
        print("======================================================================")
        print("Usage:")
        print("  bartholomew scan <trajectory_file.json>  # Scan trajectory JSON file")
        print("  bartholomew init                         # Create sample @guard template")
        print("  bartholomew version                      # Print package version")
        print("======================================================================")
        return 0

    command = args[0].lower()

    if command in ("-v", "--version", "version"):
        from . import __version__
        print(f"bartholomew-eval v{__version__}")
        return 0

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
            print(f"[ERROR] Failed to create template file: {e}")
            return 1

    if command in ("scan", "audit"):
        if len(args) < 2:
            print("[ERROR] Missing JSON trajectory file path! Usage: bartholomew scan <file.json>")
            return 1
        filepath = args[1]
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            engine = BartholomewEngine()
            result = engine.evaluate_trajectory(data)
            print(json.dumps(result, indent=2))
            return 0 if result.get("audit_summary", {}).get("compliance_status") == "SOC2_PASSED" else 1
        except Exception as e:
            print(f"[ERROR] Failed to scan file `{filepath}`: {e}")
            return 1

    print(f"[ERROR] Unknown command `{command}`. Run `bartholomew --help` for usage.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
