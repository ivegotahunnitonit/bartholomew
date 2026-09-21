# LlamaIndex Quickstart: 1-Line Tool Safety & Spend Bounds

Stop worrying about autonomous LlamaIndex agents or text-to-SQL query engines hallucinating destructive database statements (`DROP TABLE`, `TRUNCATE`), traversing unapproved filesystem paths, or burning through API budgets during retrieval loops.

Bartholomew provides a zero-overhead decorator (`@btp_llamaindex_tool`) that protects your index queries and tools directly inside memory.

---

## 30-Second Setup

### 1. Install `btp-guard`
```bash
pip install btp-guard llama-index
```

### 2. Protect Your LlamaIndex Tools & Query Engines
Add `@btp_llamaindex_tool` directly to your tool definitions:

```python
from framework_adapters.llamaindex import btp_llamaindex_tool

@btp_llamaindex_tool(spend_cap=25.0, required_capability="db:query")
def query_vector_index(sql_or_query: str) -> str:
    """Executes dynamic SQL queries on vector databases or metadata stores."""
    # Your database query logic here...
    return db.query(sql_or_query)

@btp_llamaindex_tool(spend_cap=10.0, required_capability="tools:execute")
def document_reader_tool(file_path: str) -> str:
    """Loads external documents into LlamaIndex context."""
    # Your document loader logic here...
    return load_document(file_path)
```

---

## What Happens at Runtime?

When your LlamaIndex agent executes a tool call:

1. **Clean Queries Pass Instantly**: Standard embeddings and metadata queries execute with sub-25us latency.
2. **Accidental Drops Blocked**: If an LLM hallucinates `DROP TABLE documents` or `TRUNCATE table`, Bartholomew intercepts the argument in process memory and raises `BTPViolationError` before the database query fires.
3. **Destructive Shell Commands Blocked**: Recursive deletes (`rm -rf`) and path escapes are physically halted before execution.
4. **Spend Bounds**: Speeds up RAG development while ensuring loop retries don't spin up runaway API costs.

---

## Try the Executable Demo

Run our ready-to-use sample script:
```bash
python cookbook/already_built/llamaindex_agent_guard.py
```

Or test attacks live in your browser:
[https://bartholomew.info/cookbook](https://bartholomew.info/cookbook)

---

## Pricing for Startups & Small Teams

- **Core Engine**: 100% Free & Open-Source (Apache 2.0).
- **Sovereign Enterprise**: Unrestricted access to cloud telemetry, AST gating, and Keystone passkeys.
- **Fleet Tier**: $199/month for teams needing multi-agent cluster synchronization.
