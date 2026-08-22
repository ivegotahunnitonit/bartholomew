"""
Test Suite for Bartholomew Enterprise Verification Commitment SLA & eBPF Kernel Interceptor
"""

import sys
import os
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.verification_sla import VerificationCommitmentSLA
from src.kernel_interceptor import KernelTrajectoryInterceptor

def test_verification_commitment_sla():
    print("=" * 80)
    print("  TESTING ENTERPRISE VERIFICATION COMMITMENT & SLA ENGINE")
    print("=" * 80)
    
    sla_engine = VerificationCommitmentSLA(monthly_service_fee_usd=499.0)
    
    # 1. Issue Verification Receipt
    receipt = sla_engine.issue_verification_receipt(
        attestation_hash="d1bb1ca624ce43a903484a877bf95819",
        agent_id="Agent-OpenAI-GPT4o",
        action_type="DEPLOY_PATCH",
        sandbox_tests_passed=48,
        sandbox_tests_total=48
    )
    print(f"[RECEIPT ISSUED] ID: {receipt['receipt_id']} | Status: {receipt['status']}")
    print(f"   Audit: {receipt['sandbox_audit']}")
    assert receipt["status"] == "VERIFIED_ACTIVE"
    
    # 2. Test Invalid Claim
    claimed, msg, _ = sla_engine.evaluate_sla_claim(
        receipt_id=receipt["receipt_id"],
        incident_proof={"production_exit_code": 0}
    )
    print(f"[CLAIM 1: BOGUS] Result: {msg}")
    assert not claimed
    
    # 3. Test Verified SLA Credit Claim
    claimed, msg, credit = sla_engine.evaluate_sla_claim(
        receipt_id=receipt["receipt_id"],
        incident_proof={"production_exit_code": 1, "incident_trace_hash": "trace_err_500_auth_fail"}
    )
    print(f"[CLAIM 2: VALID INCIDENT] Result: {msg} | Credits: ${credit:,.2f}")
    assert claimed
    assert credit == 499.0
    print("[PASS] Enterprise Verification Commitment SLA verified 100%!")

def test_ebpf_kernel_interceptor():
    print("\n" + "=" * 80)
    print("  TESTING eBPF KERNEL TRAJECTORY INTERCEPTOR (RING-0 POSIX)")
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
    print("[PASS] eBPF Kernel Interceptor verified 100%!")

if __name__ == "__main__":
    test_verification_commitment_sla()
    test_ebpf_kernel_interceptor()
    print("\n[OK] All Verification Commitment & eBPF tests passed successfully.")
