# Secure Design and Architectural Invariants

This document outlines the formal secure design principles implemented across the **Bartholomew Trust Protocol (BTP v2.2)**.

---

## 1. Core Principles

### Principle 1: Fail-Safe Defaults
All execution paths default to `DENY`. Unless a tool action satisfies all configured AST rules, path boundaries, spend limits, and entropy invariants, execution is blocked immediately.

### Principle 2: Complete Mediation
Every action initiated by an autonomous agent must pass through the evaluation gate (`@guard.protect` or `guard.check()`). The execution effector is never exposed directly to untrusted LLM output.

### Principle 3: Least Privilege
Agent tools operate within minimal necessary scopes:
* Filesystem write access is restricted via hermetic path scoping (`is_relative_to(sandbox_root)`).
* Shell execution disables raw shell interpolation (`shell=False` POSIX tokenization).
* Spend tranches are restricted by monotonic decrementing balance caps.

### Principle 4: Deterministic Canonicalization (RFC 8785)
All intent evaluations and audit records are serialized using JSON Canonicalization Scheme (RFC 8785) prior to hashing. This guarantees byte-exact signature verification across Python, Go, and C.

### Principle 5: Defense-in-Depth
1. **Tier 1 (In-Memory Microsecond Invariants)**: Sub-5.0 µs pure-C AST node traversal and spend cap checks.
2. **Tier 2 (POSIX Hermetic Sandbox)**: Argument tokenization and directory isolation.
3. **Tier 3 (Container & Cluster Sidecars)**: Ephemeral Docker containers and Kubernetes cgroup resource constraints.

---

## 2. Threat Mitigation Matrix

| Threat | Attack Vector | Mitigation in Bartholomew |
| :--- | :--- | :--- |
| **Command Injection** | `echo cm0g... \| base64 -d \| sh` | POSIX tokenization, shell=False, binary whitelist |
| **Path Traversal** | `../../etc/passwd` | `os.path.commonpath` / `Path.is_relative_to()` scoping |
| **Infinite Retry Loops** | Runaway prompt failures burning money | Law of Diminishing Marginal Utility ($MU = e^{-\lambda n}$) decay |
| **Audit Log Tampering** | Retroactive log alteration | SHA-256 Merkle tree inclusion proofs with Ed25519 root signatures |
