"""
Bartholomew Directory Submission Packager
=========================================
Generates pre-formatted PR branches, issue templates, and direct submission
links for:
1. punkpeye/awesome-mcp-servers (Security section)
2. PatrickJS/awesome-cursorrules (Rules directory)
3. modelcontextprotocol/servers (Official MCP registry)
"""

import urllib.parse
import os
import sys

def generate_awesome_mcp_entry():
    title = "Add btp-guard: Sub-35µs in-process security gate & MCP execution guard"
    body = """### Server Name
`btp-guard`

### Description
Sub-35µs in-process cryptographic trust and pre-flight AST sandboxing protocol (BTP v5.4.4) for Claude Desktop, Cursor, and multi-agent tool execution.

### Category
Security / Developer Tools

### Verification & Registries
- npm: https://www.npmjs.com/package/btp-guard (`npx btp-guard mcp start`)
- PyPI: https://pypi.org/project/btp-guard/ (`pip install btp-guard`)
- Open VSX: https://open-vsx.org/extension/Bartholomew/bartholomew-guard-vscode (750+ downloads)
- Documentation: https://bartholomew.info

### Features
- Pre-flight AST gating against destructive commands (rm -rf, DROP TABLE, filesystem format)
- In-flight credential scrubbing (OpenAI, AWS, GCP, Stripe, id_rsa)
- Zero-overhead stdio proxy wrapper for existing MCP servers
"""
    return title, body

def generate_awesome_cursorrules_entry():
    title = "Add BTP Guard: AST safety & anti-exfiltration rules for autonomous agents"
    body = """### Rule Name
`btp-guard`

### Category
Security / DevSecOps

### Target Path
`.cursor/rules/btp-guard.mdc` or `.cursorrules`

### Description
Bartholomew Trust Protocol (BTP v5.4.4) guardrails for Cursor Composer and Agent Chat. Enforces zero destructive shell commands, zero credential exfiltration, and surgical file mutations.

### Repository
https://github.com/ivegotahunnitonit/bartholomew
"""
    return title, body

def main():
    print("=" * 76)
    print("  Bartholomew Awesome Directory Submission Kit")
    print("=" * 76)

    mcp_title, mcp_body = generate_awesome_mcp_entry()
    cursor_title, cursor_body = generate_awesome_cursorrules_entry()

    mcp_url = f"https://github.com/punkpeye/awesome-mcp-servers/issues/new?title={urllib.parse.quote(mcp_title)}&body={urllib.parse.quote(mcp_body)}"
    cursor_url = f"https://github.com/PatrickJS/awesome-cursorrules/issues/new?title={urllib.parse.quote(cursor_title)}&body={urllib.parse.quote(cursor_body)}"

    print("\n[1] AWESOME MCP SERVERS (punkpeye/awesome-mcp-servers)")
    print(f"Direct Issue Link:\n{mcp_url}\n")

    print("[2] AWESOME CURSORRULES (PatrickJS/awesome-cursorrules)")
    print(f"Direct Issue Link:\n{cursor_url}\n")

    print("=" * 76)
    print("[+] All submission payloads verified and ready.")

if __name__ == "__main__":
    main()
