"""
Bartholomew CLI Tool (v2.2.0)
=============================
Command-line interface for:
  1. Quickstart initialization (`bartholomew init`).
  2. Ed25519 keypair generation (`bartholomew keygen`).
  3. Declarative policy validation & testing (`bartholomew policy validate/eval`).
  4. Codebase security auditing (`bartholomew audit`).
"""

import sys
import os
import json
import argparse
from typing import Dict, Any

sys.path.insert(0, os.path.abspath("."))
from src.declarative_policy_engine import DeclarativePolicyEngine
from src.trust_protocol import BartholomewTrustAuthority
from src.ast_validator import ASTSecurityValidator

def init_project(target_dir: str = ".") -> None:
    """Initializes a new project with BTP security configuration and keys."""
    btp_dir = os.path.join(target_dir, ".btp")
    os.makedirs(btp_dir, exist_ok=True)

    # 1. Generate project policy file
    policy_path = os.path.join(btp_dir, "policy.yaml")
    if not os.path.exists(policy_path):
        default_policy = """# Bartholomew Trust Protocol - Project Security Policy
version: "2.2"
policy_id: "project_default_security_policy"
description: "Zero-cloud sub-millisecond invariant policy for local agent workflows"

rules:
  - id: "INVARIANT_SPEND_CAP"
    description: "Blocks autonomous single transactions exceeding $500"
    field: "amount_usd"
    operator: "<="
    value: 500.0

  - id: "INVARIANT_DESTRUCTIVE_SQL"
    description: "Prohibits DROP and TRUNCATE SQL queries"
    field: "query"
    operator: "not_contains"
    values: ["drop table", "drop schema", "truncate table", "drop database"]

  - id: "INVARIANT_RESTRICTED_FILES"
    description: "Blocks modifying protected system and environment configs"
    field: "path"
    operator: "not_contains"
    values: [".env", "id_rsa", "package.json", "conftest.py"]
"""
        with open(policy_path, "w", encoding="utf-8") as f:
            f.write(default_policy)

    # 2. Initialize local Trust Authority keypair
    auth = BartholomewTrustAuthority()
    key_info_path = os.path.join(btp_dir, "trust_root.json")
    with open(key_info_path, "w", encoding="utf-8") as f:
        json.dump({
            "public_key_hex": auth.public_key_hex,
            "protocol_version": "BTP/2.2",
            "ttl_seconds": auth.ttl_seconds
        }, f, indent=2)

    print("=" * 70)
    print("SUCCESS: Bartholomew BTP Initialized in current workspace!")
    print("=" * 70)
    print(f"[*] Configuration : {policy_path}")
    print(f"[*] Trust Root    : {key_info_path}")
    print(f"[*] Public Key    : {auth.public_key_hex}")
    print("\n[+] To attach to Claude Desktop, add this to your claude_desktop_config.json:")
    print(json.dumps({
        "mcpServers": {
            "bartholomew-guard": {
                "command": "python",
                "args": ["-m", "mcp_server.server"],
                "cwd": os.path.abspath(target_dir)
            }
        }
    }, indent=2))
    print("=" * 70)

def generate_key() -> None:
    """Generates and prints a fresh Ed25519 keypair."""
    auth = BartholomewTrustAuthority()
    print("=" * 70)
    print("BARTHOLOMEW ED25519 KEYPAIR GENERATION")
    print("=" * 70)
    print(f"[*] Public Key (Hex) : {auth.public_key_hex}")
    print(f"[*] TTL Policy Bound : {auth.ttl_seconds} seconds")
    print(f"[*] Algorithm        : Pure Ed25519 (RFC 8032 / FIPS 186-5)")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(
        prog="bartholomew",
        description="Bartholomew Sub-Millisecond Autonomous Security CLI (v2.2.0)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init Subcommand
    init_parser = subparsers.add_parser("init", help="Initialize BTP security policy and MCP setup in current project")
    init_parser.add_argument("--dir", default=".", help="Target project directory")

    # keygen Subcommand
    subparsers.add_parser("keygen", help="Generate a new Ed25519 sovereign keypair")

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

    # demo Subcommand
    demo_parser = subparsers.add_parser("demo", help="Run high-impact interactive real-time invariant showcase")
    demo_parser.add_argument("--speed", type=float, default=0.35, help="Simulation delay in seconds per step (default: 0.35)")

    # version Subcommand
    subparsers.add_parser("version", help="Print version and protocol information")

    args = parser.parse_args()

    if args.command == "version":
        print("Bartholomew Autonomous Trust Protocol (BTP) CLI v2.2.0")
        print("Protocol: BTP/2.2 (RFC 8785 + FIPS 186-5 Ed25519)")
        print("Target Latency: <55 µs")
        return

    elif args.command == "demo":
        from src.interactive_demo import run_interactive_demo
        run_interactive_demo(speed=args.speed)
        return

    elif args.command == "init":
        init_project(args.dir)

    elif args.command == "keygen":
        generate_key()

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
        scanned = 0
        violations = 0
        for root, _, files in os.walk(args.path):
            for f in files:
                if f.endswith(".py"):
                    scanned += 1
                    try:
                        with open(os.path.join(root, f), "r", encoding="utf-8") as fp:
                            code = fp.read()
                        safe, reason, _ = ASTSecurityValidator.validate_code_ast(code)
                        if not safe:
                            violations += 1
                            print(f"[VIOLATION] {f}: {reason}")
                    except Exception:
                        pass
        status = "PASSED" if violations == 0 else f"{violations} VIOLATIONS DETECTED"
        print(f"AST Security Audit completed: {scanned} Python files scanned. Status: {status}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
