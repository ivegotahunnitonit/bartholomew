# 🛡️ ACN Agentic Security & Secret Scanner (GitHub Action)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Go Version](https://img.shields.io/badge/Go-1.26+-00ADD8.svg)](https://go.dev)
[![CI/CD Status](https://img.shields.io/badge/CI%2FCD-Active-10b981.svg)]()

Prevent API key leaks, credential exposure, and silent error fallbacks in your AI agent codebases before code merges into production.

---

## ⚡ Quick Start

Add the following step to your `.github/workflows/security.yml` file:

```yaml
name: Security & Secret Audit

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main ]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Run ACN Security & Secret Audit
        uses: ./github_action
        with:
          scan-path: '.'
          fail-on-leak: 'true'
```

---

## 🔒 Key Features

1. **Automated Secret Leak Prevention:** Detects OpenAI (`sk-`), GitHub (`ghp_`), AWS (`AKIA`), and custom tokens in commits.
2. **Trajectory & Error Fallback Checks:** Identifies unhandled exceptions and silent null returns in step dispatchers.
3. **CI/CD Build Enforcer:** Automatically fails builds if critical credential leaks are introduced in a Pull Request.
4. **SHA-256 Cryptographic Checksums:** Generates an attestation hash for every audit run.

---

## 💼 Licensing & Commercial Retainers

For enterprise custom rules, dedicated SLA support, or custom FastAPI routing patches, contact the ACN Security Team at `security@acn-network.org` or visit our live auditor dashboard:

`https://acn-network.org/dashboard/orchestrator.html`
