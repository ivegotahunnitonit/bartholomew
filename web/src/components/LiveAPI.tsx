import { useState } from 'react'
import { Check, Copy, Cpu, CheckCircle2 } from 'lucide-react'

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
    <section id="live-api" className="py-24 px-5 sm:px-8 bg-black text-white border-t border-[#222222]">
      <div className="max-w-5xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-[#0a0a0a] border border-[#2a2a2a] text-[#f59e0b] text-xs sm:text-sm font-mono font-bold uppercase tracking-wider mb-3">
            <Cpu size={14} />
            <span>[ PROTOCOL SPECIFICATION ]</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white font-sans">
            BTP Protocol Architecture
          </h2>
          <p className="mt-3 text-[#d4d4d8] text-base font-sans">
            Vendor-neutral cryptographic control plane for autonomous tool-calling agents.
          </p>
        </div>

        {/* Specification Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
          <div className="p-5 sm:p-6 bg-[#0a0a0a] border border-[#262626]">
            <div className="text-xs font-mono uppercase text-[#9ca3af] mb-1.5 font-semibold">[STANDARD]</div>
            <div className="text-lg font-bold text-[#ffffff] font-mono">RFC 8785</div>
            <div className="text-xs sm:text-sm text-[#d4d4d8] mt-1.5 font-sans leading-relaxed">Deterministic Canonical JSON serialization</div>
          </div>

          <div className="p-5 sm:p-6 bg-[#0a0a0a] border border-[#262626]">
            <div className="text-xs font-mono uppercase text-[#9ca3af] mb-1.5 font-semibold">[SIGNATURE]</div>
            <div className="text-lg font-bold text-[#10b981] font-mono">Ed25519</div>
            <div className="text-xs sm:text-sm text-[#d4d4d8] mt-1.5 font-sans leading-relaxed">FIPS 186-5 asymmetric attestation</div>
          </div>

          <div className="p-5 sm:p-6 bg-[#0a0a0a] border border-[#262626]">
            <div className="text-xs font-mono uppercase text-[#9ca3af] mb-1.5 font-semibold">[TARGET LATENCY]</div>
            <div className="text-lg font-bold text-[#f59e0b] font-mono">&lt;50 µs</div>
            <div className="text-xs sm:text-sm text-[#d4d4d8] mt-1.5 font-sans leading-relaxed">Sub-millisecond in-process evaluation</div>
          </div>

          <div className="p-5 sm:p-6 bg-[#0a0a0a] border border-[#262626]">
            <div className="text-xs font-mono uppercase text-[#9ca3af] mb-1.5 font-semibold">[ISOLATION]</div>
            <div className="text-lg font-bold text-[#ffffff] font-mono">3-Tier Boundary</div>
            <div className="text-xs sm:text-sm text-[#d4d4d8] mt-1.5 font-sans leading-relaxed">Compiler AST + Sandbox + Proof</div>
          </div>
        </div>

        {/* REST Evaluation Gateway Demo */}
        <div className="bg-[#0a0a0a] border border-[#262626] shadow-2xl overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-[#000000] border-b border-[#262626]">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 bg-[#ef4444]" />
              <div className="w-2.5 h-2.5 bg-[#f59e0b]" />
              <div className="w-2.5 h-2.5 bg-[#10b981]" />
            </div>
            <span className="text-xs sm:text-sm font-mono text-[#9ca3af] font-semibold">curl — evaluate-intent.sh</span>
            <button
              onClick={handleCopy}
              className={`px-3 py-1.5 text-xs sm:text-sm font-mono font-semibold transition flex items-center gap-1.5 border ${
                copied === 'curl'
                  ? 'bg-[#10b981] text-[#000000] border-[#10b981]'
                  : 'bg-[#000000] text-[#d4d4d8] border-[#262626] hover:text-[#ffffff]'
              }`}
            >
              {copied === 'curl' ? (
                <>
                  <Check size={12} />
                  <span>[COPIED]</span>
                </>
              ) : (
                <>
                  <Copy size={12} />
                  <span>[COPY CURL]</span>
                </>
              )}
            </button>
          </div>

          <div className="p-6 sm:p-8">
            <pre className="p-4 sm:p-5 bg-[#000000] border border-[#222222] font-mono text-xs sm:text-sm text-[#f59e0b] overflow-x-auto leading-relaxed font-semibold">
              {curlExample}
            </pre>

            <div className="mt-6 pt-6 border-t border-[#262626] grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs sm:text-sm text-[#d4d4d8] font-mono">
              <div className="flex items-center gap-2">
                <CheckCircle2 size={14} className="text-[#f59e0b] shrink-0" />
                <span className="font-semibold">POST /v1/evaluate</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 size={14} className="text-[#10b981] shrink-0" />
                <span className="font-semibold">POST /v1/verify</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 size={14} className="text-[#ffffff] shrink-0" />
                <span className="font-semibold">GET /v1/status</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
