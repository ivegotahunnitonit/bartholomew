# Awesome MCP Servers Submission Kit

Use this kit to list Bartholomew on the official and community Model Context Protocol directories:
- **Primary Repository**: [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)
- **Model Context Protocol Community**: [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)

---

## 1. Directory Entry Snippet

Under the **Security** or **Developer Tools** section:

```markdown
- [mcp-proxy-guard](https://github.com/ivegotahunnitonit/bartholomew) - Sub-35µs in-process security proxy for MCP servers in Claude Desktop and Cursor. Intercepts destructive commands (`rm -rf`, `DROP TABLE`) and scrubs API keys in-flight with zero configuration.
```

---

## 2. GitHub Issue / PR Template

**Title:**
```text
Add mcp-proxy-guard: Sub-35µs security proxy & credential scrubber for MCP servers
```

**Body:**
```markdown
### Summary
Add **mcp-proxy-guard** to the Security / Developer Tools category.

- **Repository**: https://github.com/ivegotahunnitonit/bartholomew
- **Website**: https://bartholomew.info
- **npm Registry**: https://www.npmjs.com/package/mcp-proxy-guard (`npx mcp-proxy-guard`)
- **PyPI Registry**: https://pypi.org/project/btp-guard/ (`pip install btp-guard`)
- **Open VSX**: https://open-vsx.org/extension/Bartholomew/bartholomew-guard-vscode
- **License**: MIT / Apache-2.0 (100% Pro Bono & Free for Developers)

### What it does:
`mcp-proxy-guard` wraps any Model Context Protocol server (filesystem, terminal, sqlite, postgres) across stdio:
1. **Destructive Tool Veto**: Intercepts and blocks destructive arguments (`rm -rf`, `mkfs`, `DROP TABLE`, `TRUNCATE`, `/etc/shadow`) in <35 microseconds before reaching the OS or database.
2. **In-Flight Secret Redaction**: Scrubs OpenAI, Anthropic, AWS, GitHub, Stripe, and private keys from tool inputs and output logs.
3. **Zero Configuration**: Simply prepend `npx -y mcp-proxy-guard --` to your existing MCP server command in `claude_desktop_config.json`.

### Verification:
Run instant in-terminal test:
```bash
npx mcp-proxy-guard test
```
```

---

## 3. Direct Submission Links
- **Open Issue on awesome-mcp-servers**: [https://github.com/punkpeye/awesome-mcp-servers/issues/new](https://github.com/punkpeye/awesome-mcp-servers/issues/new)
- **Edit README directly to open a PR**: [https://github.com/punkpeye/awesome-mcp-servers/edit/main/README.md](https://github.com/punkpeye/awesome-mcp-servers/edit/main/README.md)
