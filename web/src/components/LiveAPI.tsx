import { useState } from 'react'
import { Terminal, Check, Copy, Cpu, CheckCircle2 } from 'lucide-react'

export default function LiveAPI() {
  const [copied, setCopied] = useState<string | null>(null)

  const curlExample = `curl -X POST http://127.0.0.1:8080/v1/evaluate \\
  -H "Content-Type: application/json" \\
  -d '{"agent_id": "agent-01", "action_type": "EXEC_TOOL", "payload": {"command": "git status"}}'`

  const handleCopy = () => {
    navigator.clipboard.writeText(curlExample)
    setCopied('curl')
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <section id="live-api" className="py-24 px-5 sm:px-8 bg-slate-950 text-white border-t border-slate-900">
      <div className="max-w-5xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <Cpu size={13} />
            Gateway Specification
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
            BTP Protocol Architecture
          </h2>
          <p className="mt-3 text-slate-400 text-sm sm:text-base">
            Vendor-neutral cryptographic control plane for autonomous tool-calling agents.
          </p>
        </div>

        {/* Specification Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <div className="text-xs font-mono uppercase text-slate-500 mb-1">Standard</div>
            <div className="text-lg font-bold text-cyan-300 font-mono">RFC 8785</div>
            <div className="text-xs text-slate-400 mt-1">Deterministic Canonical JSON serialization</div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <div className="text-xs font-mono uppercase text-slate-500 mb-1">Asymmetric Signature</div>
            <div className="text-lg font-bold text-emerald-300 font-mono">Ed25519</div>
            <div className="text-xs text-slate-400 mt-1">FIPS 186-5 asymmetric attestation</div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <div className="text-xs font-mono uppercase text-slate-500 mb-1">Target Latency</div>
            <div className="text-lg font-bold text-indigo-300 font-mono">&lt;50 µs</div>
            <div className="text-xs text-slate-400 mt-1">Sub-millisecond in-process evaluation</div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <div className="text-xs font-mono uppercase text-slate-500 mb-1">Execution Boundary</div>
            <div className="text-lg font-bold text-rose-300 font-mono">3-Tier Isolation</div>
            <div className="text-xs text-slate-400 mt-1">Compiler AST + Hermetic Sandbox + Proof</div>
          </div>
        </div>

        {/* REST Evaluation Gateway Demo */}
        <div className="p-6 sm:p-8 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-2xl">
          <div className="flex items-center justify-between gap-4 mb-4">
            <div className="flex items-center gap-2">
              <Terminal size={16} className="text-cyan-400" />
              <span className="text-sm font-bold text-white font-mono">Gateway cURL Evaluation</span>
            </div>
            <button
              onClick={handleCopy}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold transition flex items-center gap-1.5 border border-slate-700"
            >
              {copied === 'curl' ? (
                <>
                  <Check size={12} className="text-emerald-400" />
                  <span className="text-emerald-400">Copied</span>
                </>
              ) : (
                <>
                  <Copy size={12} />
                  <span>Copy cURL</span>
                </>
              )}
            </button>
          </div>

          <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-cyan-300 overflow-x-auto">
            {curlExample}
          </pre>

          <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs text-slate-400">
            <div className="flex items-center gap-2">
              <CheckCircle2 size={13} className="text-cyan-400" />
              <span>POST /v1/evaluate (Microsecond Gating)</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 size={13} className="text-emerald-400" />
              <span>POST /v1/verify (Independent Offline Verification)</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 size={13} className="text-indigo-400" />
              <span>GET /v1/trust-root (Public Key Distribution)</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
