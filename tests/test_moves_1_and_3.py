"""
Test Suite for Move 1 (Bonded Execution Warranty) and Move 3 (eBPF Kernel Interceptor)
"""

import sys
import os
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.bonded_warranty import BondedExecutionWarranty
from src.kernel_interceptor import KernelTrajectoryInterceptor

def test_bonded_warranty():
    print("=" * 80)
    print("  TESTING MOVE 1: BONDED EXECUTION WARRANTY & FINANCIALIZED TRUST")
    print("=" * 80)
    
    warranty_engine = BondedExecutionWarranty(reserve_pool_usd=100_000.0, max_bond_per_action_usd=10_000.0)
    
    # 1. Issue Bond
    bond = warranty_engine.issue_warranty_bond(
        attestation_hash="d1bb1ca624ce43a903484a877bf95819",
        agent_id="Agent-OpenAI-GPT4o",
        action_type="DEPLOY_PATCH",
        bond_amount_usd=10_000.0
    )
    print(f"[BOND ISSUED] ID: {bond['bond_id']} | Coverage: ${bond['bond_amount_usd']:,.2f}")
    assert bond["status"] == "ACTIVE_BONDED"
    
    # 2. Test Bogus Claim (No regression)
    claimed, msg, _ = warranty_engine.claim_warranty_payout(
        bond_id=bond["bond_id"],
        regression_proof={"production_exit_code": 0}
    )
    print(f"[CLAIM 1: BOGUS] Result: {msg}")
    assert not claimed
    
    # 3. Test Legitimate Incident Claim (Simulated regression proof)
    claimed, msg, payout = warranty_engine.claim_warranty_payout(
        bond_id=bond["bond_id"],
        regression_proof={"production_exit_code": 1, "incident_trace_hash": "trace_err_500_auth_fail"}
    )
    print(f"[CLAIM 2: VALID INCIDENT] Result: {msg} | Disbursed: ${payout:,.2f}")
    assert claimed
    assert payout == 10_000.0
    assert warranty_engine.reserve_pool_usd == 90_000.0
    print("[PASS] Move 1 Bonded Execution Warranty verified 100%!")

def test_ebpf_kernel_interceptor():
    print("\n" + "=" * 80)
    print("  TESTING MOVE 3: eBPF KERNEL TRAJECTORY INTERCEPTOR (RING-0 POSIX)")
    print("=" * 80)
    
    interceptor = KernelTrajectoryInterceptor()
    
    # 1. Safe Syscall
    allowed, msg = interceptor.intercept_syscall(
        syscall="sys_enter_execve",
        process_pid=1042,
        agent_ctx="Agent-OpenAI",
        payload_args=["/usr/bin/pytest", "-q", "tests/"]
    )
    print(f"[SAFE SYSCALL] {msg}")
    assert allowed
    
    # 2. Malicious Syscall Attempt
    allowed, msg = interceptor.intercept_syscall(
        syscall="sys_enter_openat",
        process_pid=1043,
        agent_ctx="Agent-Compromised",
        payload_args=["cat", "/etc/shadow"]
    )
    print(f"[BLOCKED SYSCALL] {msg}")
    assert not allowed
    assert interceptor.stats["blocked_threats"] == 1
    print("[PASS] Move 3 eBPF Kernel Interceptor verified 100%!")

if __name__ == "__main__":
    test_bonded_warranty()
    test_ebpf_kernel_interceptor()
    print("\n[OK] All Move 1 & Move 3 verification tests passed successfully.")
