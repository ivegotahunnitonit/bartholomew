# Cursor Directory & Windsurf Registry Submission Dossier
=====================================================================

### 1. Extension Profile
- **Name:** Bartholomew Guard — AI Agent Safety & Runtime Seam
- **Publisher ID:** `itsubsolomon`
- **Extension ID:** `itsubsolomon.bartholomew-guard-vscode`
- **Companion Passkey:** `itsubsolomon.bartholomew-keystone`
- **Open-VSX URL:** https://open-vsx.org/extension/itsubsolomon/bartholomew-guard-vscode
- **Open-VSX Publisher Hub:** https://open-vsx.org/publisher/itsubsolomon
- **Version:** `5.4.21`
- **License:** MIT
- **Website:** https://bartholomew.info
- **Verification Authority:** https://bartholomew.info/verify

---

### 2. Short Description (Max 140 chars)
Sub-35µs in-process tool execution gateway, runtime dispatch seam, zero-leak credential scrubbing, and offline Merkle receipts for Cursor and Windsurf.

---

### 3. Detailed Pitch / Overview
Bartholomew Guard is a zero-latency runtime execution gate engineered specifically for autonomous AI coding agents (Cursor, Windsurf, Claude Code, Cline, Roo-Code). It enforces deterministic AST safety invariants before tools execute:
- **Sub-35µs In-Process Seam:** Evaluates polyglot AST syntax trees directly in-process with zero network overhead.
- **Zero-Leak Credential Containment:** Prevents agents from exfiltrating environment variables, API keys, private keys, or SSH credentials into tool calls or prompt contexts.
- **Keystone Non-Human Identity (NHI):** Scoped cryptographic capability passkeys for every autonomous agent session.
- **Cryptographic Attestation Records:** Automatically generates RFC 8785 canonical JSON-LD and Ed25519-signed Merkle audit receipts.

---

### 4. 1-Click Installation Command
```bash
code --install-extension itsubsolomon.bartholomew-guard-vscode && code --install-extension itsubsolomon.bartholomew-keystone
```

---

### 5. Cursor MCP Configuration (`~/.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "bartholomew-guard": {
      "command": "npx",
      "args": ["-y", "btp-guard-mcp@latest"]
    }
  }
}
```

---

### 6. Suggested Categories & Tags
- **Categories:** AI Safety, Security, Linters, Developer Tools, Machine Learning
- **Tags:** `ai-safety`, `cursor`, `windsurf`, `mcp`, `mcp-server`, `guardrails`, `secret-scanner`, `prompt-injection`, `zero-leak`, `ast-linter`, `ed25519`