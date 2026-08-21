"""
Bartholomew CLI Tool
====================
Command-line interface for policy validation, payload evaluation, and security auditing.
"""

import sys
import os
import json
import argparse

sys.path.insert(0, os.path.abspath("."))
from src.declarative_policy_engine import DeclarativePolicyEngine
from autonomous_assurance_scanner import AutonomousAssuranceEngine

def main():
    parser = argparse.ArgumentParser(
        prog="bartholomew",
        description="Bartholomew Sub-Millisecond Autonomous Security CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Policy Subcommand
    policy_parser = subparsers.add_parser("policy", help="Manage and test declarative policies")
    policy_sub = policy_parser.add_subparsers(dest="policy_action")

    # policy validate
    val_p = policy_sub.add_parser("validate", help="Validate a YAML/JSON policy file")
    val_p.add_argument("--file", "-f", required=True, help="Path to policy YAML/JSON file")

    # policy eval
    eval_p = policy_sub.add_parser("eval", help="Evaluate a JSON payload against a policy")
    eval_p.add_argument("--file", "-f", required=True, help="Path to policy YAML/JSON file")
    eval_p.add_argument("--payload", "-p", required=True, help="JSON string payload to test")

    # audit Subcommand
    audit_parser = subparsers.add_parser("audit", help="Audit local codebase for OWASP Agentic AI vulnerabilities")
    audit_parser.add_argument("--path", default=".", help="Target directory path to audit")

    # version Subcommand
    subparsers.add_parser("version", help="Print version and protocol information")

    args = parser.parse_args()

    if args.command == "version":
        print("Bartholomew Autonomous Trust Protocol (BTP) CLI v2.2.0")
        print("Protocol: BTP/2.2 (RFC 8785 + FIPS 186-5 Ed25519)")
        print("Target Latency: <175 µs")
        return

    elif args.command == "policy":
        if args.policy_action == "validate":
            try:
                engine = DeclarativePolicyEngine(args.file)
                print(f"[OK] Policy '{engine.policy_id}' is valid.")
                print(f"     Loaded {len(engine.rules)} active declarative rules.")
            except Exception as e:
                print(f"[ERROR] Failed to load policy: {str(e)}")
                sys.exit(1)

        elif args.policy_action == "eval":
            try:
                engine = DeclarativePolicyEngine(args.file)
                payload = json.loads(args.payload)
                allowed, reason, latency_us = engine.evaluate_payload(payload)
                verdict = "ALLOW" if allowed else "DENY"
                print(f"Verdict  : {verdict}")
                print(f"Latency  : {latency_us} µs")
                print(f"Reason   : {reason}")
                if not allowed:
                    sys.exit(2)
            except Exception as e:
                print(f"[ERROR] Evaluation failed: {str(e)}")
                sys.exit(1)

    elif args.command == "audit":
        engine = AutonomousAssuranceEngine()
        res = engine.audit_environment(args.path)
        print(f"Audit completed: {res['total_files_scanned']} files scanned. Status: {res['audit_status']}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
