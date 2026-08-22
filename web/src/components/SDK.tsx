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
      className="text-xs font-mono font-semibold px-2.5 py-1 bg-[#141414] hover:bg-[#222222] border border-[#333333] text-[#d4d4d8] hover:text-white transition flex items-center gap-1"
    >
      {copied ? <Check size={11} className="text-[#10b981]" /> : <Copy size={11} />}
      <span>{copied ? '[COPIED]' : '[COPY]'}</span>
    </button>
  )
}

export default function SDK() {
  const [activeTab, setActiveTab] = useState(TABS[0].id)
  const current = TABS.find((t) => t.id === activeTab) || TABS[0]

  return (
    <section id="sdk" className="py-24 bg-black border-t border-[#1c1c1c] text-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#0a0a0a] border border-[#222222] text-[#f59e0b] text-xs font-mono font-bold uppercase tracking-wider mb-4">
            <Shield size={13} className="text-[#f59e0b]" />
            <span>[ IN-PROCESS TOOL EXECUTION GATING ]</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white font-sans">
            Protect Agent Tool Execution in 3 Lines
          </h2>
          <p className="mt-4 text-base text-[#a1a1aa] font-sans">
            Bartholomew gates tool execution directly in application memory. Intercepts bash, SQL, and API payloads before they execute on your host or database.
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex flex-wrap gap-2 mb-4">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 text-xs font-mono font-bold transition border ${
                activeTab === tab.id
                  ? 'bg-[#f59e0b] text-[#000000] border-[#f59e0b]'
                  : 'bg-[#0a0a0a] text-[#a1a1aa] border-[#222222] hover:text-[#ffffff]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Code Box */}
        <div className="bg-[#0a0a0a] border border-[#222222] shadow-2xl overflow-hidden">
          <div className="flex items-center justify-between px-4 py-2.5 bg-[#000000] border-b border-[#222222]">
            <span className="text-xs font-mono text-[#a1a1aa] flex items-center gap-2">
              <Code2 size={13} className="text-[#f59e0b]" />
              {current.filename}
            </span>
            <CopyButton text={current.code} />
          </div>
          <pre className="p-6 font-mono text-xs sm:text-sm text-[#d4d4d8] leading-relaxed overflow-x-auto bg-[#000000]">
            <code>{current.code}</code>
          </pre>
        </div>
      </div>
    </section>
  )
}
