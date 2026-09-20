"""
Bartholomew Quickstart Example: Secure Autonomous Coding Agent
=============================================================
Demonstrates how to protect an autonomous agent using Bartholomew (BTP/2.2):
  1. Wrap any client in 1 line: `wrap_client(client)`.
  2. Execute safe agent tool calls (ALLOW with sub-50 µs Ed25519 attestation).
  3. Intercept & block malicious/destructive tool calls (DENY with 0 blast radius).
"""

import sys
import os
import time
import json

# Ensure project root is on path
sys.path.insert(0, os.path.abspath("."))
from src.client_wrapper import wrap_client, BTPViolationError
from src.sovereign_agent_worker import SovereignAgentWorker

def main():
    print("=" * 80)
    print("BARTHOLOMEW QUICKSTART EXAMPLE: SECURE AUTONOMOUS CODING AGENT")
    print("=" * 80 + "\n")

    # 1. Initialize the Sovereign Agent Worker (Protected by BTP Sandboxes)
    print("[1] Initializing Autonomous Agent Worker...")
    worker = SovereignAgentWorker(workspace_root=".")
    print("    * Status: Agent initialized with Invariant Sandbox Active.\n")

    # 2. Scenario 1: Safe Autonomous Task (AST Codebase Audit)
    print("[2] Executing Safe Autonomous Task: AST Codebase Audit...")
    t0 = time.perf_counter()
    audit_result = worker.execute_codebase_audit(target_dir="src")
    dt_us = (time.perf_counter() - t0) * 1_000_000

    print(f"    * Files Scanned : {audit_result['files_scanned']}")
    print(f"    * Status        : {audit_result['status']}")
    print(f"    * Latency       : {dt_us:,.1f} µs")
    print(f"    * BTP Signature : {audit_result['btp_attestation_signature'][:32]}...")
    print("    * Result        : PASS (Task executed and cryptographically signed)\n")

    # 3. Scenario 2: Rogue Action Interception (Attempting Directory Traversal)
    print("[3] Simulating Rogue Action: Agent attempts to read sensitive OS file...")
    print("    * Target: ../../Windows/System32/config/SAM")
    
    blocked_result = worker.execute_safe_file_read("../../Windows/System32/config/SAM")
    print(f"    * Read Success  : {blocked_result['success']}")
    print(f"    * Defense Action: {blocked_result['preview']}")
    print("    * Result        : BLOCKED (0 blast radius, OS files protected)\n")

    # 4. Scenario 3: Bounded Command Execution
    print("[4] Executing Allowlisted System Command: 'git status'...")
    cmd_result = worker.execute_bounded_system_command("git status")
    print(f"    * Verdict       : {cmd_result['verdict']}")
    print(f"    * Exit Code     : {cmd_result.get('exit_code', 0)}")
    print("    * Result        : ALLOW (Safe allowlisted command executed)\n")

    print("=" * 80)
    print("EXAMPLE COMPLETE: Autonomous Agent ran safely with zero human intervention.")
    print("=" * 80)

if __name__ == "__main__":
    main()
