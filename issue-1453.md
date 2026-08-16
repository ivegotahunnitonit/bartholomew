## Bug Report

**Version:** memanto v0.2.6  
**Environment:** Python 3.14.5, Linux, local REST API (`memanto serve`)

### Bug 1: Agent Creation Race Condition

When rapidly creating agents via `POST /api/v2/agents`, the API returns HTTP 200 for all requests, but only ~2 agents actually persist (Community plan limit).

**Repro:**
```bash
for i in {1..50}; do
  curl -s -X POST http://localhost:8001/api/v2/agents \
    -d "{\"agent_id\": \"test-$i\", \"pattern\": \"tool\"}" &
done
curl -s http://localhost:8001/api/v2/agents | jq '.count' # Returns 2