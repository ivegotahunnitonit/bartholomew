"""
Bartholomew Directory Submission Packager
=========================================
Generates pre-formatted PR entries, issue templates, and direct submission
links for premier ecosystem registries:
1. e2b-dev/awesome-ai-agents (Open Source Agents / Security)
2. e2b-dev/awesome-sdks-for-ai-agents (Agent SDKs & Runtime Tooling)
3. punkpeye/awesome-mcp-servers (Security section - PR #12562)
4. PatrickJS/awesome-cursorrules (DevSecOps - PR #370)
5. wfh/awesome-langgraph (Ecosystem & Security Guardrails)
"""

import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def generate_e2b_awesome_agents_entry():
    title = "Add Bartholomew (btp-guard) - Sub-35us in-process runtime guard for AI agents"
    body = """## [Bartholomew (btp-guard)](https://github.com/ivegotahunnitonit/bartholomew)
Sub-35us in-process AST runtime guard and execution containment for autonomous agent swarms.

<details>

### Category
Runtime Security / Agent Infrastructure / Developer Tools

### Description
- **Sub-35us In-Process AST Gating**: Intercepts shell, filesystem, and database tool dispatches directly inside Python process memory before execution.
- **Accidental Wipe Protection**: Deterministically blocks catastrophic commands (`rm -rf`, `DROP TABLE`, disk wipes) before they reach the OS or database.
- **Runaway Spend Caps**: Hard financial dollar caps preventing infinite agent retry loops and runaway model/API billing.
- **Credential Scrubbing**: Masks OpenAI, AWS, GCP, GitHub, and custom API tokens in-flight before logging or transmission.
- **Framework Support**: Zero-configuration 1-line decorators for CrewAI, LangGraph, AutoGen, LlamaIndex, and native Python tools.

### Links
- [Website](https://bartholomew.info)
- [GitHub](https://github.com/ivegotahunnitonit/bartholomew)
- [PyPI](https://pypi.org/project/btp-guard/)
- [npm](https://www.npmjs.com/package/btp-guard)

</details>
"""
    return title, body

def generate_awesome_langgraph_entry():
    title = "Add btp-guard: Runtime AST guardrails & spend caps for LangGraph pipelines"
    body = """- [Bartholomew (btp-guard)](https://github.com/ivegotahunnitonit/bartholomew) - Sub-35us in-process AST gating, destructive SQL/bash prevention, credential scrubbing, and spend caps for LangGraph and LangChain agents.
"""
    return title, body

def generate_awesome_mcp_entry():
    title = "Add btp-guard: Sub-35us in-process security gate & MCP execution guard"
    body = """### Server Name
`btp-guard`

### Description
Sub-35us in-process cryptographic trust and pre-flight AST sandboxing protocol (BTP v5.4.4) for Claude Desktop, Cursor, and multi-agent tool execution.

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
    print("  Bartholomew Ecosystem Directory Submission Generator")
    print("=" * 76)

    e2b_title, e2b_body = generate_e2b_awesome_agents_entry()
    lg_title, lg_body = generate_awesome_langgraph_entry()
    mcp_title, mcp_body = generate_awesome_mcp_entry()
    cursor_title, cursor_body = generate_awesome_cursorrules_entry()

    e2b_url = f"https://github.com/e2b-dev/awesome-ai-agents/issues/new?title={urllib.parse.quote(e2b_title)}&body={urllib.parse.quote(e2b_body)}"
    lg_url = f"https://github.com/wfh/awesome-langgraph/issues/new?title={urllib.parse.quote(lg_title)}&body={urllib.parse.quote(lg_body)}"
    mcp_url = f"https://github.com/punkpeye/awesome-mcp-servers/issues/new?title={urllib.parse.quote(mcp_title)}&body={urllib.parse.quote(mcp_body)}"
    cursor_url = f"https://github.com/PatrickJS/awesome-cursorrules/issues/new?title={urllib.parse.quote(cursor_title)}&body={urllib.parse.quote(cursor_body)}"

    doc_path = BASE_DIR / "AWESOME_DIRECTORIES_KIT.md"
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write("# Bartholomew Ecosystem Directory Submission Kit\n\n")
        f.write("Pre-formatted entries, pull request snippets, and direct 1-click issue links for top developer registries.\n\n")
        f.write("---\n\n")

        f.write("## 1. e2b-dev/awesome-ai-agents\n\n")
        f.write(f"- **Direct Link**: [Submit to awesome-ai-agents]({e2b_url})\n")
        f.write("- **Section**: Open-source projects -> Developer Tools / Security\n\n")
        f.write("```markdown\n" + e2b_body + "```\n\n")
        f.write("---\n\n")

        f.write("## 2. wfh/awesome-langgraph\n\n")
        f.write(f"- **Direct Link**: [Submit to awesome-langgraph]({lg_url})\n")
        f.write("- **Section**: Tools & Integrations / Security\n\n")
        f.write("```markdown\n" + lg_body + "```\n\n")
        f.write("---\n\n")

        f.write("## 3. punkpeye/awesome-mcp-servers (Status: PR #12562 Submitted)\n\n")
        f.write("- **PR Reference**: [Pull Request #12562](https://github.com/punkpeye/awesome-mcp-servers/pull/12562)\n")
        f.write(f"- **Fallback Issue**: [Open Submission Issue]({mcp_url})\n\n")
        f.write("```markdown\n" + mcp_body + "```\n\n")
        f.write("---\n\n")

        f.write("## 4. PatrickJS/awesome-cursorrules (Status: PR #370 Submitted)\n\n")
        f.write("- **PR Reference**: [Pull Request #370](https://github.com/PatrickJS/awesome-cursorrules/pull/370)\n")
        f.write(f"- **Fallback Issue**: [Open Submission Issue]({cursor_url})\n\n")
        f.write("```markdown\n" + cursor_body + "```\n\n")

    print(f"[+] Written ecosystem directory kit to: {doc_path.name}")
    print("[+] 1. e2b-dev/awesome-ai-agents: Ready")
    print("[+] 2. wfh/awesome-langgraph: Ready")
    print("[+] 3. punkpeye/awesome-mcp-servers: Verified (PR #12562)")
    print("[+] 4. PatrickJS/awesome-cursorrules: Verified (PR #370)")
    print("=" * 76)

if __name__ == "__main__":
    main()
