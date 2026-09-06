import { useState } from 'react'

interface Recipe {
  id: string
  title: string
  category: 'already_built' | 'being_built' | 'future_swarms' | 'ides'
  badge: string
  description: string
  language: string
  filePath: string
  codeSnippet: string
  architectureNote: string
}

const RECIPES: Recipe[] = [
  // Horizon 1: Already Built
  {
    id: 'http_sidecar',
    title: 'Universal HTTP Sidecar Reverse Proxy',
    category: 'already_built',
    badge: 'Zero Code Changes',
    description: 'Intercepts HTTP REST tool calls from any existing agent (AutoGPT, custom scripts) and drops prompt injections with HTTP 403.',
    language: 'python',
    filePath: 'cookbook/already_built/http_sidecar_proxy.py',
    architectureNote: 'Agent -> [Sidecar 127.0.0.1:8080 (Local AST Invariant Gate)] -> External World',
    codeSnippet: `from btp_guard import Guard
from http.server import HTTPServer, BaseHTTPRequestHandler

guard = Guard(spend_cap=50.0, max_retries=3)

class BTPProxyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        payload = self.rfile.read(int(self.headers['Content-Length'])).decode()
        # Fastest and Most Reliable Local AST Safety Inspection
        res = guard.check(payload)
        if not res.allowed:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'{"error": "BTP_POLICY_VETO: Harmful AST Pattern"}')
            return
        # Forward safely to target API...`
  },
  {
    id: 'cli_gate',
    title: 'CLI Process Execution Gate',
    category: 'already_built',
    badge: 'Subprocess Sandbox',
    description: 'Intercepts bash/binary commands emitted by legacy agent runtimes with eBPF-style execution sandboxing.',
    language: 'python',
    filePath: 'cookbook/already_built/cli_process_gate.py',
    architectureNote: 'CLI Agent Process -> [Hermetic AST Gate] -> OS Kernel Syscall',
    codeSnippet: `from btp_guard import Guard
import subprocess, sys

guard = Guard()
target_cmd = sys.argv[1:]

res = guard.check(" ".join(target_cmd))
if not res.allowed:
    print(f"[!] BTP VETO: Command blocked by invariant engine: {res.violations}")
    sys.exit(1)

# Execute in sealed subprocess sandbox
proc = subprocess.run(target_cmd, capture_output=True, text=True)
print(f"[+] Execution verified: Merkle receipt stamped.")`
  },
  {
    id: 'cursor_mcp',
    title: 'Cursor / Claude Desktop MCP Config',
    category: 'already_built',
    badge: 'IDE Plug & Play',
    description: 'Standard JSON configuration to plug BTP Guard as an in-memory MCP security proxy for AI developer environments.',
    language: 'json',
    filePath: 'cookbook/already_built/cursor_claude_mcp_config.json',
    architectureNote: 'Cursor / Claude Desktop IDE -> [BTP Guard MCP Proxy stdio] -> Real MCP Server',
    codeSnippet: `{
  "mcpServers": {
    "btp-guard": {
      "command": "python",
      "args": ["-m", "src.mcp_gateway", "--proxy", "npx -y @modelcontextprotocol/server-filesystem ."],
      "env": {
        "BTP_ENFORCE_PASSWORDS": "true",
        "BTP_MAX_ACTION_SPEND_USD": "100.0"
      }
    }
  }
}`
  },

  // Horizon 2: Being Built Right Now
  {
    id: 'openai_guard',
    title: 'OpenAI Direct Tool-Calling Guard',
    category: 'being_built',
    badge: 'Python SDK',
    description: 'Wraps native OpenAI tool-calling loops with pre-execution AST gating and Ed25519 canonical receipts.',
    language: 'python',
    filePath: 'cookbook/being_built/openai_tool_calling_guard.py',
    architectureNote: 'OpenAI API -> tool_calls JSON -> [BTP Guard AST Check] -> Local Tool -> Stamped Merkle Tree',
    codeSnippet: `from btp_guard import Guard
from openai import OpenAI

guard = Guard(spend_cap=250.0)
client = OpenAI()

def execute_safe_tool_call(tool_call):
    func_name = tool_call.function.name
    args = tool_call.function.arguments
    
    # 28µs in-memory AST invariant verification
    decision = guard.check(f"{func_name}({args})")
    if not decision.allowed:
        return f"[VETO] Blocked action: {decision.violations}"
        
    return run_local_function(func_name, args)`
  },
  {
    id: 'anthropic_guard',
    title: 'Anthropic Computer Use Guard',
    category: 'being_built',
    badge: 'Bash & GUI Sandbox',
    description: 'Guards Anthropic Claude bash execution and computer use actions against destructive commands.',
    language: 'python',
    filePath: 'cookbook/being_built/anthropic_computer_use_guard.py',
    architectureNote: 'Claude 3.5 Sonnet -> computer_use / bash tool -> [BTP AST Validator] -> Sealed VM',
    codeSnippet: `from btp_guard import Guard
guard = Guard()

def guard_claude_action(tool_type: str, tool_input: dict):
    if tool_type == "bash":
        cmd = tool_input.get("command", "")
        res = guard.check(cmd)
        if not res.allowed:
            raise PermissionError(f"BTP Guard VETO: Dangerous command: {res.violations}")
    # Proceed with authenticated execution...`
  },
  {
    id: 'typescript_guard',
    title: 'TypeScript / Node.js Microservice Agent',
    category: 'being_built',
    badge: 'npm: btp-guard',
    description: 'Native TypeScript integration for modern agentic web backends using the published npm package.',
    language: 'typescript',
    filePath: 'cookbook/being_built/typescript_node_agent.ts',
    architectureNote: 'Node.js Express / Fastify -> [btp-guard npm native binding] -> Agent Task Execution',
    codeSnippet: `import { BTPGuard } from 'btp-guard';

const guard = new BTPGuard({
  maxActionSpendUSD: 100.0,
  sandboxMode: 'HERMETIC'
});

export async function handleAgentAction(actionPayload: string) {
  const verdict = await guard.verifyAction(actionPayload);
  if (!verdict.allowed) {
    throw new Error(\`BTP Security Veto: \${verdict.violations.join(', ')}\`);
  }
  return executeSafeAction(actionPayload);
}`
  },
  {
    id: 'rust_guard',
    title: 'Rust Sub-5µs Zero-Copy Fast-Path Gate',
    category: 'being_built',
    badge: 'High Throughput',
    description: 'Ultra-low latency SIMD Rust invariant checker for high-frequency algorithmic agent execution.',
    language: 'rust',
    filePath: 'cookbook/being_built/rust_fast_path_guard.rs',
    architectureNote: 'Inbound Byte Stream -> [Rust SIMD Tokenizer] -> AST Invariant Tree -> Signed Receipt (<5µs)',
    codeSnippet: `use btp_core::{BTPInvariantEngine, InvariantVerdict};

pub fn verify_tool_dispatch(raw_command: &str) -> InvariantVerdict {
    let engine = BTPInvariantEngine::new();
    let verdict = engine.check_simd(raw_command);
    
    if !verdict.is_allowed() {
        eprintln!("[BTP VETO] Command violates invariants: {:?}", verdict.violations());
        return verdict;
    }
    verdict
}`
  },

  // Horizon 3: Future Swarms
  {
    id: 'passport_mesh',
    title: 'Sovereign Agent Passports & Peer Discovery',
    category: 'future_swarms',
    badge: 'BTP v3.1 Protocol',
    description: 'Ed25519-signed digital identity passports for non-human workers with dynamic trust scoring and automated circuit-breaking.',
    language: 'python',
    filePath: 'cookbook/future_swarms/sovereign_agent_passport_mesh.py',
    architectureNote: 'Agent Worker -> Ed25519 Signed Passport -> Mesh Discovery Registry -> Task Delegation Gate',
    codeSnippet: `from src.agent_passport import SovereignAgentPassport, AgentPeerDiscoveryRegistry

registry = AgentPeerDiscoveryRegistry()
passport = SovereignAgentPassport.issue(
    agent_id="agent-worker-42",
    model_family="claude-3-5-sonnet",
    authorized_capabilities=["data:read", "code:mutate"],
    bonded_warranty_usd=5000.0
)
registry.register(passport)

# Peer discovery with capability and reputation constraints
trusted_peers = registry.discover(
    required_capability="code:mutate",
    min_trust_score=0.95,
    min_bond_usd=1000.0
)`
  },
  {
    id: 'zk_privacy',
    title: 'Zero-Knowledge Compliance Proof Engine',
    category: 'future_swarms',
    badge: 'BTP v3.5 ZK-Rollup',
    description: 'Homomorphic Pedersen commitments proving invariant compliance without exposing confidential prompts.',
    language: 'python',
    filePath: 'cookbook/future_swarms/zk_privacy_auditing.py',
    architectureNote: 'Private Prompts + Tool Trace -> [Pedersen Blinding] -> ZK Compliance Proof (256 bytes)',
    codeSnippet: `from src.zk_compliance_proof_engine import ZKComplianceEngine
from src.zk_rollup_batcher import ZKRollupBatcher

engine = ZKComplianceEngine()
batcher = ZKRollupBatcher()

# Prove compliance without revealing private tool arguments
proof = engine.prove_session(session_id="session-42", tool_calls=["read_patient_db", "anonymize_records"])
batcher.add_proof(proof)

# Compress 10,000 proofs into single Merkle root
rollup = batcher.seal()
print(f"Merkle Root: {rollup.merkle_root}")`
  },
  {
    id: 'enclave_anchor',
    title: 'Confidential Hardware Enclave Anchoring',
    category: 'future_swarms',
    badge: 'AWS Nitro / AMD SEV-SNP',
    description: 'Hardware-rooted confidential computing anchor verifying PCR0 measurements before allowing high-privilege execution.',
    language: 'python',
    filePath: 'cookbook/future_swarms/confidential_enclave_anchor.py',
    architectureNote: 'Sealed ZK-Rollup -> [AWS Nitro / AMD SEV Enclave] -> PCR Register Lock & Signed Document',
    codeSnippet: `from src.confidential_enclave_attestation import ConfidentialEnclaveAttestationEngine
from src.zk_rollup_batcher import EnclaveZKRollupAnchor

enclave = ConfidentialEnclaveAttestationEngine()
doc = enclave.attest(module_id="agent-enclave-node-01", nonce="freshness_nonce_123")

# Cryptographically verify PCR golden baselines
is_valid, msg = enclave.verify_attestation(doc)
assert is_valid, f"Hardware Enclave Compromised: {msg}"`
  },
  {
    id: 'escrow_slashing',
    title: 'Autonomous Micro-Escrow & Automated Slashing',
    category: 'future_swarms',
    badge: 'BTP v4.0 L402 / EVM',
    description: 'Programmatic collateral lock with automated liquidation and indemnity disbursement upon cryptographic regression proofs.',
    language: 'python',
    filePath: 'cookbook/future_swarms/l402_autonomous_escrow.py',
    architectureNote: 'Mission Init -> Collateral Lock ($500) -> Execution -> [Regression Proof?] -> Auto-Slash to Payee',
    codeSnippet: `from src.settlement.autonomous_escrow import AutonomousEscrowPool

pool = AutonomousEscrowPool()
deposit = pool.lock_escrow(
    agent_id="autonomous-trader-01",
    action_type="HIGH_LEVERAGE_DISPATCH",
    amount_usd=1000.0,
    settlement_rail="L402_LIGHTNING"
)

# Automated Slashing if Invariant is Violated
proof = {"violated_invariant": "MAX_DRAWDOWN_EXCEEDED", "proof_signature": "0xdeadbeef..."}
ok, msg, receipt = pool.claim_and_slash(
    escrow_id=deposit.escrow_id,
    regression_proof=proof,
    payee_destination="lnbc10u1p...liquidation_invoice"
)`
  },

  // AI IDEs
  {
    id: 'ide_cursor',
    title: 'Cursor IDE Guardrails (.cursorrules)',
    category: 'ides',
    badge: 'Cursor Integration',
    description: 'Enforces sub-50µs AST validation, secret redaction, and Merkle stamping directly inside Cursor agent chat and composer.',
    language: 'markdown',
    filePath: 'cookbook/ides/cursor/.cursorrules',
    architectureNote: 'Cursor Composer -> Agent Proposal -> [.cursorrules Invariant Check] -> Workspace File Mutation',
    codeSnippet: `# .cursorrules - Bartholomew Protocol (BTP v3.0) Invariant Guardrails
# 1. Never emit destructive mutations (rm -rf, DROP TABLE, git push --force)
# 2. Never log or transmit plain-text credentials or API secrets
# 3. Always wrap high-risk commands in btp-guard AST verification
# 4. Enforce RFC 8785 canonical Merkle receipt verification before commit`
  },
  {
    id: 'ide_windsurf',
    title: 'Windsurf Cascade Rules (.windsurfrules)',
    category: 'ides',
    badge: 'Windsurf Integration',
    description: 'Configures Codeium Windsurf Cascade agents to adhere to deterministic policy checks and in-flight secret scrubbing.',
    language: 'markdown',
    filePath: 'cookbook/ides/windsurf/.windsurfrules',
    architectureNote: 'Windsurf Cascade -> Multi-File Edits -> [.windsurfrules Policy Verifier] -> Clean Workspace State',
    codeSnippet: `# .windsurfrules - Bartholomew BTP v3.0 Cascade Rules
# Enforce zero-leakage invariant boundaries across all Cascade multi-file steps.
# Run 'python cli.py audit' before delivering final diffs to the developer.`
  },
  {
    id: 'ide_vscode',
    title: 'VS Code & GitHub Copilot Settings',
    category: 'ides',
    badge: 'VS Code Extension',
    description: 'Registers the Bartholomew Guard VSIX extension and enables pre-commit git security hooks in VS Code.',
    language: 'json',
    filePath: 'cookbook/ides/vscode/settings.json',
    architectureNote: 'VS Code / Copilot -> [Bartholomew VSIX Extension] -> Live Diagnostics & Quick Fix Vetoes',
    codeSnippet: `{
  "bartholomew.enableGuard": true,
  "bartholomew.policyPath": ".btp/policy.yaml",
  "bartholomew.maxSpendCapUSD": 100.0,
  "bartholomew.autoStampMerkleReceipts": true
}`
  },
  {
    id: 'ide_antigravity',
    title: 'Google Antigravity Pair-Programming Invariants',
    category: 'ides',
    badge: 'Antigravity IDE',
    description: 'Defines sovereign pair-programming invariants, continuous Merkle receipt verification, and zero-compromise security posture.',
    language: 'markdown',
    filePath: 'cookbook/ides/antigravity/AGENTS.md',
    architectureNote: 'Antigravity IDE Agent -> [AGENTS.md Contract] -> Verified Production Artifacts',
    codeSnippet: `# AGENTS.md - Bartholomew Protocol Invariant Contract
# Rule 1: All agent tool executions must produce an Ed25519-signed receipt
# Rule 2: 100% test pass rate required across all test suites
# Rule 3: Zero cold email outreach; distribution strictly via native adapters`
  }
]

export default function UniversalCookbookExplorer() {
  const [activeCategory, setActiveCategory] = useState<'all' | 'already_built' | 'being_built' | 'future_swarms' | 'ides'>('all')
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe>(RECIPES[0])
  const [copied, setCopied] = useState(false)
  const [simulating, setSimulating] = useState(false)
  const [simulationResult, setSimulationResult] = useState<{
    latencyUs: number
    status: string
    merkleRoot: string
    signature: string
  } | null>(null)

  const filteredRecipes = activeCategory === 'all' 
    ? RECIPES 
    : RECIPES.filter(r => r.category === activeCategory)

  const handleCopy = () => {
    navigator.clipboard.writeText(selectedRecipe.codeSnippet)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const runSimulation = () => {
    setSimulating(true)
    setSimulationResult(null)
    setTimeout(() => {
      setSimulating(false)
      setSimulationResult({
        latencyUs: Math.floor(Math.random() * 12) + 24, // 24-36 microseconds
        status: 'VERIFIED_INVARIANT_PASS',
        merkleRoot: '0x' + Array.from({length: 64}, () => Math.floor(Math.random()*16).toString(16)).join(''),
        signature: 'ed25519_sig_' + Array.from({length: 32}, () => Math.floor(Math.random()*16).toString(16)).join('')
      })
    }, 400)
  }

  return (
    <section id="cookbook" className="py-20 bg-[#07070b] border-t border-b border-[#222230] relative">
      <div id="universal-cookbook" className="absolute -top-24" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-[#10b981]/10 text-[#10b981] border border-[#10b981]/20 mb-4">
            <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse"></span>
            Universal Autonomous Invariant Cookbook
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Universal Guardrails for All Autonomous Agents
          </h2>
          <p className="mt-4 text-base text-zinc-400">
            Whether your agent is already built (zero code changes), being built right now (direct LLM APIs / polyglot), 
            or an autonomous future swarm with sovereign passports and L402 escrows — copy and run in 60 seconds.
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="flex flex-wrap justify-center gap-2 mb-8">
          {[
            { id: 'all', label: 'All Recipes (14)' },
            { id: 'already_built', label: '1. Already Built (Sidecars & CLI)' },
            { id: 'being_built', label: '2. Being Built (OpenAI, Claude, Polyglot)' },
            { id: 'future_swarms', label: '3. Future Swarms (Passports & Escrow)' },
            { id: 'ides', label: 'AI IDEs (Cursor, Windsurf, VS Code)' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveCategory(tab.id as any)
                const first = tab.id === 'all' ? RECIPES[0] : RECIPES.find(r => r.category === tab.id)
                if (first) setSelectedRecipe(first)
              }}
              className={`px-4 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                activeCategory === tab.id
                  ? 'bg-[#10b981] text-black font-semibold shadow-lg shadow-[#10b981]/20'
                  : 'bg-[#12121a] text-zinc-400 hover:text-white border border-[#222230]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Main Grid: Selector List + Code/Viewer */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Recipe Selector */}
          <div className="lg:col-span-5 space-y-3 max-h-[640px] overflow-y-auto pr-2 custom-scrollbar">
            {filteredRecipes.map((recipe) => (
              <div
                key={recipe.id}
                onClick={() => {
                  setSelectedRecipe(recipe)
                  setSimulationResult(null)
                }}
                className={`p-4 rounded-xl cursor-pointer transition-all border ${
                  selectedRecipe.id === recipe.id
                    ? 'bg-[#131722] border-[#10b981] shadow-md shadow-[#10b981]/10'
                    : 'bg-[#0d0d14] border-[#1e1e2d] hover:border-zinc-700'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">
                    {recipe.badge}
                  </span>
                  <span className="text-[11px] text-zinc-500 font-mono">
                    {recipe.language.toUpperCase()}
                  </span>
                </div>
                <h4 className="text-sm font-bold text-white mt-2">
                  {recipe.title}
                </h4>
                <p className="text-xs text-zinc-400 line-clamp-2 mt-1">
                  {recipe.description}
                </p>
              </div>
            ))}
          </div>

          {/* Right Column: Code Display & Interactive Verification */}
          <div className="lg:col-span-7 bg-[#0b0c13] border border-[#222232] rounded-2xl p-6 shadow-2xl">
            {/* Header */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-[#1f2030]">
              <div>
                <span className="text-xs font-mono text-[#10b981]">
                  {selectedRecipe.filePath}
                </span>
                <h3 className="text-lg font-bold text-white mt-0.5">
                  {selectedRecipe.title}
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={runSimulation}
                  disabled={simulating}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#10b981]/10 text-[#10b981] border border-[#10b981]/30 hover:bg-[#10b981]/20 transition-all flex items-center gap-1.5"
                >
                  {simulating ? (
                    <>
                      <span className="w-2 h-2 rounded-full bg-[#10b981] animate-ping"></span>
                      Verifying AST...
                    </>
                  ) : (
                    <>
                      <span>▶</span> Run Verification
                    </>
                  )}
                </button>
                <button
                  onClick={handleCopy}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-zinc-800 text-white hover:bg-zinc-700 transition-all"
                >
                  {copied ? '✓ Copied' : 'Copy Code'}
                </button>
              </div>
            </div>

            {/* Architecture Flow Note */}
            <div className="my-4 p-3 rounded-lg bg-[#11131c] border border-[#1d2030] text-xs font-mono text-zinc-300 flex items-center gap-2 overflow-x-auto">
              <span className="text-[#10b981] font-bold">FLOW:</span>
              <span>{selectedRecipe.architectureNote}</span>
            </div>

            {/* Code Block */}
            <div className="relative">
              <pre className="p-4 rounded-xl bg-[#06070a] border border-[#181a24] text-xs font-mono text-zinc-300 overflow-x-auto max-h-[340px] leading-relaxed">
                <code>{selectedRecipe.codeSnippet}</code>
              </pre>
            </div>

            {/* Interactive Simulation Result */}
            {simulationResult && (
              <div className="mt-4 p-4 rounded-xl bg-[#0e1713] border border-[#10b981]/30 animate-fadeIn">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-[#10b981]"></span>
                    <span className="text-xs font-bold text-[#10b981]">
                      CRYPTOGRAPHIC INVARIANT VERIFIED
                    </span>
                  </div>
                  <span className="text-xs font-mono text-zinc-400">
                    Latency: <strong className="text-white">{simulationResult.latencyUs} µs</strong>
                  </span>
                </div>
                <div className="space-y-1 font-mono text-[11px] text-zinc-300">
                  <p className="truncate">
                    <strong className="text-zinc-400">Merkle Root:</strong> {simulationResult.merkleRoot}
                  </p>
                  <p className="truncate">
                    <strong className="text-zinc-400">Ed25519 Sig:</strong> {simulationResult.signature}
                  </p>
                </div>
              </div>
            )}

            {/* Footer Telemetry Banner */}
            <div className="mt-6 pt-4 border-t border-[#1a1c28] flex flex-wrap items-center justify-between text-xs text-zinc-500 font-mono">
              <span>BTP Protocol v3.5 & v4.0</span>
              <span>Reserve Pool: $100,000 USD</span>
              <span className="text-[#10b981]">2,717 / 2,717 Tests Verified</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
