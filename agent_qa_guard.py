#!/usr/bin/env python3
"""
Agentic-Eval CLI Tool (agent-qa-guard)
Command-line security scanner and OWASP LLM Top 10 trajectory auditor.
Usage:
    python agent_qa_guard.py audit trajectory.json
    python agent_qa_guard.py sanitize trajectory.json
"""
import sys
import json
import argparse
from python_backend.app.agent_eval_janitor import janitor_engine
from python_backend.app.micro_api_suite import micro_api_suite

def main():
    parser = argparse.ArgumentParser(description="Agentic-Eval Security & OWASP Trajectory Auditor CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    audit_parser = subparsers.add_parser("audit", help="Audit trajectory JSON file against OWASP LLM Top 10 rules")
    audit_parser.add_argument("file", help="Path to JSON trajectory file")

    sanitize_parser = subparsers.add_parser("sanitize", help="Sanitize trajectory JSON file and scrub unmasked secrets")
    sanitize_parser.add_argument("file", help="Path to JSON trajectory file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading file '{args.file}': {e}")
        sys.exit(1)

    if args.command == "audit":
        report = janitor_engine.evaluate_agent_trajectory(data)
        print(json.dumps(report, indent=2))
        if report.get("audit_summary", {}).get("compliance_status") == "SECURITY_RISK":
            sys.exit(1)
        sys.exit(0)

    elif args.command == "sanitize":
        raw_str = json.dumps(data)
        masked_res = micro_api_suite.mask_secrets(raw_str)
        print(json.dumps(masked_res, indent=2))
        sys.exit(0)

if __name__ == "__main__":
    main()
