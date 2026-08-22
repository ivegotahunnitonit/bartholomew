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
