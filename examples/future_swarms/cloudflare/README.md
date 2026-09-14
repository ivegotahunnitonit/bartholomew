# Bartholomew Cloudflare Workers AI & Edge Agent Guard (BTP v5.4.12)

Sub-50 microsecond AST invariant enforcement and A2A cryptographic delegation gate running on Cloudflare's global edge network across 300+ cities.

---

## Capabilities

1. **Sub-50µs Edge Invariant Gating**: Intercepts destructive SQL, system wipes, and arbitrary code execution at Cloudflare's edge before reaching origin APIs or backends.
2. **Zero Remote Cloud Token Spend**: Evaluates AST rules purely in V8 isolates without calling external LLM guardrails.
3. **KV-Backed Nonce Replay Protection**: Blocks replayed agent envelopes using Cloudflare KV with automated TTL expiration.
4. **Agent-to-Agent (A2A) Support**: Verifies RFC 8785 canonical envelopes and temporal skew windows.

---

## 1-Click Deployment

```bash
cd examples/future_swarms/cloudflare

# Local edge simulation
npx wrangler dev

# Production deployment to Cloudflare's global network
npx wrangler deploy
```

---

## API Endpoints

### 1. Edge Health Check
```bash
curl https://btp-edge-guard.<your-subdomain>.workers.dev/health
```
Response:
```json
{
  "service": "Bartholomew Edge Security Gate",
  "status": "healthy",
  "runtime": "cloudflare-workers-ai",
  "protocol": "BTP/A2A/3.1",
  "edge_guard": "ACTIVE",
  "sub_50us_ast_eval": true
}
```

### 2. Dispatch Tool Evaluation (`POST /guard/dispatch`)

#### Safe Request:
```bash
curl -X POST https://btp-edge-guard.<your-subdomain>.workers.dev/guard/dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "protocol": "BTP/A2A/3.1",
    "sender_agent": "cloudflare-worker-01",
    "target_agent": "database-executor",
    "timestamp": 1789344000,
    "nonce": "a1b2c3d4e5f60718",
    "task_payload": { "command": "SELECT id, email FROM users WHERE id = 42;" },
    "capability_scope": ["db:read"]
  }'
```
Response:
```json
{
  "verdict": "ALLOW",
  "protocol": "BTP/A2A/3.1",
  "nonce": "a1b2c3d4e5f60718",
  "sender": "cloudflare-worker-01",
  "target": "database-executor",
  "edge_latency_us": 38
}
```

#### Malicious Request (Blocked in <50µs):
```bash
curl -X POST https://btp-edge-guard.<your-subdomain>.workers.dev/guard/dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "protocol": "BTP/A2A/3.1",
    "sender_agent": "malicious-worker",
    "target_agent": "database-executor",
    "timestamp": 1789344000,
    "nonce": "deadbeef12345678",
    "task_payload": { "command": "DROP TABLE users CASCADE;" },
    "capability_scope": ["db:write"]
  }'
```
Response:
```json
{
  "verdict": "VETO",
  "error": "SECURITY_VETO: Edge AST rule matched forbidden invariant: /DROP\\s+(TABLE|DATABASE|SCHEMA)/i",
  "cloud_token_spend_usd": 0.0,
  "evaluation_tier": "Cloudflare Edge Sub-50us Gate"
}
```
