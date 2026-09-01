"""
Bartholomew Live Dangerous Code Interception Test
=================================================
Runs real-world hostile tool payloads through btp-guard in memory.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath("."))
import btp_guard

DANGEROUS_SUITE = [
    (
        "Hostile OS Wipe",
        "import os; os.system('rm -rf /')",
        "Should block destructive filesystem wipe."
    ),
    (
        "SQL Table Drop",
        "DROP TABLE customers CASCADE;",
        "Should block dangerous DDL database drop."
    ),
    (
        "Obfuscated Shell Execution",
        "getattr(__import__('os'), 'system')('cat /etc/shadow')",
        "Should detect dynamic reflection/obfuscation and block."
    ),
    (
        "Disk Formatting Subprocess",
        "import subprocess; subprocess.Popen(['mkfs.ext4', '/dev/sda'])",
        "Should block raw disk partition formatting."
    ),
    (
        "Normal Safe Business Logic",
        "import math\ndef calculate_invoice(hours, rate):\n    return round(hours * rate, 2)",
        "Should allow safe standard Python math functions."
    )
]

def main():
    print("=" * 80)
    print("  BARTHOLOMEW LIVE DANGEROUS CODE INTERCEPTION TEST (IN-MEMORY)")
    print("=" * 80)

    from src.polyglot_ast_validator import PolyglotASTValidator
    from src import Guard

    guard_instance = Guard()

    for idx, (label, code, expectation) in enumerate(DANGEROUS_SUITE, start=1):
        t0 = time.perf_counter()
        is_safe, verdict_reason, meta = PolyglotASTValidator.validate_code(code)
        latency_us = (time.perf_counter() - t0) * 1_000_000

        badge = "[PASSED (SAFE)]" if is_safe else "[BLOCKED (VETO)]"

        print(f"\n[{idx}] PAYLOAD: {label.upper()} -> {badge}")
        print(f"    Target Code:  {code.replace(chr(10), ' ')}")
        print(f"    Verdict:      {verdict_reason}")
        print(f"    Latency:      {latency_us:.2f} microseconds (us)")
        print(f"    Expected:     {expectation}")
        print("-" * 80)

    print("=" * 80)
    print("Test finished successfully.")

if __name__ == "__main__":
    main()
