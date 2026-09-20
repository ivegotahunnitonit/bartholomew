# OpenAI Agents SDK & Function Calling Security Seam
**Bartholomew Trust Protocol (BTP v5.4.16)**

The OpenAI Agents SDK and OpenAI function calling orchestrate autonomous agent loops, tool dispatch, and multi-agent swarms. Bartholomew sits directly on the execution seam to verify AST safety, enforce spend limits, and block destructive operations before they reach your databases, shell, or file systems.

---

### Key Capabilities
- **Sub-Millisecond In-Process Inspection**: Evaluates tool names and parameters in `<40 µs` before execution.
- **Runaway Loop & Spend Protection**: Caps transaction spend and halts recursive retry loops before budgets are exhausted.
- **Cryptographic Ed25519 Receipts**: Emits signed, RFC 8785 canonical audit receipts for every allow/deny turn.
- **1-Line Drop-in Client Wrapper**: Wraps the OpenAI client with zero architectural refactoring.

---

### 1-Minute Quickstart

#### Installation
```bash
pip install btp-guard openai
```

#### Option A: Direct Tool Gating (`protect_tool_call`)
```python
from btp_guard import protect_tool_call

# Intercept tool call before running it
tool_name = "sql_query_tool"
tool_args = {"query": "SELECT id, email FROM users LIMIT 10;"}

result = protect_tool_call(tool_name, tool_args)
if result["status"] == "APPROVED":
    execute_tool(tool_name, tool_args)
else:
    print(f"Action blocked: {result['reason']}")
```

#### Option B: 1-Line Drop-in Client Wrapper (`BTPClientWrapper`)
```python
from openai import OpenAI
from btp_guard.client_wrapper import BTPClientWrapper, BTPViolationError

# Wrap your existing OpenAI client
client = BTPClientWrapper(OpenAI(), auto_raise=True)

# Responses containing dangerous tool calls are intercepted automatically:
try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Clean up database tables"}]
    )
except BTPViolationError as err:
    print(f"Blocked dangerous tool call {err.action_type}: {err.reason}")
```

---

### Running the Live Integration Demo
```bash
python examples/openai_agents_sdk_guard.py
```
