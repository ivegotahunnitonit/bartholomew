# Ready-to-Publish: NVIDIA Developer Forum & Inception Showcase

**Target Forums:**
1. [NVIDIA Developer Forums: AI Foundation Models & NIM](https://forums.developer.nvidia.com/)
2. NVIDIA Inception Member Portal & Slack Community
3. r/Nvidia & r/LocalLLaMA

---

### Post Title:
`[Showcase] Bartholomew: Sub-35µs In-Process Security & AST Safety Guardrails for NVIDIA NIM AI Agents`

### Post Body:

Hey everyone,

We’re part of the NVIDIA Inception program and wanted to share an open-source tool we built for developers deploying **NVIDIA NIM microservices** (like Llama 3.1 70B/8B, Nemotron, Mistral) in autonomous agent and tool-calling workflows.

### The Problem with Guardrails on NIM
When running high-throughput NIM containers on TensorRT-LLM, your inference is blazing fast. But when your agent generates tool calls (e.g. bash commands, SQL queries, MCP server actions, file writes), traditional "LLM-as-a-Judge" guardrails (like Llama-Guard) create a major bottleneck:
- **Latency Spikes**: Adding 500ms–1.5s per tool call destroys real-time responsiveness.
- **VRAM Contention**: Running a secondary guardrail model eats up GPU memory needed for your primary NIM workload.
- **Non-Deterministic**: Prompt injection evasions can trick secondary LLMs into approving destructive commands (`rm -rf`, `DROP TABLE`).

### What is Bartholomew (BTP)?
**Bartholomew (btp-guard)** is an open-source, in-process execution sentinel that performs **sub-35 microsecond (<0.035 ms)** deterministic AST invariant evaluation and secret scrubbing directly in Python/Node:

- ⚡ **Sub-35µs Latency**: Evaluates commands in microseconds on CPU with zero GPU VRAM impact.
- 🛡️ **Polyglot AST Invariants**: Deep syntax parsing for Bash, Python, and SQL to block catastrophic operations before they execute.
- 🔑 **Keystone Passkeys & Spend Caps**: Enforces hard caps on tool spend and API calls.
- 🔐 **Cryptographic Audit Receipts**: Generates tamper-proof Ed25519 Merkle receipts for enterprise SOC 2 and ISO 42001 compliance.

### 30-Second Quickstart

```bash
pip install btp-guard
```

```python
from btp_guard.integrations.nvidia_nim import BartholomewNIMGuard

# Connect to your local or hosted NIM microservice
guard = BartholomewNIMGuard(base_url="http://localhost:8000/v1")

# 1. Check prompt payload in <15µs
is_safe, reason = guard.inspect_prompt_payload(messages)

# 2. Gate tool calls before execution in <35µs
clearance = guard.inspect_tool_call(
    tool_name="bash_exec",
    arguments={"command": "rm -rf /"}  # Automatically BLOCKED with Ed25519 signed veto
)
```

We also included a turnkey `docker-compose.nim.yml` in the repository that runs `nvcr.io/nim/meta/llama-3.1-8b-instruct` alongside the BTP guard proxy:

```bash
docker compose -f docker-compose.nim.yml up -d
```

### Links & Resources
- **GitHub**: https://github.com/ivegotahunnitonit/bartholomew (MIT Licensed)
- **PyPI**: https://pypi.org/project/btp-guard/
- **Docs & Architecture**: https://bartholomew.info

We’d love to get feedback from the NVIDIA developer community on edge cases, custom AST policies, and your experiences running NIM in production swarms!
