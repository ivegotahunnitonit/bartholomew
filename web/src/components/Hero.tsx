import { useState } from 'react'
import { 
  Check, 
  Copy, 
  Cpu, 
  CheckCircle2, 
  Terminal, 
  Package, 
  Code2, 
  GitBranch, 
  ShieldCheck, 
  ExternalLink, 
  Lock, 
  ChevronDown, 
  ChevronUp, 
  Zap
} from 'lucide-react'

type AgentTarget = 'simple' | 'claude' | 'openai' | 'gemini' | 'kimi' | 'langchain'
type InstallTarget = 'npx' | 'mcp' | 'pip' | 'npm' | 'action' | 'git'

export default function Hero() {
  const [selectedAgent, setSelectedAgent] = useState<AgentTarget>('simple')
  const [activeInstallTab, setActiveInstallTab] = useState<InstallTarget>('npx')
  const [nodePm, setNodePm] = useState<'npm' | 'pnpm' | 'yarn' | 'bun'>('npm')
  const [pythonPm, setPythonPm] = useState<'pip' | 'uv' | 'poetry'>('pip')
  const [showIntegrityDrawer, setShowIntegrityDrawer] = useState(false)
  const [copiedCode, setCopiedCode] = useState(false)
  const [copiedCommand, setCopiedCommand] = useState(false)

  const getDynamicCommand = (tab: InstallTarget) => {
    switch (tab) {
      case 'npx':
        return 'npx -y btp-guard@latest demo'
      case 'mcp':
        return 'npx -y btp-guard mcp'
      case 'pip':
        if (pythonPm === 'uv') return 'uv add btp-guard'
        if (pythonPm === 'poetry') return 'poetry add btp-guard'
        return 'pip install btp-guard'
      case 'npm':
        if (nodePm === 'pnpm') return 'pnpm add btp-guard'
        if (nodePm === 'yarn') return 'yarn add btp-guard'
        if (nodePm === 'bun') return 'bun add btp-guard'
        return 'npm install btp-guard'
      case 'action':
        return 'uses: ivegotahunnitonit/bartholomew@v2.8.0'
      case 'git':
        return 'git clone https://github.com/ivegotahunnitonit/bartholomew.git && cd bartholomew && pip install -e .'
    }
  }

  const tabDetails: Record<InstallTarget, {
    badge: string
    latency: string
    description: string
    icon: typeof Terminal
  }> = {
    npx: {
      badge: 'Zero-Install Interactive Demo',
      latency: '< 1ms dispatch',
      description: 'Live in-flight secret scrubbing, 2.3µs micro-rollback, and Merkle root verification in local CPU memory.',
      icon: Terminal
    },
    mcp: {
      badge: 'Claude 5 Desktop, Cursor & Astra MCP Server',
      latency: 'Sub-microsecond gating',
      description: 'Model Context Protocol security proxy intercepting bash commands, file edits, and network requests before dispatch.',
      icon: Cpu
    },
    pip: {
      badge: 'Python 3.10+ · PyPI Verified',
      latency: '2.3 µs per tool call',
      description: 'Universal drop-in decorators & safety middleware for Anthropic Computer-Use, CrewAI, AutoGen, and LangChain.',
      icon: Package
    },
    npm: {
      badge: 'TypeScript / ESM / CJS · npmjs.com',
      latency: '0-dependency reference',
      description: 'Pure RFC 8785 JSON Canonicalization Scheme and FIPS 186-5 Ed25519 verification with zero external dependencies.',
      icon: Code2
    },
    action: {
      badge: 'GitHub Marketplace Action',
      latency: 'Automated CI/CD gatekeeper',
      description: 'Blocks pull requests if unauthorized file deletions, dependency tampering, or unauthenticated prompt injections occur.',
      icon: ShieldCheck
    },
    git: {
      badge: 'Audited Open Source Pre-Print',
      latency: '31/31 Unit Tests Passing',
      description: 'Full repository source code with mathematical benchmarks, reproducible adversarial suites, and research pre-print.',
      icon: GitBranch
    }
  }

  const agentPairingSnippets: Record<AgentTarget, { title: string; filename: string; code: string; desc: string }> = {
    simple: {
      title: 'Simple 3-Line Python Guard',
      filename: 'protect_agent.py',
      desc: 'Wrap any agent function or tool in 3 lines. Destructive calls (rm -rf, DROP TABLE) and budget spikes are blocked in <5 microseconds.',
      code: `from btp_guard import Guard

# Set spend limit and max retries
guard = Guard(spend_cap=100.0, max_retries=5)

@guard.protect
def execute_tool(command_or_sql: str):
    # Automatically blocked in <5 µs if destructive or over budget
    return run_on_system(command_or_sql)`
    },
    claude: {
      title: 'Claude 5 Desktop & Cursor (MCP)',
      filename: 'claude_desktop_config.json',
      desc: 'In-process Model Context Protocol security server for Anthropic Claude 5 and Cursor. Intercepts tool calls and redacts secrets in-flight.',
      code: `// Paste into claude_desktop_config.json:
{
  "mcpServers": {
    "bartholomew": {
      "command": "npx",
      "args": ["-y", "btp-guard", "mcp"]
    }
  }
}`
    },
    openai: {
      title: 'OpenAI GPT-6 Astra & Swarms',
      filename: 'openai_assistant_guard.py',
      desc: 'Wraps GPT-6 Astra / Computer-Use agent function calling with hermetic path containment and spend limits.',
      code: `from btp_guard import Guard
import openai

guard = Guard(spend_cap=50.0)

# Intercept tool calls before OS dispatch
def on_tool_call(name, args):
    res = guard.check(args.get("query", ""))
    if not res["allowed"]:
        return f"Error: {res['reason']}"
    return execute_safely(name, args)`
    },
    gemini: {
      title: 'Google Gemini 2.5 Pro & Agentic SDK',
      filename: 'gemini_agent_guard.py',
      desc: 'Protects Google Gemini 2.5 Pro/Flash and Agentic ADK tool executions with sub-50µs AST safety gates and transactional micro-rollbacks.',
      code: `from btp_guard import Guard
from google import genai

guard = Guard(spend_cap=100.0, max_retries=5)
client = genai.Client()

# Protect Gemini function calls before execution
@guard.protect
def handle_gemini_tool(call_name: str, parameters: dict):
    return execute_contained_tool(call_name, parameters)`
    },
    kimi: {
      title: 'Moonshot AI Kimi (k1.5 Context Core)',
      filename: 'kimi_agent_guard.py',
      desc: 'Invariant gating for Moonshot AI Kimi long-context agent workflows, filtering prompt injections and unauthorized filesystem access.',
      code: `from btp_guard import Guard
from openai import OpenAI

guard = Guard(spend_cap=75.0)
client = OpenAI(base_url="https://api.moonshot.cn/v1")

def execute_kimi_tool(name: str, arguments: dict):
    check = guard.check(arguments.get("command", ""))
    if not check["allowed"]:
        raise PermissionError(f"Blocked by Bartholomew: {check['reason']}")
    return run_tool(name, arguments)`
    },
    langchain: {
      title: 'LangChain, DeepSeek & Multi-Agent Swarms',
      filename: 'swarm_guard.py',
      desc: 'Halts infinite retry loops and traps runaway token consumption across agent swarms.',
      code: `from btp_guard import Guard
from langchain.agents import initialize_agent

guard = Guard(spend_cap=200.0, max_retries=6)

# Evaluates each step with Law of Diminishing Marginal Utility
result = guard.check("EXECUTE_BATCH", amount_usd=12.50)
if result["allowed"]:
    agent.run("Refactor payment service")`
    }
  }

  const currentSnippet = agentPairingSnippets[selectedAgent]

  const handleCopySnippet = () => {
    navigator.clipboard.writeText(currentSnippet.code)
    setCopiedCode(true)
    setTimeout(() => setCopiedCode(false), 2000)
  }

  const handleCopyCommand = () => {
    navigator.clipboard.writeText(getDynamicCommand(activeInstallTab))
    setCopiedCommand(true)
    setTimeout(() => setCopiedCommand(false), 2000)
  }

  return (
    <section className="relative min-h-[90vh] flex flex-col justify-center pt-28 pb-20 px-5 sm:px-8 bg-black text-white overflow-x-hidden">
      <div className="max-w-5xl mx-auto w-full relative z-10">
        
        {/* Launch Day Announcements & Telemetry */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-6">
          <a
            href="https://www.producthunt.com/products/bartholomew-2"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-[#ff6154]/10 border border-[#ff6154]/40 hover:border-[#ff6154] text-xs font-mono font-bold uppercase tracking-wider text-[#ff6154] transition shadow-sm group"
          >
            <span className="w-2 h-2 rounded-full bg-[#ff6154] animate-pulse" />
            <span>[FEATURED ON PRODUCT HUNT &middot; JOIN LAUNCH DISCUSSION &rarr;]</span>
          </a>
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-[#0a0a0a] border border-[#222222] text-xs font-mono font-bold uppercase tracking-wider text-[#a1a1aa] shadow-sm">
            <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse" />
            <span className="text-[#10b981]">[220+ PYPI &middot; 130+ NPM &middot; 1.05M EVALS/SEC]</span>
          </div>
        </div>

        {/* Hero Headline */}
        <div className="text-center max-w-5xl mx-auto mb-4 px-2">
          <h1
            className="font-bold font-sans hero-metallic-title text-center inline-block break-words"
            style={{
              fontSize: 'clamp(1.5rem, 4.5vw, 2.75rem)',
              lineHeight: 1.2,
              letterSpacing: '-0.02em',
              paddingBottom: '0.18em'
            }}
          >
            The Fastest In-Memory Safety Guard for AI Agents.
          </h1>
        </div>

        {/* Hero Subtitle */}
        <p className="text-center mx-auto mb-8 sm:mb-10 text-[#d4d4d8] leading-relaxed max-w-2xl text-xs sm:text-base font-sans px-2">
          Zero cloud lag. Zero external telemetry. Intercepts destructive commands (<code>rm -rf</code>, <code>DROP TABLE</code>), redacts leaked API keys, and restores pristine files in 2.3µs—stopping runaway agent mutations in local CPU memory before OS dispatch.
        </p>

        {/* Verified Package Install Box - Redesigned Frontier UI */}
        <div className="relative rounded-xl border border-[#27272a] bg-gradient-to-b from-[#0e0e11] via-[#09090b] to-[#040405] max-w-3xl mx-auto mb-10 sm:mb-12 shadow-[0_20px_50px_-20px_rgba(16,185,129,0.18)] overflow-hidden w-full transition-all duration-300">
          {/* Top Glowing Ambient Highlight */}
          <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#10b981] to-transparent" />
          
          {/* Terminal Header Chrome */}
          <div className="flex flex-wrap items-center justify-between px-3.5 sm:px-5 py-2.5 bg-[#08080a] border-b border-[#1f1f23] gap-2">
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#ef4444] inline-block shadow-[0_0_8px_rgba(239,68,68,0.4)]" />
                <span className="w-2.5 h-2.5 rounded-full bg-[#f59e0b] inline-block shadow-[0_0_8px_rgba(245,158,11,0.4)]" />
                <span className="w-2.5 h-2.5 rounded-full bg-[#10b981] inline-block shadow-[0_0_8px_rgba(16,185,129,0.4)]" />
              </div>
              <div className="h-3.5 w-[1px] bg-[#27272a] mx-1" />
              {/* Core Badge */}
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#10b981]/10 border border-[#10b981]/30">
                <span className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse" />
                <span className="text-[10px] sm:text-[11px] font-mono font-bold tracking-wider text-[#10b981] uppercase">
                  verified-package-install
                </span>
              </div>
            </div>

            {/* Right Badges */}
            <div className="flex items-center gap-2 text-[10px] sm:text-[11px] font-mono">
              <a
                href="https://www.npmjs.com/package/btp-guard"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-[#a1a1aa] hover:text-[#10b981] transition px-2 py-0.5 rounded bg-[#141417] border border-[#27272a]"
                title="View verified npm package page"
              >
                <Package size={12} className="text-[#10b981]" />
                <span>npm: <strong className="text-white">btp-guard@2.5.0</strong></span>
                <ExternalLink size={10} className="opacity-70 ml-0.5" />
              </a>
              <span className="hidden sm:inline-flex items-center gap-1 text-[#10b981] px-2 py-0.5 rounded bg-[#10b981]/10 border border-[#10b981]/20">
                <ShieldCheck size={12} />
                <span>Zero-Daemon</span>
              </span>
            </div>
          </div>

          {/* Ecosystem Tab Selector Chips */}
          <div className="flex bg-[#060608] border-b border-[#1f1f23] p-1.5 sm:p-2 gap-1.5 overflow-x-auto no-scrollbar">
            {(['npx', 'mcp', 'pip', 'npm', 'action', 'git'] as const).map((tab) => {
              const TabIcon = tabDetails[tab].icon
              const isActive = activeInstallTab === tab
              return (
                <button
                  key={tab}
                  onClick={() => setActiveInstallTab(tab)}
                  className={`flex-1 min-w-[90px] sm:min-w-0 py-1.5 px-2 text-[11px] sm:text-xs font-mono font-semibold transition rounded flex items-center justify-center gap-1.5 border whitespace-nowrap text-center ${
                    isActive
                      ? 'bg-[#10b981]/15 text-[#ffffff] border-[#10b981] shadow-[0_0_15px_rgba(16,185,129,0.2)]'
                      : 'bg-[#0b0b0e] text-[#a1a1aa] border-[#222226] hover:text-white hover:border-[#38383f]'
                  }`}
                >
                  <TabIcon size={13} className={isActive ? 'text-[#10b981]' : 'text-[#71717a]'} />
                  <span>
                    {tab === 'npx' && 'NPX Demo'}
                    {tab === 'mcp' && 'MCP Proxy'}
                    {tab === 'pip' && 'PyPI (Python)'}
                    {tab === 'npm' && 'NPM (Node)'}
                    {tab === 'action' && 'GH Action'}
                    {tab === 'git' && 'Git Source'}
                  </span>
                </button>
              )
            })}
          </div>

          {/* Sub-Package Manager Switcher for npm and pip */}
          {activeInstallTab === 'npm' && (
            <div className="px-4 py-1.5 bg-[#0b0b0e] border-b border-[#1c1c20] flex items-center justify-between text-[11px] font-mono">
              <span className="text-[#71717a] flex items-center gap-1.5">
                <Code2 size={12} className="text-[#10b981]" />
                <span>Select Node Package Manager:</span>
              </span>
              <div className="flex items-center gap-1">
                {(['npm', 'pnpm', 'yarn', 'bun'] as const).map((pm) => (
                  <button
                    key={pm}
                    onClick={() => setNodePm(pm)}
                    className={`px-2 py-0.5 rounded text-[10px] font-mono transition border ${
                      nodePm === pm
                        ? 'bg-[#10b981]/20 text-[#10b981] border-[#10b981]/50 font-bold'
                        : 'bg-[#141418] text-[#a1a1aa] border-[#27272a] hover:text-white'
                    }`}
                  >
                    {pm}
                  </button>
                ))}
              </div>
            </div>
          )}

          {activeInstallTab === 'pip' && (
            <div className="px-4 py-1.5 bg-[#0b0b0e] border-b border-[#1c1c20] flex items-center justify-between text-[11px] font-mono">
              <span className="text-[#71717a] flex items-center gap-1.5">
                <Package size={12} className="text-[#10b981]" />
                <span>Select Python Toolchain:</span>
              </span>
              <div className="flex items-center gap-1">
                {(['pip', 'uv', 'poetry'] as const).map((pm) => (
                  <button
                    key={pm}
                    onClick={() => setPythonPm(pm)}
                    className={`px-2 py-0.5 rounded text-[10px] font-mono transition border ${
                      pythonPm === pm
                        ? 'bg-[#10b981]/20 text-[#10b981] border-[#10b981]/50 font-bold'
                        : 'bg-[#141418] text-[#a1a1aa] border-[#27272a] hover:text-white'
                    }`}
                  >
                    {pm}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Interactive Terminal Command Row */}
          <div className="p-3.5 sm:p-5 flex items-center justify-between gap-3 bg-[#030304] font-mono text-xs sm:text-sm">
            <div className="flex items-center gap-2.5 truncate flex-1">
              <span className="text-[#10b981] font-bold select-none text-sm sm:text-base">❯</span>
              <code className="text-[#f59e0b] truncate selection:bg-[#10b981]/30 selection:text-white">
                {getDynamicCommand(activeInstallTab)}
              </code>
            </div>
            
            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={handleCopyCommand}
                className={`px-3 py-1.5 text-[11px] sm:text-xs font-mono font-bold transition-all rounded flex items-center gap-1.5 border shadow-sm ${
                  copiedCommand
                    ? 'bg-[#10b981] text-black border-[#10b981] shadow-[0_0_15px_rgba(16,185,129,0.3)]'
                    : 'bg-[#111115] text-[#ffffff] border-[#2e2e33] hover:border-[#10b981] hover:text-[#10b981]'
                }`}
                title="Copy command to clipboard"
              >
                {copiedCommand ? <Check size={13} className="stroke-[3]" /> : <Copy size={13} />}
                <span>{copiedCommand ? 'COPIED!' : 'COPY'}</span>
              </button>
            </div>
          </div>

          {/* Dynamic Context Descriptor */}
          <div className="px-3.5 sm:px-5 py-2.5 bg-[#08080a] border-t border-[#1a1a1e] flex flex-col sm:flex-row sm:items-center justify-between text-[11px] font-mono text-[#a1a1aa] gap-1.5">
            <div className="flex items-center gap-2 text-white">
              <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]" />
              <span className="text-[#e4e4e7] font-sans font-medium text-xs">
                {tabDetails[activeInstallTab].description}
              </span>
            </div>
            <div className="flex items-center gap-1.5 text-[#10b981] shrink-0">
              <Zap size={12} className="text-[#f59e0b]" />
              <span className="font-semibold">{tabDetails[activeInstallTab].latency}</span>
            </div>
          </div>

          {/* Footer Security Badges & Expandable Checksum Toggle */}
          <div className="px-3.5 sm:px-5 py-2 bg-[#050507] border-t border-[#161619] flex flex-wrap items-center justify-between text-[10px] sm:text-[11px] font-mono text-[#71717a] gap-2">
            <div className="flex items-center gap-3">
              <span className="inline-flex items-center gap-1 text-[#10b981]">
                <CheckCircle2 size={12} />
                <span>100% In-Memory</span>
              </span>
              <span>&bull;</span>
              <span className="inline-flex items-center gap-1 text-[#a1a1aa]">
                <Lock size={11} className="text-[#10b981]" />
                <span>Zero Telemetry</span>
              </span>
              <span>&bull;</span>
              <span className="hidden xs:inline text-[#a1a1aa]">FIPS 186-5 Ed25519</span>
            </div>

            <button
              onClick={() => setShowIntegrityDrawer(!showIntegrityDrawer)}
              className="inline-flex items-center gap-1 text-[#a1a1aa] hover:text-[#10b981] transition"
            >
              <span>{showIntegrityDrawer ? '[Hide Checksums]' : '[Verify Checksum & Integrity]'}</span>
              {showIntegrityDrawer ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>
          </div>

          {/* Expandable Cryptographic Checksum & Audit Drawer */}
          {showIntegrityDrawer && (
            <div className="p-4 bg-[#020203] border-t border-[#1f1f23] font-mono text-[11px] text-[#a1a1aa] space-y-2 animate-in fade-in duration-200">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pb-2 border-b border-[#1c1c20]">
                <div>
                  <span className="text-[#71717a] block text-[10px] uppercase">Package Tarball Registry</span>
                  <span className="text-[#10b981] break-all">registry.npmjs.org/btp-guard/-/btp-guard-2.5.0.tgz</span>
                </div>
                <div>
                  <span className="text-[#71717a] block text-[10px] uppercase">Canonical Serialization</span>
                  <span className="text-white">RFC 8785 JSON Canonicalization Scheme (JCS)</span>
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div>
                  <span className="text-[#71717a] block text-[10px] uppercase">SHA-256 Release Digest</span>
                  <span className="text-[#f59e0b] break-all">3c8e77a807f7f90be092b3a985e5ebad6b0c20188efee31e7c98b67cc1d89fa3</span>
                </div>
                <div>
                  <span className="text-[#71717a] block text-[10px] uppercase">Cryptographic Identity Signer</span>
                  <span className="text-white">itsub_sa &lt;itsub@bartholomew.info&gt; (Ed25519)</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Integration Selector - Frontier Glassmorphism */}
        <div className="rounded-xl border border-[#27272a] max-w-3xl mx-auto bg-gradient-to-b from-[#0e0e11] via-[#09090b] to-[#040405] p-6 shadow-[0_20px_50px_-20px_rgba(16,185,129,0.12)] relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-[#10b981]/40 to-transparent pointer-events-none" />

          <div className="text-xs font-mono text-[#10b981] uppercase tracking-wider font-bold mb-4 flex items-center gap-2">
            <Cpu size={14} className="text-[#10b981]" />
            <span>[ SELECT YOUR INTEGRATION OR RUNTIME ]</span>
          </div>

          {/* Framework Selector Buttons */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 mb-6">
            {(['simple', 'claude', 'openai', 'gemini', 'kimi', 'langchain'] as const).map((agent) => (
              <button
                key={agent}
                onClick={() => setSelectedAgent(agent)}
                className={`p-2.5 text-left transition font-mono border rounded-lg ${
                  selectedAgent === agent
                    ? 'bg-[#10b981]/15 border-[#10b981] text-white shadow-[0_0_15px_rgba(16,185,129,0.2)]'
                    : 'bg-[#0b0b0e] border-[#222226] text-[#a1a1aa] hover:text-[#ffffff] hover:border-[#38383f]'
                }`}
              >
                <div className={`text-[10px] uppercase mb-1 font-bold ${selectedAgent === agent ? 'text-[#10b981]' : 'text-[#71717a]'}`}>
                  [{agent === 'simple' ? 'PYTHON' : agent.toUpperCase()}]
                </div>
                <div className="text-xs font-semibold truncate text-white">
                  {agent === 'simple' ? '3-Line Guard' :
                   agent === 'claude' ? 'Claude 5' :
                   agent === 'openai' ? 'GPT-6 Astra' :
                   agent === 'gemini' ? 'Gemini 2.5' :
                   agent === 'kimi' ? 'Moonshot Kimi' : 'Swarms'}
                </div>
              </button>
            ))}
          </div>

          {/* Code Preview */}
          <div className="bg-[#030304] border border-[#1f1f23] rounded-lg overflow-hidden shadow-inner">
            <div className="flex items-center justify-between px-4 py-2 bg-[#09090c] border-b border-[#1f1f23] text-xs font-mono">
              <span className="text-[#a1a1aa] flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]" />
                <span>{currentSnippet.filename}</span>
              </span>
              <button
                onClick={handleCopySnippet}
                className="text-[#10b981] hover:text-white font-bold flex items-center gap-1 transition"
              >
                {copiedCode ? <Check size={11} className="stroke-[3]" /> : <Copy size={11} />}
                <span>{copiedCode ? '[COPIED]' : '[COPY SNIPPET]'}</span>
              </button>
            </div>
            <pre className="p-4 font-mono text-xs text-[#d4d4d8] leading-relaxed overflow-x-auto selection:bg-[#10b981]/30">
              {currentSnippet.code}
            </pre>
            <div className="p-3 bg-[#070709] border-t border-[#1a1a1e] text-xs text-[#a1a1aa] font-sans">
              {currentSnippet.desc}
            </div>
          </div>
        </div>

      </div>
    </section>
  )
}
