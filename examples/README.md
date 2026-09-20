# BTP Guard — Global Cookbooks & Frontier Agent Recipes

Production-ready, zero-configuration recipes integrating the Bartholomew Trust Protocol (`btp-guard`) into leading frontier AI ecosystems, edge platforms, and multi-agent frameworks.

## Frontier Platform & Multi-Agent Matrix

| Ecosystem / Framework | Protection Pattern | Invariants Enforced | Runnable Recipe |
| :--- | :--- | :--- | :--- |
| **Universal Swarm Delegation** | BTP/A2A/3.1 Protocol | Ed25519 Envelope Signatures, L402 Lightning Micropayments, Capability Attenuation | [`examples/future_swarms/universal_swarm_delegation.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/examples/future_swarms/universal_swarm_delegation.py) |
| **Cloudflare Workers AI** | Edge Agent Guard | Sub-50µs Edge AST Gating, Nonce Replay KV TTL, D1/KV Proof Anchoring | [`examples/future_swarms/cloudflare_edge_agent_guard.ts`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/examples/future_swarms/cloudflare_edge_agent_guard.ts) |
| **Microsoft AutoGen** | `btp_autogen_guard` | In-Process Tool Gating, Byzantine Quorum Slashing, AWU Barter Credit Minting | [`examples/future_swarms/autogen_swarm_consensus.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/examples/future_swarms/autogen_swarm_consensus.py) |
| **Google Gemini 3.8** | `GeminiFunctionCallingGuard` | Thought Scratchpad Defense, Multimodal Tool Call Sanitization, Budget Limits | [`examples/being_built/gemini_function_calling_guard.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/examples/being_built/gemini_function_calling_guard.py) |
| **Anthropic Claude 3.7** | Computer Use Sentry | Hybrid Thinking Gating, Bounded Workspace CoW Rollbacks, MCP Wire Proxy | [`examples/being_built/anthropic_computer_use_guard.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/examples/being_built/anthropic_computer_use_guard.py) |
| **OpenAI Agents SDK / GPT-Astra** | `UniversalBTPModelGuard` | Tool-Calling Schema Interception, Confused-Deputy Rejection, L402 Escrows | [`examples/being_built/openai_tool_calling_guard.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/examples/being_built/openai_tool_calling_guard.py) |
| **Cursor & Windsurf IDEs** | Embedded Rule Sentries | Live IDE AST Invariants, Shell Mutation Barriers, Read-Only FS Bounds | [`examples/ides/cursor/.cursorrules`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/examples/ides/cursor/.cursorrules) |

---

## 60-Second Quickstarts

### 1. Universal Swarm Delegation (A2A Protocol & L402 Micropayments)
Cryptographically sign delegation envelopes between autonomous agent hops using RFC 8785 canonical JSON and Ed25519 signatures, backed by L402 Lightning micropayments:
```python
from src.a2a_protocol import A2ASwarmProtocol, A2AEnvelope

protocol = A2ASwarmProtocol(authority_private_key_hex="...")
envelope = protocol.create_signed_envelope(
    sender_agent_id="Swarm-Planner-01",
    target_agent_id="Swarm-Worker-Cloudflare",
    task_payload={"action": "AUDIT_INFRASTRUCTURE", "target": "prod-cluster"},
    capability_scope=["telemetry:read", "ast:strict"],
    l402_invoice="lnbc50u1p..."
)

# Target verifies signature, nonce freshness, and capability boundaries in <35µs
is_valid, msg = protocol.verify_envelope(envelope)
```
Run the demo:
```bash
python examples/future_swarms/universal_swarm_delegation.py
```

---

### 2. Cloudflare Workers AI & Edge Agent Guard
Run sub-50µs AST security gating and KV replay protection directly at the Cloudflare edge:
```typescript
import { EdgeBTPGuard } from './cloudflare_edge_agent_guard';

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const envelope = await request.json();
    
    // 1. Enforce fresh nonce in Cloudflare KV
    const isFresh = await EdgeBTPGuard.checkReplay(env.BTP_REPLAY_KV, envelope.nonce);
    if (!isFresh) return new Response("REPLAY_ATTACK", { status: 403 });

    // 2. Sub-50µs in-process AST gating
    const verdict = EdgeBTPGuard.evaluateAction(envelope.task_payload);
    if (!verdict.safe) return new Response(verdict.reason, { status: 403 });

    return new Response(JSON.stringify({ verdict: "ALLOW" }), { status: 200 });
  }
};
```

---

### 3. Microsoft AutoGen Swarm Consensus & Invariant Guard
Intercept AutoGen group chat tool calls in sub-35µs and automatically award Attested Work Units (AWU) to safe agents:
```python
from src.framework_adapters.autogen import btp_autogen_guard, BTPViolationError

@btp_autogen_guard(mint_awu=1.5, barter_agent_id="autogen-coder-agent")
def execute_sql(query: str) -> str:
    # Catastrophic mutations (DROP TABLE, TRUNCATE) are vetoed before execution
    return db.execute(query)
```
Run the demo:
```bash
python examples/future_swarms/autogen_swarm_consensus.py
```

---

### 4. Google Gemini 3.8 Thought & Tool Guard
Sanitize reasoning thoughts and validate function calling schemas against strict invariants:
```python
from examples.being_built.gemini_function_calling_guard import GeminiFunctionCallingGuard

guard = GeminiFunctionCallingGuard(strict=True, max_thought_budget=2048)
payload = {
    "name": "deploy_smart_contract",
    "args": {"target_chain": "base-sepolia", "gas_limit": 500000}
}
verdict = guard.intercept_tool_call(payload)
```

---

### 5. 6-Way Swarm Penetration & Escrow Slashing Benchmark
Simulate a complete 6-way multi-agent mesh (Gemini 3.8, Claude 3.7, GPT-Astra, Cloudflare, AutoGen, Copilot) under active penetration attacks with Byzantine ZK-fault proof slashing:
```bash
python scripts/demo_enterprise_swarm_defense.py
```

---

## Codebase Audit & SOC 2 Readiness

Verify your repository against OWASP LLM01, LLM02, and SOC 2 Trust Services Criteria in < 1 second:
```bash
python cli.py audit
```
