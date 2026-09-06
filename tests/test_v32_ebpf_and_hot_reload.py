"""
Test Suite for BTP v3.2: Hot-Pluggable Invariants & Dynamic Threshold Rebalancing
Verifies:
1. Live reloading of kernel invariant rulesets without process restarts.
2. Rollback to previous policy generations on demand.
3. Real-time threat entropy calculation from syscall event streams.
4. Autonomous quorum rebalancing (2-of-3 -> 3-of-5 -> 5-of-7) under adversarial attacks.
"""

from src.ebpf_kernel_guard import (
    KernelSecurityPolicy,
    EBPFKernelGuard,
    HotPluggableInvariantEngine,
    DynamicThresholdRebalancer,
    KernelSyscallEvent
)


def test_hot_pluggable_invariant_reload():
    policy = KernelSecurityPolicy(blocked_binaries=["/bin/rm"])
    engine = HotPluggableInvariantEngine(initial_policy=policy)
    assert engine.generation == 1

    # Evaluation on baseline: 'curl' is allowed
    ok, _ = engine.active_policy.evaluate_execve("curl")
    assert ok is True

    # Hot-reload rule: block 'curl' live
    success, msg, gen = engine.hot_reload_rules(
        new_blocked_binaries=["curl", "wget"],
        change_rationale="Block unverified egress tooling"
    )
    assert success is True
    assert gen == 2
    assert engine.generation == 2

    # Verification: 'curl' is now blocked without restarting any agent processes
    ok_now, err = engine.active_policy.evaluate_execve("curl")
    assert ok_now is False
    assert "BTP-KERNEL-001" in err


def test_hot_pluggable_policy_rollback():
    policy = KernelSecurityPolicy()
    engine = HotPluggableInvariantEngine(initial_policy=policy)

    # Hot-reload generation 2
    engine.hot_reload_rules(new_blocked_binaries=["python_script.py"])
    assert engine.generation == 2

    # Rollback to generation 1
    rb_success, rb_msg, rb_gen = engine.rollback()
    assert rb_success is True
    assert rb_gen == 1
    assert engine.generation == 1

    # Secondary rollback should be rejected (already at baseline)
    rb2_ok, rb2_msg, _ = engine.rollback()
    assert rb2_ok is False
    assert "baseline" in rb2_msg.lower()


def test_dynamic_threshold_rebalancer():
    rebalancer = DynamicThresholdRebalancer(baseline_threshold=2, baseline_total=3)

    # Scenario 1: Empty or benign events -> 2-of-3 normal baseline
    benign_events = [
        KernelSyscallEvent(1001, 1000, 59, "ALLOW", "worker", "/usr/bin/python", 1000)
        for _ in range(10)
    ]
    entropy, k, n, status = rebalancer.evaluate_threat_entropy(benign_events)
    assert entropy == 0.0
    assert (k, n) == (2, 3)
    assert status == "NORMAL_BASELINE"

    # Scenario 2: Elevated threat (20% blocked syscalls) -> 3-of-5 rebalanced
    elevated_events = benign_events + [
        KernelSyscallEvent(1001, 1000, 59, "BLOCK", "worker", "/bin/rm", 2000),
        KernelSyscallEvent(1001, 1000, 263, "BLOCK", "worker", "/etc/shadow", 2001)
    ]
    entropy, k, n, status = rebalancer.evaluate_threat_entropy(elevated_events)
    assert entropy >= 0.15
    assert (k, n) == (3, 5)
    assert status == "ELEVATED_THREAT_REBALANCED"

    # Scenario 3: Critical attack spike (50% blocked syscalls) -> 5-of-7 quorum
    critical_events = [
        KernelSyscallEvent(1001, 1000, 59, "BLOCK", "worker", "/bin/dd", 3000)
        for _ in range(10)
    ] + [
        KernelSyscallEvent(1001, 1000, 59, "ALLOW", "worker", "/bin/ls", 3001)
        for _ in range(10)
    ]
    entropy, k, n, status = rebalancer.evaluate_threat_entropy(critical_events)
    assert entropy >= 0.40
    assert (k, n) == (5, 7)
    assert status == "CRITICAL_ATTACK_ELEVATION"
