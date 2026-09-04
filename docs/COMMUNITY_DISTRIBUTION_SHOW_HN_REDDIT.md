# Bartholomew Trust Protocol (BTP v2.5.0) - Community Distribution & Launch Kit

This document provides fully drafted, copy-paste-ready community announcements, technical write-ups, and benchmarks tailored for Hacker News, Reddit, and developer communities.

---

## 1. Hacker News: Show HN

### Post Details
- **Title**: Show HN: Bartholomew – Deterministic runtime safety and micro-rollbacks for LLM agents
- **URL**: https://bartholomew.info (or Leave blank if submitting text post with direct link)

### Submission Text
```text
Hey HN,

We built Bartholomew (BTP v2.5.0), a deterministic, low-latency execution runtime and transparent MCP security gateway for autonomous AI agents.

Repo: https://github.com/ivegotahunnitonit/bartholomew
Live Sandbox: https://bartholomew.info
Zenodo Preprint: https://doi.org/10.5281/zenodo.18843719

The Problem:
Current agent safety relies almost exclusively on LLM self-moderation or prompt guardrails. When an agent enters an infinite loop, attempts an unauthorized recursive file deletion, or leaks an API token via tool stdout, probabilistic prompt filters either miss it entirely or return a refusal string that triggers agent hallucination spirals.

What Bartholomew Does:
1. Sub-Microsecond Event Gating (0.95 µs): Evaluates OS-level events and synthetic input (clicks, keypresses, system calls) before execution using native C bindings.
2. In-Memory Static AST Analysis (86 µs): Detects obfuscated payloads (base64 decoding, chr() concats, dynamic lambdas) without spawning sub-processes.
3. Transactional Micro-Rollbacks: Uses memory-mapped Copy-on-Write (CoW) state buffers. If an agent executes an unauthorized file mutation or violates security invariants, state rolls back to a known-clean baseline in under 3 ms.
4. Latent Dirichlet Metric Unit (LDMU): Mathematically quantifies agent behavioral drift across multi-step execution graphs, catching runaway loops before token budgets are exhausted.
5. Zero-Config MCP Security Proxy: Drops between your agent orchestrator (LangChain, AutoGen, CrewAI, Claude Desktop, Cursor) and MCP tool servers to intercept and sanitize tool calls.

Benchmarks (Apple M-series & AMD EPYC Linux):
- In-memory AST safety evaluations: 1,050,000 evals/sec
- RFC 8785 Canonical JSON hashing: 28.3 µs
- Ed25519 cryptographic receipt signing: 46.3 µs
- Sliding window credential redaction: 12.1 µs per 4KB chunk

Try it locally:
$ pip install btp-guard
$ npx btp-guard check --file policy.yaml

Or interact with the live presets directly in your browser:
https://bartholomew.info

We would love feedback on our threat model, formal verification proofs, and AST heuristics.
```

---

## 2. Reddit: r/MachineLearning

### Post Title
`[P] Bartholomew: Deterministic Runtime Invariants and Micro-Rollbacks for Agentic Systems (1.05M evals/sec)`

### Post Body
```markdown
Hi r/MachineLearning,

As multi-agent architectures (AutoGen, CrewAI, LangGraph) gain autonomy over tool execution and filesystem modifications, stochastic safety guards (system prompt instructions, judge LLM calls) have shown severe vulnerabilities to multi-turn goal hijacking, prompt injection, and hallucinated bash commands.

We are sharing Bartholomew (BTP v2.5.0), an open-source runtime security substrate designed to provide formal, deterministic guarantees for tool-using agents.

**Key Technical Pillars:**
1. **Deterministic Pre-Execution Invariant Gates**: Replaces judge LLM evaluation with compiled abstract syntax tree (AST) inspection and static analysis. It parses shell and Python invocations into typed nodes, evaluating constant-folded expressions and identifying obfuscated system calls (such as dynamic lambda executions or hex-encoded calls) in ~86 microseconds.
2. **Latent Dirichlet Metric Unit (LDMU)**: A state-space metric model that models agent drift. It tracks divergence between intended goal embeddings and intermediate action trajectories, terminating runaway execution loops with minimal compute overhead.
3. **Hardware-Accelerated Rollback**: Uses CoW memory-mapped snapshots to ensure atomic execution. If an agent script fails post-condition verification (e.g. unexpected schema deletion or permission elevation), the runtime rolls back the local environment in sub-5 ms without container restarts.
4. **Cryptographic Proofs of Execution**: Every tool invocation produces an RFC 8785 canonical JSON digest signed with an agent-specific Ed25519 key, providing non-repudiable audit trails for SOC 2 and ISO 27001 compliance.

- **Paper Preprint**: [Zenodo DOI 10.5281/zenodo.18843719](https://doi.org/10.5281/zenodo.18843719)
- **Source Code**: [GitHub](https://github.com/ivegotahunnitonit/bartholomew)
- **Live Interactive Bench**: [https://bartholomew.info](https://bartholomew.info)

We welcome discussion regarding the formal verification models, state rollback overhead, and multi-turn stateful attack mitigations.
```

---

## 3. Reddit: r/LangChain

### Post Title
`How to gate LangChain & CrewAI tools with sub-microsecond deterministic checks (No more LLM judge latency)`

### Post Body
```markdown
Hey everyone,

If you run agents with code execution or terminal tools, you have likely run into the safety dilemma:
- Option A: Trust system prompts (easily bypassed by indirect prompt injection).
- Option B: Run a secondary LLM as a judge (adds 500ms–2000ms latency per step and increases API costs).

We built an open-source drop-in middleware called Bartholomew (`btp-guard`) that provides deterministic security in under 100 microseconds:

```python
from langchain.tools import tool
from btp_guard.integrations import BartholomewLangChainTool

@tool
def execute_sql(query: str) -> str:
    """Executes a database query."""
    return db.run(query)

# Wrap tool with deterministic invariant gates and secret scrubbing
secure_sql_tool = BartholomewLangChainTool(
    execute_sql,
    policy_path="security_policy.yaml"
)
```

**What happens at runtime:**
1. **Pre-execution AST Check**: If the agent generates `DROP TABLE` obfuscated with comments (`DROP/**/TABLE`) or string concatenation, it is rejected immediately (0.08 ms) without making an LLM API call.
2. **Secret Redaction**: Any database credentials, API keys, or JWT tokens in the tool output are automatically masked before being sent back to the model context.
3. **SIEM Export**: Every query and decision is streamed asynchronously to Datadog, Splunk, or CloudWatch with cryptographic Ed25519 signatures.

- **Package**: `pip install btp-guard`
- **GitHub**: https://github.com/ivegotahunnitonit/bartholomew
- **Interactive Sandbox**: https://bartholomew.info
```

---

## 4. Reddit: r/LocalLLaMA

### Post Title
`Benchmarking local agent safety: 1.05M evals/sec deterministic runtime without GPU overhead`

### Post Body
```markdown
Hey LocalLLaMA community,

When running autonomous agents locally (e.g. Llama 3, Mistral, Qwen via Ollama or vLLM), you do not want to dedicate precious VRAM to a separate guardrail model.

Bartholomew is a lightweight C/Python runtime substrate that runs entirely on CPU:
- **Throughput**: Over 1,050,000 security evaluations per second on a single thread.
- **Latency**: Sub-5 µs for OS event gating; 86 µs for complete AST static analysis.
- **Memory Footprint**: Under 12 MB resident memory.

It provides:
1. Real-time file system write protection with micro-rollbacks.
2. Detection of prompt injection and comment-obfuscated commands.
3. Token budget governor preventing runaway inference loops.
4. Offline air-gapped verification (`btp verify-offline`) for secure enclave deployments.

Check out the benchmarks and run it locally:
```bash
pip install btp-guard
btp benchmark --cycles 10000
```
GitHub: https://github.com/ivegotahunnitonit/bartholomew
Sandbox: https://bartholomew.info
```

---

## 5. Discord / Slack Communities (LangChain, AutoGen, AI Engineers, DevSecOps)

### Message Template
```text
Hey everyone! We just released Bartholomew (BTP v2.5.0), an open-source deterministic runtime guard for autonomous agents.

Instead of relying on slow LLM judges (which add 1-2s latency and can hallucinate), Bartholomew intercepts agent actions at the runtime level in <100 µs:
- Intercepts shell scripts, SQL queries, and tool parameters via static AST inspection
- Memory-mapped transactional rollbacks if an invariant is violated
- Live in-flight token/secret masking for stdout streams
- Native middleware for LangChain, CrewAI, AutoGen, and LlamaIndex

Quick install: `pip install btp-guard` / `npx btp-guard`
Live playground: https://bartholomew.info
Docs & GitHub: https://github.com/ivegotahunnitonit/bartholomew

Would love to hear your thoughts or answer any questions about the threat model!
```
