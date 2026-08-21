import { useState, useEffect } from 'react'
import { Download, Check, Copy, Cpu, CheckCircle2, ChevronDown } from 'lucide-react'

type AgentTarget = 'claude' | 'openai' | 'langchain' | 'custom'
type InstallTarget = 'windows' | 'mac' | 'pip' | 'npm'

export default function Hero() {
  const [selectedAgent, setSelectedAgent] = useState<AgentTarget>('claude')
  const [activeInstallTab, setActiveInstallTab] = useState<InstallTarget>('windows')
  const [copiedCode, setCopiedCode] = useState(false)
  const [copiedCommand, setCopiedCommand] = useState(false)
  const [showDownloadMenu, setShowDownloadMenu] = useState(false)
  const [osName, setOsName] = useState<'windows' | 'mac' | 'linux'>('windows')

  useEffect(() => {
    const userAgent = window.navigator.userAgent.toLowerCase()
    if (userAgent.includes('mac')) {
      setOsName('mac')
      setActiveInstallTab('mac')
    } else if (userAgent.includes('linux')) {
      setOsName('linux')
      setActiveInstallTab('mac')
    } else {
      setOsName('windows')
      setActiveInstallTab('windows')
    }
  }, [])

  const installCommands = {
    windows: 'irm https://bartholomew.info/install.ps1 | iex',
    mac: 'curl -fsSL https://bartholomew.info/install.sh | bash',
    pip: 'pip install git+https://github.com/ivegotahunnitonit/bartholomew.git',
    npm: 'npm i @bartholomew/btp-guard'
  }

  const agentPairingSnippets: Record<AgentTarget, { title: string; filename: string; code: string; desc: string }> = {
    claude: {
      title: 'Claude Desktop / Anthropic',
      filename: 'claude_agent_guard.py',
      desc: 'Intercepts tool execution calls from Claude Desktop before any OS subprocess or file mutation executes.',
      code: `from btp_guard import wrap_client
import anthropic

# 1-Line Bartholomew Drop-In Guard
client = wrap_client(anthropic.Anthropic())

# Destructive tool calls (rm -rf, DROP TABLE) are blocked in <50 µs
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Analyze project codebase"}]
)`
    },
    openai: {
      title: 'OpenAI Assistants & Cursor',
      filename: 'openai_assistant_guard.py',
      desc: 'Wraps GPT-4o / Cursor agent function calling with hermetic path bounding and spend caps.',
      code: `from btp_guard import wrap_client
import openai

# 1-Line Bartholomew Drop-In Guard
client = wrap_client(openai.OpenAI())

# Any rogue command outside ./workspace is trapped in memory
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Execute database refactoring"}]
)`
    },
    langchain: {
      title: 'LangChain & CrewAI Swarms',
      filename: 'swarm_callback_guard.py',
      desc: 'Attaches a sub-millisecond invariant callback to entire multi-agent swarms.',
      code: `from btp_guard import BTPCallbackHandler
from langchain.agents import initialize_agent

# Attach BTP sub-millisecond callback handler
handler = BTPCallbackHandler(policy_file=".btp/policy.yaml")

agent = initialize_agent(
    tools=tools,
    llm=llm,
    callbacks=[handler]
)`
    },
    custom: {
      title: 'Custom Python & TS Scripts',
      filename: 'sovereign_evaluator.ts',
      desc: 'Microsecond in-process intent evaluator for custom autonomous agent loops.',
      code: `import { BartholomewTrustAuthority } from '@bartholomew/btp-guard';

const authority = new BartholomewTrustAuthority();

// Evaluate agent tool call in <50 microseconds
const { allowed, reason, signature } = authority.evaluateIntent({
  agentId: 'worker-node-01',
  actionType: 'EXECUTE_TOOL',
  payload: { command: 'git status' }
});`
    }
  }

  const currentSnippet = agentPairingSnippets[selectedAgent]

  const handleCopySnippet = () => {
    navigator.clipboard.writeText(currentSnippet.code)
    setCopiedCode(true)
    setTimeout(() => setCopiedCode(false), 2000)
  }

  const handleCopyCommand = () => {
    navigator.clipboard.writeText(installCommands[activeInstallTab])
    setCopiedCommand(true)
    setTimeout(() => setCopiedCommand(false), 2000)
  }

  const handleDirectDownload = () => {
    if (osName === 'windows') {
      window.location.href = '/install.bat'
    } else {
      window.location.href = '/install.sh'
    }
  }

  return (
    <section className="relative min-h-[96vh] flex flex-col justify-center pt-28 pb-20 px-5 sm:px-8 bg-black text-white overflow-hidden">
      <div className="max-w-5xl mx-auto w-full relative z-10">
        {/* Floating Status Pill Indicator */}
        <div className="flex items-center justify-center mb-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 bg-[#0a0a0a] border border-[#222222] text-xs font-mono font-bold uppercase tracking-wider text-[#a1a1aa] shadow-sm">
            <span className="w-2 h-2 bg-[#10b981] animate-pulse" />
            <span className="text-[#10b981]">[BTP v2.2 ACTIVE]</span>
            <span className="text-[#555555]">|</span>
            <span className="text-[#d4d4d8]">UNIVERSAL COMPATIBILITY · READY FOR ALL AI AGENTS &amp; FRAMEWORKS</span>
          </div>
        </div>

        {/* Action-Oriented Hero Headline */}
        <h1
          className="text-center font-bold mb-5 font-sans hero-metallic-title"
          style={{
            fontSize: 'clamp(2.1rem, 3.8vw, 3.25rem)',
            lineHeight: 1.12,
            letterSpacing: '-0.025em'
          }}
        >
          Pair Bartholomew With Your AI Agents.
        </h1>

        {/* Action-Oriented Subtitle */}
        <p className="text-center mx-auto mb-8 text-[#d4d4d8] leading-relaxed max-w-2xl text-sm sm:text-base font-sans">
          Download the sub-millisecond local engine or drop the SDK wrapper straight into your Python, Node, or Go projects. Wrap any AI agent, framework, or custom script in a single line of code with guaranteed cryptographic boundaries.
        </p>

        {/* 1-Click Direct Download & Copy CTA Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 mb-10 relative">
          <div className="relative">
            <div className="inline-flex rounded-none shadow-lg">
              <button
                onClick={handleDirectDownload}
                className="px-6 py-3 text-sm font-mono font-bold bg-[#f59e0b] hover:bg-[#d97706] text-[#000000] border border-[#f59e0b] transition flex items-center gap-2"
              >
                <Download size={15} />
                <span>[ 1-CLICK DOWNLOAD ({osName === 'windows' ? 'WINDOWS .BAT' : 'MACOS/LINUX .SH'}) ]</span>
              </button>
              <button
                onClick={() => setShowDownloadMenu(!showDownloadMenu)}
                className="px-3 py-3 bg-[#d97706] hover:bg-[#b45309] text-[#000000] border-t border-b border-r border-[#f59e0b] transition flex items-center justify-center"
                aria-label="More download options"
              >
                <ChevronDown size={15} />
              </button>
            </div>

            {/* Dropdown Options */}
            {showDownloadMenu && (
              <div className="absolute left-0 mt-1 w-64 bg-[#0a0a0a] border border-[#222222] shadow-2xl z-50 font-mono text-xs">
                <a
                  href="/install.bat"
                  download="install.bat"
                  onClick={() => setShowDownloadMenu(false)}
                  className="p-3 block hover:bg-[#141414] text-[#d4d4d8] hover:text-[#ffffff] border-b border-[#1a1a1a]"
                >
                  <div className="font-bold text-[#f59e0b]">[DOWNLOAD FOR WINDOWS]</div>
                  <div className="text-[10px] text-[#71717a]">install.bat (Direct 1-Click)</div>
                </a>
                <a
                  href="/install.ps1"
                  download="install.ps1"
                  onClick={() => setShowDownloadMenu(false)}
                  className="p-3 block hover:bg-[#141414] text-[#d4d4d8] hover:text-[#ffffff] border-b border-[#1a1a1a]"
                >
                  <div className="font-bold text-[#10b981]">[POWERSHELL SCRIPT]</div>
                  <div className="text-[10px] text-[#71717a]">install.ps1</div>
                </a>
                <a
                  href="/install.sh"
                  download="install.sh"
                  onClick={() => setShowDownloadMenu(false)}
                  className="p-3 block hover:bg-[#141414] text-[#d4d4d8] hover:text-[#ffffff]"
                >
                  <div className="font-bold text-[#ffffff]">[MACOS / LINUX BASH]</div>
                  <div className="text-[10px] text-[#71717a]">install.sh (Direct 1-Click)</div>
                </a>
              </div>
            )}
          </div>

          <button
            onClick={handleCopySnippet}
            className="px-6 py-3 text-sm font-mono font-semibold bg-[#0a0a0a] hover:bg-[#141414] border border-[#222222] hover:border-[#444444] text-[#ffffff] transition flex items-center gap-2"
          >
            <Copy size={15} className="text-[#10b981]" />
            <span>{copiedCode ? '[ COPIED WRAPPER ]' : '[ COPY SDK WRAPPER ]'}</span>
          </button>
        </div>

        {/* Front-and-Center 1-Click Terminal Box */}
        <div className="bg-[#0a0a0a] border border-[#222222] max-w-3xl mx-auto mb-12 shadow-2xl overflow-hidden">
          <div className="flex items-center justify-between px-4 py-2 bg-[#000000] border-b border-[#222222]">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 bg-[#ef4444]" />
              <div className="w-2.5 h-2.5 bg-[#f59e0b]" />
              <div className="w-2.5 h-2.5 bg-[#10b981]" />
            </div>
            <span className="text-[11px] font-mono text-[#71717a]">quick-install-terminal</span>
            <div className="flex items-center gap-2">
              <a
                href={activeInstallTab === 'windows' ? '/install.bat' : '/install.sh'}
                download={activeInstallTab === 'windows' ? 'install.bat' : 'install.sh'}
                className="text-[10px] font-mono text-[#f59e0b] hover:underline flex items-center gap-1"
              >
                <Download size={10} />
                <span>Direct File</span>
              </a>
            </div>
          </div>

          {/* Tab Selector */}
          <div className="flex bg-[#000000] border-b border-[#222222] p-1.5 gap-1.5">
            {(['windows', 'mac', 'pip', 'npm'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveInstallTab(tab)}
                className={`flex-1 py-1.5 px-2 text-xs font-mono font-bold transition border ${
                  activeInstallTab === tab
                    ? 'bg-[#f59e0b] text-[#000000] border-[#f59e0b]'
                    : 'bg-[#0a0a0a] text-[#a1a1aa] border-[#222222] hover:text-[#ffffff]'
                }`}
              >
                {tab === 'windows' && '[WINDOWS]'}
                {tab === 'mac' && '[MACOS / BASH]'}
                {tab === 'pip' && '[PYTHON PIP]'}
                {tab === 'npm' && '[NODE NPM]'}
              </button>
            ))}
          </div>

          {/* Command Row */}
          <div className="p-4 sm:p-5 flex items-center justify-between gap-3 bg-[#000000] font-mono text-xs sm:text-sm text-[#f59e0b]">
            <span className="truncate">$ {installCommands[activeInstallTab]}</span>
            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={handleCopyCommand}
                className={`px-3 py-1.5 text-xs font-mono font-bold transition flex items-center gap-1.5 border ${
                  copiedCommand
                    ? 'bg-[#10b981] text-[#000000] border-[#10b981]'
                    : 'bg-[#0a0a0a] text-[#ffffff] border-[#333333] hover:border-[#555555]'
                }`}
              >
                {copiedCommand ? <Check size={12} /> : <Copy size={12} />}
                <span>{copiedCommand ? '[COPIED]' : '[COPY]'}</span>
              </button>
            </div>
          </div>

          <div className="px-5 py-2.5 bg-[#0a0a0a] border-t border-[#1c1c1c] flex items-center justify-between text-xs font-mono text-[#a1a1aa]">
            <span className="text-[#10b981] flex items-center gap-1.5">
              <CheckCircle2 size={13} />
              Guard Active: Localhost (In-Memory | &lt;50 µs)
            </span>
            <span className="text-[#71717a]">Zero Cloud Telemetry</span>
          </div>
        </div>

        {/* Interactive Compatibility Matrix */}
        <div className="border border-[#222222] max-w-3xl mx-auto bg-[#0a0a0a] p-6 shadow-2xl">
          <div className="text-xs font-mono text-[#f59e0b] uppercase tracking-wider font-bold mb-2 flex items-center gap-2">
            <Cpu size={14} />
            <span>[ SELECT YOUR FRAMEWORK OR RUNTIME TO PAIR ]</span>
          </div>

          {/* Compatibility Selector Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-6">
            {(['claude', 'openai', 'langchain', 'custom'] as const).map((agent) => (
              <button
                key={agent}
                onClick={() => setSelectedAgent(agent)}
                className={`p-3 text-left transition font-mono border ${
                  selectedAgent === agent
                    ? 'bg-[#141414] border-[#f59e0b] text-white shadow-sm'
                    : 'bg-[#000000] border-[#222222] text-[#a1a1aa] hover:text-[#ffffff] hover:border-[#383838]'
                }`}
              >
                <div className="text-[10px] text-[#f59e0b] uppercase mb-1 font-bold">[{agent.toUpperCase()}]</div>
                <div className="text-xs font-semibold truncate">{agentPairingSnippets[agent].title.split(' ')[0]}</div>
              </button>
            ))}
          </div>

          {/* Dynamic Pairing Code Preview */}
          <div className="bg-[#000000] border border-[#222222] overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 bg-[#0a0a0a] border-b border-[#222222] text-xs font-mono">
              <span className="text-[#a1a1aa]">{currentSnippet.filename}</span>
              <button
                onClick={handleCopySnippet}
                className="text-[#f59e0b] hover:text-white font-bold flex items-center gap-1"
              >
                {copiedCode ? <Check size={11} /> : <Copy size={11} />}
                <span>{copiedCode ? '[COPIED]' : '[COPY SNIPPET]'}</span>
              </button>
            </div>
            <pre className="p-4 font-mono text-xs text-[#d4d4d8] leading-relaxed overflow-x-auto">
              {currentSnippet.code}
            </pre>
            <div className="p-3 bg-[#0a0a0a] border-t border-[#222222] text-xs text-[#a1a1aa] font-sans">
              {currentSnippet.desc}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
