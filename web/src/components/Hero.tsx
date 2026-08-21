import { ArrowRight, Terminal, Shield, Activity, Download, CheckCircle2, Zap, Lock } from 'lucide-react'

export default function Hero() {
  return (
    <section className="relative min-h-[92vh] flex flex-col justify-center pt-28 pb-20 px-5 sm:px-8 bg-slate-950 overflow-hidden text-white">
      {/* Ambient background light glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[850px] h-[550px] bg-gradient-to-r from-cyan-500/10 via-emerald-500/10 to-indigo-500/10 rounded-full blur-[150px] pointer-events-none" />

      <div className="max-w-5xl mx-auto w-full relative z-10">
        {/* Top Investor & Developer Badge */}
        <div className="flex items-center justify-center mb-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 shadow-sm">
            <Shield size={14} className="text-cyan-400" />
            Safety Infrastructure for Autonomous AI
          </div>
        </div>

        {/* Primary Layman Headline */}
        <h1
          className="text-center font-extrabold leading-tight mb-6 tracking-tight text-white"
          style={{ fontSize: 'clamp(2.4rem, 5.8vw, 4.2rem)', letterSpacing: '-0.03em' }}
        >
          The Seatbelt and Black Box <br className="hidden sm:block" />
          for{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-emerald-400 to-indigo-400">
            Autonomous AI Agents.
          </span>
        </h1>

        {/* Layman Subtitle for Investors & Teams */}
        <p className="text-center mx-auto mb-10 text-slate-300 leading-relaxed max-w-3xl text-base sm:text-lg">
          When companies give AI agents permission to run code, query databases, and spend money, accidents happen. <strong>Bartholomew</strong> makes it mathematically impossible for an AI to delete files, wipe databases, or drain bank accounts—intercepting rogue actions in <strong>under 50 microseconds</strong>.
        </p>

        {/* 3 Core Value Pillars for Non-Technical & Technical Investors */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto mb-12">
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-sm">
            <div className="flex items-center gap-2 text-cyan-400 font-bold text-sm mb-1.5">
              <Shield size={16} />
              <span>1. Zero Rogue Accidents</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Traps AI inside a strict sandbox. If an agent tries to delete operating system files or drop tables, it is blocked instantly.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-sm">
            <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm mb-1.5">
              <Zap size={16} />
              <span>2. Sub-Millisecond Speed</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Runs in under 50 microseconds directly in memory. Adds zero perceptible lag and requires zero expensive cloud calls.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-sm">
            <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm mb-1.5">
              <Lock size={16} />
              <span>3. Tamper-Proof Audit Trail</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Every action generates a cryptographic digital receipt, giving enterprise compliance teams complete proof of what happened.
            </p>
          </div>
        </div>

        {/* Visual Workflow Card */}
        <div className="p-6 sm:p-8 rounded-2xl border border-slate-800 max-w-3xl mx-auto mb-12 relative overflow-hidden bg-slate-900/90 shadow-2xl backdrop-blur-sm">
          <div className="flex flex-col items-center space-y-4 font-mono text-xs">
            {/* Top Node */}
            <div className="px-4 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-bold tracking-wider uppercase flex items-center gap-2">
              <Terminal size={14} />
              AI AGENT PROPOSES AN ACTION (CODE, SQL, API SPEND)
            </div>

            <div className="w-px h-5 bg-gradient-to-b from-cyan-500/50 to-emerald-500/50" />

            {/* Core Verification Box */}
            <div className="w-full p-4 rounded-xl bg-slate-950 border border-emerald-500/30 space-y-3">
              <div className="text-center text-emerald-400 font-extrabold tracking-widest text-xs sm:text-sm uppercase flex items-center justify-center gap-2">
                <Shield size={16} />
                BARTHOLOMEW DETERMINISTIC BRAKE PEDAL (&lt;50 µs)
              </div>
              <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-200">
                  <span className="font-bold text-cyan-400 block mb-0.5">THE SCANNER</span>
                  <span className="text-[10px] text-slate-400">Pre-flight Code Scan</span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-200">
                  <span className="font-bold text-emerald-400 block mb-0.5">THE CAGE</span>
                  <span className="text-[10px] text-slate-400">Locked Sandbox</span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-200">
                  <span className="font-bold text-indigo-400 block mb-0.5">THE SEAL</span>
                  <span className="text-[10px] text-slate-400">Digital Audit Proof</span>
                </div>
              </div>
            </div>

            <div className="w-px h-5 bg-gradient-to-b from-emerald-500/50 to-indigo-500/50" />

            {/* Output Node */}
            <div className="px-4 py-2 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 font-bold tracking-wider uppercase flex items-center gap-2">
              <CheckCircle2 size={14} />
              SAFE, AUDITED, AND VERIFIED EXECUTION
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
            Install on Desktop (1 Command)
          </a>
          <a
            href="#how-it-works"
            className="px-6 py-3 rounded-xl text-sm font-semibold bg-slate-900 hover:bg-slate-800 border border-slate-700 text-white transition flex items-center gap-2"
          >
            <Activity size={16} className="text-cyan-400" />
            See How It Works
          </a>
          <a
            href="https://github.com/ivegotahunnitonit/bartholomew"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 rounded-xl text-sm font-semibold bg-slate-900/60 hover:bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition flex items-center gap-2"
          >
            <Terminal size={16} />
            View Open Source Code
            <ArrowRight size={14} />
          </a>
        </div>
      </div>
    </section>
  )
}
