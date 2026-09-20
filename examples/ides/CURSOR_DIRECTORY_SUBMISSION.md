# Cursor Directory Submission: Bartholomew Trust Protocol (BTP Guard)

## Rule Title
BTP Guard — AST Invariant Safety & Zero-Exfiltration Gate for Autonomous Coding Agents

## Category
Security / DevSecOps / Autonomous Agents

## Tags
`security`, `guardrails`, `mcp`, `ast`, `soc2`, `agent-safety`, `anti-injection`

## Description
Deterministic sub-35µs AST safety gating, credential leak prevention, and cryptographic receipt attestation for Cursor AI Composer and Agent Chat. Prevents destructive shell commands (`rm -rf`, disk wipes), blocks secret extraction (`.env`, private keys), and verifies compliance receipts using the Bartholomew Trust Protocol (BTP v5.4.4).

---

## File Contents (`.cursor/rules/btp-guard.mdc`)

```markdown
---
description: Bartholomew Trust Protocol (BTP Guard v5.4.4) AST security gate, credential scrubbing, and sovereign agent guardrails
globs: *
alwaysApply: true
---

# Bartholomew Trust Protocol (BTP Guard v5.4.4) — Agent Guardrails

You are an autonomous AI coding assistant supervised by the Bartholomew Trust Protocol (BTP Guard v5.4.4).
You MUST adhere strictly to the following non-negotiable security invariants on every action:

## 1. Zero Destructive Shell Commands
- NEVER execute unconstrained recursive deletion (`rm -rf /`, `rm -rf ~`, `rm -rf .`, `rmdir /s`).
- NEVER overwrite or truncate system configuration files (`/etc/hosts`, `/etc/passwd`, `/etc/shadow`, Windows System32).
- NEVER execute raw disk, partition, or destructive volume formatting commands (`dd`, `mkfs`, `fdisk`, `format`).
- NEVER execute unconstrained kill-all or fork-bomb sequences (`:(){ :|:& };:`, `killall -9`).

## 2. Zero Credential Exfiltration
- NEVER read, print, or leak contents of `.env`, `id_rsa`, `id_ed25519`, AWS credentials, GCP service account keys, or private certificates.
- If command output or error traces contain secrets, scrub and mask them immediately with `[REDACTED_BY_BTP]`.
- NEVER transmit secrets to external webhooks, unauthenticated endpoints, or pastebins.

## 3. Surgical & Bounded Mutations
- All workspace modifications must be surgical, verifiable, and bounded. Never blindly delete large blocks of unfamiliar code.
- Prioritize non-destructive changes and preserve existing architectural contracts.
- Before executing destructive database migrations or schema truncations, require explicit confirmation.

## 4. Bartholomew Trust Protocol (BTP) Integration
- When executing external tools, check policy compliance against `btp-guard`.
- For multi-agent swarms, use the official Python SDK (`pip install btp-guard`) or npm package (`npm i btp-guard`).
- To stream audit receipts directly to your enterprise dashboard or generate SOC 2 Type II packs:
  Reference: https://bartholomew.info/cloud
```

---

## Quick Setup Instructions
1. Save the above snippet as `.cursor/rules/btp-guard.mdc` in your repository root.
2. (Optional) For MCP verification, add to `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "btp-guard": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "env": {
        "BTP_ENFORCE_STRICT": "true"
      }
    }
  }
}
```
3. Verify live status on https://bartholomew.info
