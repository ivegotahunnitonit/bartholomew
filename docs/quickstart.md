# Bartholomew Guard — Startup & Small Business Quickstart

> **The 30-second safety net for fast-moving startups, solo builders, and lean dev teams shipping AI agents to production.**

---

### Why Startups Need Bartholomew

Running autonomous AI agents (LangChain, CrewAI, AutoGen, Claude, or custom LLM scripts) without safety bounds is risky:
1. **Accidental Database Wipes**: An agent hallucinates a `DROP TABLE`, `TRUNCATE`, or destructive migration on customer data.
2. **Runaway Spend Loops**: An agent gets stuck in a retry loop overnight, draining $2,000+ from your OpenAI or cloud budget.
3. **Leaked Secrets**: Raw API keys, AWS credentials, or customer tokens dumped into public logs or prompt histories.
4. **Approval Bottlenecks**: You or your engineers are forced to manually click "Approve" 50 times a day, slowing down shipping.

**Bartholomew stops all of this locally in under 35 microseconds with zero slowdown.**

---

### Step 1: Install the Free Open-Source Library (30 seconds)

#### Python:
```bash
pip install btp-guard
```

#### Node.js / TypeScript:
```bash
npm install btp-guard
```

---

### Step 2: Protect Your Agent Functions (1 line of code)

Wrap your agent's database or execution functions with `@guard.protect`:

```python
from btp_guard import Guard

# 1. Initialize guard with a hard budget limit
guard = Guard(spend_cap=50.0, max_retries=5)

# 2. Protect your database or execution function
@guard.protect
def run_database_query(query: str):
    # Destructive SQL (DROP TABLE, TRUNCATE) is hard-blocked in <35 microseconds
    # before the query ever touches your database!
    return db.execute(query)

# 3. Protect shell / CLI execution
@guard.protect
def run_shell(command: str):
    # Catastrophic shell commands (rm -rf, config overwrites) are physically blocked
    return subprocess.run(command, shell=True, capture_output=True)
```

---

### Step 3: Use with Your Framework

#### CrewAI:
```python
from framework_adapters.crewai import btp_crewai_tool

@btp_crewai_tool(strict=True)
def execute_sql(query: str) -> str:
    return db.execute(query)
```

#### Microsoft AutoGen:
```python
from framework_adapters.autogen import btp_autogen_guard

@btp_autogen_guard
def run_command(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True).decode()
```

#### LangChain / LangGraph:
```python
from framework_adapters.langgraph import btp_langchain_tool

@btp_langchain_tool
def fetch_user_data(sql: str) -> str:
    return db.execute(sql)
```

---

### Step 4: AI IDE Rules (Cursor & VS Code)

Drop `.cursor/rules/btp-guard.mdc` into your repository or install via terminal:

```bash
code --install-extension Bartholomew.bartholomew-guard-vscode
# or in Cursor:
cursor --install-extension Bartholomew.bartholomew-guard-vscode
```

---

### Try the Live In-Browser Playground (5 seconds)

Want to see it in action without installing anything?  
Test preset attacks (`rm -rf`, `DROP TABLE`, credential leak) live in your browser:  
👉 **[https://bartholomew.info/cookbook](https://bartholomew.info/cookbook)**

---

### Simple, Transparent Pricing

| Tier | Price | Best For | What You Get |
| :--- | :--- | :--- | :--- |
| **Builder / OSS** | **$0** (Free Forever) | Indie builders & solo devs | Unlimited local evals, in-memory AST engine, IDE rules |
| **Pro Startup** | **$49 / month** | Startups & lean teams | 1M evals/mo, real-time secret scrubber, runaway spend caps, Slack threat alerts |
| **Team Fleet** | **$199 / month** | Scaling teams & agencies | Multi-tenant workspaces, SOC 2 Type II audit packs, dedicated CISO ledger |

* Direct Checkout: [Subscribe to Pro ($49/mo)](https://buy.stripe.com/fZu28rbNz5TYcmAddK9R600) &bull; [Subscribe to Team Fleet ($199/mo)](https://buy.stripe.com/fZu14ng3PgyC9ao2z69R601)
* Web Portal: [https://bartholomew.info](https://bartholomew.info)
