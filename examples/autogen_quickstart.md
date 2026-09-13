# Microsoft AutoGen Quickstart: 1-Line Tool Safety & Spend Bounds

Stop worrying about autonomous AutoGen agents hallucinating dangerous shell commands (`rm -rf`), wiping database tables, or draining API budgets during unconstrained multi-agent dialogue loops.

Bartholomew provides a zero-overhead decorator (`@btp_autogen_guard`) that protects your tools and code executors in microseconds before execution.

---

## 30-Second Setup

### 1. Install `btp-guard`
```bash
pip install btp-guard pyautogen
```

### 2. Protect Your AutoGen Tools & Functions
Add `@btp_autogen_guard` directly to functions registered with your AutoGen agents:

```python
from framework_adapters.autogen import btp_autogen_guard

@btp_autogen_guard(spend_cap=20.0, strict=True)
def run_code_tool(code: str) -> str:
    """Executes Python or bash scripts on behalf of AutoGen agents."""
    # Your execution logic here...
    return execute_in_sandbox(code)

@btp_autogen_guard(spend_cap=50.0, strict=True)
def run_db_migration(sql_script: str) -> str:
    """Applies schema migrations to staging or production."""
    # Your migration logic here...
    return db.execute(sql_script)
```

---

## What Happens at Runtime?

When your AutoGen agent generates code or calls a registered tool:

1. **Clean Code Passes Instantly**: Standard computations and queries execute with sub-25us latency.
2. **Destructive Shell Commands Blocked**: Recursive wipes (`rm -rf`) and system file modifications are intercepted and halted before the OS executes them.
3. **Accidental Database Drops Blocked**: Dangerous queries (`DROP TABLE`, `DROP SCHEMA`) raise `BTPViolationError` before touching your database.
4. **Budget Protection**: Speeds up development while ensuring multi-agent conversational loops don't spin up infinite compute.

---

## Try the Executable Demo

Run our ready-to-use sample script:
```bash
python cookbook/already_built/autogen_agent_guard.py
```

Or test attacks live in your browser:
[https://bartholomew.info/cookbook](https://bartholomew.info/cookbook)

---

## Pricing for Startups & Small Teams

- **Core Engine**: 100% Free & Open-Source (Apache 2.0).
- **Pro Tier**: $49/month for growing startups needing team metrics and cloud telemetry.
- **Fleet Tier**: $199/month for teams needing multi-agent cluster synchronization.
