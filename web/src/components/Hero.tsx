import { useState } from 'react'
import { Check, Copy, Cpu, CheckCircle2, Shield } from 'lucide-react'

type AgentTarget = 'simple' | 'claude' | 'openai' | 'langchain'
type InstallTarget = 'pip' | 'npm' | 'vscode' | 'git'

export default function Hero() {
  const [selectedAgent, setSelectedAgent] = useState<AgentTarget>('simple')
  const [activeInstallTab, setActiveInstallTab] = useState<InstallTarget>('pip')
  const [copiedCode, setCopiedCode] = useState(false)
  const [copiedCommand, setCopiedCommand] = useState(false)

  const installCommands = {
    pip: 'pip install btp-guard',
    npm: 'npm install @bartholomew/btp-guard',
    vscode: 'code --install-extension https://bartholomew.info/bartholomew.vsix',
    git: 'git clone https://github.com/ivegotahunnitonit/bartholomew.git && cd bartholomew'
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
      title: 'Claude Desktop / MCP Server',
      filename: 'claude_desktop_config.json',
      desc: 'In-process MCP Guard for Claude Desktop. Intercepts tool calls and bash commands before OS execution.',
      code: `// In %APPDATA%/Claude/claude_desktop_config.json:
{
  "mcpServers": {
    "bartholomew-guard": {
      "command": "python",
      "args": ["-m", "mcp_server"]
    }
  }
}`
    },
    openai: {
      title: 'OpenAI Assistants & Cursor',
      filename: 'openai_assistant_guard.py',
      desc: 'Wraps GPT-4o / Cursor agent function calling with hermetic path containment and spend limits.',
      code: `from btp_guard import Guard
import openai

guard = Guard(spend_cap=50.0)

# Check tool calls before execution
def on_tool_call(name, args):
    res = guard.check(args.get("query", ""))
    if not res["allowed"]:
        return f"Error: {res['reason']}"
    return execute_safely(name, args)`
    },
    langchain: {
      title: 'LangChain & Multi-Agent Swarms',
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
    navigator.clipboard.writeText(installCommands[activeInstallTab])
    setCopiedCommand(true)
    setTimeout(() => setCopiedCommand(false), 2000)
  }

  return (
    <section className="relative min-h-[90vh] flex flex-col justify-center pt-28 pb-20 px-5 sm:px-8 bg-black text-white overflow-x-hidden">
      <div className="max-w-5xl mx-auto w-full relative z-10">
        
        {/* Status Pill */}
        <div className="flex items-center justify-center mb-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 bg-[#0a0a0a] border border-[#222222] text-xs font-mono font-bold uppercase tracking-wider text-[#a1a1aa] shadow-sm">
            <span className="w-2 h-2 bg-[#10b981] animate-pulse" />
            <span className="text-[#10b981]">[BTP v2.2.0 OPEN SOURCE]</span>
            <span className="text-[#555555]">|</span>
            <span className="text-[#d4d4d8]">SUB-5 µS DETERMINISTIC INVARIANT GATEWAY</span>
          </div>
        </div>

        {/* Hero Headline */}
        <div className="text-center max-w-4xl mx-auto mb-4 px-2">
          <h1
            className="font-bold font-sans hero-metallic-title text-center inline-block"
            style={{
              fontSize: 'clamp(2.2rem, 4vw, 3.5rem)',
              lineHeight: 1.25,
              letterSpacing: '-0.02em',
              paddingBottom: '0.18em'
            }}
          >
            Stop AI Agents from Breaking Things.
          </h1>
        </div>

        {/* Hero Subtitle */}
        <p className="text-center mx-auto mb-10 text-[#d4d4d8] leading-relaxed max-w-2xl text-sm sm:text-base font-sans">
          A fast, lightweight Python &amp; Node.js drop-in guard. Blocks destructive commands (<code>rm -rf</code>, <code>DROP TABLE</code>), runaway infinite loops, and budget spikes in &lt;5 microseconds.
        </p>

        {/* Standard Package Install Box (NO PIPED SCRIPTS) */}
        <div className="bg-[#0a0a0a] border border-[#222222] max-w-3xl mx-auto mb-12 shadow-2xl overflow-hidden">
          <div className="flex items-center justify-between px-4 py-2.5 bg-[#000000] border-b border-[#222222]">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 bg-[#ef4444]" />
              <div className="w-2.5 h-2.5 bg-[#f59e0b]" />
              <div className="w-2.5 h-2.5 bg-[#10b981]" />
            </div>
            <span className="text-[11px] font-mono text-[#71717a]">verified-package-install</span>
            <div className="flex items-center gap-2 text-[11px] font-mono text-[#10b981]">
              <Shield size={12} />
              <span>Zero-Daemon In-Process Library</span>
            </div>
          </div>

          {/* Tab Selector */}
          <div className="flex bg-[#000000] border-b border-[#222222] p-1.5 gap-1.5">
            {(['pip', 'npm', 'vscode', 'git'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveInstallTab(tab)}
                className={`flex-1 py-1.5 px-2 text-xs font-mono font-bold transition border ${
                  activeInstallTab === tab
                    ? 'bg-[#f59e0b] text-[#000000] border-[#f59e0b]'
                    : 'bg-[#0a0a0a] text-[#a1a1aa] border-[#222222] hover:text-[#ffffff]'
                }`}
              >
                {tab === 'pip' && '[PYTHON PYPI]'}
                {tab === 'npm' && '[NODE NPM]'}
                {tab === 'vscode' && '[VS CODE VSIX]'}
                {tab === 'git' && '[AUDITABLE SOURCE]'}
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
              <span>In-Memory Evaluation (&lt;5.0 µs Latency)</span>
            </span>
            <span className="text-[#71717a]">Zero Open Sockets · Zero Telemetry</span>
          </div>
        </div>

        {/* Integration Selector */}
        <div className="border border-[#222222] max-w-3xl mx-auto bg-[#0a0a0a] p-6 shadow-2xl">
          <div className="text-xs font-mono text-[#f59e0b] uppercase tracking-wider font-bold mb-3 flex items-center gap-2">
            <Cpu size={14} />
            <span>[ SELECT YOUR INTEGRATION OR RUNTIME ]</span>
          </div>

          {/* Framework Selector Buttons */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-6">
            {(['simple', 'claude', 'openai', 'langchain'] as const).map((agent) => (
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

          {/* Code Preview */}
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
