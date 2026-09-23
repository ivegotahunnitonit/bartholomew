# Claude Code + Bartholomew Trust Protocol (BTP v5.4.20)
## Zero-Latency Execution Sentinel & Invariant Gating for Anthropic Claude Code

[![Claude Code](https://img.shields.io/badge/Anthropic-Claude%20Code-D97706?logo=anthropic)](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)
[![PyPI](https://img.shields.io/pypi/v/btp-guard.svg)](https://pypi.org/project/btp-guard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

### Overview
Claude Code is Anthropic's terminal agent capable of editing files, running bash commands, and orchestrating developer workflows directly on your machine.

When Claude Code is granted autonomous execution permissions, indirect prompt injections, hallucinated commands, or rogue subshell expansions pose severe risks:
- Unintended file tree wipes (`rm -rf`)
- Credential exposure (`.env`, `.pem`, SSH keys)
- Dangerous remote piping (`curl | sh`)

Bartholomew acts as an in-process sentinel that intercepts all Claude Code actions in sub-35 microseconds before OS dispatch.

---

### 1-Click Quickstart

Initialize Bartholomew in your Claude Code workspace:

```bash
npx btp-guard claude
# or: python -m btp_guard claude
```

This automatically:
1. Generates `CLAUDE.md` with deterministic boundary invariants.
2. Configures the Bartholomew MCP gate for Claude Code tool invocations.
3. Sets up `.cursorrules` and `.windsurfrules` for multi-editor synchronization.

---

### Test the Sentinel

Run the standalone cookbook verification:

```bash
python examples/06_claude_code_sentinel.py
```
