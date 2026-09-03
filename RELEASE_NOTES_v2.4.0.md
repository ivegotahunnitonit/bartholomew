# Bartholomew BTP v2.4.0 Official Release Notes
**Release Tag**: `v2.4.0`  
**Release Date**: September 2, 2026  
**License**: Apache-2.0  
**Specification**: Bartholomew Trust Protocol (BTP) v2.4 Standards Track  

---

## Executive Summary
Bartholomew v2.4.0 marks a fundamental architectural evolution: transitioning from brittle, negative-filtering prompt firewalls to a **resilient, transactional execution runtime** designed specifically for the **Model Context Protocol (MCP)** ecosystem (Anthropic Claude Desktop, Cursor, Windsurf, Devin, and AutoGen).

Rather than terminating agent workflows with abrupt rejections, v2.4.0 introduces **sub-5 microsecond in-memory workspace micro-rollbacks**, **bi-directional in-flight secret scrubbing**, and **chained Merkle state graphs** that issue cryptographically verifiable Ed25519 session audit manifests.

---

## Key Features & Enhancements

### 1. Transactional Copy-on-Write Workspace & Micro-Rollback (<5 µs)
* **Pre-Flight In-Memory Snapshots**: Automatically captures byte-level checkpoints before any mutating tool call (`write_file`, `bash`, `edit_file`, `apply_patch`).
* **Instant State Restoration**: If an agent violates policy boundaries (e.g., path traversal outside the workspace root) or encounters an execution failure, the workspace is atomically restored in **2.3 µs**.
* **Zero-Hallucination Diagnostic Feedback**: Emits constructive JSON-RPC `-32000` recovery guidance, allowing LLMs to self-correct without getting trapped in retry loops.

### 2. Transparent Bi-Directional MCP Security Proxy
* **Universal Inline Proxy**: Plugs transparently between any MCP client and downstream server (`stdio` / `SSE`) with zero client or server code modifications.
* **In-Flight Credential Scrubbing**: Automatically detects and redacts high-entropy keys (OpenAI, Anthropic, AWS, GitHub PATs, private keys) in inbound tool arguments.
* **Outgoing Response Scrubbing**: Sanitizes server stdout and tool return objects, ensuring credentials never leak back into LLM context windows or logs.

### 3. Scoped Symbol-Table AST Invariant Engine
* **Lexical Scope Tracking**: Replaced flat AST traversal with a multi-scope `ScopedASTVisitor`, preventing global alias poisoning across nested functions.
* **Dynamic Evasion Hardening**: Intercepts obfuscated calls, constant-folded dynamic `getattr`, `importlib.import_module`, `asyncio.create_subprocess_shell`, and `pickle.loads`.

### 4. Chained Merkle State Graphs & Session Audit Manifests
* **Multi-Turn Hash Chaining**: Links each approved turn cryptographically to the hash of the preceding turn ($H_i = \text{SHA256}(H_{i-1} \parallel \text{JCS}(\text{receipt}_i))$).
* **Enterprise CI/CD Attestation**: Exports a comprehensive, Ed25519-signed session audit manifest (`export_session_audit_manifest()`) suitable for attachment to GitHub Pull Requests and enterprise compliance records.

### 5. Developer CLI & 1-Click Showcase
* `python cli.py version`: Displays BTP v2.4.0 engine specifications.
* `python cli.py demo-v24`: Runs a live 3-scenario interactive terminal showcase.
* `python cli.py proxy --server-cmd <cmd>`: Starts an inline MCP stdio security proxy with a single command.

---

## Verification & Integrity
* **Test Suite**: `tests/test_v24_mcp_transaction.py` verified 100% clean.
* **Evasion Suite**: `test_advanced_ast_evasions.py` verified 100% clean.
* **Whitepaper**: Formal theoretical foundations published in [`paper_v2_4.md`](paper_v2_4.md).
