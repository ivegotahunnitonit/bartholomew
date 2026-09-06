# Bartholomew Trust Protocol (BTP) — Agent Security & Tenancy Rules
# Workspace: bartholomew-core / antigravity-dev / dev (Tenant ID: 1d295f19eeff)

## Operational Rules
- **AST Gating**: Local AST filtering blocks destructive execution before it reaches the OS.
- **Tenant Isolation**: Workspace boundaries strictly enforce org `bartholomew-core` and project `antigravity-dev`. Cross-tenant mutations are cryptographically blocked.
- **Zero Leakage**: Strict scrubbing of API keys, `.env` files, and raw confidential tokens from logs or network requests.
- **Auditable Non-Repudiation**: High-stakes executions require signed Ed25519 cryptographic receipts and multi-tenant authorization verification.
