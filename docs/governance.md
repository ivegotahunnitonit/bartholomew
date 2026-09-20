# Project Governance and Maintainer Policy

## 1. Governance Model

Bartholomew is managed under an open, multi-maintainer consensus model designed to avoid single points of failure (Bus Factor > 1) and ensure long-term sustainability.

---

## 2. Roles and Responsibilities

* **Core Maintainers**: Responsible for architectural direction, reviewing pull requests, merging to `main`, releasing signed versions, and managing security disclosure.
* **Security Officers**: Dedicated individuals responsible for private vulnerability triage (`security@bartholomew.info`), coordination of CVE assignments, and issuing security advisories.
* **Contributors**: Anyone who submits issues, documentation improvements, bug fixes, or new features via pull requests.

---

## 3. Decision-Making Process

* **Standard Changes**: Require review and approval from at least one Core Maintainer and passing the 17-suite automated CI gate (`python ci_security_gate.py`).
* **Breaking Changes & Invariant Modifications**: Require consensus from at least two Core Maintainers following a formal Request for Comments (RFC) period.
* **Security Hotfixes**: Security Officers have authority to fast-track security hotfixes following regression testing.

---

## 4. Multi-Maintainer Access and 2FA Enforcement

* All maintainers with write or release permissions must enforce **Two-Factor Authentication (2FA)** on their GitHub and package registry accounts.
* Branch protection is enforced on `main`: direct pushes without PR review and passing status checks are disabled.

---

## 5. Release Authorization

Releases require:
1. 100% clean execution of `python ci_security_gate.py`.
2. Clean static analysis scan (Bandit & Ruff).
3. Cryptographically signed Git release tag (`git tag -s`).
4. Automated SBOM generation via `python scripts/generate_sbom.py`.
