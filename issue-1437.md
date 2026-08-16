## Bug Description

The Memanto REST API has **inconsistent authentication enforcement** — memory operations (`/api/v2/agents/{agent_id}/remember`, `/recall`, `/answer`, etc.) properly require a session token, but **all agent management endpoints and the status endpoint are accessible without any caller authentication**.

## Affected Endpoints

These endpoints use only `Depends(get_moorcheh_api_key)` or `Depends(verify_moorcheh_api_key)`, which merely checks whether the **server** has an API key configured — it does NOT authenticate the **caller**:

- `POST   /api/v2/agents` — Create new agents
- `GET    /api/v2/agents` — List all agents
- `GET    /api/v2/agents/{agent_id}` — Get agent details
- `DELETE /api/v2/agents/{agent_id}` — Delete agents
- `POST   /api/v2/agents/{agent_id}/activate` — Activate an agent and **obtain a valid session token**

Additionally, this endpoint has **zero authentication dependencies**:

- `GET    /api/v2/status` — Returns active session info including `agent_id`, `session_id`, `namespace`, `started_at`, `expires_at`

## Impact

1. **On on-prem deployments** (where `MOORCHEH_API_KEY` is not required), ALL agent management endpoints are completely unauthenticated. Any network-adjacent attacker (the server binds to `0.0.0.0:8000` by default, config.py line 126) can:
   - Enumerate all agents
   - Activate any existing agent to obtain a **valid session token**
   - Use that token to read/write/delete all memories for that agent

2. **On cloud deployments**, agent management is still unauthenticated — the `get_moorcheh_api_key()` dependency only verifies the server config has a key, not that the caller presents one.

3. **Information disclosure** via `/api/v2/status`: unauthenticated callers learn which agents are active and session details.

## Root Cause

In `memanto/app/routes/auth_deps.py`:

```python
def get_moorcheh_api_key() -> str:
    """..."""
    if parse_backend(settings.MEMANTO_BACKEND) == Backend.ON_PREM:
        return "on-prem"  # ← placeholder, no auth gate
    
    if settings.MOORCHEH_API_KEY:
        return settings.MOORCHEH_API_KEY  # ← returns server's key, does NOT verify caller
    ...
```

And in `memanto/app/routes/sessions.py` lines 268-290, the `/status` endpoint has no `Depends` at all.

Compare with memory operations in `memory.py` which all use `session: Session = Depends(get_current_session)`.

## Reproduction Steps

1. Start memanto server: `memanto serve` (or `uvicorn memanto.app.main:app`)

2. Without any authentication:
```bash
# List all agents — no auth required
curl http://localhost:8000/api/v2/agents

# Get active session info — no auth required  
curl http://localhost:8000/api/v2/status

# Create a new agent — no auth required
curl -X POST http://localhost:8000/api/v2/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "attacker-agent", "pattern": "tool"}'

# Activate an existing agent — no auth required, gets session token
curl -X POST http://localhost:8000/api/v2/agents/attacker-agent/activate

# Now use the returned session_token to access all memories
curl -X POST http://localhost:8000/api/v2/agents/attacker-agent/recall \
  -H "X-Session-Token: <token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "secrets"}'
```

## Suggested Fix

Apply `Depends(get_current_session)` (or a new caller-authentication dependency) to agent management endpoints, consistent with memory operation endpoints. At minimum, the `/status` endpoint should require authentication.

## Environment

- memanto version: latest `main`
- Server: bound to `0.0.0.0:8000` (default config)
- Backend: both cloud and on-prem affected; on-prem severity is higher

---
Found during the Memanto Bug Challenge (#770)