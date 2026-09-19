# Bartholomew Zero-Install Cloud Execution Gateway
### Protecting Grok (xAI), Muse, Meta AI (Llama), and Frontier Chatbots Without Any Extension

Bartholomew operates directly off the cloud infrastructure, providing sub-35 microsecond AST invariant gating, automated secret scrubbing, and Ed25519 attestation receipts **without requiring users or bots to download or install an IDE extension or local binaries**.

---

## 1. Architecture Overview

```
 [Grok Bot / Muse / Meta AI / Web Agent]
                   │
                   ▼ (HTTP / Webhook / REST / MCP)
      [Bartholomew Cloud Gateway]
      • Sub-35µs Polyglot AST Engine (Python, JS/TS, Go, Rust, Bash)
      • In-flight Secret & Token Redaction (OpenAI, AWS, GitHub PATs)
      • Ed25519 Attestation Ledger
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
      [ALLOW]             [DENY]
  Execute safe tool    Intercept & return
  with signed proof    mitigation receipt
```

### Public Endpoints:
- Cloud Engine: `https://bartolomew-cloud-engine-322603900775.us-central1.run.app`
- VM MCP Node: `http://35.222.210.105:8080`
- Domain Gateway: `https://gateway.bartholomew.info`

---

## 2. Integration Modes

### Mode A: 1-Click Drop-in Base URL (OpenAI / xAI / Meta AI Compatible)

If you are using an OpenAI-compatible SDK (Python `openai`, Node.js `openai`, or LangChain/LlamaIndex) with Grok or Meta AI models, you do not need to install Bartholomew locally. Simply point the `base_url` to the Bartholomew Cloud Gateway:

#### Python Example (Grok Bot via xAI API):
```python
from openai import OpenAI

# Zero-install: just point base_url to Bartholomew cloud gateway
client = OpenAI(
    api_key="xai-your-key-here",
    base_url="https://bartolomew-cloud-engine-322603900775.us-central1.run.app/v1"
)

# Every tool call is inspected in-flight before returning to your agent
response = client.chat.completions.create(
    model="grok-2-latest",
    messages=[{"role": "user", "content": "Clean up temporary logs"}],
    tools=[...]
)
# Dangerous tool calls (e.g., rm -rf, DROP TABLE, secret leaks) are automatically blocked.
```

#### Meta AI / Llama 3 Example:
```python
from openai import OpenAI

client = OpenAI(
    api_key="your-inference-api-key",
    base_url="https://bartolomew-cloud-engine-322603900775.us-central1.run.app/v1",
    default_headers={"X-Downstream-URL": "https://api.groq.com/openai/v1"}
)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Query production database"}],
    tools=[...]
)
```

---

### Mode B: Direct REST Tool Evaluation (`POST /v1/eval`)

For bots running on Discord, Slack, X, or serverless functions, make a standard HTTP POST request to evaluate any command, SQL query, or script before execution:

#### Request:
```bash
curl -X POST https://bartolomew-cloud-engine-322603900775.us-central1.run.app/v1/eval \
  -H "Content-Type: application/json" \
  -d '{
    "bot_type": "grok",
    "action": "execute_command",
    "arguments": {"command": "rm -rf /var/data"},
    "agent_id": "grok-bot-prod"
  }'
```

#### Response:
```json
{
  "allowed": false,
  "verdict": "DENY",
  "reason": "BTP-AST-001: Catastrophic shell pattern detected in SHELL source",
  "bot_type": "grok",
  "tool": "execute_command",
  "sanitized_arguments": {"command": "rm -rf /var/data"},
  "secret_scrubbed": false,
  "latency_us": 28.4,
  "receipt": {
    "attestation": {
      "verdict": "DENY",
      "nonce": "7c12f5a9...",
      "originating_agent": "grok-bot-prod"
    },
    "signature": "3a0b89..."
  }
}
```

---

### Mode C: Muse Workflows & Automation Webhooks (`POST /v1/webhooks/bot`)

Muse AI and event-driven automation platforms can configure Bartholomew as an automated webhook node. Before running any mutating step, Muse posts the event payload:

```json
{
  "event": "tool_execution",
  "bot": "muse",
  "tool": "database_migration",
  "payload": {
    "query": "TRUNCATE TABLE accounts;"
  },
  "agent_id": "muse-worker-node"
}
```

Bartholomew immediately returns `{ "allowed": false, "verdict": "DENY" }`, halting destructive pipeline executions before state is modified.

---

### Mode D: 1-Click Custom Action (OpenAPI Specification)

For Grok custom bots, Custom GPTs, and web platforms that support OpenAPI plugins:
1. Open your bot configuration dashboard.
2. In the "Actions" or "Tools" tab, enter the schema URL:
   `https://bartolomew-cloud-engine-322603900775.us-central1.run.app/openapi.json`
3. The `btp_evaluate_action` tool is immediately available to the model with zero code and zero local installations.

---

### Mode E: Remote Cloud Model Context Protocol (MCP)

Cloud-hosted agent environments supporting MCP can connect to Bartholomew over HTTP without downloading any package:
- **Protocol:** JSON-RPC 2.0 over HTTP
- **URL:** `https://bartolomew-cloud-engine-322603900775.us-central1.run.app/mcp`
- **Supported Tools:** `btp_guard_eval`, `btp_get_manifest`

---

## 3. Threat Interception Rules

Bartholomew inspects tool calls across all cloud bot integrations against these deterministic invariants:

| Category | Pattern Detected | Action |
|:---|:---|:---|
| **Destructive Filesystem** | `rm -rf`, `mkfs`, `dd if=`, `chmod 777 /` | DENY (<35µs) |
| **SQL Mutations** | `DROP TABLE`, `DROP DATABASE`, `TRUNCATE TABLE` | DENY (<35µs) |
| **Credential Leaks** | OpenAI keys, AWS keys, GitHub PATs, private keys | AUTO-SCRUB & REDACT |
| **Code Injection** | `base64 -d \| sh`, `eval()`, `os.system()` | DENY (<35µs) |
| **Spend Caps** | Runaway spend loops exceeding tenant limits | DENY & Escrow Halt |
