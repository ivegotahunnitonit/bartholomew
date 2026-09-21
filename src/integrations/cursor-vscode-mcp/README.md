# Bartholomew Guard — Agent Security & MCP Gateway

**Sub-35µs deterministic execution firewall, AST safety gate, and autonomous micro-escrow gateway for AI agents running in Cursor and VS Code.**

[![BTP Protocol](https://img.shields.io/badge/BTP-v5.4.0-blue.svg)](https://bartholomew.info)
[![SOC 2 Type II](https://img.shields.io/badge/SOC%202%20Type%20II-Compliant-green.svg)](https://bartholomew.info/cloud)

---

## ⚡ What is Bartholomew Guard?

Bartholomew Guard is an in-process safety seam for AI developer agents (Cursor Composer, Windsurf, Claude Code, AutoGen, CrewAI, LangGraph). It intercepts tool invocations in memory before commands touch the filesystem, database, or network:

- **Catastrophic Execution Blocking**: Blocks `rm -rf`, `DROP TABLE`, and credential dumping in `<35 microseconds`.
- **Dynamic Spend & Retry Caps**: Enforces strict session spend caps and prevents infinite agent loops.
- **Model Context Protocol (MCP) Gateway**: Seamlessly bridges your local IDE agents to compliant execution boundaries.
- **SOC 2 Type II Merkle Receipts**: Cryptographically signs every decision with Ed25519 signatures.

---

## 🚀 Quickstart

1. Install this extension in **Cursor** or **VS Code**.
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS) and run:
   ```text
   Bartholomew: Auto-Configure MCP Gateway in Cursor / VS Code
   ```
3. Your local Cursor agent will automatically be guarded against destructive tool calls!

---

## 💼 Sovereign Enterprise Architecture

Bartholomew provides 100% unrestricted sovereign execution gating for developer agents:
- **Zero Paywalls**: AST gating, secret scrubbing, and local Merkle receipts are fully unlocked.
- **Keystone Capability Passkeys**: Ephemeral cryptographically signed capability tokens.
- **SOC 2 Type II Dossiers**: Machine-verifiable audit proofs out of the box.

👉 **Get Your Cloud API Key**: [https://bartholomew.info/cloud](https://bartholomew.info/cloud)  
👉 **Pricing & Subscriptions**: [https://bartholomew.info/store/](https://bartholomew.info/store/)
