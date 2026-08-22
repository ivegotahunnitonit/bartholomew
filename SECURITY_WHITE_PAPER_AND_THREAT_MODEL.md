# Bartholomew Architecture White Paper & Formal Threat Model

**Version:** 2.2.0 (Standards Track)  
**Author:** Bartholomew AI Security Contributors  
**Classification:** Public Security Specification  

---

## 1. Executive Summary

Bartholomew is an open-source, deterministic cryptographic invariant gateway designed to secure autonomous AI agent workflows across local environments, cloud containers, and multi-agent swarms. 

Unlike probabilistic prompt filters, Bartholomew provides **sub-50 microsecond in-process Abstract Syntax Tree (AST) static analysis**, **epistemic provenance grounding**, and **FIPS 186-5 / RFC 8785 Ed25519 cryptographic execution receipts**.

This document outlines the formal threat model, privilege boundaries, attack surfaces, and architectural justifications for enterprise security auditors.

---

## 2. Formal Threat Model & Adversary Capabilities

### 2.1 Adversary Assumptions
We model an adversary who can:
1. **Manipulate LLM Contexts (Indirect Prompt Injection)**: Inject malicious natural language instructions into retrieved documents, API responses, or repository source code to coerce an autonomous agent into executing unauthorized tool calls (`rm -rf`, `DROP TABLE`, exfiltration).
2. **Exploit Multi-Agent Confused Deputies**: Transmit forged messages across peer-to-peer agent swarms (e.g. in LangGraph, CrewAI, AutoGen) to trigger unauthorized downstream actions.
3. **Induce Infinite Resource Exhaustion**: Cause an agent to enter repetitive tool retry loops, exhausting API tokens and computational budgets.

### 2.2 Out-of-Scope Threats
* **Hardware-Level Physical Attacks**: Side-channel physical probing of CPU silicon.
* **Compromised Host Kernel**: If the host OS kernel is compromised prior to deployment, all application-level sandboxes are untrusted.

---

## 3. Privilege Architecture & Attack Surface Minimization

```
[ UNTRUSTED INPUT ] ---> [ AUTONOMOUS LLM ]
                                |
                        (Proposed Action AST)
                                |
                                v
               [ BARTHOLOMEW INVARIANT GATEWAY ]
               • Sub-50 µs In-Process Memory Boundary
               • Abstract Syntax Tree (AST) Parsing
               • Path Containment is_relative_to()
               • Law of Diminishing Marginal Utility (LDMU)
               • Epistemic Grounding Proofs
                                |
                   +------------+------------+
                   |                         |
               [ ALLOW ]                  [ DENY ]
                   |                         |
                   v                         v
        [ ED25519 NOTARY SEAL ]     [ HARD EXECUTION BLOCK ]
                   |                (No OS syscall dispatched)
                   v
        [ DOWNSTREAM EFFECTOR ]
        (Database, POSIX Shell,
         Docker / K8s Container)
```

### 3.1 In-Process Library Mode (Zero-Daemon Principle)
To eliminate "confused deputy" risks associated with local proxy daemons, Bartholomew runs as an **in-process embedded library**:
* **No Inter-Process Communication (IPC)**: Code executes inside the caller's process memory space.
* **No Network Sockets**: BTP invariant evaluation requires zero external network connections or remote webhooks.
* **Deterministic Sub-Microsecond Execution**: Invariant checks execute in $<5.0 \text{ }\mu\text{s}$ via compiled pure-C routines.

### 3.2 Supply-Chain & Package Integrity
* **Distribution Channel**: Published exclusively through standard, hash-verifiable package registries (PyPI: `btp-guard`, NPM: `@bartholomew/btp-guard`, VS Code Marketplace: `.vsix`).
* **Cryptographic Signatures**: All release wheels and packages contain published SHA-256 digests.
* **Zero Remote Script Execution**: Source code is inspectable offline with reproducible test batteries.

---

## 4. Architectural Comparison: Native UI Prompts vs. Mathematical Invariants

| Security Capability | Native Human Confirmation Dialog | Bartholomew Invariant Gateway |
| :--- | :--- | :--- |
| **Alert Fatigue Resistance** | Fails under high volume (humans blindly click "Allow") | 100% deterministic mathematical evaluation |
| **Unattended Autonomous Swarms** | Blocked (human cannot click 1,000 dialogs/hr) | Seamless autonomous pre-flight evaluation |
| **Loop & Rate Damping** | None (allows infinite repetitive retries) | Law of Diminishing Marginal Utility ($MU = e^{-\lambda n}$) |
| **Spend Quota Enforcement** | None (no cumulative tracking) | Strict cumulative conservation caps ($E \le \text{Limit}$) |
| **Downstream Attestation** | None (no proof generated) | RFC 8785 Ed25519 signed verifiable receipts |
| **Audit Compliance** | Manual text logs | Immutable SHA-256 Merkle inclusion proofs |

---

## 5. Formal Verification & Standards Adherence

* **RFC 8785 (JSON Canonicalization Scheme)**: Ensures deterministic, byte-exact JSON hashing across all languages.
* **FIPS 186-5 / RFC 8032 (Ed25519 Signatures)**: 128-bit security level elliptic-curve digital signatures.
* **FIPS 180-4 (SHA-256)**: Cryptographic hashing for Merkle Audit Trees and Holographic Event Horizons.

---

## 6. Conclusion

Bartholomew replaces subjective prompt expectations with formal, deterministic systems engineering. By decoupling LLM reasoning from physical execution boundaries, it provides verifiable safety for enterprise AI deployments.
