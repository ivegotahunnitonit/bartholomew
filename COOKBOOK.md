# BTP Guard — The Universal Autonomous Agent Cookbook

> **The invariant, attestation, and financialized trust layer for every autonomous AI agent:**
> 1. **Already Built**: Black-box, proprietary, or legacy agents protected with *zero code modifications*.
> 2. **Being Built Right Now**: Direct SDK integrations across OpenAI, Anthropic Claude, Google Gemini, TypeScript, Go, and Rust.
> 3. **Agents of the Future**: Sovereign Digital Passports, Zero-Knowledge proofs, Hardware Enclaves (AWS Nitro / AMD SEV-SNP), and L402 automated micro-escrow slashing.

---

## The Universal Matrix: Which Recipe Do You Need?

| Your Agent's State | Framework / Model / Language | Architecture Pattern | Recipe Link |
| :--- | :--- | :--- | :--- |
| **Already Built** | Any HTTP/REST Containerized Agent | Drop-In Reverse Proxy Sidecar | [`cookbook/already_built/http_sidecar_proxy.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/already_built/http_sidecar_proxy.py) |
| **Already Built** | Any Executable / Python script | CLI Subprocess Gate | [`cookbook/already_built/cli_process_gate.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/already_built/cli_process_gate.py) |
| **Already Built** | Cursor / Claude Desktop / Windsurf | MCP Invariant Daemon | [`cookbook/already_built/cursor_claude_mcp_config.json`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/already_built/cursor_claude_mcp_config.json) |
| **Being Built** | OpenAI Function Calling (GPT-4o) | Function Dispatcher Guard | [`cookbook/being_built/openai_tool_calling_guard.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/being_built/openai_tool_calling_guard.py) |
| **Being Built** | Anthropic Claude & Computer Use | Tool Use / Bash Sandbox Block | [`cookbook/being_built/anthropic_computer_use_guard.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/being_built/anthropic_computer_use_guard.py) |
| **Being Built** | Google Gemini 1.5 / 2.0 | Function Calling Attestation | [`cookbook/being_built/gemini_function_calling_guard.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/being_built/gemini_function_calling_guard.py) |
| **Being Built** | Node.js / TypeScript | `btp-guard` npm Module | [`cookbook/being_built/typescript_node_agent.ts`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/being_built/typescript_node_agent.ts) |
| **Being Built** | Go Cloud Microservices | Ed25519 Native Gateway | [`cookbook/being_built/go_microservice_gate.go`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/being_built/go_microservice_gate.go) |
| **Being Built** | Rust Trading Bots / Low-Latency | Sub-5µs Invariant Engine | [`cookbook/being_built/rust_fast_path_guard.rs`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/being_built/rust_fast_path_guard.rs) |
| **Frameworks** | CrewAI Multi-Agent Swarms | `CrewAIBTPTaskGuard` | [`examples/crewai_secure_coding_swarm/run_swarm.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/examples/crewai_secure_coding_swarm/run_swarm.py) |
| **Frameworks** | LangGraph State Graphs | `LangGraphBTPGuard` | [`examples/langgraph_financial_analyst/run_workflow.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/examples/langgraph_financial_analyst/run_workflow.py) |
| **Frameworks** | AutoGen GroupChats | `AutoGenBTPInterceptor` + Entropy Rebalancer | [`examples/autogen_multiagent_defense/run_groupchat.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/examples/autogen_multiagent_defense/run_groupchat.py) |
| **Frameworks** | LlamaIndex RAG Engines | `@btp_llamaindex_tool` + AST Interceptor | [`examples/llamaindex_rag_guard/run_rag.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/examples/llamaindex_rag_guard/run_rag.py) |
| **Future Mesh** | Multi-Agent Swarms & DAOs | Sovereign Passports & Peer Discovery | [`cookbook/future_swarms/sovereign_agent_passport_mesh.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/future_swarms/sovereign_agent_passport_mesh.py) |
| **Future Mesh** | Enterprise Auditing & Regulators | Zero-Knowledge Session Proofs | [`cookbook/future_swarms/zk_privacy_auditing.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/future_swarms/zk_privacy_auditing.py) |
| **Future Mesh** | Cloud Confidential Computing | AWS Nitro / AMD SEV-SNP Enclave Anchor | [`cookbook/future_swarms/confidential_enclave_anchor.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/future_swarms/confidential_enclave_anchor.py) |
| **Future Mesh** | Autonomous Financial Settlements | L402 / EVM Automated Micro-Escrow Slashing | [`cookbook/future_swarms/l402_autonomous_escrow.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/future_swarms/l402_autonomous_escrow.py) |

---

## 1. Protecting "Already Built" Agents (Zero Code Changes)

If you have an existing autonomous agent running in production, in a Docker container, or as a compiled binary, **you do not need to modify its source code**.

### Recipe A: Universal HTTP Sidecar Proxy
Run the BTP Sidecar proxy alongside your agent:
```bash
python cookbook/already_built/http_sidecar_proxy.py
```
Direct your agent's outbound tool calls to `http://localhost:18080`. Malicious payloads (`rm -rf`, path traversal, SQL drops, key exfiltration) are vetoed at the HTTP layer with `403 Forbidden` before they ever reach your databases or APIs.

### Recipe B: CLI Process Gate
Wrap any command-line agent or script:
```bash
python -c "from cookbook.already_built.cli_process_gate import CLIProcessGate; CLIProcessGate.run_guarded_process(['python', 'my_legacy_agent.py'])"
```

### Recipe C: Cursor IDE & Claude Desktop MCP Hook
Add BTP Guard as a persistent MCP supervisor in `~/.codeium/windsurf/mcp_config.json` or Cursor Settings:
```json
{
  "mcpServers": {
    "btp-guard": {
      "command": "python",
      "args": ["-m", "mcp_server"]
    }
  }
}
```

---

## 2. AI IDEs & Developer Agent Environments

BTP Guard provides turnkey guardrails for all modern agentic coding environments:

| IDE / Environment | Guardrail Pattern | Setup Artifact | One-Line Installation |
| :--- | :--- | :--- | :--- |
| **Cursor IDE** | Background MCP Supervisor + `.cursorrules` | [`cookbook/ides/cursor/`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/ides/cursor/) | Drop `.cursorrules` into workspace root |
| **VS Code** | Packaged VSIX Extension + Settings | [`cookbook/ides/vscode/`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/ides/vscode/) | `code --install-extension vscode-extension/bartholomew-guard-vscode-3.0.0.vsix` |
| **Windsurf (Codeium)** | Cascade Agent Rules + MCP Gateway | [`cookbook/ides/windsurf/`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/ides/windsurf/) | Copy `.windsurfrules` into workspace root |
| **Cline / Roo Code** | Pre-authorized MCP Security Layer | [`cookbook/ides/cline_roo_code/`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/ides/cline_roo_code/) | Import `cline_mcp_settings.json` |
| **Zed Editor** | Context Server Assistant Protocol | [`cookbook/ides/zed/`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/ides/zed/) | Merge `zed_settings.json` into Zed config |
| **Antigravity IDE** | Customization System Skills & Rules | [`cookbook/ides/antigravity/`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/cookbook/ides/antigravity/) | Place in `.agents/rules/` or `AGENTS.md` |

---

## 3. Protecting Agents "Being Built Right Now"

### OpenAI Function Calling Guard
Wrap function execution dispatchers in 5 lines:
```python
from cookbook.being_built.openai_tool_calling_guard import OpenAIToolGuard

guard = OpenAIToolGuard()
guard.register_tool("execute_query", my_db_query_func)

# Intercepts arguments, blocks prompt injection, returns safe error block to LLM
response = guard.dispatch_tool_call(openai_tool_call)
```

### Anthropic Claude Computer Use & Bash Guard
Intercept Claude 3.5 / 3.7 Sonnet `tool_use` blocks:
```python
from cookbook.being_built.anthropic_computer_use_guard import AnthropicToolGuard

# Safely validates and returns tool_result block with is_error=True if violated
claude_tool_result = AnthropicToolGuard.execute_tool_block(tool_use_block)
```

### TypeScript / Node.js Agents
Install the official npm package:
```bash
npm install btp-guard
```
```typescript
import { TypeScriptAgentGuard } from './cookbook/being_built/typescript_node_agent';

const guard = new TypeScriptAgentGuard(TRUSTED_PUBKEY);
const { allowed, reason } = await guard.guardToolCall(toolCall);
```

---

## 4. Future-Proof Autonomous Swarms & Economic Networks

### Sovereign Digital Passports & Peer Discovery
Issue non-human cryptographic passports with Ed25519 signatures:
```python
from src.agent_passport import SovereignAgentPassport, AgentPeerDiscoveryRegistry

passport = SovereignAgentPassport(
    agent_id="Agent-01",
    worker_model="Claude-3.5-Sonnet",
    owner_pubkey=ROOT_KEY,
    granted_capabilities=["db:query", "fs:read"],
    bonded_warranty_balance_usd=25000.0
)
passport.sign(private_key)

# Query mesh for peers by capability
registry = AgentPeerDiscoveryRegistry()
registry.register_agent(passport)
available_peers = registry.discover_peers(required_capability="db:query")
```

### Zero-Knowledge Compliance Auditing
Generate privacy-preserving proofs that your agent obeyed safety policies without revealing private prompts or customer data:
```python
from src.zk_compliance_proof_engine import ZKComplianceEngine

engine = ZKComplianceEngine()
proof = engine.prove_session(session_id="sess_123", tool_calls=["query_balance", "export_pdf"])
receipt = proof.to_receipt()  # Contains zero plaintext; 100% mathematically verifiable
is_valid = engine.verify_proof(proof)  # True
```

### Autonomous L402 Micro-Escrow & Automated Slashing
Lock collateral before high-risk tasks and enable trustless, automated indemnity payouts upon attested failure:
```python
from src.settlement.autonomous_escrow import AutonomousEscrowPool

pool = AutonomousEscrowPool()
deposit = pool.lock_escrow(agent_id="Agent-01", action_type="TRANSACTION", amount_usd=1000.0)

# If regression proof is submitted, collateral is slashed instantly to claimant Lightning invoice
pool.claim_and_slash(deposit.escrow_id, regression_proof, payee_destination="lnbc...")
```
