# Official Model Context Protocol (MCP) Registry Submission Kit

---

## 1. Registry Submission Metadata

* **Server Name**: `btp-guard`
* **Category**: `Security` / `Governance & Verification`
* **Repository**: [https://github.com/ivegotahunnitonit/bartholomew](https://github.com/ivegotahunnitonit/bartholomew)
* **npm**: [https://www.npmjs.com/package/btp-guard](https://www.npmjs.com/package/btp-guard)
* **PyPI**: [https://pypi.org/project/btp-guard/](https://pypi.org/project/btp-guard/)
* **License**: Apache-2.0
* **Description**: `Sub-35µs in-process cryptographic trust and pre-flight AST sandboxing protocol (BTP v5.4.4) for Claude Desktop, Cursor, and multi-agent tool execution.`

---

## 2. One-Click Setup Configurations

### A. Claude Desktop Configuration (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "btp-guard": {
      "command": "npx",
      "args": ["-y", "btp-guard", "mcp", "start"]
    }
  }
}
```

*Or via local Python:*

```json
{
  "mcpServers": {
    "bartholomew-guard": {
      "command": "python",
      "args": ["-m", "mcp_server.server"]
    }
  }
}
```

### B. Cursor IDE (`.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "btp-guard": {
      "command": "npx",
      "args": ["-y", "btp-guard", "mcp", "start"]
    }
  }
}
```

---

## 3. Pull Request Submission Body for `awesome-mcp-servers` & `modelcontextprotocol/servers`

**Target PR Title:**
```text
Add btp-guard: Sub-35µs in-process security gate & MCP execution guard
```

**Target PR Body:**
```markdown
### Server Name
`btp-guard`

### Description
An open, offline cryptographic trust protocol (BTP v5.4.4) for autonomous agent delegation, pre-flight tool sandboxing, and tamper-evident Ed25519 attestations.

### Features
- **`btp_evaluate_action`**: Runs candidate tool calls in isolated pre-flight AST sandboxes in sub-35µs and signs RFC 8785 Ed25519 evidence receipts.
- **`btp_verify_attestation`**: Evaluates incoming attestation receipts 100% offline with zero cloud roundtrips.
- **`btp_get_trust_roots`**: Returns registered security invariants and decentralized authority public keys.

### Repository
https://github.com/ivegotahunnitonit/bartholomew
```

---

## 4. Verification & Testing

* **Protocol Compliance**: 100% JSON-RPC 2.0 compliant across `initialize`, `tools/list`, and `tools/call`.
* **Zero Cloud Roundtrips**: Pure offline mathematical verification with pinned root authority keys.
* **Test Command**:
  ```bash
  python test_mcp_server_e2e.py
  ```
