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
    <section id="live-api" className="py-24 px-5 sm:px-8 bg-[#040406] text-white border-t border-[#27272a]/70 relative overflow-hidden">
      {/* Top ambient glowing accent line */}
      <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#f59e0b]/70 to-transparent pointer-events-none" />

      {/* Background glow accents */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[700px] h-[300px] bg-gradient-to-b from-[#f59e0b]/10 via-[#10b981]/5 to-transparent blur-[140px] pointer-events-none" />

      <div className="max-w-5xl mx-auto relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-[#f59e0b]/10 border border-[#f59e0b]/30 text-[#f59e0b] rounded-full text-xs font-mono font-bold tracking-wider mb-4 shadow-[0_0_15px_rgba(245,158,11,0.15)]">
            <Cpu size={13} />
            <span>[ PROTOCOL SPECIFICATION ]</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white font-sans">
            BTP Protocol Architecture
          </h2>
          <p className="mt-4 text-[#a1a1aa] text-sm sm:text-base font-sans leading-relaxed">
            Vendor-neutral cryptographic control plane for autonomous tool-calling agents.
          </p>
        </div>

        {/* Specification Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
          <div className="p-6 bg-gradient-to-b from-[#0e0e14]/90 via-[#09090d]/90 to-[#040406] border border-[#27272a]/75 hover:border-[#ffffff]/40 rounded-2xl transition-all duration-300 shadow-xl group backdrop-blur-md">
            <div className="text-[11px] font-mono uppercase text-[#71717a] mb-2 font-semibold">[STANDARD]</div>
            <div className="text-lg font-bold text-[#ffffff] font-mono">RFC 8785</div>
            <div className="text-xs text-[#a1a1aa] mt-1.5 font-sans leading-relaxed">Deterministic Canonical JSON serialization</div>
          </div>

          <div className="p-6 bg-gradient-to-b from-[#0e0e14]/90 via-[#09090d]/90 to-[#040406] border border-[#27272a]/75 hover:border-[#10b981]/50 rounded-2xl transition-all duration-300 shadow-xl group backdrop-blur-md">
            <div className="text-[11px] font-mono uppercase text-[#71717a] mb-2 font-semibold">[SIGNATURE]</div>
            <div className="text-lg font-bold text-[#10b981] font-mono">Ed25519</div>
            <div className="text-xs text-[#a1a1aa] mt-1.5 font-sans leading-relaxed">FIPS 186-5 asymmetric attestation</div>
          </div>

          <div className="p-6 bg-gradient-to-b from-[#0e0e14]/90 via-[#09090d]/90 to-[#040406] border border-[#27272a]/75 hover:border-[#f59e0b]/50 rounded-2xl transition-all duration-300 shadow-xl group backdrop-blur-md">
            <div className="text-[11px] font-mono uppercase text-[#71717a] mb-2 font-semibold">[TARGET LATENCY]</div>
            <div className="text-lg font-bold text-[#f59e0b] font-mono">&lt;50 µs</div>
            <div className="text-xs text-[#a1a1aa] mt-1.5 font-sans leading-relaxed">Sub-millisecond in-process evaluation</div>
          </div>

          <div className="p-6 bg-gradient-to-b from-[#0e0e14]/90 via-[#09090d]/90 to-[#040406] border border-[#27272a]/75 hover:border-[#38bdf8]/50 rounded-2xl transition-all duration-300 shadow-xl group backdrop-blur-md">
            <div className="text-[11px] font-mono uppercase text-[#71717a] mb-2 font-semibold">[ISOLATION]</div>
            <div className="text-lg font-bold text-[#ffffff] font-mono">3-Tier Boundary</div>
            <div className="text-xs text-[#a1a1aa] mt-1.5 font-sans leading-relaxed">Compiler AST + Hermetic Sandbox + Proof</div>
          </div>
        </div>

        {/* REST Evaluation Gateway Demo */}
        <div className="bg-gradient-to-b from-[#0e0e14]/95 via-[#09090d]/95 to-[#050507] border border-[#27272a]/80 rounded-2xl shadow-2xl overflow-hidden relative backdrop-blur-xl">
          <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#f59e0b]/50 to-transparent pointer-events-none" />

          {/* Header */}
          <div className="flex items-center justify-between px-5 py-3.5 bg-[#111118]/80 border-b border-[#27272a]/70">
            <div className="flex items-center gap-2.5">
              <div className="flex items-center gap-1.5 mr-1">
                <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
                <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
              </div>
              <span className="text-[11px] font-mono text-[#a1a1aa]">curl — evaluate-intent.sh</span>
            </div>
            <button
              onClick={handleCopy}
              className={`px-3 py-1.5 text-xs font-mono font-semibold rounded-lg transition flex items-center gap-1.5 border cursor-pointer ${
                copied === 'curl'
                  ? 'bg-[#10b981] text-black border-[#10b981]'
                  : 'bg-[#14141a] hover:bg-[#202028] text-white border-[#2e2e38]'
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
            <pre className="p-5 bg-[#030305] border border-[#27272a]/70 rounded-xl font-mono text-xs sm:text-sm text-[#f59e0b] overflow-x-auto leading-relaxed">
              {curlExample}
            </pre>

            <div className="mt-6 pt-6 border-t border-[#27272a]/70 grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs text-[#a1a1aa] font-mono">
              <div className="flex items-center gap-2">
                <CheckCircle2 size={14} className="text-[#f59e0b] shrink-0" />
                <span>POST /v1/evaluate</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 size={14} className="text-[#10b981] shrink-0" />
                <span>POST /v1/verify</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 size={14} className="text-[#ffffff] shrink-0" />
                <span>GET /v1/trust-root</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
