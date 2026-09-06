import { useState } from 'react'
import { 
  Check, 
  Copy, 
  Terminal, 
  ShieldCheck, 
  Zap, 
  CheckCircle2, 
  ChevronDown, 
  ChevronUp, 
  Sparkles, 
  ArrowRight, 
  ArrowRightLeft,
  ExternalLink 
} from 'lucide-react'


type ConsoleTab = 'quickstart' | 'crewai' | 'langgraph' | 'autogen' | 'openai' | 'docker'

interface ConsoleItem {
  tab: ConsoleTab
  label: string
  pill: string
  filename: string
  command?: string
  code: string
  explanation: string
  latency: string
}

const CONSOLE_ITEMS: Record<ConsoleTab, ConsoleItem> = {
  quickstart: {
    tab: 'quickstart',
    label: '10s Quickstart',
    pill: 'Auto-Detect',
    filename: 'terminal — btp-guard init',
    command: 'pip install btp-guard',
    code: `❯ pip install btp-guard
❯ btp-guard init
[BTP v5.4] Scanning project environment...
[+] Detected Agent Framework : CrewAI & LangGraph
[+] Sovereign Ed25519 Keypair : Generated (pubkey: 3d2b0e...7fabc5)
[+] Multi-Tenant Workspace   : acme-corp / prod-workers (btp_live_94a7e...)
[+] Local AST Security Policy: .btp/policy.yaml initialized (12 rules)
[+] Fast Framework Guard     : Generated src/guards/agent_guard.py
======================================================================
100% In-Memory Guardrails Verified • Zero External Prompt Leakage`,
    explanation: 'Interactive 10-second developer wizard. Automatically detects your agent framework and scaffolds sovereign credentials, AST policies, and drop-in guards.',
    latency: 'Instant Local Memory Gate'
  },
  crewai: {
    tab: 'crewai',
    label: 'CrewAI Guard',
    pill: 'Python SDK',
    filename: 'crewai_agent_guard.py',
    command: 'pip install btp-guard',
    code: `from crewai import Agent, Task, Crew
from btp_guard.adapters.crewai import BTPTaskGuard

# Fastest and most reliable local AST safety inspection
guard = BTPTaskGuard(tenant_id="acme-corp", spend_cap=150.0)

auditor = Agent(
    role="Autonomous Code Auditor",
    goal="Refactor backend services and run test suites",
    tools=guard.wrap_tools([execute_shell_command, query_postgres_db])
)

# Destructive syscalls (rm -rf, DROP TABLE) and secret leaks are blocked locally
crew = Crew(agents=[auditor], tasks=[refactor_task])
crew.kickoff()`,
    explanation: 'Native CrewAI task and tool interceptor. Enforces deterministic AST safety and secret scrubbing before execution crosses the OS syscall boundary.',
    latency: 'Fastest & Most Reliable AST Gate'
  },
  langgraph: {
    tab: 'langgraph',
    label: 'LangGraph Node',
    pill: 'StateGraph Gate',
    filename: 'langgraph_guard.py',
    command: 'pip install btp-guard',
    code: `from langgraph.graph import StateGraph
from btp_guard.adapters.langgraph import BTPLangGraphGuard

guard = BTPLangGraphGuard(workspace_id="antigravity-dev")

def tool_execution_node(state):
    # Pre-execution AST invariant verification
    decision = guard.evaluate_node_state(state["current_tool_call"])
    if not decision.allowed:
        return {"error": decision.reason, "veto": True}
    return execute_safe_tool(state["current_tool_call"])

graph = StateGraph(AgentState)
graph.add_node("tool_node", tool_execution_node)`,
    explanation: 'In-flight LangGraph state graph validator. Traps runaway loops, spend spikes, and malicious mutations between agent state transitions.',
    latency: 'In-Process State Gate'
  },
  autogen: {
    tab: 'autogen',
    label: 'AutoGen Mesh',
    pill: 'Swarm Interceptor',
    filename: 'autogen_interceptor.py',
    command: 'pip install btp-guard',
    code: `from autogen import ConversableAgent
from btp_guard.adapters.autogen import BTPConversableInterceptor

interceptor = BTPConversableInterceptor(org="bartholomew-core")

agent = ConversableAgent(
    name="DevOpsAssistant",
    system_message="Autonomous infrastructure deployer"
)
# Hooks outgoing tool calls and peer messages with zero prompt leakage
interceptor.attach(agent)
agent.initiate_chat(recipient, message="Deploy k8s cluster")`,
    explanation: 'Wire-level interceptor for Microsoft AutoGen agents. Guarantees zero sensitive prompt exfiltration and drops adversarial syscalls in caller memory.',
    latency: 'Zero Syscall Wire Gate'
  },
  openai: {
    tab: 'openai',
    label: 'OpenAI Tools',
    pill: 'Function Calling',
    filename: 'openai_tool_guard.py',
    command: 'pip install btp-guard',
    code: `from btp_guard import BTPGuard

guard = BTPGuard(workspace_id="prod-finance", spend_cap=250.0)

# Pre-execution validation for OpenAI function / tool calling
def dispatch_safe_tool(tool_call):
    decision = guard.verify_tool_call(
        tool_name=tool_call.function.name,
        arguments_json=tool_call.function.arguments
    )
    if not decision.allowed:
        raise PermissionError(f"BTP Veto: {decision.violations}")
    return execute_internal_tool(tool_call)`,
    explanation: 'Pre-dispatch validation for OpenAI function calling. Verifies JSON arguments and drops destructive SQL, shell, or file mutations in memory.',
    latency: 'In-Process Gate'
  },
  docker: {
    tab: 'docker',
    label: 'Sandbox Defense',
    pill: 'Defense-in-Depth',
    filename: 'container_defense.py',
    command: 'pip install btp-guard',
    code: `from btp_guard.sandbox import ContainerGuardPolicy

# Layer-7 Invariant Gating paired with OS Container Sandboxing
policy = ContainerGuardPolicy(
    container_runtime="docker",
    block_dynamic_exec=True,        # Vetoes eval, exec, base64 decoding sinks
    allowed_egress_domains=["api.github.com", "pypi.org"]
)
# AST gating intercepts tool dispatches inside isolated container namespaces`,
    explanation: 'Production defense-in-depth model. Pairs Layer-7 semantic AST invariant gating with OS-level Docker / gVisor container sandboxing.',
    latency: 'Container Safe'
  }
}

export default function Hero() {
  const [activeTab, setActiveTab] = useState<ConsoleTab>('quickstart')
  const [copiedCode, setCopiedCode] = useState(false)
  const [copiedCmd, setCopiedCmd] = useState(false)
  const [showChecksums, setShowChecksums] = useState(false)

  const current = CONSOLE_ITEMS[activeTab]

  const handleCopyCode = () => {
    navigator.clipboard.writeText(current.code)
    setCopiedCode(true)
    setTimeout(() => setCopiedCode(false), 2000)
  }

  return (
    <section className="relative min-h-[85vh] flex flex-col justify-center pt-28 pb-16 px-4 sm:px-6 lg:px-8 bg-black text-white overflow-hidden">
      {/* Dynamic Background Glow Radial */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] bg-gradient-to-r from-emerald-500/15 via-cyan-500/10 to-purple-500/10 blur-[140px] rounded-full pointer-events-none" />

      <div className="max-w-4xl mx-auto w-full relative z-10 text-center">
        
        {/* Protocol Version Badge */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#0a0a0f] border border-[#1f1f26] mb-6 shadow-sm">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_#10b981]" />
          <span className="text-xs font-mono font-bold tracking-wider text-white">
            Bartholomew Trust Protocol v5.4.0
          </span>
          <span className="text-[10px] font-mono px-2 py-0.2 rounded bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30">
            SOVEREIGN AGENT PROTOCOL
          </span>
        </div>

        {/* Impactful Headline */}
        <h1 
          className="font-bold font-sans tracking-tight text-white mb-5 mx-auto max-w-3xl"
          style={{
            fontSize: 'clamp(1.85rem, 5vw, 3.4rem)',
            lineHeight: 1.15,
            letterSpacing: '-0.03em'
          }}
        >
          The Sovereign Trust &amp; Settlement Protocol for AI Agents.
        </h1>

        {/* Subtitle */}
        <p className="text-center mx-auto mb-8 text-[#a1a1aa] leading-relaxed max-w-2xl text-sm sm:text-base font-sans">
          Zero cloud lag. Zero prompt leakage. The fastest and most reliable local AST safety gating stops catastrophic tool calls (<code className="text-cyan-400 bg-zinc-900 px-1.5 py-0.5 rounded border border-zinc-800">rm -rf</code>, <code className="text-cyan-400 bg-zinc-900 px-1.5 py-0.5 rounded border border-zinc-800">DROP TABLE</code>) in memory before reaching the OS. Cross-tenant agent marketplace, EigenTrust peer reputation, and atomic multi-chain escrow bridging across Base, Arbitrum, and Lightning.
        </p>

        {/* Minimalist Action & Quick-Start Pill */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-10">
          {/* Quick Terminal Copy Pill */}
          <div className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#0c0c10] border border-[#27272a] font-mono text-xs text-[#e4e4e7] shadow-inner max-w-full">
            <span className="text-emerald-400 select-none font-bold">❯</span>
            <span className="text-amber-400 truncate">pip install btp-guard</span>
            <button
              onClick={() => {
                navigator.clipboard.writeText('pip install btp-guard')
                setCopiedCmd(true)
                setTimeout(() => setCopiedCmd(false), 2000)
              }}
              className="ml-2 px-2.5 py-1 text-[11px] font-bold rounded bg-[#181820] hover:bg-emerald-500 text-[#a1a1aa] hover:text-black transition border border-[#33333d]"
              title="Copy quickstart command"
            >
              {copiedCmd ? 'COPIED!' : 'COPY'}
            </button>
          </div>

          {/* Jump to Interactive Swarm Arena Button */}
          <a
            href="#swarm-arena"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-400 border border-emerald-500/40 hover:border-emerald-400 text-xs font-mono font-bold transition shadow-[0_0_15px_rgba(16,185,129,0.15)]"
          >
            <Sparkles size={14} />
            <span>ENTER LIVE SWARM ARENA</span>
            <ArrowRight size={13} />
          </a>
        </div>

        {/* Trust & Performance Metrics Bar */}
        <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-6 text-xs font-mono text-[#71717a] mb-10 pb-2">
          <span className="flex items-center gap-1.5 text-emerald-400">
            <Zap size={13} className="text-amber-400" />
            <span>Fastest &amp; Most Reliable AST Gating</span>
          </span>
          <span className="hidden xs:inline">&bull;</span>
          <span className="flex items-center gap-1.5 text-cyan-300">
            <CheckCircle2 size={13} className="text-cyan-400" />
            <span>Zero Prompt Leakage</span>
          </span>
          <span className="hidden xs:inline">&bull;</span>
          <span className="flex items-center gap-1.5 text-purple-300">
            <ArrowRightLeft size={13} className="text-purple-400" />
            <span>Base / Arb / Lightning Bridges</span>
          </span>
          <span className="hidden xs:inline">&bull;</span>
          <span className="flex items-center gap-1.5 text-zinc-300">
            <ShieldCheck size={13} className="text-emerald-400" />
            <span>2,791 Passing Tests (100%)</span>
          </span>
        </div>

        {/* Unified Frontier Console Showcase */}
        <div className="rounded-xl border border-[#27272a] bg-gradient-to-b from-[#0d0d12] via-[#08080b] to-[#040406] shadow-[0_25px_60px_-20px_rgba(0,0,0,0.85)] text-left overflow-hidden relative transition-all duration-300">
          {/* Top Ambient Glow line */}
          <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-emerald-500/80 to-transparent pointer-events-none" />

          {/* Console Header Chrome */}
          <div className="flex items-center justify-between px-4 py-3 bg-[#0a0a0e] border-b border-[#1f1f26]">
            {/* MacOS Window Dots */}
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-red-500/80 inline-block" />
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80 inline-block" />
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80 inline-block" />
              <span className="text-xs font-mono text-[#71717a] ml-2 hidden sm:inline">{current.filename}</span>
            </div>

            {/* Latency & Quick Action */}
            <div className="flex items-center gap-3">
              <span className="text-[11px] font-mono text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-500/30">
                {current.latency}
              </span>
              <button
                onClick={handleCopyCode}
                className="text-xs font-mono text-[#a1a1aa] hover:text-emerald-400 transition flex items-center gap-1"
                title="Copy code to clipboard"
              >
                {copiedCode ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                <span>{copiedCode ? 'COPIED' : 'COPY'}</span>
              </button>
            </div>
          </div>

          {/* Unified Clean Tab Bar */}
          <div className="flex bg-[#07070a] border-b border-[#1a1a20] px-2 pt-1 gap-1 overflow-x-auto no-scrollbar">
            {(Object.keys(CONSOLE_ITEMS) as ConsoleTab[]).map((tabKey) => {
              const item = CONSOLE_ITEMS[tabKey]
              const isActive = activeTab === tabKey
              return (
                <button
                  key={tabKey}
                  onClick={() => setActiveTab(tabKey)}
                  className={`px-3 py-2 text-xs font-mono transition-all rounded-t-md border-t border-x whitespace-nowrap flex items-center gap-1.5 ${
                    isActive
                      ? 'bg-[#0d0d12] text-white border-[#2e2e38] border-b-transparent -mb-[1px] font-bold text-emerald-400'
                      : 'text-[#71717a] border-transparent hover:text-[#d4d4d8]'
                  }`}
                >
                  <Terminal size={12} className={isActive ? 'text-emerald-400' : 'text-[#52525b]'} />
                  <span>{item.label}</span>
                </button>
              )
            })}
          </div>

          {/* Console Code Body */}
          <div className="p-4 sm:p-5 bg-[#040406] overflow-x-auto selection:bg-emerald-500/30">
            <pre className="font-mono text-xs sm:text-[13px] text-[#e4e4e7] leading-relaxed">
              {current.code}
            </pre>
          </div>

          {/* Console Description & Expandable Checksum Footer */}
          <div className="px-4 py-2.5 bg-[#09090d] border-t border-[#1a1a22] flex flex-col sm:flex-row sm:items-center justify-between text-xs font-sans text-[#a1a1aa] gap-2">
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>{current.explanation}</span>
            </div>

            <div className="flex items-center gap-3 shrink-0 self-end sm:self-auto">
              <button
                onClick={() => setShowChecksums(!showChecksums)}
                className="font-mono text-[11px] text-[#71717a] hover:text-emerald-400 transition flex items-center gap-1 cursor-pointer"
              >
                <span>{showChecksums ? 'Hide Release Digest' : 'View Release Digest'}</span>
                {showChecksums ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>
              <a
                href="https://pypi.org/project/btp-guard/#files"
                target="_blank"
                rel="noopener noreferrer"
                className="font-mono text-[11px] text-emerald-400 hover:text-emerald-300 transition flex items-center gap-1 border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 rounded"
              >
                <span>PyPI Hashes</span>
                <ExternalLink size={10} />
              </a>
            </div>
          </div>

          {/* Checksum Drawer */}
          {showChecksums && (
            <div className="p-3 bg-[#020204] border-t border-[#1a1a22] font-mono text-[11px] text-[#71717a] grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div>
                <span className="text-[#52525b] block text-[10px] uppercase">Official Package Channel</span>
                <span className="text-emerald-400">btp-guard on PyPI (FIPS 186-5 Ed25519)</span>
              </div>
              <div>
                <span className="text-[#52525b] block text-[10px] uppercase">Verifiable Checksums</span>
                <a
                  href="https://pypi.org/project/btp-guard/#files"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-amber-400 hover:underline inline-flex items-center gap-1"
                >
                  <span>Verify SHA-256 hashes on PyPI</span>
                  <ExternalLink size={10} />
                </a>
              </div>
            </div>
          )}

        </div>

      </div>
    </section>
  )
}
