# 📚 Bartholomew — Product & Technical Documentation

Welcome to the official technical documentation for **Bartholomew**, the sub-millisecond AI-Powered Observability and Security Engine.

---

## 🏗️ 1. Architecture Overview

Bartholomew combines a **native Golang daemon core** with high-level Python SDK bindings to deliver real-time AI agent trajectory evaluation:

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent Execution                       │
│    (LangChain, CrewAI, AutoGPT, LlamaIndex, Custom Python)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ @guard() Decorator / cURL
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Bartholomew Golang Native Daemon                │
│       (1.44 μs Latency | 775,935 ops/sec SIMD Regex)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
         ┌─────────────────────┴─────────────────────┐
         ▼                                           ▼
┌───────────────────────────┐           ┌───────────────────────────┐
│ OWASP LLM 2026 Kill-Switch│           │ Cryptographic Attestation │
│ (Scrub Keys, Block Loops) │           │ (SHA-256 PDF / SVG Badge) │
└───────────────────────────┘           └───────────────────────────┘
```

---

## ⚡ 2. Golang Core vs Legacy Standards

### Bartholomew vs Datadog
- **Datadog**: Captures HTTP request/response metrics. Cannot parse multi-step AI reasoning loops or evaluate step-by-step tool state changes.
- **Bartholomew**: Native trajectory step parser that inspects every thought, tool parameter, and response payload in **1.44 microseconds**.

### Bartholomew vs OpenTelemetry (OTel)
- **OpenTelemetry**: Provides standardized JSON/proto schemas for traces and spans. Does NOT inspect payload content for vulnerabilities.
- **Bartholomew**: Fully compatible with OTel spans while adding active real-time OWASP threat detection and secret scrubbing proxies.

### Bartholomew vs OWASP LLM Standards
- **OWASP LLM Top 10**: Defines security vulnerabilities theoretically.
- **Bartholomew**: Implements continuous, automated, sub-millisecond enforcement of all 10 OWASP LLM threat categories out-of-the-box.

---

## 💻 3. SDK & CLI Integration

### Python SDK (`@guard()`)
```python
from bartholomew_sdk import guard

@guard(api_key="age_live_your_key_here")
def run_agent_step(payload):
    # Trajectory data is automatically evaluated inline in 0.04 ms
    return agent.execute(payload)
```

### CLI Trajectory Linter
```bash
python agent_qa_guard.py audit trajectory.json --fail-on-vulnerability
```

### REST API Endpoint
```bash
curl -X POST https://bartholomew.ai/api/janitor/audit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer age_live_your_key_here" \
  -d '{
    "agent_name": "SupportBot",
    "steps": [
      { "type": "thought", "content": "Checking ledger..." },
      { "type": "tool_call", "tool_name": "query_db", "content": "SELECT * FROM users" }
    ]
  }'
```

---

## 🛡️ 4. OWASP LLM 2026 Rule Matrix

1. **LLM01: Prompt Injection**: Intercepts `ignore previous instructions` and system prompt override attempts.
2. **LLM02: Sensitive Info Disclosure**: Scrubs OpenAI (`sk-`), AWS (`AKIA`), GitHub (`ghp_`), Stripe, and RSA keys.
3. **LLM03: Supply Chain Risks**: Scans untrusted PyPI/npm imports in tool scripts.
4. **LLM04: Model DoS**: Intercepts unhandled silent exceptions (`except: pass`) and token budget explosions.
5. **LLM05: Improper Output Handling**: Prevents XSS / HTML injection vectors in responses.
6. **LLM06: Excessive Agency**: Blocks null tool IDs and unauthorized shell executions.
7. **LLM07: System Prompt Leakage**: Prevents exfiltration of base developer prompts.
8. **LLM08: Infinite Tool Loop**: Interrupts back-to-back duplicate tool call traps.
9. **LLM09: Overreliance**: Flags hallucinated API endpoints and false confidence scores.
10. **LLM10: Model Theft**: Prevents model extraction via repetitive probe queries.
