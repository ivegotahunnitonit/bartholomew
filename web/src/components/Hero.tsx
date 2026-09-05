import { useState } from 'react'
import { 
  Check, 
  Copy, 
  Terminal, 
  ShieldCheck, 
  Zap, 
  CheckCircle2, 
  Lock, 
  ChevronDown, 
  ChevronUp, 
  Sparkles,
  ArrowRight
} from 'lucide-react'

type ConsoleTab = 'demo' | 'python' | 'claude' | 'node' | 'swarms'

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
  demo: {
    tab: 'demo',
    label: 'Live NPX Demo',
    pill: 'Zero Install',
    filename: 'terminal — btp-guard demo',
    command: 'npx -y btp-guard@latest demo',
    code: `❯ npx -y btp-guard@latest demo
[BTP Kernel v2.8] In-process memory gate active on PID 48210
[AST Invariant] Intercepted: "rm -rf /production/data"  --> BLOCKED (1.8µs)
[Secret Scrubber] Detected: "sk_live_94a7e..."            --> REDACTED (0.4µs)
[State Rollback] CoW Transaction Reverted                --> RESTORED (2.3µs)
======================================================================
100% In-Memory Guardrails Verified • Zero Telemetry Dispatched`,
    explanation: 'Interactive zero-install demo showing live command trapping, secret scrubbing, and 2.3µs state restoration in memory.',
    latency: '< 2.3µs Gate'
  },
  python: {
    tab: 'python',
    label: 'Python SDK',
    pill: 'pip install',
    filename: 'protect_agent.py',
    command: 'pip install btp-guard',
    code: `from btp_guard import Guard

# Set spend limit and maximum repetition budget
guard = Guard(spend_cap=100.0, max_retries=5)

@guard.protect
def execute_agent_tool(command_or_sql: str):
    # Destructive operations (rm -rf, DROP TABLE) blocked in <5µs
    return run_on_system(command_or_sql)`,
    explanation: 'Wrap any agent function or tool in 3 lines of Python. Destructive calls and budget runaway are blocked before OS execution.',
    latency: '1.44µs per call'
  },
  claude: {
    tab: 'claude',
    label: 'Claude & Cursor',
    pill: 'MCP Server',
    filename: 'claude_desktop_config.json',
    command: 'npx -y btp-guard mcp',
    code: `{
  "mcpServers": {
    "bartholomew-guard": {
      "command": "npx",
      "args": ["-y", "btp-guard", "mcp"]
    }
  }
}`,
    explanation: 'Standard Model Context Protocol security proxy for Claude 5 Desktop, Cursor, and Windsurf with in-flight secret masking.',
    latency: 'Sub-microsecond'
  },
  node: {
    tab: 'node',
    label: 'TypeScript / Node',
    pill: 'npm i btp-guard',
    filename: 'agent-gate.ts',
    command: 'npm install btp-guard',
    code: `import { Guard } from 'btp-guard';

const guard = new Guard({ spendCap: 50.0, maxRetries: 3 });

// Intercept autonomous agent tool calls
const decision = await guard.evaluate(toolCall.command);
if (!decision.allowed) {
  throw new Error(\`Bartholomew Trapped: \${decision.reason}\`);
}`,
    explanation: 'Zero-dependency TypeScript & ESM engine with RFC 8785 canonicalization and FIPS 186-5 Ed25519 cryptographic receipts.',
    latency: 'Zero Cloud Lag'
  },
  swarms: {
    tab: 'swarms',
    label: 'Agent Swarms',
    pill: 'Multi-Agent',
    filename: 'swarm_governor.py',
    command: 'pip install btp-guard',
    code: `from btp_guard import SwarmGovernor

# Law of Diminishing Marginal Utility (LDMU) loop damping
governor = SwarmGovernor(swarm_id="autonomous-cluster-01", max_drift=0.02)

# Halts runaway token loops across distributed agent swarms
verdict = governor.verify_swarm_attestation(step_intent, budget_usd=15.0)
if verdict.is_valid:
    dispatch_next_agent_turn()`,
    explanation: 'Traps infinite retry loops and cross-agent mutation drift across LangChain, AutoGen, and CrewAI swarms.',
    latency: '2.3µs Attestation'
  }
}

export default function Hero() {
  const [activeTab, setActiveTab] = useState<ConsoleTab>('demo')
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
      {/* Subtle Background Glow Radial */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-[#10b981]/10 blur-[130px] rounded-full pointer-events-none" />

      <div className="max-w-4xl mx-auto w-full relative z-10 text-center">
        
        {/* Single Refined Status Badge */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#0a0a0f] border border-[#1f1f26] mb-6 shadow-sm">
          <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse" />
          <span className="text-xs font-mono font-semibold text-[#a1a1aa]">
            Bartholomew Engine v2.8 &middot; <strong className="text-white font-medium">Sub-Microsecond In-Memory AI Safety</strong>
          </span>
        </div>

        {/* Clean, Impactful Headline */}
        <h1 
          className="font-bold font-sans tracking-tight text-white mb-5 mx-auto max-w-3xl"
          style={{
            fontSize: 'clamp(1.75rem, 5vw, 3.25rem)',
            lineHeight: 1.15,
            letterSpacing: '-0.03em'
          }}
        >
          The Fastest In-Memory Safety Guard for AI Agents.
        </h1>

        {/* Crisp Subtitle */}
        <p className="text-center mx-auto mb-8 text-[#a1a1aa] leading-relaxed max-w-2xl text-sm sm:text-base font-sans">
          Zero cloud lag. Zero external telemetry. Intercepts destructive commands (<code className="text-[#38bdf8] bg-[#111118] px-1 py-0.5 rounded border border-[#27272a]">rm -rf</code>, <code className="text-[#38bdf8] bg-[#111118] px-1 py-0.5 rounded border border-[#27272a]">DROP TABLE</code>), redacts leaked secrets in-flight, and restores pristine files in 2.3µs—stopping runaway agent mutations in local CPU memory before OS dispatch.
        </p>

        {/* Minimalist Action & Quick-Start Pill */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-10">
          {/* Quick Terminal Copy Pill */}
          <div className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#0c0c10] border border-[#27272a] font-mono text-xs text-[#e4e4e7] shadow-inner max-w-full">
            <span className="text-[#10b981] select-none font-bold">❯</span>
            <span className="text-[#f59e0b] truncate">npx -y btp-guard@latest demo</span>
            <button
              onClick={() => {
                navigator.clipboard.writeText('npx -y btp-guard@latest demo')
                setCopiedCmd(true)
                setTimeout(() => setCopiedCmd(false), 2000)
              }}
              className="ml-2 px-2.5 py-1 text-[11px] font-bold rounded bg-[#181820] hover:bg-[#10b981] text-[#a1a1aa] hover:text-black transition border border-[#33333d]"
              title="Copy demo command"
            >
              {copiedCmd ? 'COPIED!' : 'COPY'}
            </button>
          </div>

          {/* Jump to Interactive Simulator Button */}
          <a
            href="#threat-simulator"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#10b981]/15 hover:bg-[#10b981]/25 text-[#10b981] border border-[#10b981]/40 hover:border-[#10b981] text-xs font-mono font-bold transition shadow-[0_0_15px_rgba(16,185,129,0.15)]"
          >
            <Sparkles size={14} />
            <span>EXPLORE THREAT SANDBOX</span>
            <ArrowRight size={13} />
          </a>
        </div>

        {/* Minimalist Trust Metrics Bar */}
        <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-6 text-xs font-mono text-[#71717a] mb-10 pb-2">
          <span className="flex items-center gap-1.5 text-[#10b981]">
            <Zap size={13} className="text-[#f59e0b]" />
            <span>&lt; 2.3µs Intercept</span>
          </span>
          <span className="hidden xs:inline">&bull;</span>
          <span className="flex items-center gap-1.5 text-[#d4d4d8]">
            <CheckCircle2 size={13} className="text-[#10b981]" />
            <span>100% In-Memory</span>
          </span>
          <span className="hidden xs:inline">&bull;</span>
          <span className="flex items-center gap-1.5 text-[#a1a1aa]">
            <Lock size={12} className="text-[#38bdf8]" />
            <span>Zero Telemetry</span>
          </span>
          <span className="hidden xs:inline">&bull;</span>
          <span className="flex items-center gap-1.5 text-[#a1a1aa]">
            <ShieldCheck size={13} className="text-[#10b981]" />
            <span>FIPS 186-5 Ed25519</span>
          </span>
        </div>

        {/* Unified Frontier Console Showcase (Single Clean Terminal Window) */}
        <div className="rounded-xl border border-[#27272a] bg-gradient-to-b from-[#0d0d12] via-[#08080b] to-[#040406] shadow-[0_25px_60px_-20px_rgba(0,0,0,0.85)] text-left overflow-hidden relative transition-all duration-300">
          {/* Top Ambient Green Glow line */}
          <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#10b981]/80 to-transparent pointer-events-none" />

          {/* Console Header Chrome */}
          <div className="flex items-center justify-between px-4 py-3 bg-[#0a0a0e] border-b border-[#1f1f26]">
            {/* MacOS Window Dots */}
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#ef4444]/80 inline-block" />
              <span className="w-2.5 h-2.5 rounded-full bg-[#f59e0b]/80 inline-block" />
              <span className="w-2.5 h-2.5 rounded-full bg-[#10b981]/80 inline-block" />
              <span className="text-xs font-mono text-[#71717a] ml-2 hidden sm:inline">{current.filename}</span>
            </div>

            {/* Latency & Quick Action */}
            <div className="flex items-center gap-3">
              <span className="text-[11px] font-mono text-[#10b981] bg-[#10b981]/10 px-2 py-0.5 rounded border border-[#10b981]/30">
                {current.latency}
              </span>
              <button
                onClick={handleCopyCode}
                className="text-xs font-mono text-[#a1a1aa] hover:text-[#10b981] transition flex items-center gap-1"
                title="Copy code to clipboard"
              >
                {copiedCode ? <Check size={12} className="text-[#10b981]" /> : <Copy size={12} />}
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
                      ? 'bg-[#0d0d12] text-white border-[#2e2e38] border-b-transparent -mb-[1px] font-bold text-[#10b981]'
                      : 'text-[#71717a] border-transparent hover:text-[#d4d4d8]'
                  }`}
                >
                  <Terminal size={12} className={isActive ? 'text-[#10b981]' : 'text-[#52525b]'} />
                  <span>{item.label}</span>
                </button>
              )
            })}
          </div>

          {/* Console Code Body */}
          <div className="p-4 sm:p-5 bg-[#040406] overflow-x-auto selection:bg-[#10b981]/30">
            <pre className="font-mono text-xs sm:text-[13px] text-[#e4e4e7] leading-relaxed">
              {current.code}
            </pre>
          </div>

          {/* Console Description & Expandable Checksum Footer */}
          <div className="px-4 py-2.5 bg-[#09090d] border-t border-[#1a1a22] flex flex-col sm:flex-row sm:items-center justify-between text-xs font-sans text-[#a1a1aa] gap-2">
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]" />
              <span>{current.explanation}</span>
            </div>

            <button
              onClick={() => setShowChecksums(!showChecksums)}
              className="font-mono text-[11px] text-[#71717a] hover:text-[#10b981] transition flex items-center gap-1 shrink-0 self-end sm:self-auto"
            >
              <span>{showChecksums ? 'Hide Checksum' : 'Verify Checksum'}</span>
              {showChecksums ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>
          </div>

          {/* Checksum Drawer */}
          {showChecksums && (
            <div className="p-3 bg-[#020204] border-t border-[#1a1a22] font-mono text-[11px] text-[#71717a] grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div>
                <span className="text-[#52525b] block text-[10px] uppercase">Ed25519 Signer</span>
                <span className="text-[#10b981]">itsub@bartholomew.info</span>
              </div>
              <div>
                <span className="text-[#52525b] block text-[10px] uppercase">RFC 8785 Canonical Digest</span>
                <span className="text-[#f59e0b] break-all">3c8e77a807f7f90be092b3a985e5ebad6b0c20188efee31e7c98b67cc1d89fa3</span>
              </div>
            </div>
          )}

        </div>

      </div>
    </section>
  )
}
