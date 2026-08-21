import { ArrowRight, Terminal, Shield, Cpu, Activity, Download, Lock } from 'lucide-react'

export default function Hero() {
  return (
    <section className="relative min-h-[90vh] flex flex-col justify-center pt-28 pb-20 px-5 sm:px-8 bg-slate-950 overflow-hidden text-white">
      {/* Ambient background light */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] bg-gradient-to-r from-cyan-500/10 via-emerald-500/10 to-indigo-500/10 rounded-full blur-[140px] pointer-events-none" />

      <div className="max-w-5xl mx-auto w-full relative z-10">
        {/* Top Badge */}
        <div className="flex items-center justify-center mb-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Cpu size={14} className="text-cyan-400" />
            Bartholomew Trust Protocol (BTP/2.2)
          </div>
        </div>

        {/* Primary Headline */}
        <h1
          className="text-center font-extrabold leading-tight mb-6 tracking-tight text-white"
          style={{ fontSize: 'clamp(2.4rem, 5.5vw, 4rem)', letterSpacing: '-0.03em' }}
        >
          Sub-Millisecond Cryptographic <br className="hidden sm:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-emerald-400 to-indigo-400">
            Safety Guardrails
          </span>{' '}
          for Autonomous Agents.
        </h1>

        {/* Subtitle */}
        <p className="text-center mx-auto mb-10 text-slate-300 leading-relaxed max-w-2xl text-base sm:text-lg">
          Deterministic 3-Tier invariant defense for AI tool execution. Eliminates Rice’s theorem bypasses using compiler AST constant-folding, hermetic sandboxing, and &lt;50 µs Ed25519 cryptographic attestations.
        </p>

        {/* Architecture Flow Card */}
        <div className="p-6 sm:p-8 rounded-2xl border border-slate-800 max-w-3xl mx-auto mb-12 relative overflow-hidden bg-slate-900/90 shadow-2xl backdrop-blur-sm">
          <div className="flex flex-col items-center space-y-4 font-mono text-xs">
            {/* Input Node */}
            <div className="px-4 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-bold tracking-wider uppercase flex items-center gap-2">
              <Terminal size={14} />
              AI AGENT INTENT &amp; TOOL CALL
            </div>

            <div className="w-px h-5 bg-gradient-to-b from-cyan-500/50 to-emerald-500/50" />

            {/* Core Verification Box */}
            <div className="w-full p-4 rounded-xl bg-slate-950 border border-emerald-500/30 space-y-3">
              <div className="text-center text-emerald-400 font-extrabold tracking-widest text-xs sm:text-sm uppercase flex items-center justify-center gap-2">
                <Shield size={16} />
                BARTHOLOMEW 3-TIER INVARIANT ENGINE (&lt;50 µs)
              </div>
              <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-200">
                  <span className="font-bold text-cyan-400 block mb-0.5">TIER 1: AST</span>
                  <span className="text-[10px] text-slate-400">Static AST Analysis</span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-200">
                  <span className="font-bold text-emerald-400 block mb-0.5">TIER 2: SANDBOX</span>
                  <span className="text-[10px] text-slate-400">Hermetic Isolation</span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-200">
                  <span className="font-bold text-indigo-400 block mb-0.5">TIER 3: PROOF</span>
                  <span className="text-[10px] text-slate-400">Ed25519 Attestation</span>
                </div>
              </div>
            </div>

            <div className="w-px h-5 bg-gradient-to-b from-emerald-500/50 to-indigo-500/50" />

            {/* Output Node */}
            <div className="px-4 py-2 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 font-bold tracking-wider uppercase flex items-center gap-2">
              <Lock size={14} />
              CRYPTOGRAPHIC ATTESTATION &amp; ZERO-RISK EXECUTION
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4">
          <a
            href="#download"
            className="px-6 py-3 rounded-xl text-sm font-bold bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 shadow-lg shadow-cyan-500/20 transition flex items-center gap-2"
          >
            <Download size={16} />
            Download Desktop CLI
          </a>
          <a
            href="#policy-editor"
            className="px-6 py-3 rounded-xl text-sm font-semibold bg-slate-900 hover:bg-slate-800 border border-slate-700 text-white transition flex items-center gap-2"
          >
            <Activity size={16} className="text-cyan-400" />
            Interactive Policy Editor
          </a>
          <a
            href="https://github.com/ivegotahunnitonit/bartholomew"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 rounded-xl text-sm font-semibold bg-slate-900/60 hover:bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition flex items-center gap-2"
          >
            <Terminal size={16} />
            GitHub Repository
            <ArrowRight size={14} />
          </a>
        </div>
      </div>
    </section>
  )
}
