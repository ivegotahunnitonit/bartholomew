# **Bartholomew BTP v2.2 Model Context Protocol (MCP) Security Server**
### **Cryptographic Trust & Pre-Flight Sandboxing for Claude Desktop &amp; Cursor**

The Bartholomew MCP Server adds 100% offline, vendor-neutral cryptographic verification to Anthropic’s **Model Context Protocol (MCP)**.

---

## **Installation in Claude Desktop**

Add this to your Claude Desktop configuration (`claude_desktop_config.json`):

### **MacOS / Linux:**
```json
{
  "mcpServers": {
    "bartholomew-guard": {
      "command": "python3",
      "args": ["-m", "mcp_server.server"]
    }
  }
}
```

### **Windows:**
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

---

## **Available MCP Tools**

1. **`btp_evaluate_action`**: Runs candidate tool calls in pre-flight sandboxes and returns an RFC 8785 Ed25519 cryptographic receipt.
2. **`btp_verify_attestation`**: Evaluates incoming receipts 100% offline in ~175 µs.
3. **`btp_get_trust_roots`**: Lists active recognized root keys and registered security invariants (`BTP-SEC-001` to `008`).

---

## **Specifications & Verification**
* **Frozen Protocol Specification:** [BTP_PROTOCOL_SPECIFICATION.md](https://github.com/ivegotahunnitonit/bartholomew/blob/main/BTP_PROTOCOL_SPECIFICATION.md)
* **Adversarial Invariant Challenge:** [CHALLENGE_PACKAGE.md](https://github.com/ivegotahunnitonit/bartholomew/blob/main/CHALLENGE_PACKAGE.md)
