# ISO/IEC 27001:2022 ISMS Controls Matrix

This document provides the compliance mapping between **ISO/IEC 27001:2022 Annex A Security Controls** and the **Bartholomew Trust Protocol (BTP v2.2)**.

---

## Organizational Controls (Clause 5)

* **Control 5.8 (Information Security in Project Management)**: Secure coding standards and invariant tests are embedded directly in every build via `docs/CODING_STANDARDS.md` and `ci_security_gate.py`.
* **Control 5.24 (Incident Management Planning)**: Documented response SLAs and responsible disclosure channels defined in `SECURITY.md`.
* **Control 5.37 (Documented Operating Procedures)**: Architectural specifications and threat models published in `SECURITY_WHITE_PAPER_AND_THREAT_MODEL.md`.

---

## People Controls (Clause 6)

* **Control 6.3 (Information Security Awareness & Training)**: Secure development principles and common error mitigations documented in `docs/SECURE_DESIGN.md`.

---

## Technological Controls (Clause 8)

* **Control 8.4 (Access Control)**: Least privilege access enforcement across tools and APIs (`src/declarative_policy_engine.py`).
* **Control 8.8 (Management of Technical Vulnerabilities)**: Continuous automated static analysis (Bandit/Ruff) and dynamic fuzzing tests.
* **Control 8.24 (Use of Cryptography)**: Enforced FIPS 186-5 Ed25519 digital signatures and RFC 8785 canonical serialization (`src/trust_protocol.py`).
* **Control 8.25 (Secure Development Life Cycle)**: Multi-platform automated CI security gate running across Ubuntu, macOS, and Windows.
* **Control 8.28 (Secure Coding)**: Stack-only memory invariant checks and AddressSanitizer tests on native C components.
* **Control 8.30 (Outsourced Development & Supply Chain)**: Automated CycloneDX Software Bill of Materials (SBOM) generation via `scripts/generate_sbom.py`.
