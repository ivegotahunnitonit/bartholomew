---
title: Why Your AI Agent Needs In-Memory AST Invariant Guards (Under 50µs)
published: true
tags: ai, python, security, opensource
cover_image: https://bartholomew.info/assets/hero-banner.png
canonical_url: https://bartholomew.info
---

# Why Your AI Agent Needs In-Memory AST Invariant Guards (Under 50µs)

If you have built autonomous tool-calling agents with **CrewAI**, **LangChain**, or **Microsoft AutoGen**, you have likely experienced the anxiety of letting an LLM execute bash commands, run database queries, or write files.

A single prompt injection, malformed SQL query, or unhinged hallucination can run:
```bash
rm -rf /
DROP TABLE production_users;
().__class__.__base__.__subclasses__() # Sandbox breakout
```

Most developers try to solve this in one of two ways:
1. **Remote LLM Moderation Calls (OpenAI Moderation / Bedrock Guardrails)**: Adds **1,200ms to 2,500ms of latency** to *every single tool call*. Your agent feels sluggish, costs blow up, and prompt injection can still bypass LLM-as-a-judge evaluators.
2. **Heavy Virtualization (Docker / Firecracker MicroVMs)**: Secure, but heavy. High RAM overhead, cold start latency, and difficult to integrate locally in dev environments.

Here is how we solved this deterministically with zero network calls and sub-50 microsecond execution time.

---

## The Concept: Deterministic Pre-Flight Compiler Invariants

Instead of asking another LLM *"Does this command look dangerous?"*, we pass candidate code blocks directly through an in-process, compiler-level Abstract Syntax Tree (AST) validator before the tool is ever called.

If the AST contains:
- Catastrophic filesystem deletions (`rm -rf`, `mkfs`, raw device writes)
- DDL SQL purges (`DROP TABLE`, `TRUNCATE`)
- Python sandbox escapes via dunder introspection (`__subclasses__`, `__globals__`)
- Unauthorized attempts to read sensitive files (`/etc/shadow`, `.ssh`, `.env`)
- High-entropy credential exfiltration (AWS keys, OpenAI keys, GitHub PATs)

The execution is vetoed **in less than 40 microseconds** directly inside Python memory.

---

## 1-Line Drop-In Protection (`btp-guard`)

We open-sourced this under the **Bartholomew Trust Protocol (BTP)** as a drop-in library for Python and TypeScript.

### Installation
```bash
pip install btp-guard
```

### Wrapping Any Python Tool with `@secure_tool`
```python
from btp_guard import secure_tool, SecurityVetoException

@secure_tool
def execute_database_query(query: str):
    # If the LLM generates "DROP TABLE users;", Bartholomew intercepts 
    # and aborts execution before the database connection is touched.
    return db.execute(query)

@secure_tool
def run_bash_command(cmd: str):
    # Intercepts obfuscated deletes, fork bombs, and credential leakage
    return subprocess.check_output(cmd, shell=True)
```

If an agent attempts an attack, it raises a `SecurityVetoException` with a cryptographic audit receipt:
```text
[BARTHOLOMEW SECURITY VETO] BTP-AST-001: Catastrophic destructive pattern detected. Hard cryptographic veto applied.
Latency: 38.4 µs
Signature: ed25519:7a4b89f02c418e99d3e810a9c8f2b740529d8174...
```

---

## Micro-Benchmark: In-Memory AST vs Remote LLM Gate

| Method | Latency | Network Required? | Can Prompt Injection Bypass? |
| :--- | :--- | :--- | :--- |
| **Cloud LLM Evaluator** | 1,500,000 µs (1.5s) | Yes | Yes (Jailbreak prone) |
| **Bartholomew (`btp-guard`)** | **38.2 µs (0.000038s)** | **No (In-Memory)** | **No (Compiler Invariant)** |

---

## Try It or Audit Your Codebase
- **Live In-Browser Sandbox**: [https://bartholomew.info](https://bartholomew.info)
- **GitHub Repository**: [https://github.com/ivegotahunnitonit/bartholomew](https://github.com/ivegotahunnitonit/bartholomew)
- **PyPI**: `pip install btp-guard`
- **npm**: `npm install btp-guard`

Would love to hear how other teams are handling agent execution guardrails without adding 2-second cloud latency to their agent loops!
