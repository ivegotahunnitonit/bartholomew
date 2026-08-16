# 🛡️ Bartholomew — AI Agent Security & Trajectory Auditor
**Official GitHub Marketplace Action & Security App Listing**

[![GitHub Action](https://img.shields.io/badge/GitHub%20Action-Verified-green.svg)](https://github.com/marketplace/actions/bartholomew-ai-agent-security)
[![PyPI Version](https://img.shields.io/badge/PyPI-v5.0.0-blue.svg)](https://pypi.org/project/bartholomew-eval/)
[![SOC2 Compliance](https://img.shields.io/badge/SOC2-Verified-emerald.svg)](https://bartholomew.info)

Bartholomew is a sub-millisecond, inline AI agent trajectory auditor and sovereign local memory engine. Designed for LangChain, AutoGen, CrewAI, and custom LLM agent workflows, it enforces real-time OWASP LLM Top 10 guardrails, interprocedural AST taint analysis, and cryptographic SHA-256 audit attestation.

---

## 🌟 Why Bartholomew on GitHub Marketplace?

| Feature | Bartholomew | Traditional APM / Linter |
|---|---|---|
| **Execution Latency** | **1.44 μs (Sub-Millisecond)** | 35 ms - 100 ms |
| **Air-Gapped Sovereign Memory** | **Yes (Cloud-Devoid SQLite 16D Vector DB)** | No (Cloud SaaS Only) |
| **Asynchronous Dreaming Engine** | **Yes (Offline Replay & Token Optimization)** | No |
| **AST Interprocedural Taint Analysis** | **Yes (Tracks Untrusted Input to Sinks)** | No |
| **Cryptographic Attestation** | **Yes (SHA-256 Signed Audit Chain)** | No |

---

## ⚡ Quick Start: Add 1 Line to Your GitHub Workflow

Add Bartholomew to your `.github/workflows/ci.yml`:

```yaml
name: Security Audit Workflow

on: [push, pull_request]

jobs:
  bartholomew-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: ivegotahunnitonit/bartholomew@main
        with:
          fail-on-violation: 'true'
```

---

## 🏷️ Pricing Tiers

### 1. Free Community Edition ($0 / month)
- Open-Source Core PyPI Package (`bartholomew-eval`)
- Basic Secret Guard & Prompt Injection Scrubber
- Community GitHub Action Runner

### 2. Team Edition ($49 / month)
- Unlimited PR Trajectory Audits
- AST Taint & SCA Dependency Scanner
- Email & Slack Security Alerts

### 3. Enterprise Enclave Edition ($499 / month)
- Sovereign Local Memory Engine (`sovereign_memory.py`)
- Asynchronous Dreaming Engine & Counterfactual Scenario Synthesis
- SHA-256 Cryptographic Audit Attestation Chain
- On-Premises Air-Gapped Container Enclave Support

---

## 📞 Support & Enterprise Contact
- **Documentation & Live Dashboard:** [bartholomew.info](https://bartholomew.info)
- **Enterprise Licensing:** `enterprise@bartholomew.info`
- **GitHub Repository:** [ivegotahunnitonit/bartholomew](https://github.com/ivegotahunnitonit/bartholomew)
