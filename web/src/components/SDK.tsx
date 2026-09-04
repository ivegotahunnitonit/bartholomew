import { useState } from 'react'
import { Copy, Check, Code2, Shield } from 'lucide-react'

const TABS = [
  {
    id: 'wrapper',
    label: '[TOOL GUARD DECORATOR (PYTHON)]',
    filename: 'agent_tool_guard.py',
    code: `from btp_guard import Guard

# Initialize guard with spend cap and retry dampening
guard = Guard(spend_cap=100.0, max_retries=5)

# Protect tool execution functions (Bash, SQL, Payments)
@guard.protect
def execute_sql_query(query: str):
    # Blocked before DB execution if query contains DROP TABLE or schema corruption
    return db.execute(query)

@guard.protect
def execute_shell_command(command: str):
    # Enforces hermetic sandbox scoping and blocks destructive commands
    return run_in_sandbox(command)`,
    lang: 'python',
  },
  {
    id: 'langchain',
    label: '[LANGCHAIN & CREWAI PLUGIN]',
    filename: 'langchain_guard_handler.py',
    code: `from btp_guard import Guard
from langchain.agents import initialize_agent

# Attach BTP invariant guard to agent tool calls
guard = Guard(spend_cap=200.0, max_retries=6)

# Direct tool check before execution
def on_agent_action(action):
    result = guard.check(action.tool_input, amount_usd=5.0)
    if not result["allowed"]:
        raise PermissionError(result["reason"])
    return execute_tool(action.tool, action.tool_input)`,
    lang: 'python',
  },
  {
    id: 'typescript',
    label: '[TYPESCRIPT / NODE.JS SDK]',
    filename: 'agent_evaluator.ts',
    code: `import { BartholomewTrustAuthority } from '@bartholomew/btp-guard';

const authority = new BartholomewTrustAuthority();

// Evaluate agent tool call in caller memory
const { allowed, reason, signature } = authority.evaluateIntent({
  agentId: 'worker-01',
  actionType: 'EXECUTE_TOOL',
  payload: { command: 'git status' }
});`,
    lang: 'typescript',
  },
  {
    id: 'go',
    label: '[GO INVARIANT ENGINE]',
    filename: 'main.go',
    code: `package main

import (
    "fmt"
    "github.com/ivegotahunnitonit/bartholomew/sdk_go/btp"
)

func main() {
    authority := btp.NewBartholomewTrustAuthority(300)
    receipt, err := authority.EvaluateIntent("agent_go", "EXEC_TOOL", map[string]any{"cmd": "ls"})
    if err == nil {
        fmt.Printf("BTP Ed25519 Signature: %s\\n", receipt.Signature)
    }
}`,
    lang: 'go',
  },
]

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  const handleCopy = () => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <button
      onClick={handleCopy}
      className="text-xs font-mono font-semibold px-3 py-1.5 bg-[#14141a] hover:bg-[#202028] border border-[#2e2e38] text-[#d4d4d8] hover:text-white rounded-lg transition flex items-center gap-1.5 cursor-pointer"
    >
      {copied ? <Check size={12} className="text-[#10b981]" /> : <Copy size={12} />}
      <span>{copied ? '[COPIED]' : '[COPY]'}</span>
    </button>
  )
}

export default function SDK() {
  const [activeTab, setActiveTab] = useState(TABS[0].id)
  const current = TABS.find((t) => t.id === activeTab) || TABS[0]

  return (
    <section id="sdk" className="py-24 bg-[#040406] border-t border-[#27272a]/70 text-white relative overflow-hidden">
      {/* Top ambient glowing accent line */}
      <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#f59e0b]/70 to-transparent pointer-events-none" />

      {/* Background glow accents */}
      <div className="absolute top-1/3 right-1/4 w-[600px] h-[300px] bg-gradient-to-b from-[#f59e0b]/10 to-transparent blur-[140px] pointer-events-none" />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-[#f59e0b]/10 border border-[#f59e0b]/30 text-[#f59e0b] rounded-full text-xs font-mono font-bold tracking-wider mb-4 shadow-[0_0_15px_rgba(245,158,11,0.15)]">
            <Shield size={13} className="text-[#f59e0b]" />
            <span>[ IN-PROCESS TOOL EXECUTION GATING ]</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white font-sans">
            Protect Agent Tool Execution in 3 Lines
          </h2>
          <p className="mt-4 text-base text-[#a1a1aa] font-sans leading-relaxed">
            Bartholomew gates tool execution directly in application memory. Intercepts bash, SQL, and API payloads before they execute on your host or database.
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex flex-wrap gap-2.5 mb-5">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2.5 text-xs font-mono font-bold rounded-xl transition-all duration-200 border cursor-pointer ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-[#f59e0b] to-[#d97706] text-black border-[#f59e0b] shadow-[0_0_20px_rgba(245,158,11,0.25)]'
                  : 'bg-[#08080c] text-[#a1a1aa] border-[#27272a] hover:text-white hover:border-[#444455]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Code Box */}
        <div className="bg-gradient-to-b from-[#0e0e14]/95 via-[#09090d]/95 to-[#050507] border border-[#27272a]/80 rounded-2xl shadow-2xl overflow-hidden relative backdrop-blur-xl">
          <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#f59e0b]/50 to-transparent pointer-events-none" />

          <div className="flex items-center justify-between px-5 py-3.5 bg-[#111118]/80 border-b border-[#27272a]/70">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 mr-1">
                <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
                <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
              </div>
              <span className="text-xs font-mono text-[#d4d4d8] flex items-center gap-2">
                <Code2 size={14} className="text-[#f59e0b]" />
                {current.filename}
              </span>
            </div>
            <CopyButton text={current.code} />
          </div>
          <pre className="p-6 sm:p-7 font-mono text-xs sm:text-sm text-[#d4d4d8] leading-relaxed overflow-x-auto bg-[#030305]">
            <code>{current.code}</code>
          </pre>
        </div>
      </div>
    </section>
  )
}
