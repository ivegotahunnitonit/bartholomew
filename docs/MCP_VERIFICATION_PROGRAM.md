# Bartholomew Verified MCP Security Seal Program

<p align="center">
  <img src="assets/verified_mcp_seal.png" width="160" alt="Official Bartholomew Verified MCP Security Seal" />
</p>

The **Bartholomew Verified MCP Security Seal** is the cryptographic verification standard for Model Context Protocol (MCP) servers and autonomous AI agent tools.

As thousands of unvetted community MCP tools flood IDEs and agent swarms (Cursor, Windsurf, Claude Code, Cline), developers and enterprises require provable guarantees that tools will not exfiltrate credentials, execute destructive shell breakouts, or poison context.

---

## 1. What the Seal Guarantees

Every tool exposed by a Verified MCP Server is audited against the **100,000+ vector BTP benchmark**:
- **Zero Destructive Shell Breakouts:** Hard blocks `rm -rf /`, `mkfifo`, disk formatters, and reverse shells.
- **Zero Credential Exfiltration:** In-flight scrubbing of API keys (`sk-*`, `ghp_*`, AWS credentials, private keys).
- **Zero Unbounded SQL Mutations:** Prohibits `DROP TABLE`, blind DDL wipes, and schema cascades.
- **Zero Cloud Metadata SSRF:** Blocks calls to internal metadata endpoints (`169.254.169.254`).
- **Cryptographic Attestation:** Every invocation emits an RFC 8785 Ed25519-signed verification receipt.

---

## 2. Verification Workflow

### Step 1: Run the Automated Audit
Tool creators audit their server locally using `btp-guard`:

```bash
pip install btp-guard
btp-guard verify-mcp --server-cmd "python mcp_server.py" --output btp-verified-seal.json
```

### Step 2: Cryptographic Seal Generation
Upon passing 100% of invariant checks, the engine generates an Ed25519 signed verification receipt:

```json
{
  "protocol": "BTP/2.2",
  "seal_type": "MCP_VERIFIED_SECURITY_SEAL",
  "server_name": "example-filesystem-mcp",
  "authority": "Bartholomew-Trust-Authority",
  "audit_score": 100,
  "passed_invariants": 100000,
  "failed_invariants": 0,
  "ed25519_signature": "3bc02cfe1e1b1630fd7e853ca8ead7246e61a25e779d06..."
}
```

### Step 3: Embed the Verified Badge
Add the official seal badge to your MCP server repository:

```markdown
[![Bartholomew Verified MCP](https://github.com/ivegotahunnitonit/bartholomew/raw/main/docs/assets/verified_mcp_seal.png)](https://huggingface.co/spaces/acnbartholomew/agent-guardrails-leaderboard)
```

---

## 3. Verified Registry & Directory Placement
Verified MCP servers receive priority indexing on:
1. **The Hugging Face Agent Guardrails Leaderboard:** Listed in the official Verified MCP directory.
2. **The Bartholomew Registry:** Distributed to enterprise clients and agent runtimes as pre-approved safe tools.
