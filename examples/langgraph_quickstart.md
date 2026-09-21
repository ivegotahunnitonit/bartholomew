# LangGraph & LangChain Quickstart: 1-Line Tool Safety & Spend Bounds

Stop worrying about autonomous LangGraph agents and tool-calling chains hallucinating destructive database queries (`DROP TABLE`, `TRUNCATE`), executing unconstrained bash scripts, or burning through API budgets during infinite retry loops.

Bartholomew provides a zero-overhead decorator (`@btp_langchain_tool`) that protects your tools right inside process memory.

---

## 30-Second Setup

### 1. Install `btp-guard`
```bash
pip install btp-guard langchain-core langgraph
```

### 2. Protect Your LangChain / LangGraph Tools
Wrap your tool functions with `@btp_langchain_tool`:

```python
from langchain_core.tools import tool
from framework_adapters.langgraph import btp_langchain_tool

@tool
@btp_langchain_tool(spend_cap=50.0, action_type="sql_query")
def run_database_query(query: str) -> str:
    """Executes dynamic SQL on Snowflake, BigQuery, or PostgreSQL."""
    # Your database query logic here...
    return db.execute(query)

@tool
@btp_langchain_tool(spend_cap=10.0, action_type="cloud_cli")
def run_cloud_cli(command: str) -> str:
    """Executes cloud CLI or Terraform actions."""
    # Your cloud runner logic here...
    return subprocess.check_output(command, shell=True).decode()
```

---

## How It Protects Your LangGraph State Nodes

When your LangGraph workflow reaches a tool node:

1. **Microsecond Inspection**: Arguments are evaluated in microsecond time before execution.
2. **Deterministic Blocking**: Destructive patterns like `DROP TABLE` or `rm -rf` are immediately halted, raising `BTPViolationError` with structured diagnostics so your agent can adjust without corrupting state.
3. **In-Flight Secret Masking**: Credentials and API tokens (`OPENAI_API_KEY`, AWS tokens) are automatically scrubbed before hitting tool logs.
4. **Budget Protection**: Specifying `spend_cap` ensures unconstrained loops halt before racking up massive LLM or cloud bills.

---

## Try the Executable Demo

Run our ready-to-use sample script:
```bash
python cookbook/already_built/langgraph_agent_guard.py
```

Or test attacks live in your browser:
[https://bartholomew.info/cookbook](https://bartholomew.info/cookbook)

---

## Pricing for Startups & Small Teams

- **Core Engine**: 100% Free & Open-Source (Apache 2.0).
- **Sovereign Enterprise**: Unrestricted access to cloud telemetry, AST gating, and Keystone passkeys.
- **Fleet Tier**: $199/month for teams needing multi-agent cluster synchronization.
