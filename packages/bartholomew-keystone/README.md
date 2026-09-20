# Bartholomew Keystone — Agent Capability Passkey (BTP v1.0)

**Cryptographically signed clearance tokens granting autonomous AI agents scoped execution rights across IDEs, programs, and web searches.**

---

## What is Keystone?

Today, autonomous coding agents (in Cursor, VS Code, and terminal runners) operate with **all-or-nothing root privileges**. If an agent hallucinates or encounters a prompt injection, it can delete system files, exfiltrate API secrets, or run infinite compute loops.

**Bartholomew Keystone** introduces capability-based security (Object-Capability model):
1. **Developer Issues Passkey**: You click `Keystone: Issue Agent Capability Passkey` in your IDE and set the boundaries (allowed write paths, forbidden commands, max spend).
2. **Cryptographic Attestation**: An ephemeral Ed25519/HMAC signed `.btp_keystone.json` is generated.
3. **Sub-15µs Verification**: Whenever the agent proposes an action, Keystone verifies its clearance before execution reaches the host or network. Any out-of-scope action is blocked instantly.

---

## ⚡ Core Scopes & Clearance Limits

| Scope Dimension | Description | Default Clearance |
| :--- | :--- | :--- |
| **Filesystem** | Allowed read/write glob patterns | Read all, write to specified dirs, strictly deny `.env` & secrets |
| **Command Execution** | Allowed test/build binaries | Allow `npm test`, `pytest`; deny `rm`, `curl`, `sudo` |
| **Network & Web** | Approved external API & search domains | Allow `github.com`, `docs.python.org`; deny arbitrary endpoints |
| **Autonomous Spend** | Financial & API token budget ceiling | Hard dollar limit per transaction (e.g. $25.00) |

---

## 🚀 Usage in Cursor / VS Code

Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS):
- `Keystone: Issue Agent Capability Passkey`: Generate a new scoped token for your agent.
- `Keystone: Inspect Active Agent Clearance`: View active token claims, expiration, and remaining budget.
- `Keystone: Revoke Current Agent Passkey`: Instantly strip agent privileges.
- `Keystone: Validate Agent Action against Passkey`: Dry-run test any proposed command or file path.

Documentation: [https://bartholomew.info](https://bartholomew.info)
