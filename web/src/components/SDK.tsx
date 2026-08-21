import { useState } from 'react'
import { Copy, Check, Code2 } from 'lucide-react'

const TABS = [
  {
    id: 'wrapper',
    label: '[1-LINE CLIENT WRAPPER (PYTHON)]',
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
    label: '[LANGCHAIN & CREWAI PLUGIN]',
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
    label: '[TYPESCRIPT / NODE.JS SDK]',
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
    label: '[GO MICROSECOND ENGINE]',
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
      className={`flex items-center gap-1.5 text-xs sm:text-sm font-mono font-bold px-3 py-1.5 transition border ${
        copied
          ? 'bg-[#10b981] text-[#000000] border-[#10b981]'
          : 'bg-[#000000] text-[#d4d4d8] border-[#262626] hover:text-[#ffffff] hover:border-[#444444]'
      }`}
    >
      {copied ? <Check size={12} /> : <Copy size={12} />}
      <span>{copied ? '[COPIED]' : '[COPY CODE]'}</span>
    </button>
  )
}

export default function SDK() {
  const [activeTab, setActiveTab] = useState(TABS[0].id)
  const current = TABS.find(t => t.id === activeTab) || TABS[0]

  return (
    <section id="sdk" className="py-24 px-5 sm:px-8 bg-black text-white border-t border-[#222222]">
      <div className="max-w-5xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-[#0a0a0a] border border-[#2a2a2a] text-[#f59e0b] text-xs sm:text-sm font-mono font-bold uppercase tracking-wider mb-3">
            <Code2 size={14} />
            <span>[ MULTI-LANGUAGE SDKS ]</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white font-sans">
            1-Line Integration Across All Runtimes
          </h2>
          <p className="mt-3 text-[#d4d4d8] text-base font-sans">
            Drop BTP cryptographic guardrails directly into Python, TypeScript, or Go agents.
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex flex-wrap gap-2.5 mb-4 bg-[#0a0a0a] p-2.5 border border-[#262626]">
          {TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3.5 py-2.5 text-xs sm:text-sm font-mono font-bold transition border ${
                activeTab === tab.id
                  ? 'bg-[#f59e0b] text-[#000000] border-[#f59e0b]'
                  : 'bg-[#000000] text-[#c4c4cc] border-[#262626] hover:text-[#ffffff]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Code Viewer inside Cyber-Terminal Frame */}
        <div className="bg-[#0a0a0a] border border-[#262626] shadow-2xl overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-[#000000] border-b border-[#262626]">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 bg-[#ef4444]" />
              <div className="w-2.5 h-2.5 bg-[#f59e0b]" />
              <div className="w-2.5 h-2.5 bg-[#10b981]" />
            </div>
            <span className="text-xs sm:text-sm font-mono text-[#9ca3af] font-semibold">{current.filename}</span>
            <CopyButton text={current.code} />
          </div>

          <div className="p-6 sm:p-8">
            <pre className="font-mono text-xs sm:text-sm text-[#e4e4e7] overflow-x-auto leading-relaxed bg-[#000000] p-5 border border-[#222222]">
              {current.code}
            </pre>
          </div>
        </div>
      </div>
    </section>
  )
}
