<div style="font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif; line-height: 1.6;">

# **Product Hunt Launch Day Community FAQ & Response Playbook**
### **Fast-Response Cheat Sheet for Bartholomew (v2.4 Launch)**

Keep this document open during launch day. When comments, technical inquiries, or investor questions appear on Product Hunt, copy and tailor these responses in 5 seconds flat.

---

## **Q1: "How does this differ from Docker, Firecracker, or sandbox VMs?"**

**Key Insight**: Sandboxes are heavy and slow (150ms+ startup), and they don't solve the "dirty state" problem or provide microsecond rollbacks.

```text
Great question! Traditional sandboxes (like Docker or Firecracker microVMs) isolate the OS process, but they introduce 50ms-250ms of virtualization overhead per call and don't provide transactional semantics. If an agent executes an invalid file mutation or breaks an AST invariant inside a container, the files inside that container are still broken and dirty.

Bartholomew takes a database transaction approach right in local CPU memory:
1. Sub-5µs AST Invariant Gating: It inspects the abstract syntax tree and argument boundaries before dispatching to the shell or tool executor.
2. In-Memory Copy-on-Write Micro-Rollbacks (<2.3µs): It captures an in-memory byte snapshot before mutating actions. If an invariant trips, the workspace is atomically rolled back to pristine byte state with zero orphaned files.
3. Diagnostic Remediation: Instead of throwing a generic container crash, it returns structured JSON-RPC remediation hints so the model legitimately self-corrects its plan instead of hallucinating in a retry loop.
```

---

## **Q2: "Does this introduce latency to my LLM agent workflows?"**

**Key Insight**: LLM calls take 1,500ms to 4,000ms. Bartholomew runs in 2 to 5 microseconds—literally imperceptible (0.0001% of request time).

```text
Zero perceptible latency. An average LLM generation call takes anywhere from 1,000ms to 4,000ms. Bartholomew's pre-flight AST checks and secret scrubbing execute in 0.8µs to 4.8µs directly in local CPU memory with zero network roundtrips. 

It adds less than 0.0001% overhead to your agent loop while giving you complete transactional rollback safety.
```

---

## **Q3: "How does the in-flight secret scrubber catch obfuscated API keys?"**

**Key Insight**: Multi-layered detection using high-performance regex, deep base64 decoding, and Shannon entropy heuristics.

```text
The secret engine operates in three layers in sub-10 microseconds:
1. Deterministic Token Signatures: Pre-compiled regex patterns targeting known API credential formats (OpenAI sk-proj, Anthropic sk-ant, AWS AKIA, GitHub PAT, GCP, private keys).
2. Deep Encoded Inspection: It automatically detects and decodes high-entropy base64 chunks in-flight to uncover concealed keys before outbound dispatch.
3. Shannon Entropy Scoring: Any arbitrary token string with entropy > 4.5 is flagged for high-entropy credential leakage (OWASP LLM02).
```

---

## **Q4: "Can I use this with Claude Desktop, Cursor, or Windsurf?"**

**Key Insight**: Yes, out of the box via standard MCP (Model Context Protocol).

```text
Yes, completely out of the box! You can plug Bartholomew into Claude Desktop, Cursor, or Windsurf via the standard Model Context Protocol:

Add this to your claude_desktop_config.json:
{
  "mcpServers": {
    "bartholomew": {
      "command": "npx",
      "args": ["-y", "btp-guard", "mcp"]
    }
  }
}

It starts an in-process JSON-RPC security proxy that monitors tool calls and bash execution on your machine.
```

---

## **Q5: "Can I use this with LangGraph, CrewAI, or Microsoft AutoGen?"**

**Key Insight**: Yes, native Python decorators and middleware are available.

```text
Yes! We maintain dedicated adapters and drop-in decorators for AutoGen, LangGraph, and CrewAI:
- Python Package: pip install btp-guard
- 1-Line Guard: @guard.protect on any tool function or executor.
- AutoGen Recipe: SafeCommandLineCodeExecutor wrapping LocalCommandLineCodeExecutor.

Check out our complete integration guide here:
https://github.com/ivegotahunnitonit/bartholomew/blob/main/docs/FRAMEWORK_GUIDE.md
```

---

## **Q6: "Is it really free and open source?"**

**Key Insight**: Apache 2.0 open-source core library with commercial enterprise licensing available for proprietary fleet hosting.

```text
Yes! The core execution harness, CLI, MCP server, and framework adapters are 100% open source under the Apache 2.0 license. You can inspect the source code, fork it, and run it locally on your machine today:
$ npx btp-guard
```

</div>
