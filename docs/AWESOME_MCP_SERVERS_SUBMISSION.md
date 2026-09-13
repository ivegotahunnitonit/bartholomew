# Awesome MCP Servers Submission Kit

Use this kit to list Bartholomew on the official and community Model Context Protocol directories:
- **Primary Repository**: [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)
- **Model Context Protocol Community**: [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)

---

## 1. Directory Entry Snippet

Under the **Security** or **Developer Tools** section:

```markdown
- [btp-guard](https://github.com/ivegotahunnitonit/bartholomew) - Sub-35µs in-process security proxy for MCP servers in Claude Desktop and Cursor. Intercepts destructive commands (`rm -rf`, `DROP TABLE`) and scrubs API keys in-flight with zero configuration.
```

---

## 2. GitHub Issue / PR Template

**Title:**
```text
Add btp-guard: Sub-35µs in-process security proxy & credential scrubber for MCP servers
```

**Body:**
```markdown
### Summary
Add **btp-guard** to the Security / Developer Tools category.

- **Repository**: https://github.com/ivegotahunnitonit/bartholomew
- **Website**: https://bartholomew.info
- **npm Registry**: https://www.npmjs.com/package/btp-guard (`npx btp-guard init`)
- **PyPI Registry**: https://pypi.org/project/btp-guard/ (`pip install btp-guard`)
- **License**: MIT (100% Free & Open-Source for Developers)

### What it does:
`btp-guard` sits at the execution boundary of Model Context Protocol (MCP) clients (Claude Desktop, Cursor, Windsurf):
1. **Destructive Tool Veto**: Intercepts and blocks destructive arguments (`rm -rf`, `mkfs`, `DROP TABLE`, `TRUNCATE`, `/etc/shadow`) in <35 microseconds before reaching the OS or database.
2. **In-Flight Secret Redaction**: Scrubs OpenAI, Anthropic, AWS, GitHub, Stripe, and private keys from tool inputs and output logs.
3. **Zero Configuration**: 1-command setup via `npx btp-guard init` or prepending `npx -y btp-guard mcp` in your MCP client configuration.

### Verification:
Run instant in-terminal test:
```bash
npx btp-guard demo
```
```

---

## 3. Direct Submission Links
- **Open Issue on awesome-mcp-servers**: [https://github.com/punkpeye/awesome-mcp-servers/issues/new](https://github.com/punkpeye/awesome-mcp-servers/issues/new)
- **Edit README directly to open a PR**: [https://github.com/punkpeye/awesome-mcp-servers/edit/main/README.md](https://github.com/punkpeye/awesome-mcp-servers/edit/main/README.md)
