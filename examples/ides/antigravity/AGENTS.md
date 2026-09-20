# BTP Guard — Antigravity Agent Configuration
# Place in .agents/rules/btp-guard.md or in workspace root as AGENTS.md

## Security Invariants
- All autonomous tools executed by Antigravity agents must satisfy BTP safety invariants:
  - Destructive filesystem commands (`rm -rf`, `format`, `dd`) are prohibited.
  - Secret credentials (`.env`, private keys, cloud tokens) must never be exfiltrated.
  - Multi-agent handoffs must include Ed25519-signed sovereign digital passports.
