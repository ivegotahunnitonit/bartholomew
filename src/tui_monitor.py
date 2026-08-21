"""
Bartholomew Real-Time Terminal Activity & Invariant Monitor (TUI)
=================================================================
Live terminal monitoring interface displaying real-time agent tool evaluations,
Ed25519 attestations, and microsecond latency metrics.
"""

import sys
import os
import time
import random

sys.path.insert(0, os.path.abspath("."))
from src.trust_protocol import BartholomewTrustAuthority

def run_tui_monitor(duration_seconds: int = 10):
    print("=" * 80)
    print("BARTHOLOMEW REAL-TIME AGENT INVARIANT MONITOR (TUI)")
    print("=" * 80)
    print("[*] Listening on local BTP stdio / IPC socket...")
    print("[*] Press Ctrl+C to stop monitoring.\n")

    authority = BartholomewTrustAuthority(ttl_seconds=300)
    
    actions = [
        ("EXECUTE_COMMAND", {"command": "git status"}, True),
        ("EXECUTE_COMMAND", {"command": "rm -rf /var/data"}, False),
        ("FILE_WRITE", {"path": "src/feature.py", "code": "def run(): pass"}, True),
        ("FILE_WRITE", {"path": "package.json", "code": "{}"}, False),
        ("FINANCIAL_TRANSFER", {"amount_usd": 49.00}, True),
        ("FINANCIAL_TRANSFER", {"amount_usd": 8500.00}, False),
        ("PYTHON_EXEC", {"code": "import os; s = os; s.system('id')"}, False),
        ("PYTHON_EXEC", {"code": "def fib(n): return n if n<=1 else fib(n-1)+fib(n-2)"}, True)
    ]

    start_time = time.time()
    total_evals = 0
    total_blocked = 0

    try:
        while time.time() - start_time < duration_seconds:
            action_type, payload, is_intended_clean = random.choice(actions)
            t0 = time.perf_counter()
            receipt = authority.evaluate_intent("agent-swarm-worker", action_type, payload)
            dt_us = (time.perf_counter() - t0) * 1_000_000
            
            verdict = receipt['attestation']['verdict']
            total_evals += 1
            if verdict == "DENY":
                total_blocked += 1

            status_color = "[ALLOW]" if verdict == "ALLOW" else "[BLOCKED]"
            sig_short = receipt['signature'][:16]
            ts = time.strftime("%H:%M:%S")

            print(f"[{ts}] {status_color:<9} | {action_type:<20} | {dt_us:6.2f} us | Sig: {sig_short}...")
            time.sleep(0.3)

    except KeyboardInterrupt:
        pass

    print("\n" + "=" * 80)
    print(f"MONITOR SUMMARY: {total_evals} Actions Evaluated | {total_blocked} Invariant Violations Blocked")
    print("=" * 80)

if __name__ == "__main__":
    run_tui_monitor(duration_seconds=3)
