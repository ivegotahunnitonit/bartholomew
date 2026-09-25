# Bartholomew Keystone — Control What Your AI Agent Can Do

Give your AI agent a signed permission slip. It can only do what you said it could.

[![Open VSX](https://img.shields.io/badge/Open%20VSX-v5.4.21-blue)](https://open-vsx.org/extension/itsubsolomon/bartholomew-keystone)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Works With](https://img.shields.io/badge/Works%20With-Bartholomew%20Guard-blue)](https://open-vsx.org/extension/itsubsolomon/bartholomew-guard-vscode)

---

## Quick Installation

```bash
# Via VS Code / Cursor Terminal
code --install-extension itsubsolomon.bartholomew-keystone

# Or search "Bartholomew Keystone" in Extensions (Ctrl+Shift+X)
```

👉 **Recommended Companion:** Pair with [Bartholomew Guard](https://open-vsx.org/extension/itsubsolomon/bartholomew-guard-vscode) (`code --install-extension itsubsolomon.bartholomew-guard-vscode`) for AST invariant gating and sub-35µs zero-leak protection.

---

## What It Does

Right now, AI coding agents work with all-or-nothing access. If you give Cursor or Copilot permission to run code, it can run *anything* — including things you didn't intend.

Keystone fixes that. You issue a cryptographically signed passkey that defines exactly what the agent can and can't do. Then Keystone enforces those limits on every action the agent attempts.

---

## Guard vs. Keystone — Start Here

| | **Guard** | **Keystone** (this extension) |
|---|---|---|
| **What it does** | Automatically blocks known-dangerous code and credential leaks | Lets you define custom rules — what files, commands, and actions are allowed |
| **Install order** | Install Guard first | Add Keystone for fine-grained control |
| **Get Guard** | [Install Bartholomew Guard](https://open-vsx.org/extension/itsubsolomon/bartholomew-guard-vscode) | You're here |

---

## What You Can Control

When you issue a passkey, you decide:

| Permission | Example |
|---|---|
| **Which files the agent can write** | Allow `src/` only, block everything else |
| **Which commands are allowed** | Allow `pytest`, `npm test` — block `rm`, `curl`, `sudo` |
| **Which external domains it can reach** | Allow `github.com`, block everything else |
| **How long the permission lasts** | Session-only, or time-bounded |

Every decision the agent makes is logged with a tamper-evident Ed25519 signed receipt — so you always have a record of what it did.

---

## How It Works

1. Press `Ctrl+Shift+P` then run **`Keystone: Issue Agent Capability Passkey`**
2. Set your rules — allowed paths, allowed commands, expiry
3. Keystone generates a signed `.btp_keystone.json` permission file
4. The agent can now only act within what you defined — anything outside gets blocked instantly

---

## Commands

Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS):

| Command | What It Does |
|---|---|
| `Keystone: Issue Agent Capability Passkey` | Create a new signed permission for your agent |
| `Keystone: Inspect Active Agent Clearance` | See what the current passkey allows |
| `Keystone: Revoke Current Agent Passkey` | Immediately remove the agent permissions |
| `Keystone: Validate Agent Action against Passkey` | Test whether a specific action would be allowed |

---

## Open Source

Bartholomew Keystone is **MIT licensed** and fully open source.

- [bartholomew.info](https://bartholomew.info)
- [Guard Extension](https://open-vsx.org/extension/itsubsolomon/bartholomew-guard-vscode) — install this first
- Python: `pip install btp-guard`
- npm: `npm install btp-guard`
