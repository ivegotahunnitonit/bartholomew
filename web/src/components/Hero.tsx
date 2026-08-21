import { useState } from 'react'
import { Download, Check, Copy, Cpu, CheckCircle2 } from 'lucide-react'

type AgentTarget = 'claude' | 'openai' | 'langchain' | 'custom'
type InstallTarget = 'windows' | 'mac' | 'pip' | 'npm'

export default function Hero() {
  const [selectedAgent, setSelectedAgent] = useState<AgentTarget>('claude')
  const [activeInstallTab, setActiveInstallTab] = useState<InstallTarget>('windows')
  const [copiedCode, setCopiedCode] = useState(false)
  const [copiedCommand, setCopiedCommand] = useState(false)

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

  return (
    <section className="relative min-h-[96vh] flex flex-col justify-center pt-28 pb-20 px-5 sm:px-8 bg-black text-white overflow-hidden">
      <div className="max-w-5xl mx-auto w-full relative z-10">
        {/* Floating Status Pill Indicator */}
        <div className="flex items-center justify-center mb-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-[#0a0a0a] border border-[#2a2a2a] text-xs sm:text-sm font-mono font-bold uppercase tracking-wider text-[#d4d4d8] shadow-sm">
            <span className="w-2 h-2 bg-[#10b981] animate-pulse" />
            <span className="text-[#10b981]">[BTP v2.2 ACTIVE]</span>
            <span className="text-[#666666]">|</span>
            <span>UNIVERSAL COMPATIBILITY · READY FOR ALL AI AGENTS &amp; FRAMEWORKS</span>
          </div>
        </div>

        {/* Action-Oriented Hero Headline */}
        <h1
          className="text-center font-bold mb-5 font-sans hero-metallic-title"
          style={{
            fontSize: 'clamp(2.15rem, 4vw, 3.4rem)',
            lineHeight: 1.14,
            letterSpacing: '-0.025em'
          }}
        >
          Pair Bartholomew With Your AI Agents.
        </h1>

        {/* Action-Oriented Subtitle */}
        <p className="text-center mx-auto mb-10 text-[#e4e4e7] leading-relaxed max-w-2xl text-base font-sans">
          Download the sub-millisecond local engine or drop the SDK wrapper straight into your Python, Node, or Go projects. Wrap any AI agent, framework, or custom script in a single line of code with guaranteed cryptographic boundaries.
        </p>

        {/* Front-and-Center 1-Click Terminal Box */}
        <div className="bg-[#0a0a0a] border border-[#262626] max-w-3xl mx-auto mb-12 shadow-2xl overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 bg-[#000000] border-b border-[#262626]">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 bg-[#ef4444]" />
              <div className="w-2.5 h-2.5 bg-[#f59e0b]" />
              <div className="w-2.5 h-2.5 bg-[#10b981]" />
            </div>
            <span className="text-xs font-mono text-[#9ca3af]">quick-install-terminal</span>
            <div className="flex items-center gap-2">
              <a
                href={activeInstallTab === 'windows' ? '/install.bat' : '/install.sh'}
                download={activeInstallTab === 'windows' ? 'install.bat' : 'install.sh'}
                className="text-xs font-mono text-[#f59e0b] hover:underline flex items-center gap-1 font-bold"
              >
                <Download size={12} />
                <span>Direct File Download</span>
              </a>
            </div>
          </div>

          {/* Tab Selector */}
          <div className="flex bg-[#000000] border-b border-[#262626] p-1.5 gap-1.5">
            {(['windows', 'mac', 'pip', 'npm'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveInstallTab(tab)}
                className={`flex-1 py-2 px-2 text-xs sm:text-sm font-mono font-bold transition border ${
                  activeInstallTab === tab
                    ? 'bg-[#f59e0b] text-[#000000] border-[#f59e0b]'
                    : 'bg-[#0a0a0a] text-[#c4c4cc] border-[#262626] hover:text-[#ffffff]'
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
          <div className="p-4 sm:p-5 flex items-center justify-between gap-3 bg-[#000000] font-mono text-sm text-[#f59e0b]">
            <span className="truncate font-semibold">$ {installCommands[activeInstallTab]}</span>
            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={handleCopyCommand}
                className={`px-3.5 py-1.5 text-xs sm:text-sm font-mono font-bold transition flex items-center gap-1.5 border ${
                  copiedCommand
                    ? 'bg-[#10b981] text-[#000000] border-[#10b981]'
                    : 'bg-[#0a0a0a] text-[#ffffff] border-[#383838] hover:border-[#666666]'
                }`}
              >
                {copiedCommand ? <Check size={13} /> : <Copy size={13} />}
                <span>{copiedCommand ? '[COPIED]' : '[COPY]'}</span>
              </button>
            </div>
          </div>

          <div className="px-5 py-3 bg-[#0a0a0a] border-t border-[#202020] flex items-center justify-between text-xs sm:text-sm font-mono text-[#d4d4d8]">
            <span className="text-[#10b981] flex items-center gap-1.5 font-semibold">
              <CheckCircle2 size={14} />
              Guard Active: Localhost (In-Memory | &lt;50 µs)
            </span>
            <span className="text-[#9ca3af]">Zero Cloud Telemetry</span>
          </div>
        </div>

        {/* Interactive Compatibility Matrix */}
        <div className="border border-[#262626] max-w-3xl mx-auto bg-[#0a0a0a] p-6 shadow-2xl">
          <div className="text-xs sm:text-sm font-mono text-[#f59e0b] uppercase tracking-wider font-bold mb-3 flex items-center gap-2">
            <Cpu size={15} />
            <span>[ SELECT YOUR FRAMEWORK OR RUNTIME TO PAIR ]</span>
          </div>

          {/* Compatibility Selector Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mb-6">
            {(['claude', 'openai', 'langchain', 'custom'] as const).map((agent) => (
              <button
                key={agent}
                onClick={() => setSelectedAgent(agent)}
                className={`p-3.5 text-left transition font-mono border ${
                  selectedAgent === agent
                    ? 'bg-[#161616] border-[#f59e0b] text-white shadow-md'
                    : 'bg-[#000000] border-[#262626] text-[#c4c4cc] hover:text-[#ffffff] hover:border-[#444444]'
                }`}
              >
                <div className="text-xs text-[#f59e0b] uppercase mb-1 font-bold">[{agent.toUpperCase()}]</div>
                <div className="text-xs sm:text-sm font-semibold truncate">{agentPairingSnippets[agent].title.split(' ')[0]}</div>
              </button>
            ))}
          </div>

          {/* Dynamic Pairing Code Preview */}
          <div className="bg-[#000000] border border-[#262626] overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2.5 bg-[#0a0a0a] border-b border-[#262626] text-xs sm:text-sm font-mono">
              <span className="text-[#d4d4d8] font-semibold">{currentSnippet.filename}</span>
              <button
                onClick={handleCopySnippet}
                className="text-[#f59e0b] hover:text-white font-bold flex items-center gap-1"
              >
                {copiedCode ? <Check size={12} /> : <Copy size={12} />}
                <span>{copiedCode ? '[COPIED]' : '[COPY SNIPPET]'}</span>
              </button>
            </div>
            <pre className="p-4 sm:p-5 font-mono text-xs sm:text-sm text-[#e4e4e7] leading-relaxed overflow-x-auto">
              {currentSnippet.code}
            </pre>
            <div className="p-3.5 bg-[#0a0a0a] border-t border-[#262626] text-xs sm:text-sm text-[#d4d4d8] font-sans">
              {currentSnippet.desc}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
