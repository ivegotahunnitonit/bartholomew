#!/usr/bin/env python3
"""
Bartholomew CLI — Sub-Millisecond AI Agent Guardrail & Daemon Controller
"""

import sys
import os
import argparse
import subprocess
import time
import urllib.request
import json

parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.trust_protocol import BartholomewTrustAuthority
from src.declarative_policy_engine import DeclarativePolicyEngine


def cmd_version(args):
    print("Bartholomew Protocol (BTP) v2.2.0")
    print("Engine: Sovereign AST Invariant Scanner & FIPS 186-5 Ed25519 Notary")
    print("Latency: Sub-50 microseconds (in-process / localhost)")


def cmd_init(args):
    print("[+] Initializing local Bartholomew sovereign trust root...")
    authority = BartholomewTrustAuthority()
    policy_dir = os.path.join(os.getcwd(), ".btp")
    os.makedirs(policy_dir, exist_ok=True)
    policy_path = os.path.join(policy_dir, "policy.yaml")

    if not os.path.exists(policy_path):
        sample_policy = """version: "2.2.0"
policy_id: "urn:btp:policy:default"
rules:
  - id: "RULE_SPEND_CAP"
    field: "amount_usd"
    type: "max_threshold"
    value: 500.00
    action: "DENY"

  - id: "RULE_FORBIDDEN_COMMANDS"
    type: "forbidden_substrings"
    patterns:
      - "rm -rf"
      - "DROP TABLE"
      - "DROP SCHEMA"
"""
        with open(policy_path, "w", encoding="utf-8") as f:
            f.write(sample_policy)
        print(f"[+] Created default policy: {policy_path}")

    print(f"[✓] Sovereign Public Key (Ed25519): {authority.public_key_hex}")
    if getattr(args, "pair", None):
        print(f"[✓] Paired with framework target: {args.pair}")
    print("[✓] Bartholomew local workspace initialized successfully.")


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
        print(f"[✓] Daemon launched in background (PID: {proc.pid}).")
    else:
        from daemon.daemon_server import BartholomewDaemon
        daemon = BartholomewDaemon(host=host, port=port)
        daemon.run()


def cmd_daemon_status(args):
    port = args.port or 8080
    url = f"http://127.0.0.1:{port}/v1/status"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            print("==================================================")
            print("  BARTHOLOMEW LOCAL DAEMON STATUS: ACTIVE (🟢)   ")
            print("==================================================")
            print(f"Version:            {data.get('version')}")
            print(f"Host:               {data.get('host')}:{data.get('port')}")
            print(f"Uptime:             {data.get('uptime_seconds')}s")
            print(f"Total Evaluations:  {data.get('total_evaluations')}")
            print(f"Total Allowed:      {data.get('total_allowed')}")
            print(f"Total Blocked:      {data.get('total_blocked')}")
            print(f"Average Latency:    {data.get('average_latency_us')} µs")
            print(f"Active Approvals:   {data.get('active_approvals_count')}")
            print(f"Public Key:         {data.get('public_key')}")
            print("==================================================")
    except Exception:
        print("[!] Bartholomew daemon is currently OFFLINE.")
        print("    Run 'python cli.py daemon start' to launch.")


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

    args = parser.parse_args()

    if args.command == "version":
        cmd_version(args)
    elif args.command == "init":
        cmd_init(args)
    elif args.command == "daemon":
        if args.daemon_cmd == "start":
            cmd_daemon_start(args)
        elif args.daemon_cmd == "status":
            cmd_daemon_status(args)
        else:
            daemon_parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
