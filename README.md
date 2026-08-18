#  Bartholomew AI: Autonomous Developer Copilot & CI Failure Rescue

[![Edge Add-on](https://img.shields.io/badge/Microsoft%20Edge-Add--ons%20In%20Review-0078D7?logo=microsoftedge&logoColor=white&style=flat-square)](https://partner.microsoft.com/dashboard/microsoftedge)
[![Chrome Extension](https://img.shields.io/badge/Chrome%20Extension-Manifest%20V3-4285F4?logo=googlechrome&logoColor=white&style=flat-square)](chrome_extension/)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.11%20%7C%203.14-blue.svg?style=flat-square)](https://github.com/ivegotahunnitonit/bartholomew)
[![Tests Passing](https://img.shields.io/badge/tests-28%2F28%20passing%20(0.16s)-brightgreen.svg?style=flat-square)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

> **"Turn failing CI runs into green builds with verifiable reproduction tests and minimal AST patches."**

Bartholomew AI is a unified autonomous developer copilot ecosystem designed for software engineers, DevOps teams, and open-source contributors:
1. ** Chrome & Edge Developer Extension**: Gemini-style persistent Side Panel assistant with live in-page GitHub CI/CD diagnostics.
2. ** Autonomous GitHub App**: Catches failing pull request checks, isolates regressions, and opens verified auto-fix PRs.
3. ** Terminal CLI (`bartholomew`)**: Fast, zero-dependency command-line diagnostics and reproduction test synthesizer.

---

##  Ecosystem Architecture

```

                                   BARTHOLOMEW AI                                       

  BROWSER EXTENSION       GITHUB APP AGENT        TERMINAL CLI                  
 • Gemini-Style Sidepanel  • Webhook Auto-Fix        • `bartholomew diagnose`         
 • Floating GitHub Badge   • Pytest-xdist Isolation  • `bartholomew repro <test.py>`  
 • BYOK (Gemini/Ollama)    • AST Modernization       • `bartholomew fix --ci`         

```

---

##  1. Browser Extension (Chrome & Microsoft Edge)

Transform your browser into an autonomous software engineering cockpit.

### Key Capabilities:
* ** 1-Click CI Failure Diagnosis**: Click the floating badge on any GitHub Actions run to extract error logs and isolate the exact root cause.
* ** Autonomous Reproduction Synthesizer**: Generates standalone, zero-dependency reproduction tests to prove defects before fixing them.
* ** Gemini-Style Persistent Side Panel**: Interactive chat with multi-provider support:
  * **Google Gemini** (`gemini-2.0-flash` / `gemini-1.5-pro`)
  * **Local Ollama** (`localhost:11434` for 100% offline private execution)
  * **OpenAI** (`gpt-4o` / `gpt-4o-mini`)
  * **Built-in Autonomous Heuristic Engine** (Zero setup required)
* ** In-Page Context Menu**: Highlight any code snippet on the web $\to$ Right-click $\to$ *"Ask Bartholomew to Explain Code"*.

### Quick Installation (Load Unpacked):
1. Clone this repository:
   ```bash
   git clone https://github.com/ivegotahunnitonit/bartholomew.git
   ```
2. In **Chrome** navigate to `chrome://extensions` (or in **Edge** `edge://extensions`).
3. Toggle **Developer mode** to **ON**.
4. Click **Load unpacked** and select the [`chrome_extension/`](chrome_extension/) folder.

---

##  2. Command Line Interface (`bartholomew`)

Bartholomew includes a developer CLI for local test suites and terminal workflows:

```bash
# Install locally in development mode
pip install -e pypi_package/

# Diagnose a failing test suite or CI run
bartholomew diagnose

# Synthesize a standalone minimal reproduction test
bartholomew repro tests/test_failing_suite.py

# Launch the local SaaS & Webhook daemon
bartholomew server --port 8080
```

---

##  3. Autonomous CI Auto-Fix Engine

Bartholomew’s core engine specializes in automated software repair across 4 core fault domains:

| Fault Domain | Root Cause Diagnosed | Automated Resolution |
|---|---|---|
|  **Async Teardown Leaks** | Event loop lifecycle race during worker teardown | Function-scoped loop isolation fixture |
|  **Pytest-xdist Contamination** | Global mock state leaking across worker threads | Session-isolated fixture boundary |
|  **AST Deprecations** | Python version-branched AST compilation | Unified `ast.Constant` cross-version modernization |
|  **Cryptographic Boundaries** | Buffer wrap under zero-length parameters | Strict lower-bound length validation check |

---

##  Verification & Test Suite

All 28 unit and integration tests execute with zero external cloud dependencies:

```bash
python -m pytest -o pythonpath=pypi_package tests/
```

```text
============================= 28 passed in 0.16s =============================
```

---

##  Privacy & Security

* **Privacy Policy**: [privacy.html](privacy.html)
* **Client-Side First**: Your code stays on your machine. All extension evaluations occur locally in your browser.
* **Zero Telemetry Tracking**: Bartholomew does not track, collect, or sell developer credentials or source code.

---

##  Author & Maintainer

**Itsub Alemayehu**  
* **GitHub**: [@ivegotahunnitonit](https://github.com/ivegotahunnitonit)  
* **Repository**: [github.com/ivegotahunnitonit/bartholomew](https://github.com/ivegotahunnitonit/bartholomew)

---

*Licensed under the [MIT License](LICENSE).*
