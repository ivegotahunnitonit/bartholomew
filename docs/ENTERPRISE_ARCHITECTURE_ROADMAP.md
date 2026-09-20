# Bartholomew Trust Protocol (BTP) — Enterprise Architecture & Hardening Roadmap

This document specifies the enterprise security architecture, key management delegation, SIEM audit streaming, and kernel-level isolation roadmap for the Bartholomew Trust Protocol (BTP v2.5.0).

---

## 1. Hardware Security Module (HSM) & Cloud KMS Key Delegation

### Current Architecture (Step 3: The Digital Notary)
BTP currently generates sovereign, ephemeral Ed25519 keypairs in-memory at process initialization, signing RFC 8785 canonical JSON receipts in `<5 µs` with zero external cloud dependencies.

### Enterprise Target State
For regulated enterprise and institutional deployments (SOC 2 CC7.1, ISO 27001 A.8.30, FIPS 140-3 Level 3/4), BTP delegates root-of-trust key generation and periodic receipt rotation to managed key vaults:

1. **AWS KMS & GCP Cloud KMS Asymmetric Signing**:
   - Agent workers utilize an asymmetric Ed25519 or NIST P-256 signing key hosted in KMS.
   - To preserve sub-5µs hot-path execution, workers sign per-transaction Merkle leaves using an ephemeral session key that is certified by a periodic KMS-signed delegation token (valid for 5 to 60 minutes).
2. **HashiCorp Vault Transit Engine**:
   - The Transit Secrets Engine provides centralized key rotation, key versioning, and immediate trust-root revocation without restarting agent worker fleets.
3. **Hardware Security Module (PKCS#11)**:
   - For on-premises banking, defense, and sovereign clouds, BTP provides C FFI bindings directly to PKCS#11 hardware appliances (YubiHSM 2, Thales Luna, AWS CloudHSM).

---

## 2. Dynamic Multi-Tenant Policy Distribution (`btp sync`)

### Current State
Invariants are defined in local YAML/JSON configurations (`.btp/policy.yaml`) and evaluated synchronously in-process.

### Enterprise Control Plane Architecture
1. **Atomic In-Memory Hot-Reload**:
   - Agent workers expose a local Unix domain socket or loopback HTTP endpoint (`/v1/policy/reload`).
   - The `btp sync` CLI tool calculates an RFC 8785 canonical JSON SHA-256 digest of the candidate policy and pushes it to active workers.
   - Active execution harnesses atomically swap the active invariant pointer (`atomic.Value` / threading locks), ensuring ongoing transactions are never interrupted.
2. **Centralized Policy Orchestration**:
   - Distributed worker pools subscribe to an authenticated pub/sub control channel or poll a secure endpoint (`/v1/policy/active`) using HTTP ETag / If-None-Match caching.
   - Policies failing static invariant checks (e.g. contradictory spend limits or invalid regex patterns) are rejected before memory swap, automatically falling back to the immutable local baseline.

---

## 3. Automated Compliance Archiving & SIEM Streaming

### Current State
Deterministic Ed25519 Merkle receipts are persisted locally in canonical JSON Lines format (`audit_receipts.jsonl`) for automated test and CI/CD attestation.

### Enterprise Streaming Connectors
1. **Splunk HTTP Event Collector (HEC)**:
   - Batch-buffered asynchronous HTTP streaming of signed receipts directly to Splunk indexing clusters with zero latency impact on agent tool dispatch.
2. **Datadog Logs & Security Monitoring**:
   - Structured JSON streaming tagged with agent identity, capability scope, invariant evaluation verdict (`ALLOW`, `DENY`, `AUTO_REDACT`, `ROLLBACK`), and sub-microsecond latency metrics.
3. **AWS CloudWatch Logs & Amazon Kinesis Data Firehose**:
   - High-throughput streaming into immutable Amazon S3 Object Lock buckets for long-term SOC 2 and financial audit compliance.

---

## 4. Fine-Grained Kernel-Level Sandbox Isolation

### Current State
Step 2 workspace isolation enforces rigorous path traversal containment, file-write boundaries, and AST syntax tree verification.

### Enterprise Hardening: OS & Container Boundary Layer
1. **Linux Namespaces & cgroups v2 (`unshare`)**:
   - Restricts agent execution processes to private mount, PID, network, and IPC namespaces.
   - Enforces hard memory caps, CPU quotas, and process count limits to prevent runaway fork bombs or infinite allocation loops.
2. **eBPF Syscall Filtering**:
   - Attaches eBPF probes to low-level syscalls (`execve`, `ptrace`, `connect`, `bind`), killing unauthorized OS invocations before the kernel executes them.
3. **WebAssembly / WASI Isolation**:
   - For polyglot tool execution (Python, Node.js, Go, Rust), tools run inside an isolated WASM sandbox with zero access to the host filesystem unless explicitly granted by capability-based file descriptors.

---

## 5. Non-Human Identity (NHI) & Agent Identity Governance

1. **Per-Agent Cryptographic Identifiers**:
   - Each running agent instance is provisioned with a unique Ed25519 sub-identity registered in the cluster trust directory.
2. **Capability Scopes & Least Privilege**:
   - Tool capabilities are cryptographically bounded. An agent cannot call `EXECUTE_PAYMENT` unless its ephemeral attestation token explicitly includes the `payment:write` capability signed by the policy authority.
3. **Automatic Compromise Revocation**:
   - If an agent triggers two consecutive `DENY` verdicts on critical invariant gates (e.g. obfuscated syscall or raw disk wipe), the BTP harness automatically invalidates its active session token and isolates its network socket.
