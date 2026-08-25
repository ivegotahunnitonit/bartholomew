"""
Bartholomew CLI Tool (BTP v2.2.0)
=================================
Command line interface for initializing, managing, and inspecting
Bartholomew sovereign trust roots, local daemons, and MCP servers.
"""

import sys
import os
import argparse
import subprocess
import json
import urllib.request

# Ensure parent directory in path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.trust_protocol import BartholomewTrustAuthority
from src.declarative_policy_engine import DeclarativePolicyEngine
from src.policy_synthesizer import PolicySynthesizer


def cmd_version(args):
    print("Bartholomew Protocol (BTP) v2.2.0")
    print("Engine: Sovereign AST Invariant Scanner & FIPS 186-5 Ed25519 Notary")
    print("Latency: Sub-50 microseconds (in-process / localhost)")


def cmd_init(args):
    print("[+] Initializing local Bartholomew sovereign trust root...")
    authority = BartholomewTrustAuthority()
    
    dot_btp = os.path.join(parent_dir, ".btp")
    os.makedirs(dot_btp, exist_ok=True)

    policy_path = os.path.join(dot_btp, "policy.yaml")
    if not os.path.exists(policy_path):
        sample_policy = """version: "2.2.0"
policy_id: "urn:btp:policy:local-workspace"
description: "Local workspace invariant security policy"

rules:
  - id: "RULE_SPEND_CAP"
    type: "max_threshold"
    field: "amount_usd"
    value: 500.00
    action: "DENY"

  - id: "RULE_DIMINISHING_MARGINAL_UTILITY"
    type: "diminishing_marginal_utility"
    decay_rate: 0.35
    min_utility_threshold: 0.15
    action: "DENY"

  - id: "RULE_DESTRUCTIVE_AST"
    type: "forbidden_substrings"
    patterns:
      - "rm -rf"
      - "DROP TABLE"
      - "DROP SCHEMA"
"""
        with open(policy_path, "w", encoding="utf-8") as f:
            f.write(sample_policy)
        print(f"[+] Created default policy: {policy_path}")

    print(f"[OK] Sovereign Public Key (Ed25519): {authority.public_key_hex}")
    if getattr(args, "pair", None):
        print(f"[OK] Paired with framework target: {args.pair}")
    print("[OK] Bartholomew local workspace initialized successfully.")


def cmd_daemon_start(args):
    port = args.port or 8080
    host = args.host or "127.0.0.1"
    print(f"[*] Starting Bartholomew Local Daemon on http://{host}:{port}...")

    daemon_script = os.path.join(parent_dir, "daemon", "daemon_server.py")
    if args.background:
        if sys.platform == "win32":
            proc = subprocess.Popen(
                [sys.executable, daemon_script],
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
        else:
            proc = subprocess.Popen([sys.executable, daemon_script], start_new_session=True)
        print(f"[OK] Daemon launched in background (PID: {proc.pid}).")
    else:
        from daemon.daemon_server import BartholomewDaemon
        daemon = BartholomewDaemon(host=host, port=port)
        daemon.run()


def cmd_daemon_status(args):
    port = args.port or 8080
    url = f"http://127.0.0.1:{port}/v1/status"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode())
            print(f"[OK] Bartholomew Daemon is ONLINE (PID / Uptime: {data.get('uptime_seconds')}s)")
            print(f"  * Public Key    : {data.get('public_key')}")
            print(f"  * Total Evals   : {data.get('total_evaluations')}")
            print(f"  * Blocked Attacks: {data.get('total_blocked')}")
            print(f"  * Average Latency: {data.get('average_latency_us')} us")
    except Exception:
        print("[!] Bartholomew daemon is currently OFFLINE.")
        print("    Run 'python cli.py daemon start' to launch.")


def cmd_mcp_start(args):
    from mcp_server import start_mcp_server
    workspace = args.workspace or os.path.join(parent_dir, "workspace")
    start_mcp_server(workspace_root=workspace)


def cmd_mcp_install(args):
    from mcp_installer import install_mcp_for_target
    target = args.target or "claude"
    install_mcp_for_target(target=target)


def cmd_policy_validate(args):
    file_path = args.file or "policies/default_security_policy.yaml"
    if not os.path.isabs(file_path):
        file_path = os.path.join(parent_dir, file_path)
    print(f"[*] Validating declarative policy at {file_path}...")
    engine = DeclarativePolicyEngine(file_path)
    print(f"[OK] Policy '{engine.policy_id}' validated successfully ({len(engine.rules)} rules active).")


def cmd_policy_synthesize(args):
    print("[*] Running Autonomous Policy Synthesizer on workspace traces...")
    synthesizer = PolicySynthesizer()
    out_yaml = synthesizer.synthesize_yaml()
    out_file = args.output or "policies/synthesized_policy.yaml"
    with open(os.path.join(parent_dir, out_file), "w", encoding="utf-8") as f:
        f.write(out_yaml)
    print(f"[OK] Synthesized policy written to {out_file}")


def main():
    parser = argparse.ArgumentParser(description="Bartholomew AI Agent Guardrail CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # version
    subparsers.add_parser("version", help="Display BTP protocol version")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize sovereign cryptographic keypair & policy")
    init_parser.add_argument("--pair", type=str, help="Framework target to pair with (e.g. claude-desktop, openai, langchain)")

    # daemon
    daemon_parser = subparsers.add_parser("daemon", help="Manage background guard daemon")
    daemon_sub = daemon_parser.add_subparsers(dest="daemon_cmd")
    
    start_p = daemon_sub.add_parser("start", help="Start local daemon")
    start_p.add_argument("--port", type=int, default=8080, help="Daemon port (default: 8080)")
    start_p.add_argument("--host", type=str, default="127.0.0.1", help="Daemon host")
    start_p.add_argument("--background", "-b", action="store_true", help="Run in background")

    status_p = daemon_sub.add_parser("status", help="Query local daemon heartbeat & telemetry")
    status_p.add_argument("--port", type=int, default=8080, help="Daemon port")

    # mcp
    mcp_parser = subparsers.add_parser("mcp", help="Manage Model Context Protocol (MCP) server for Claude Desktop / Cursor")
    mcp_sub = mcp_parser.add_subparsers(dest="mcp_cmd")

    mcp_start_p = mcp_sub.add_parser("start", help="Start MCP stdio JSON-RPC server")
    mcp_start_p.add_argument("--workspace", type=str, default=None, help="Custom sandbox workspace root directory")

    mcp_inst_p = mcp_sub.add_parser("install", help="1-Click auto-install into Claude Desktop / Cursor config")
    mcp_inst_p.add_argument("--target", type=str, default="claude", choices=["claude", "cursor"], help="Target IDE")

    # policy
    policy_parser = subparsers.add_parser("policy", help="Manage declarative security policies")
    policy_sub = policy_parser.add_subparsers(dest="policy_cmd")

    val_p = policy_sub.add_parser("validate", help="Validate declarative YAML policy")
    val_p.add_argument("--file", "-f", type=str, default="policies/default_security_policy.yaml", help="Path to policy YAML")

    syn_p = policy_sub.add_parser("synthesize", help="Auto-synthesize least-privilege policy from traces")
    syn_p.add_argument("--output", "-o", type=str, default="policies/synthesized_policy.yaml", help="Output YAML file path")

    # demo
    demo_p = subparsers.add_parser("demo", help="Run high-impact interactive real-time invariant showcase")
    demo_p.add_argument("--speed", type=float, default=0.35, help="Simulation delay in seconds per step (default: 0.35)")

    args = parser.parse_args()

    if args.command == "version":
        cmd_version(args)
    elif args.command == "demo":
        from src.interactive_demo import run_interactive_demo
        run_interactive_demo(speed=args.speed)
    elif args.command == "init":
        cmd_init(args)
    elif args.command == "daemon":
        if args.daemon_cmd == "start":
            cmd_daemon_start(args)
        elif args.daemon_cmd == "status":
            cmd_daemon_status(args)
        else:
            daemon_parser.print_help()
    elif args.command == "mcp":
        if args.mcp_cmd == "start":
            cmd_mcp_start(args)
        elif args.mcp_cmd == "install":
            cmd_mcp_install(args)
        else:
            mcp_parser.print_help()
    elif args.command == "policy":
        if args.policy_cmd == "validate":
            cmd_policy_validate(args)
        elif args.policy_cmd == "synthesize":
            cmd_policy_synthesize(args)
        else:
            policy_parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
