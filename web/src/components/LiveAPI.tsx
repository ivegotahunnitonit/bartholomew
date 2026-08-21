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
    <section id="live-api" className="py-24 px-5 sm:px-8 bg-black text-white border-t border-[#1c1c1c]">
      <div className="max-w-5xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#0a0a0a] border border-[#222222] text-[#f59e0b] text-xs font-mono font-bold uppercase tracking-wider mb-3">
            <Cpu size={13} />
            <span>[ PROTOCOL SPECIFICATION ]</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white font-sans">
            BTP Protocol Architecture
          </h2>
          <p className="mt-3 text-[#a1a1aa] text-sm sm:text-base font-sans">
            Vendor-neutral cryptographic control plane for autonomous tool-calling agents.
          </p>
        </div>

        {/* Specification Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
          <div className="p-5 bg-[#0a0a0a] border border-[#222222]">
            <div className="text-[11px] font-mono uppercase text-[#71717a] mb-1">[STANDARD]</div>
            <div className="text-base font-bold text-[#ffffff] font-mono">RFC 8785</div>
            <div className="text-xs text-[#a1a1aa] mt-1 font-sans">Deterministic Canonical JSON serialization</div>
          </div>

          <div className="p-5 bg-[#0a0a0a] border border-[#222222]">
            <div className="text-[11px] font-mono uppercase text-[#71717a] mb-1">[SIGNATURE]</div>
            <div className="text-base font-bold text-[#10b981] font-mono">Ed25519</div>
            <div className="text-xs text-[#a1a1aa] mt-1 font-sans">FIPS 186-5 asymmetric attestation</div>
          </div>

          <div className="p-5 bg-[#0a0a0a] border border-[#222222]">
            <div className="text-[11px] font-mono uppercase text-[#71717a] mb-1">[TARGET LATENCY]</div>
            <div className="text-base font-bold text-[#f59e0b] font-mono">&lt;50 µs</div>
            <div className="text-xs text-[#a1a1aa] mt-1 font-sans">Sub-millisecond in-process evaluation</div>
          </div>

          <div className="p-5 bg-[#0a0a0a] border border-[#222222]">
            <div className="text-[11px] font-mono uppercase text-[#71717a] mb-1">[ISOLATION]</div>
            <div className="text-base font-bold text-[#ffffff] font-mono">3-Tier Boundary</div>
            <div className="text-xs text-[#a1a1aa] mt-1 font-sans">Compiler AST + Hermetic Sandbox + Proof</div>
          </div>
        </div>

        {/* REST Evaluation Gateway Demo */}
        <div className="bg-[#0a0a0a] border border-[#222222] shadow-2xl overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-2.5 bg-[#000000] border-b border-[#222222]">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 bg-[#ef4444]" />
              <div className="w-2.5 h-2.5 bg-[#f59e0b]" />
              <div className="w-2.5 h-2.5 bg-[#10b981]" />
            </div>
            <span className="text-[11px] font-mono text-[#71717a]">curl — evaluate-intent.sh</span>
            <button
              onClick={handleCopy}
              className={`px-2.5 py-1 text-xs font-mono font-semibold transition flex items-center gap-1 border ${
                copied === 'curl'
                  ? 'bg-[#10b981] text-[#000000] border-[#10b981]'
                  : 'bg-[#000000] text-[#a1a1aa] border-[#222222] hover:text-[#ffffff]'
              }`}
            >
              {copied === 'curl' ? (
                <>
                  <Check size={11} />
                  <span>[COPIED]</span>
                </>
              ) : (
                <>
                  <Copy size={11} />
                  <span>[COPY CURL]</span>
                </>
              )}
            </button>
          </div>

          <div className="p-6 sm:p-8">
            <pre className="p-4 bg-[#000000] border border-[#1a1a1a] font-mono text-xs sm:text-sm text-[#f59e0b] overflow-x-auto leading-relaxed">
              {curlExample}
            </pre>

            <div className="mt-6 pt-6 border-t border-[#222222] grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs text-[#a1a1aa] font-mono">
              <div className="flex items-center gap-2">
                <CheckCircle2 size={13} className="text-[#f59e0b] shrink-0" />
                <span>POST /v1/evaluate</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 size={13} className="text-[#10b981] shrink-0" />
                <span>POST /v1/verify</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 size={13} className="text-[#ffffff] shrink-0" />
                <span>GET /v1/trust-root</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
