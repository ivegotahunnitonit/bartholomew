# Official Model Context Protocol (MCP) Registry Submission Kit

---

## 1. Registry Submission Metadata

* **Server Name**: `bartholomew-sentinel` (`btp-guard`)
* **Display Name**: `Bartholomew AI Security Gate & Execution Sentinel`
* **Category**: `Security` / `Governance & Verification` / `Developer Tools`
* **Version**: `5.4.6`
* **Repository**: [https://github.com/bartholomew-ai/bartholomew](https://github.com/bartholomew-ai/bartholomew)
* **npm**: [https://www.npmjs.com/package/btp-guard](https://www.npmjs.com/package/btp-guard)
* **PyPI**: [https://pypi.org/project/btp-guard/5.4.6/](https://pypi.org/project/btp-guard/5.4.6/)
* **Live Discovery**: [https://acn-26670.web.app/.well-known/mcp.json](https://acn-26670.web.app/.well-known/mcp.json)
* **License**: Apache-2.0
* **Description**: `Sub-35µs deterministic in-process AST execution firewall and cryptographic proof verification protocol (BTP v5.4.6) for Claude Desktop, Cursor, Windsurf, and autonomous agent swarms.`

---

## 2. One-Click Client Configurations

### A. Zero-Install Remote HTTP (Claude Desktop, Cursor, Windsurf, Zed)

```json
{
  "mcpServers": {
    "bartholomew-sentinel": {
      "url": "https://bartolomew-cloud-engine-322603900775.us-central1.run.app/api/v1/m2m/verify",
      "type": "http"
    }
  }
}
```

### B. Local Stdio via PyPI / Python

```bash
pip install btp-guard==5.4.6
```

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

### C. Smithery CLI (1-Click Auto-Install)

```bash
npx -y @smithery/cli install @bartholomew-ai/bartholomew --client claude
npx -y @smithery/cli install @bartholomew-ai/bartholomew --client cursor
```

---

## 3. Pull Request Submission Template for `modelcontextprotocol/servers` & `awesome-mcp-servers`

**Target PR Title:**
```text
Add bartholomew-sentinel: Sub-35µs in-process AST execution firewall & agent trust protocol
```

**Target PR Body:**
```markdown
### Server Name
`bartholomew-sentinel` (`btp-guard`)

### Description
A high-speed in-process deterministic execution firewall and cryptographic attestation gate (BTP v5.4.6). Evaluates candidate agent actions (Bash commands, SQL queries, file operations, webhooks) before OS syscall commitment, preventing catastrophic tool calls (`rm -rf`, `DROP TABLE`, secret leaks, and reverse shells).

### Key Features
- **Deterministic Sub-35µs AST Filtering**: In-memory inspection across Python, JavaScript, Go, Rust, and Shell. Verified 19.10µs median latency under 100,000 multi-swarm cycles.
- **RFC 8785 Ed25519 Execution Receipts**: Cryptographically signed zk-TCP proofs generated for every tool invocation.
- **Universal Multi-Framework Adapters**: Zero-modification drop-in guards for CrewAI, LangGraph, AutoGen, LlamaIndex, Claude 3.7, and OpenAI Swarm.
- **Enterprise SOC 2 / ISO 27001 Dossier**: Exportable audit trail via `python cli.py dossier`.

### Repository
https://github.com/bartholomew-ai/bartholomew

### Package Registry
- PyPI: https://pypi.org/project/btp-guard/5.4.6/
- npm: https://www.npmjs.com/package/btp-guard
```

---

## 4. Verification & Conformance Status

* **Protocol Compliance**: 100% JSON-RPC 2.0 compliant across `initialize`, `tools/list`, and `tools/call`.
* **Empirical 100K Benchmark**: Verified 6,300 ops/sec, 0 false negatives, 0 false positives.
* **Automated Tests**: Passed all tests in `tests/test_mcp_registry_spec.py` and `tests/test_standing_mesh_daemon.py`.
