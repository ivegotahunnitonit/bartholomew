# Bartholomew Agent Security Gate (GitHub Action)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Go Version](https://img.shields.io/badge/Go-1.26+-00ADD8.svg)](https://go.dev)
[![CI/CD Status](https://img.shields.io/badge/CI%2FCD-Active-10b981.svg)]()

Prevent API key leaks, credential exposure, and silent error fallbacks in your AI agent codebases before code merges into production.

---

##  Quick Start

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

      - name: Run Bartholomew Security Gate
        uses: ivegotahunnitonit/bartholomew@main
        with:
          audit-path: '.'
          action-command: 'python scripts/run_agent.py'
          action-type: 'shell'
          agent-id: 'github-actions'
          fail-on-action-deny: 'true'
```

---

## Key Features

1. **Automated Secret Leak Prevention:** Audits the repository for credential exposure.
2. **Execution Gate:** Evaluates `action-command` through Bartholomew and returns `ALLOW` or `DENY`.
3. **CI/CD Build Enforcer:** Fails the workflow when the configured action is denied.
4. **Receipts:** Exposes the rule ID and SHA-256 authorization receipt as action outputs.

---

##  Licensing & Commercial Retainers

For enterprise custom rules, dedicated SLA support, or custom FastAPI routing patches, contact the ACN Security Team at `security@acn-network.org` or visit our live auditor dashboard:

`https://acn-network.org/dashboard/orchestrator.html`
