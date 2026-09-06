# Security Policy and Vulnerability Disclosure Procedure

## 1. Supported Versions

Security updates are provided for the following versions of the Bartholomew Trust Protocol:

| Version | Supported |
| :--- | :--- |
| 2.4.x | Supported (Active Production) |
| 2.3.x | Supported (Active) |
| 2.2.x | Supported (Security Patches Only) |
| < 2.1 | Unsupported |

---

## 2. Reporting a Vulnerability

The Bartholomew team takes software security and vulnerability reports seriously. If you discover a security flaw, sandbox breakout, or cryptographic defect, please report it via private disclosure:

* **Private Security Email**: `security@bartholomew.info`
* **Encrypted Advisory**: You may also report vulnerabilities privately through GitHub Private Vulnerability Reporting at `https://github.com/ivegotahunnitonit/bartholomew/security/advisories/new`.

### Information to Include:
1. Clear description of the vulnerability, attack vector, or evasion method.
2. Minimal reproducible proof-of-concept (PoC) script or test trajectory.
3. Assessment of potential severity and affected components.

---

## 3. Vulnerability Response SLA

* **Initial Acknowledgment**: Within 24 hours of receipt (guaranteed < 7 business days).
* **Triage & Reproduction**: Within 48 hours.
* **Security Patch Release**: Within 7 days for critical severity issues.

Please do not disclose security issues publicly on public issue trackers until a patched release has been published and coordinated.

---

## 4. Boundary Protection & Capability Matrix

Bartholomew enforces a strict decoupling between **Pre-Execution Invariant Gates** (for non-idempotent/irreversible operations like networks and subprocesses) and **Transactional State Rollbacks** (for local mutable filesystem state):

| Boundary Layer | Inspection Mechanism | Enforcement Timing | Failure Action | Containment & Recovery Guarantee | Target Latency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Filesystem** | In-Memory Copy-on-Write (CoW) Shadow Ledger & Path Canonicalization | **Post-Mutation Atomic Checkpoint** | **ROLLBACK (Revert Tree)** | Zero orphaned files or partial edits; atomic filesystem tree restoration + JSON-RPC diagnostic hint | `< 120µs` |
| **Subprocess** | Local AST Abstract Syntax Parsing & Shell Delimiter Normalization | **Pre-Execution Gate** (Before OS `fork`/`exec`) | **DROP (DENY Call)** | Subprocess is never spawned; zero OS-level side effects; invariant violation logged to Merkle tree | `< 18µs` |
| **Network Egress** | CIDR/Domain Allowlist & High-Entropy Payload Heuristics | **Pre-Execution Gate** (Before Socket `connect()`) | **VETO (Block Socket)** | TCP handshake never initiates; raw exfiltration credentials stripped before wire dispatch | `< 35µs` |
| **External APIs** | Schema Policy Validator & Bearer Credential In-Memory Scrubber | **Pre-Execution Gate** (Before HTTP Dispatch) | **SCRUB or REJECT** | Private prompts/tokens sanitized in-memory; unapproved endpoints fail closed with 403 Forbidden | `< 45µs` |

