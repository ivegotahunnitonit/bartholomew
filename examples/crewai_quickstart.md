# CrewAI Quickstart: 1-Line Tool Safety & Spend Bounds

Stop worrying about autonomous CrewAI agents hallucinating dangerous shell commands (`rm -rf`), wiping database tables (`DROP TABLE`), or triggering runaway API loops while running unattended.

Bartholomew provides a zero-overhead, in-process decorator (`@btp_crewai_tool`) that inspects all arguments in microsecond time before execution.

---

## 30-Second Setup

### 1. Install `btp-guard`
```bash
pip install btp-guard crewai
```

### 2. Protect Your CrewAI Tools
Add `@btp_crewai_tool` directly to your tool definitions:

```python
from crewai.tools import tool
from framework_adapters.crewai import btp_crewai_tool

@tool("Production SQL Runner")
@btp_crewai_tool(spend_cap=25.0, action_type="sql_query")
def execute_sql(query: str) -> str:
    """Executes analytics SQL queries against production databases."""
    # Your database query logic here...
    return db.query(query)

@tool("Terminal Execution Tool")
@btp_crewai_tool(spend_cap=5.0, action_type="bash_exec")
def execute_shell(command: str) -> str:
    """Executes approved terminal operations."""
    # Your shell runner logic here...
    return subprocess.check_output(command, shell=True).decode()
```

---

## What Happens at Runtime?

When your CrewAI agent decides to call a tool:

1. **Safe Calls Pass Instantly**: Normal SQL queries and standard shell commands execute with sub-25us latency.
2. **Accidental Drops Blocked**: If an LLM hallucinates `DROP TABLE customers` or `TRUNCATE orders`, Bartholomew intercepts the argument in process memory and raises `BTPViolationError` before the database connection is even opened.
3. **Destructive Shell Commands Blocked**: Recursive deletes (`rm -rf`), formatting, or disk wipes are physically halted before reaching your operating system.
4. **Budget Protections**: If an agent enters an infinite retry loop, your specified `spend_cap` halts execution before inflating your model or cloud bill.

---

## Try the Executable Demo

Run our ready-to-use sample script:
```bash
python cookbook/already_built/crewai_agent_guard.py
```

Or test attacks live in your browser with zero setup:
[https://bartholomew.info/cookbook](https://bartholomew.info/cookbook)

---

## Pricing for Startups

- **Core Engine**: 100% Free & Open-Source (Apache 2.0).
- **Sovereign Enterprise**: Unrestricted access to cloud telemetry, AST gating, and Keystone passkeys.
- **Fleet Tier**: $199/month for teams needing multi-agent cluster synchronization.
