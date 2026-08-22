#  Official Anthropic Model Context Protocol (MCP) Registry Submission Kit

---

## 1. Registry Submission Metadata

* **Server Name**: `mcp-server-bartholomew` / `@bartholomew/mcp-server`
* **Category**: `Security` / `Governance & Verification`
* **Repository**: [https://github.com/ivegotahunnitonit/bartholomew](https://github.com/ivegotahunnitonit/bartholomew)
* **License**: MIT
* **Description**: `100% offline, vendor-neutral cryptographic trust & pre-flight sandboxing protocol (BTP) for Claude Desktop, Cursor, and multi-agent tool execution.`

---

## 2. One-Click Setup Configurations

### A. Claude Desktop Configuration (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "bartholomew-guard": {
      "command": "uvx",
      "args": ["mcp-server-bartholomew"]
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
    "bartholomew-security-guard": {
      "command": "npx",
      "args": ["-y", "@bartholomew/mcp-server"]
    }
  }
}
```

---

## 3. Pull Request Submission Body for `awesome-mcp-servers` & `modelcontextprotocol/servers`

**Target PR Title:**
```text
Add Bartholomew BTP (Cryptographic Trust & Attestation Server) to Security Servers
```

**Target PR Body:**
```markdown
### Server Name
`mcp-server-bartholomew`

### Description
An open, offline cryptographic trust protocol (BTP v2.2) for autonomous agent delegation, pre-flight tool sandboxing, and tamper-evident Ed25519 attestations.

### Features
- **`btp_evaluate_action`**: Runs candidate tool calls in isolated pre-flight sandboxes and signs RFC 8785 Ed25519 evidence receipts.
- **`btp_verify_attestation`**: Evaluates incoming attestation receipts 100% offline with zero cloud roundtrips in ~175 µs.
- **`btp_get_trust_roots`**: Returns registered security invariants and decentralized authority public keys.

### Repository
https://github.com/ivegotahunnitonit/bartholomew/tree/main/mcp_server
```

---

## 4. Verification & Testing

* **Protocol Compliance**: 100% JSON-RPC 2.0 compliant across `initialize`, `tools/list`, and `tools/call`.
* **Zero Cloud Roundtrips**: Pure offline mathematical verification with pinned root authority keys.
* **Test Command**:
  ```bash
  python test_mcp_server_e2e.py
  ```
