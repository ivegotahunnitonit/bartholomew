# Security Policy & Vulnerability Disclosure Procedure

## 1. Supported Versions

Security updates are actively maintained and published for the following versions:

| Version | Status | Security Support Tier |
| :--- | :--- | :--- |
| **5.4.x** | **Active Production** | Full security advisories, zero-day invariant patches, dependency updates |
| **5.3.x** | Active Enterprise | Critical vulnerability patches only |
| **< 5.3** | Deprecated / End of Life | Unsupported |

---

## 2. Reporting a Vulnerability

The Bartholomew Protocol engineering team takes runtime security, invariant evasion, and cryptographic integrity seriously. If you identify a potential security flaw, sandbox escape, secret disclosure, or AST parser bypass, disclose it privately:

- **Primary Security Contact:** `security@bartholomew.info`
- **GitHub Private Vulnerability Advisory:** [Report via GitHub Security Advisory](https://github.com/ivegotahunnitonit/bartholomew/security/advisories/new)
- **PGP Encryption (Optional):**
  - **Key ID:** `0x9B4E3FA1C2D87B04`
  - **Fingerprint:** `5E81 A20F 761C B499 D203  579E 9B4E 3FA1 C2D8 7B04`

### Vulnerability Report Requirements:
1. **Description:** High-level summary of the vulnerability and attack vector.
2. **Reproducible Trajectory:** Minimal proof-of-concept (PoC) code or agent tool call payload demonstrating the invariant bypass or flaw.
3. **Affected Subsystem:** Specific component (e.g., `polyglot_ast_validator`, `secret_masker`, `mcp_server`, or `cli`).
4. **Severity Assessment:** Proposed CVSS score and real-world blast radius.

---

## 3. Vulnerability Response SLA & Expected Timelines

We adhere to strict response and remediation SLAs:

| Phase | Guaranteed Timeframe | Action |
| :--- | :--- | :--- |
| **Initial Acknowledgment** | **< 24 Hours** | Written receipt of report with assigned tracking ticket ID |
| **Triage & Reproduction** | **< 48 Hours** | Technical reproduction, risk validation, and CVSS severity scoring |
| **Security Patch Release** | **< 7 Calendar Days** | Verified patch release on PyPI, npm, and Open VSX with CVE advisory |
| **Coordinated Disclosure** | **30 Days Post-Patch** | Public advisory publication with full researcher credit |

---

## 4. Scope & Boundary Matrix

### In-Scope:
- Invariant escapes allowing catastrophic shell commands (`rm -rf`, reverse shells) through AST parser evasion
- SQL parser bypasses permitting unauthorized DDL mutations (`DROP TABLE`, blind schema drops)
- In-flight secret masker leakage of credentials (`sk-*`, `ghp_*`, AWS keys, private keys)
- Cryptographic receipt spoofing or Ed25519 signature malleability
- MCP server boundary breakouts or privilege escalation

### Out-of-Scope:
- Volumetric denial of service (DoS) against documentation or demo websites
- Social engineering targeting maintainers or users
- Weaknesses in underlying third-party host operating system kernels

---

## 5. Defense Boundary Architecture

Bartholomew enforces strict pre-execution gating before OS dispatch:

| Boundary Layer | Inspection Mechanism | Enforcement Point | Action | Latency Target |
| :--- | :--- | :--- | :--- | :--- |
| **Filesystem & Subprocess** | Abstract Syntax Tree (AST) Parsing | Pre-OS `execve()` Dispatch | **BLOCK & VETO** | `< 18 µs` |
| **Network Egress** | CIDR / Domain Allowlist + Heuristics | Pre-Socket `connect()` | **BLOCK & LOG** | `< 25 µs` |
| **Credentials & Secrets** | Zero-Allocation Regex + Entropy Vault | In-Flight Memory Scrub | **MASK & REDACT** | `< 20 µs` |
| **Database & SQL** | Multi-Dialect AST Parsing | Pre-Client `execute()` | **ABORT MUTATION** | `< 32 µs` |
