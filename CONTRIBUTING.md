# Contributing to Bartholomew (BTP)

Thank you for contributing to **Bartholomew (BTP v5.4)**, the open runtime security standard for autonomous AI agents and Model Context Protocol (MCP) ecosystems.

---

## 1. Code Standards & Tooling

To ensure deterministic safety, zero regressive latency, and consistent code quality across Python, TypeScript, and Go runtimes:

### Python Standards
- **Linter & Formatter:** [Ruff](https://github.com/astral-sh/ruff) and [Black](https://github.com/psf/black)
  ```bash
  # Check linting & formatting
  ruff check .
  black --check .

  # Automatically format code
  ruff format .
  black .
  ```
- **Type Checking:** Strict type hints using `mypy` or `pyright`:
  ```bash
  pyright btp_guard/
  ```

### TypeScript & Web Standards
- **Formatter:** Prettier
  ```bash
  # Check formatting
  npx prettier --check "**/*.{ts,js,json,html,css,md}"

  # Auto-format
  npx prettier --write "**/*.{ts,js,json,html,css,md}"
  ```

### Pre-Commit Hooks
Run automated hooks locally before opening a pull request:
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

## 2. Commit Message Convention

We strictly follow **Conventional Commits**. Please keep commit titles concise, professional, and descriptive (under 72 characters):

- `feat: add AST invariant for base64-encoded bash pipes`
- `fix: resolve microsecond clock drift in Ed25519 receipt generation`
- `docs: update social preview and MCP verification workflow`
- `test: expand adversarial red-team invariant suite to 105k vectors`
- `perf: reduce regex allocation overhead in secret masker`
- `chore: update dependencies and release tags`

*Avoid long, repetitive, or concatenated commit messages.*

---

## 3. Pull Request Requirements

Every Pull Request must meet these criteria before merge:

1. **Deterministic Latency Invariant:** No change may increase average evaluation latency beyond **50 µs** on CPU.
2. **Zero Regressions:** All unit tests and the 105,000+ invariant regression suite must pass:
   ```bash
   python -m pytest tests/ -v
   python tests/test_million_invariant_fuzz.py --samples 50000
   ```
3. **No Secrets in History:** Never commit live API tokens, credentials, or private keys.
4. **Documentation:** Update relevant guides in `docs/` or `README.md` if adding or changing public CLI flags or SDK APIs.
5. **Signed Commits:** GPG/SSH signed commits are strongly encouraged.

---

## 4. Development Workflow

1. Fork the repository and create a feature branch from `main`:
   ```bash
   git checkout -b feat/your-improvement
   ```
2. Set up a local development environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Or on Windows: .venv\Scripts\activate
   pip install -e ".[test]"
   ```
3. Implement your changes with clean unit tests in `tests/`.
4. Ensure all linters and tests pass locally.
5. Submit your PR with a concise description of changes and test evidence.

For security-sensitive vulnerability disclosures, refer to [SECURITY.md](SECURITY.md).
