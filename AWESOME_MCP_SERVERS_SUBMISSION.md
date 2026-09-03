# Awesome MCP Servers Submission Kit

Use this kit to list Bartholomew on the official and community Model Context Protocol directories:
- **Primary Repository**: [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)
- **Model Context Protocol Community**: [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)

---

## 1. Directory Entry Snippet

Under the **Security** or **Developer Tools** section:

```markdown
- [Bartholomew](https://github.com/ivegotahunnitonit/bartholomew) - Sub-5µs transactional execution harness, in-memory Copy-on-Write micro-rollbacks, and in-flight secret scrubber for MCP agent tools.
```

---

## 2. GitHub Issue / PR Template

**Title:**
```text
Add Bartholomew: Transactional security proxy & rollback harness for MCP tools
```

**Body:**
```markdown
### Summary
Add **Bartholomew** to the Security / Developer Tools category.

- **Repository**: https://github.com/ivegotahunnitonit/bartholomew
- **Website**: https://bartholomew.info
- **npm Registry**: https://www.npmjs.com/package/btp-guard (`npx btp-guard`)
- **PyPI Registry**: https://pypi.org/project/btp-guard/ (`pip install btp-guard`)
- **License**: Apache-2.0

### What it does:
Bartholomew operates directly on the JSON-RPC stdio boundary between MCP clients (Claude Desktop, Cursor) and tool servers:
1. **In-Memory Copy-on-Write Rollbacks**: Intercepts path escapes and AST invariant breaches, restoring pristine files in 2.30µs before filesystem damage occurs.
2. **In-Flight Secret Scrubbing**: Redacts OpenAI, Anthropic, AWS, and GitHub tokens in 0.82µs across inbound arguments and outbound stdout.
3. **Offline Merkle Receipts**: Signs chained RFC 8785 Ed25519 execution manifests verifiable 100% offline.

### Verification:
You can run an instant 3-second simulation in any terminal:
```bash
npx btp-guard
```
```

---

## 3. Direct Submission Links
- **Open Issue on awesome-mcp-servers**: [https://github.com/punkpeye/awesome-mcp-servers/issues/new](https://github.com/punkpeye/awesome-mcp-servers/issues/new)
- **Edit README directly to open a PR**: [https://github.com/punkpeye/awesome-mcp-servers/edit/main/README.md](https://github.com/punkpeye/awesome-mcp-servers/edit/main/README.md)
