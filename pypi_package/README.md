# 🛡️ agent-qa-guard

**CI/CD Linter & Secret Scanner for AI Agent Codebases & Trajectories**

[![PyPI Version](https://img.shields.io/badge/pypi-v1.0.0-blue.svg)](https://pypi.org)
[![Python Version](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Stop secret key leaks, unhandled exception swallowing, and redundant tool execution loops in your AI agents before code hits production.

---

## ⚡ Installation

```bash
pip install agent-qa-guard
```

---

## 🚀 Quick Usage

### Scan Current Project Directory
```bash
agent-qa check
```

### Audit Specific Agent Log Trajectory (JSON)
```bash
agent-qa check --trajectory=agent_log.json
```

### Auto-Fix & Mask Credential Leaks
```bash
agent-qa fix
```

---

## 📊 Sample CLI Terminal Output

```text
================================================================================
  🛡️ AGENT-QA-GUARD V1.0.0 — AI AGENT AUDIT REPORT
================================================================================
  [FAIL] Step 2: Unmasked API Secret Detected (ghp_123456...)
  [WARN] Step 4: Silent Error Swallowing (Unhandled DOM Exception)
--------------------------------------------------------------------------------
  Overall Reliability Score: 65% / 100% [ACTION REQUIRED]
  👉 Run 'agent-qa fix' or visit https://acn-network.org/dashboard/orchestrator.html
================================================================================
```

---

## 📜 License
MIT License. Created by Autonomous Circularity Network (ACN).
