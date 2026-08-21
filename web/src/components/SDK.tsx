import { useState } from 'react'
import { Copy, Check, Code2 } from 'lucide-react'

const TABS = [
  {
    id: 'wrapper',
    label: '1-Line Client Wrapper (Python)',
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
      className="flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition border border-slate-700"
    >
      {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
      <span>{copied ? 'Copied' : 'Copy'}</span>
    </button>
  )
}

export default function SDK() {
  const [activeTab, setActiveTab] = useState(TABS[0].id)
  const current = TABS.find(t => t.id === activeTab) || TABS[0]

  return (
    <section id="sdk" className="py-24 px-5 sm:px-8 bg-slate-950 text-white border-t border-slate-900">
      <div className="max-w-5xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <Code2 size={13} />
            Multi-Language SDKs
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
            1-Line Integration Across All Runtimes
          </h2>
          <p className="mt-3 text-slate-400 text-sm sm:text-base">
            Drop BTP cryptographic guardrails directly into Python, TypeScript, or Go agents.
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex flex-wrap gap-2 mb-4 bg-slate-900/60 p-1.5 rounded-xl border border-slate-800">
          {TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg text-xs font-semibold transition ${
                activeTab === tab.id
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Code Viewer */}
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl relative">
          <div className="flex items-center justify-between gap-4 pb-4 mb-4 border-b border-slate-800/80">
            <span className="text-xs font-mono text-cyan-400">{current.label}</span>
            <CopyButton text={current.code} />
          </div>
          <pre className="font-mono text-xs sm:text-sm text-slate-200 overflow-x-auto leading-relaxed">
            {current.code}
          </pre>
        </div>
      </div>
    </section>
  )
}
