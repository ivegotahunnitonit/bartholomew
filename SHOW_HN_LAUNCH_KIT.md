# **Show HN & Global Developer Launch Kit (BTP v3.0)**
### **The AI Agent Execution Gateway: In-Process Tool Safety in <35 Microseconds**

---

## **1. Hacker News (Show HN)**

### **Title Options (Pick One)**
* **Option A (Recommended)**: `Show HN: Bartholomew (BTP v3.0) – In-process runtime guard for AI agents`
* **Option B**: `Show HN: Bartholomew – Stop autonomous agents from running rm -rf or DROP TABLE in <35µs`
* **Option C**: `Show HN: We built an in-process execution gateway for CrewAI, LangChain, and AutoGen`

### **Body Text**
```markdown
Hey HN,

I’m Itsub, creator of Bartholomew Protocol (BTP v3.0).

Over the last few months of building autonomous agents with LangChain, CrewAI, and AutoGen, we kept hitting a terrifying reality:
Current "AI guardrails" (NeMo, LlamaGuard, cloud API proxies) only inspect prompt text. They add 800ms to 2,000ms of latency, cost extra LLM tokens, and are completely blind to what happens when an agent actually calls a tool. Once an agent decides to call a database query or run a shell command, prompt guardrails are already out of the loop.

On the other hand, Docker / OS sandboxes isolate the host OS, but they don't stop an agent from executing `DROP TABLE customers` inside the container or getting stuck in an infinite retry loop that burns $300 in API credits.

We built Bartholomew (`btp-guard`) as an **in-process AI agent execution gateway** to solve this:
👉 https://github.com/ivegotahunnitonit/bartholomew
👉 Website & Architecture: https://bartholomew.info

### What It Does (<35µs Latency, 100% Offline)
1. **Pre-flight AST Gating**: Intercepts tool function arguments inside the Python/Node interpreter in under 35 microseconds. Blocks destructive shell commands (`rm -rf /`, `mkfs`), dangerous SQL statements (`DROP TABLE`, `TRUNCATE`), and dunder reflection exploits.
2. **In-Flight Secret Scrubbing**: Scrubs high-entropy credentials (AWS keys, GitHub PATs, JWTs, Stripe tokens) from tool arguments and stdout before they reach memory logs or LLM context.
3. **Law of Diminishing Marginal Utility (LDMU) Loop Damping**: Mathematically detects repetitive, low-value tool loops and clamps execution before agents burn runaway budgets.
4. **Offline Ed25519 & Merkle Receipts**: Every execution generates an RFC 8785 canonical hash and Ed25519 signature receipt that can be verified 100% offline without cloud roundtrips.

### 30-Second Quickstart

```bash
pip install btp-guard
```

```python
from btp_guard import Guard

guard = Guard(spend_cap=50.0, max_retries=5)

# Protect any agent tool or function with 1 line
@guard.protect
def execute_database_query(sql_query: str):
    return db.execute(sql_query)

# Testing a destructive tool call:
try:
    execute_database_query("DROP TABLE users CASCADE;")
except PermissionError as e:
    print("Intercepted in <35µs:", e)
```

For LangChain and CrewAI:
```python
from framework_adapters.langgraph.langgraph_btp_guard import btp_langchain_tool
from framework_adapters.crewai.crewai_btp_task_guard import btp_crewai_tool
```

### Pre-empting HN Questions:
- **"Why not just use Docker or gVisor?"**
  Docker isolates the host kernel, which is essential (Layer 3). But inside the container, an agent can still drop your database, leak your database credentials, or loop infinitely. Bartholomew acts at Layer 2 (in-process tool argument boundary). We actually provide a Docker Compose stack bundling both: `docker-compose -f docker-compose.defense-in-depth.yml up`.
- **"Can AST parsing be bypassed?"**
  Dynamic code execution (`eval()`, `exec()`, runtime reflection) is intercepted by our polyglot AST validator, which flags dynamic getattr and dunder access (`__subclasses__`). For native compiled C extensions, we recommend pairing with container isolation.
- **"What is the business model?"**
  The local Python and TypeScript core is open-source (Apache 2.0). The first 1,000 tool calls are completely free locally. We offer a Pro Tier ($49/mo) for cloud policy editing and an Enterprise Tier ($199/mo) for continuous SOC 2 Type II (CC6.1/CC7.2) automated audit evidence generation for teams undergoing security compliance reviews.

Would love feedback from anyone building autonomous agentic workflows in production!
```

---

## **2. Reddit Launch Strategy**

### **Target Subreddits:**
1. `r/LocalLLaMA` (Highly technical, security-focused)
2. `r/LangChain` (Developers actively experiencing agent crashes)
3. `r/Python` (Focus on AST inspection and sub-35µs performance)
4. `r/artificial` (High-level architectural discussions)

### **Reddit Post (for `r/LocalLLaMA` & `r/LangChain`)**
**Title:** `I built an open-source in-process safety gateway that halts destructive agent tool calls in <35µs`
**Hook:**
"Most AI guardrails operate outside the process (inspecting prompts with secondary LLM calls that take 1.5s). Once your agent decides to invoke a tool, prompt rails are blind.
I wrote `btp-guard` (Python + TypeScript) to evaluate raw tool parameters inside memory at the AST level. It catches `rm -rf`, SQL drops, credential leaks, and infinite loops in under 35 microseconds."

---

## **3. Twitter / X Launch Thread**

**Tweet 1:**
🚨 Prompt guardrails don't protect tool execution.
If your autonomous AI agent decides to run `rm -rf` or `DROP TABLE`, prompt filters have already completed their turn.
Today we're launching Bartholomew (BTP v3.0) — the in-process execution gateway for autonomous agents.
🧵👇

**Tweet 2:**
⚡ How it works:
Instead of making slow 1.5-second cloud proxy calls, Bartholomew evaluates tool arguments inside the Python/Node interpreter at the AST level in <35 microseconds.
Catches destructive shell scripts, SQL mutations, and leaked API keys *before* OS dispatch.

**Tweet 3:**
🔄 Runaway agent loops:
Agents get trapped in repetitive search or tool loops that rack up massive token bills.
BTP uses Law of Diminishing Marginal Utility (LDMU) mathematical decay to detect loop fatigue and halt runaway executions automatically.

**Tweet 4:**
🛡️ 1-Line Drop-in Middleware for @LangChainAI, @CrewAIInc, Microsoft AutoGen, and LlamaIndex:
`@btp_crewai_tool`
`@btp_langchain_tool`
`@btp_autogen_guard`
`@btp_llamaindex_tool`

**Tweet 5:**
🌐 Universal Cookbook for ALL Agents (Past, Present, Future & IDEs):
• Horizon 1: Existing legacy sidecars (HTTP & CLI proxy)
• Horizon 2: OpenAI, Anthropic, Gemini, TypeScript, Go, Rust
• Horizon 3: Sovereign Passports, ZK-Rollups, AWS Nitro Enclaves, L402 Micro-Escrows
• AI IDEs: Native rules for Cursor (.cursorrules), Windsurf (.windsurfrules), VS Code, Cline, Zed, and Antigravity!

**Tweet 6:**
📦 Available everywhere today:
• PyPI: `pip install btp-guard`
• npm: `npm install btp-guard` / `npx mcp-proxy-guard`
• GitHub Action: `uses: ivegotahunnitonit/bartholomew@v3`
• VS Code / Cursor: `bartholomew-guard-vscode-3.0.0.vsix`
• 100% Passing Tests: 2,717 / 2,717 verified
• Interactive Web Explorer: https://acn-26670.web.app/#universal-cookbook
• Github: https://github.com/ivegotahunnitonit/bartholomew
