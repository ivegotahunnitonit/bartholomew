# Bartholomew Trust Protocol (BTP) — Antigravity Agent Invariant Rules
# Active Workspace Profile:
# Org: bartholomew-core | Project: antigravity-dev | Environment: dev | Tenant ID: 1d295f19eeff

## Core Directives & Safety Invariants
1. **Sub-35µs Local AST Interception**:
   - All tool calls, shell executions, and file modifications in this workspace are monitored by Bartholomew Trust Protocol.
   - Destructive operations (`rm -rf /`, `format`, `dd if=/dev/zero`, unvetted drops) are strictly forbidden and immediately quarantined.

2. **Zero Sensitive Leakage**:
   - Private keys (Ed25519, SECP256k1), `.env` secrets, seed phrases, and auth tokens must never be emitted into external prompts or non-isolated networks.

3. **Multi-Tenant Cryptographic Boundaries**:
   - All sovereign agent operations are bound to Tenant ID `1d295f19eeff` (SHA-256(`bartholomew-core` || `antigravity-dev` || `dev`)).
   - Any cross-tenant escrow or slashing operations outside this tenant partition will be immediately rejected with `PermissionError`.

4. **Sovereign Agent Passports & Escrow Protection**:
   - Autonomous agent handoffs and tool actions must maintain cryptographic provenance.
   - For mission-critical tasks, collateral is staked via `@btp_universal_guard` or `AutonomousEscrowPool`.
