# Coding and Engineering Standards

This standard governs all contributions, reviews, and automated gates across the Bartholomew codebase.

---

## 1. Python Code Standards
* **Style**: Enforce strict compliance with **PEP 8**.
* **Type Annotations**: Mandatory type hints (`typing.Dict`, `typing.List`, `typing.Optional`, `typing.Tuple`) for all public function signatures.
* **Static Analysis**: Must pass `flake8`, `ruff`, and `bandit` with zero warnings or security alerts.
* **Docstrings**: Google-style docstrings for all exported classes, methods, and invariants.

---

## 2. Native C Invariant Core
* **Compiler Flags**: Enforce `-Wall -Wextra -Werror -pedantic -std=c99`.
* **Memory Safety**: Zero heap allocations (`malloc`/`free`) in critical path evaluation. Rules evaluate using fixed stack memory and direct pointer arithmetic.
* **Fuzzing & Sanitizers**: Must compile and pass tests clean with AddressSanitizer (`-fsanitize=address`) and UndefinedBehaviorSanitizer (`-fsanitize=undefined`).

---

## 3. TypeScript & Frontend
* **Type Strictness**: Enforce `"strict": true` in `tsconfig.json`. No `any` casts in core attestation routines.
* **Linter**: Must pass `oxlint` with zero errors.

---

## 4. Documentation & Commit Hygiene
* **Zero Emojis**: Do not use decorative emojis in source code, docstrings, commit messages, or public documentation.
* **Signed Commits**: Maintainers must sign release commits with GPG or SSH keys.
