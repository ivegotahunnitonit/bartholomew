# Bartholomew Agentic Runtime Protection (GitHub Action)

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/badge/PyPI-v5.4.20-blue.svg)](https://pypi.org/project/btp-guard/)
[![CI/CD Status](https://img.shields.io/badge/CI%2FCD-Active-10b981.svg)]()

Deterministic AST invariant verification, credential leak prevention, and cryptographic Ed25519 execution receipts for autonomous AI agent codebases before pull requests merge into production.

---

## Quickstart

Add the following step to your `.github/workflows/agent_security.yml` file:

```yaml
name: Agentic Runtime Protection (ARP) Audit

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
        uses: actions/checkout@v4

      - name: Run Bartholomew Security Gate
        uses: ivegotahunnitonit/bartholomew/packages/github_action@main
        with:
          audit-path: '.'
          run-ast-benchmark: 'true'
          fail-on-violation: 'true'
          export-telemetry: 'true'
```

---

## Key Capabilities

1. **Sub-35µs AST Invariant Gating:** Evaluates shell, SQL, and Python code blocks against catastrophic execution patterns (`DROP TABLE`, `rm -rf /`, fork bombs, unauthorized net egress).
2. **Zero-Leak Secret Redaction:** Scrubbing OpenAI, Anthropic, AWS, Stripe, and GitHub credentials in `<100µs`.
3. **RFC 8785 Canonical JSON Audit Receipts:** Issues FIPS 186-5 Ed25519 verifiable SHA-256 receipts on every CI/CD run.
4. **OpenTelemetry (OTel) SIEM Export:** Directly compatible with Datadog, Splunk, and corporate SOC monitoring.

---

## Support & Enterprise Retainers

For custom AST invariant rule packs, dedicated authority nodes, or enterprise fleet licenses, contact:
`security@bartholomew.info` or visit [https://bartholomew.info](https://bartholomew.info).
