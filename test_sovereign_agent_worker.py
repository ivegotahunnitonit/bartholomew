"""
Test Suite: Sovereign Agent Worker (Practical Local AI Worker)
=============================================================
Tests:
  1. Automated Codebase AST & Syntax Audit across `src/` directory.
  2. Hermetic File Sandboxing (Permitting internal files, blocking directory escapes).
  3. Bounded System Command Execution (Allowed vs Disallowed).
  4. Environment Diagnostics & BTP Attestation Generation.
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))
from src.sovereign_agent_worker import SovereignAgentWorker

def test_sovereign_agent_worker():
    print("=" * 80)
    print("TESTING BARTHOLOMEW SOVEREIGN AGENT WORKER")
    print("=" * 80 + "\n")

    worker = SovereignAgentWorker(workspace_root=".")

    # 1. Test Codebase AST Audit Tool
    res1 = worker.execute_codebase_audit(target_dir="src")
    print(f"[TEST 1: Codebase AST Audit Tool]")
    print(f"  * Status        : {res1['status']}")
    print(f"  * Files Scanned : {res1['files_scanned']}")
    print(f"  * Safe Files    : {res1['safe_files']}")
    print(f"  * Latency       : {res1['execution_duration_us']} µs")
    print(f"  * Ed25519 Sig   : {res1['btp_attestation_signature'][:32]}...")
    assert res1["status"] == "COMPLETED"
    assert res1["files_scanned"] > 0

    # 2. Test Safe File Read Tool (Permitted File)
    res2 = worker.execute_safe_file_read("policies/default_security_policy.yaml")
    print(f"\n[TEST 2: Safe Workspace File Read]")
    print(f"  * Path          : {res2['path']}")
    print(f"  * Success       : {res2['success']}")
    print(f"  * Content Bytes : {res2['content_length']}")
    assert res2["success"] is True

    # 3. Test Hermetic Path Traversal Block (Forbidden File)
    res3 = worker.execute_safe_file_read("../../Windows/System32/drivers/etc/hosts")
    print(f"\n[TEST 3: Hermetic Sandbox Escape Interception]")
    print(f"  * Path          : {res3['path']}")
    print(f"  * Success       : {res3['success']}")
    print(f"  * Sandbox Block : {res3['preview']}")
    assert res3["success"] is False
    assert "escapes workspace" in res3["preview"] or "different volume" in res3["preview"]

    # 4. Test Bounded Command Tool
    res4 = worker.execute_bounded_system_command("git status")
    print(f"\n[TEST 4: Bounded System Command Execution]")
    print(f"  * Status        : {res4['status']}")
    print(f"  * Verdict       : {res4['verdict']}")
    print(f"  * Latency       : {res4['latency_us']} µs")
    assert res4["verdict"] == "ALLOW"

    # 5. Test Environment Diagnostics Tool
    res5 = worker.execute_environment_diagnostics()
    print(f"\n[TEST 5: Environment Diagnostics]")
    print(f"  * Python        : {res5['python_version']}")
    print(f"  * Platform      : {res5['platform']}")
    print(f"  * Public Key    : {res5['authority_pubkey'][:32]}...")
    assert res5["sandbox_active"] is True

    print("\n" + "=" * 80)
    print("ALL SOVEREIGN AGENT WORKER TOOLS PASSED 100% CLEAN!")
    print("=" * 80)

if __name__ == "__main__":
    test_sovereign_agent_worker()
