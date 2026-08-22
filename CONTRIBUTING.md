# Contributing to Bartholomew & BTP

Thank you for your interest in contributing to the **Bartholomew Autonomous Trust Protocol (BTP)**.

We welcome contributions from the community to help secure autonomous AI agents and distributed machine execution.

---

## 1. Code of Conduct and Standards

To maintain high software engineering and security standards:
* **Coding Style**: Follow PEP 8 for Python code and standard TypeScript/Go conventions.
* **Formatting**: Maintain clean documentation and code without decorative emojis.
* **Security First**: Never check in secrets, credentials, API keys, or unverified binary blobs.

---

## 2. Development Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ivegotahunnitonit/bartholomew.git
   cd bartholomew
   ```

2. **Set Up Python Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   pip install pytest pyyaml cryptography
   ```

3. **Run the 17-Suite Security & Invariant Gate**:
   ```bash
   python ci_security_gate.py
   ```

---

## 3. Contribution Workflow (Pull Requests)

We use the standard GitHub Pull Request workflow:

1. **Fork or Branch**: Create a descriptive feature branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. **Implement Changes**: Write clean, modular code with accompanying unit tests in `tests/`.
3. **Verify CI Tests**: Ensure all 17 test suites pass 100% clean locally before opening a pull request.
4. **Submit PR**: Open a Pull Request targeting `main` with a clear description of the problem solved, architectural rationale, and verification steps.
5. **Code Review**: Maintainers will review the submission, request revisions if necessary, and merge once tests pass.

---

## 4. Reporting Issues and Vulnerabilities

* **Bug Reports & Enhancements**: Open an issue at [https://github.com/ivegotahunnitonit/bartholomew/issues](https://github.com/ivegotahunnitonit/bartholomew/issues).
* **Security Vulnerabilities**: For responsible disclosure of security flaws, please refer to [SECURITY.md](SECURITY.md) or email security@bartholomew.info.

---

## 5. Licensing of Contributions

By contributing to this repository, you agree that your contributions will be licensed under the project's [LICENSE](LICENSE) (Apache License 2.0 / BSL 1.1).


---

## 6. Developer Certificate of Origin (DCO)

To maintain clear ownership and licensing, this project requires all contributors to agree to the Developer Certificate of Origin (DCO). 

All commits submitted to this project must be signed off by the author, indicating agreement to the DCO. You can do this by using the `-s` or `--signoff` flag when committing:

```bash
git commit -s -m "Your commit message"
```

By signing off a commit, you certify the following:

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
1.1 Click-use Open Source Software License Agreement.

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I have the right to submit it under the open source license indicated in the file; or

(b) The contribution is based upon previous work that, to the best of my knowledge, is covered under an appropriate open source license and I have the right under that license to submit that work with modifications, whether created in whole or in part by me, under the same open source license (unless I am permitted to submit under a different license), as indicated in the file; or

(c) The contribution was provided directly to me by some other person who certified (a), (b) or (c) and I have not modified it.

(d) I understand and agree that this project and the contribution are public and that a record of the contribution (including all personal information I submit with it, including my sign-off) is maintained indefinitely and may be redistributed consistent with this project or the open source license(s) involved.
```
