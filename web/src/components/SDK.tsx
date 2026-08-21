import { useState } from 'react'
import { Copy, Check, Code2 } from 'lucide-react'

const TABS = [
  {
    id: 'wrapper',
    label: '1-Line Client Wrapper (Python)',
    filename: 'agent_safe_client.py',
    code: `from btp_guard import wrap_client
import openai

# Drop-in 1-line wrapper around OpenAI or Anthropic
client = wrap_client(openai.OpenAI())

# Any destructive SQL or filesystem breakout is intercepted in <50 µs
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Query inventory table"}]
)`,
    lang: 'python',
  },
  {
    id: 'langchain',
    label: 'LangChain & CrewAI Plugin',
    filename: 'langchain_guard_handler.py',
    code: `from btp_guard import BTPCallbackHandler
from langchain.agents import initialize_agent

# Attach BTP sub-millisecond callback handler
handler = BTPCallbackHandler(policy_file="policies/default_security_policy.yaml")

agent = initialize_agent(
    tools=tools,
    llm=llm,
    callbacks=[handler]
)`,
    lang: 'python',
  },
  {
    id: 'typescript',
    label: 'TypeScript / Node.js SDK',
    filename: 'agent_evaluator.ts',
    code: `import { BartholomewTrustAuthority, DeclarativePolicyEngine } from '@bartholomew/btp-guard';

const authority = new BartholomewTrustAuthority();
const policy = new DeclarativePolicyEngine('policies/default_security_policy.yaml');

// Evaluate agent tool call in <50 microseconds
const { allowed, reason, signature } = authority.evaluateIntent({
  agentId: 'worker-01',
  actionType: 'EXECUTE_TOOL',
  payload: { command: 'git status' }
});`,
    lang: 'typescript',
  },
  {
    id: 'go',
    label: 'Go Microsecond Engine',
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
      className={`flex items-center gap-1.5 text-xs px-3 py-1 rounded-lg transition border shadow-sm ${
        copied
          ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300'
          : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700 hover:border-cyan-400/50'
      }`}
    >
      {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
      <span>{copied ? 'Copied!' : 'Copy Code'}</span>
    </button>
  )
}

export default function SDK() {
  const [activeTab, setActiveTab] = useState(TABS[0].id)
  const current = TABS.find(t => t.id === activeTab) || TABS[0]

  return (
    <section id="sdk" className="py-24 px-5 sm:px-8 bg-slate-950 text-white border-t border-slate-900">
      <div className="max-w-5xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-400/30 text-cyan-300 text-xs font-mono font-bold uppercase tracking-wider mb-3 shadow-sm">
            <Code2 size={13} />
            Multi-Language SDKs
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white font-sans">
            1-Line Integration Across All Runtimes
          </h2>
          <p className="mt-3 text-slate-300 text-sm sm:text-base">
            Drop BTP cryptographic guardrails directly into Python, TypeScript, or Go agents.
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex flex-wrap gap-2 mb-4 bg-slate-900/60 p-2 rounded-2xl border border-white/10 backdrop-blur-md">
          {TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2.5 rounded-xl text-xs font-semibold transition-all duration-150 ${
                activeTab === tab.id
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/40 shadow-md shadow-cyan-500/10'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Code Viewer inside macOS Window Chrome */}
        <div className="rounded-2xl bg-slate-900/90 border border-white/10 shadow-2xl backdrop-blur-xl overflow-hidden hover:border-cyan-500/30 transition-all duration-200">
          {/* macOS Titlebar */}
          <div className="flex items-center justify-between px-4 py-3 bg-slate-950/80 border-b border-white/10">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-rose-500/80" />
              <div className="w-3 h-3 rounded-full bg-amber-500/80" />
              <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
            </div>
            <span className="text-[11px] font-mono text-slate-400">{current.filename}</span>
            <CopyButton text={current.code} />
          </div>

          <div className="p-6 sm:p-8">
            <pre className="font-mono text-xs sm:text-sm text-slate-200 overflow-x-auto leading-relaxed bg-slate-950 p-5 rounded-xl border border-white/5 shadow-inner">
              {current.code}
            </pre>
          </div>
        </div>
      </div>
    </section>
  )
}
