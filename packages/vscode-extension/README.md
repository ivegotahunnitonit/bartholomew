# Bartholomew Guard — AI Agent Safety for VS Code & Cursor

Stop your AI coding agent from doing things you didn't ask for.

[![Open VSX](https://img.shields.io/badge/Open%20VSX-v5.4.19-blue)](https://open-vsx.org/extension/Bartholomew/bartholomew-guard-vscode)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/Tests-2%2C956%20passed-brightgreen)](https://bartholomew.info)
[![Security Audit](https://img.shields.io/badge/Security%20Audit-0%20vulnerabilities-brightgreen)](https://bartholomew.info)

---

## What It Does

Bartholomew Guard sits between your AI agent (Cursor, Copilot, Claude) and your machine. Every time the agent tries to run code or a command, Guard checks it first — and blocks it if it looks dangerous.

It runs **entirely on your machine**. No cloud calls. No sending your code anywhere. No added cost per check.

**What it blocks:**
- - API keys and credentials getting written into your code (AWS, GitHub, OpenAI, Stripe, and more)
- - Destructive commands like `rm -rf`, `DROP TABLE`, or disk format operations
- - Obfuscation tricks agents use to bypass simple filters (dynamic imports, reflection)
- - Private key material (RSA, EC) ending up in your repository

**What it never blocks:**
- Normal code, SQL queries, file reads — anything safe passes through instantly

---

## Performance

- **< 35 microseconds** per evaluation — faster than a single camera flash
- **13/13** real attack scenarios blocked in independent testing
- **2,956** automated tests — zero failures
- **Zero** security vulnerabilities in full audit
- **10,000x** faster than cloud-based AI guardrail alternatives

---

## Guard vs. Keystone — Which Do You Need?

| | **Guard** (this extension) | **Keystone** |
|---|---|---|
| **What it does** | Blocks dangerous code and credential leaks automatically | Lets you define exactly what your agent is allowed to do, with a signed permission |
| **When to use it** | Always — it's the baseline safety layer | When you want fine-grained control over agent permissions |
| **Required?** | Yes, install this first | Optional but recommended alongside Guard |

**Start with Guard. Add Keystone when you want more control.**

---

## Commands

Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS):

| Command | What It Does |
|---|---|
| `Bartholomew: View Security Status & Trust Roots` | See Guard's active status and cryptographic trust roots |
| `Bartholomew: Validate & Lint Workspace Security Policy` | Check your security policy configuration |
| `Bartholomew: Generate SOC 2 / ISO 27001 Evidence Pack` | Export a compliance audit package |
| `Bartholomew: Dry-Run Policy against Synthetic Agent Trace` | Test your policy before going live |
| `Bartholomew: Install MCP Server (Claude & Cursor)` | Set up the Model Context Protocol gateway |

---

## Open Source

Bartholomew Guard is **MIT licensed** and fully open source at the core. No paywalls, no telemetry, no vendor lock-in.

- [bartholomew.info](https://bartholomew.info)
- [Keystone Extension](https://open-vsx.org/extension/Bartholomew/bartholomew-keystone) — add scoped agent permissions
- Python: `pip install btp-guard`
- npm: `npm install btp-guard`
