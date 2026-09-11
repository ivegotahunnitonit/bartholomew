# Hacker News (Show HN) Launch Submission Kit
**Bartholomew Protocol (BTP v5.4.5)**

Copy and paste the title, URL, and body below directly into Hacker News (https://news.ycombinator.com/submit).

---

### Suggested Title
```text
Show HN: Bartholomew – Sub-35µs in-process safety gateway and sentinel for AI agents
```

### URL (leave blank if submitting as text post, or enter):
```text
https://github.com/ivegotahunnitonit/bartholomew
```

---

### Post Body (Markdown)

```markdown
Hey HN,

We built Bartholomew (https://bartholomew.info), an open-source, in-process execution gateway for autonomous AI agents.

Most agent safety systems today operate as post-execution audit loggers or external HTTP reverse proxies. That creates two big problems:
1. Post-execution alerts are too late: if an agent executes `DROP TABLE users;` or `rm -rf /`, knowing about it 2 seconds later in a Slack webhook doesn't save your database.
2. HTTP proxy hops add 50ms–200ms of latency per tool call, which kills throughput when orchestrating multi-agent swarms.

Bartholomew runs *inline* within the agent process (Python/Go/Rust). Every tool call, database query, and shell dispatch is intercepted before it reaches the OS or database seam. It evaluates local AST syntax trees, masks credentials, checks spend caps, and produces signed Ed25519 Merkle audit receipts—with an average latency of 29.44 microseconds (<0.03 milliseconds).

### What's New in v5.4.5:
* **Frontier Model Wire Support**: Native tool normalization for OpenAI GPT-Astra / Agents SDK, Anthropic Claude 3.7 (with hybrid reasoning scratchpad isolation so `<thinking>` blocks don't cause false positives), Google Gemini 3.8 / 2.0 multimodal thought parts, and DeepSeek-R1.
* **The Sentinel Companion**: Bartholomew is designed not as a cold HTTP 403 error, but as your swarm's digital steward. If an LLM hallucination attempts an unconstrained delete, Bartholomew holds the line and prints empathetic, constructive guidance explaining what went wrong and how the agent can safely achieve its goal.
* **1-Line Multi-Agent Adapters**: Drop-in guards for CrewAI, LangGraph, Microsoft AutoGen, and LlamaIndex.

### 5-Second Test Drive:
```bash
pip install --upgrade btp-guard
```

Test a simulated runaway table drop right in your terminal:
```bash
python -m cli companion --simulate drop
```

Or converse directly with the sentinel companion in real-time:
```bash
python -m cli companion
```

### Architecture & Benchmarks:
- Source: https://github.com/ivegotahunnitonit/bartholomew
- Benchmark report: https://github.com/ivegotahunnitonit/bartholomew/blob/main/BENCHMARK_FRONTIER_MODELS.md (tested across 4,000 iterations at 33,900+ evals/sec)
- Web & Docs: https://bartholomew.info

We would love your honest feedback, critique of our AST parsing heuristics, and thoughts on agent execution security!
```

---

### Tips for Launch Timing & Comment Engagement
1. **Best Posting Window**: Weekdays between 6:30 AM – 9:00 AM PT (9:30 AM – 12:00 PM ET).
2. **First Comment**: Immediately post a brief creator comment reiterating your motivation (e.g. why you built it after seeing autonomous agents hallucinate shell scripts or spend loops).
3. **Responsiveness**: Stay active in the thread for the first 2 hours to answer technical questions about in-process gating vs eBPF, AST coverage, and zero-leakage cryptography.
