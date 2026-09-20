---
name: bartholomew-guard
description: Provides local invariant checking, multi-tenant workspace management, sub-35µs AST gating, and autonomous escrow slashing via Bartholomew Trust Protocol (BTP).
---

# Bartholomew Trust Protocol (BTP) Agent Skill

This skill allows the agent to interact with Bartholomew's sub-35µs local security engine, query real-time threat entropy, issue scoped tenant API keys, and enforce cryptographic safety invariants.

## Active Workspace Configuration
- **Organization**: `bartholomew-core`
- **Project**: `antigravity-dev`
- **Environment**: `dev`
- **Tenant Hash**: `1d295f19eeff`
- **Scoped API Key**: `btp_test_571f54a8837a284242636a87c1dd3025`
- **Local Daemon**: `http://127.0.0.1:9090`

## Common Operations

### 1. Check Local Daemon Health & Telemetry
```bash
curl http://127.0.0.1:9090/healthz
curl http://127.0.0.1:9090/api/v1/telemetry
```

### 2. Workspace Management
```bash
# List all active multi-tenant workspaces
python cli.py workspace list

# Create a new isolated workspace
python cli.py workspace create --org-id <org> --project-id <proj> --env <prod|staging|dev> --name "<name>"

# Generate a new scoped API key
python cli.py workspace keygen --tenant-id <tenant_hash>
```

### 3. Universal Python Execution Gating
```python
from framework_adapters.universal.universal_model_guard import btp_universal_guard

@btp_universal_guard(
    agent_id="antigravity-worker-01",
    org_id="bartholomew-core",
    project_id="antigravity-dev",
    environment="dev"
)
def execute_safe_action(tool_name: str, tool_args: dict):
    # Monitored and gated by Bartholomew
    pass
```

### 4. Autonomous Escrow & Slashing Pool
```bash
# Lock collateral
python cli.py escrow lock --agent-id <agent_id> --amount-usd 100.00

# Inspect escrow status
python cli.py escrow status --escrow-id <escrow_id>
```
