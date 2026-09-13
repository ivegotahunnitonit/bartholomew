# OpenAI GPT-Astra & Agents SDK Security Seam
**Bartholomew Protocol (BTP v5.4.6)**

OpenAI's GPT-Astra reasoning family and the OpenAI Agents SDK orchestrate autonomous agent-to-agent loops. Bartholomew sits directly on the execution seam to verify AST safety, enforce spend limits, and block destructive file or SQL operations before they hit your machine.

---

### Key Capabilities
- **Agents SDK Seam Interception**: Normalizes `tool_name` and `tool_arguments` payloads natively.
- **Runaway Loop Protection**: Protects your budget with spend caps before unbounded agent loops burn tokens or run up invoices.
- **Micro-Escrow Settlement**: Optionally requires agents to stake performance bonds on high-stakes tool executions.

---

### 1-Minute Quickstart

```bash
pip install --upgrade btp-guard
```

```python
from framework_adapters.universal import UniversalBTPModelGuard, ModelProvider

guard = UniversalBTPModelGuard(
    spend_cap=25.0,
    strict=True
)

# Example OpenAI Agents SDK execution object
agents_sdk_call = {
    "tool_name": "database_write",
    "tool_arguments": {
        "query": "INSERT INTO transactions (user_id, amount) VALUES (42, 100.0);"
    }
}

result = guard.intercept_and_verify(agents_sdk_call, provider=ModelProvider.OPENAI_AGENTS_SDK)
print(f"[+] Status: {result['status']} in {result['latency_us']:.2f}us")
```
