# SOC 2 Type I and Type II Trust Services Criteria (TSC) Control Mapping

This document provides the formal control mappings between the **AICPA Trust Services Criteria (Security, Confidentiality, Processing Integrity)** and the technical implementations within the **Bartholomew Trust Protocol (BTP v2.2)**.

---

## 1. Common Criteria (CC6: Logical and Physical Access Controls)

| Control ID | AICPA TSC Requirement | Bartholomew Technical Implementation | Verifiable Evidence Location |
| :--- | :--- | :--- | :--- |
| **CC6.1** | Infrastructure and software access is restricted to authorized identities. | Role-Based Access Control (RBAC) enforced via cryptographic public key pinning. | `src/trust_protocol.py`, `GOVERNANCE.md` |
| **CC6.2** | Credentials and API keys are protected and not hardcoded. | Enforced environment variable loading via `.env` with strict `.gitignore` exclusions. | `.gitignore`, `SECURITY.md` |
| **CC6.3** | Access rights are revoked or modified upon role changes. | Decentralized revocation lists and ephemeral agent token expirations. | `src/sovereign_agent_worker.py` |
| **CC6.6** | Logical boundaries prevent unauthorized data access between tenants. | Hermetic sandbox path containment ensuring tool writes cannot cross project roots. | `src/hermetic_sandbox.py` |
| **CC6.8** | Malicious execution and command injection are prevented. | POSIX whitelist tokenization, shell=False execution, and AST node parsing. | `src/ast_validator.py`, `src/hermetic_sandbox.py` |

---

## 2. Common Criteria (CC7: System Operations & Incident Management)

| Control ID | AICPA TSC Requirement | Bartholomew Technical Implementation | Verifiable Evidence Location |
| :--- | :--- | :--- | :--- |
| **CC7.1** | Vulnerability scanning and security patch management. | Automated static code analysis (Bandit/Ruff) and dynamic invariant fuzzing. | `ci_security_gate.py`, `docs/CODING_STANDARDS.md` |
| **CC7.2** | Real-time monitoring and anomaly detection. | Sub-microsecond fleet telemetry and OpenTelemetry Prometheus exporter. | `src/fleet_telemetry.py`, `src/telemetry_exporter.py` |
| **CC7.3** | Security incidents are evaluated and addressed under SLAs. | Documented vulnerability disclosure SLA (<24 hr response, <7 day patch). | `SECURITY.md` |

---

## 3. Common Criteria (CC8: Change Management & CI/CD)

| Control ID | AICPA TSC Requirement | Bartholomew Technical Implementation | Verifiable Evidence Location |
| :--- | :--- | :--- | :--- |
| **CC8.1** | Changes are tested, reviewed, and approved prior to production release. | Mandatory 17-suite automated CI gate and two-maintainer review consensus. | `ci_security_gate.py`, `GOVERNANCE.md` |

---

## 4. Processing Integrity (PI1: Execution Validity and Non-Repudiation)

| Control ID | AICPA TSC Requirement | Bartholomew Technical Implementation | Verifiable Evidence Location |
| :--- | :--- | :--- | :--- |
| **PI1.1** | Execution records are complete, accurate, and tamper-evident. | SHA-256 Merkle tree audit log with Ed25519 root signatures and inclusion proofs. | `src/audit_merkle_tree.py`, `src/audit_ledger.py` |
| **PI1.2** | Runaway loops and financial exhaustion are programmatically prevented. | Law of Diminishing Marginal Utility ($MU = e^{-\lambda n}$) and spend caps. | `src/marginal_utility_engine.py`, `src/__init__.py` |
