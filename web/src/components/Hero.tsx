import { ArrowRight, Terminal, Shield, Activity, Download, CheckCircle2, Zap, Lock, Sparkles } from 'lucide-react'

export default function Hero() {
  return (
    <section className="relative min-h-[95vh] flex flex-col justify-center pt-28 pb-20 px-5 sm:px-8 bg-slate-950 overflow-hidden text-white">
      {/* Dynamic ambient background glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[600px] bg-gradient-to-r from-cyan-500/15 via-emerald-500/10 to-indigo-500/15 rounded-full blur-[160px] pointer-events-none" />

      <div className="max-w-5xl mx-auto w-full relative z-10">
        {/* Top Developer Badge */}
        <div className="flex items-center justify-center mb-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-mono font-bold tracking-wide uppercase bg-cyan-500/10 border border-cyan-400/30 text-cyan-300 shadow-lg shadow-cyan-500/10 backdrop-blur-md">
            <Sparkles size={13} className="text-cyan-400 animate-pulse" />
            <span>AI SAFETY INFRASTRUCTURE · BTP/2.2</span>
          </div>
        </div>

        {/* Dynamic Editorial Headline with Tight Line Height */}
        <h1
          className="text-center font-extrabold mb-6 text-white font-sans"
          style={{
            fontSize: 'clamp(2.6rem, 5.5vw, 4.6rem)',
            lineHeight: 1.05,
            letterSpacing: '-0.04em'
          }}
        >
          The Seatbelt and Black Box <br className="hidden sm:block" />
          for{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-emerald-300 to-indigo-400">
            Autonomous AI Agents.
          </span>
        </h1>

        {/* Subtitle */}
        <p className="text-center mx-auto mb-10 text-slate-300 leading-relaxed max-w-3xl text-base sm:text-lg">
          When companies give AI agents permission to run code, query databases, and spend money, accidents happen. <strong>Bartholomew</strong> makes it mathematically impossible for an AI to delete files, wipe databases, or drain bank accounts—intercepting rogue actions in <strong>under 50 microseconds</strong>.
        </p>

        {/* 3 Core Value Pillars with Tactile Hover Transforms */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 max-w-4xl mx-auto mb-12">
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-white/10 backdrop-blur-xl shadow-xl hover:-translate-y-1 hover:border-cyan-500/40 hover:shadow-cyan-500/10 transition-all duration-200">
            <div className="flex items-center gap-2.5 text-cyan-400 font-bold text-sm mb-2 font-mono">
              <Shield size={16} />
              <span>1. Zero Rogue Accidents</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Traps AI inside a strict sandbox. If an agent tries to delete operating system files or drop tables, it is blocked instantly.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900/80 border border-white/10 backdrop-blur-xl shadow-xl hover:-translate-y-1 hover:border-emerald-500/40 hover:shadow-emerald-500/10 transition-all duration-200">
            <div className="flex items-center gap-2.5 text-emerald-400 font-bold text-sm mb-2 font-mono">
              <Zap size={16} />
              <span>2. Sub-Millisecond Speed</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Runs in under 50 microseconds directly in memory. Adds zero perceptible lag and requires zero expensive cloud calls.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900/80 border border-white/10 backdrop-blur-xl shadow-xl hover:-translate-y-1 hover:border-indigo-500/40 hover:shadow-indigo-500/10 transition-all duration-200">
            <div className="flex items-center gap-2.5 text-indigo-400 font-bold text-sm mb-2 font-mono">
              <Lock size={16} />
              <span>3. Tamper-Proof Audit Trail</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Every action generates a cryptographic digital receipt, giving enterprise compliance teams complete proof of what happened.
            </p>
          </div>
        </div>

        {/* Illuminated Interactive Flow Diagram inside macOS Frame */}
        <div className="rounded-2xl border border-white/10 max-w-3xl mx-auto mb-12 bg-slate-900/90 shadow-2xl backdrop-blur-xl overflow-hidden hover:border-cyan-500/30 transition-all">
          {/* macOS Titlebar */}
          <div className="flex items-center justify-between px-4 py-3 bg-slate-950/80 border-b border-white/10">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-rose-500/80" />
              <div className="w-3 h-3 rounded-full bg-amber-500/80" />
              <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
            </div>
            <span className="text-[11px] font-mono text-slate-400">btp-runtime-control-plane.live</span>
            <div className="w-12" />
          </div>

          <div className="p-6 sm:p-8">
            <div className="flex flex-col items-center space-y-4 font-mono text-xs">
              {/* Top Node */}
              <div className="px-5 py-2.5 rounded-xl bg-cyan-500/15 border border-cyan-400/40 text-cyan-300 font-bold tracking-wider uppercase flex items-center gap-2 shadow-lg shadow-cyan-500/10">
                <Terminal size={14} className="text-cyan-400" />
                AI AGENT PROPOSES AN ACTION (CODE, SQL, API SPEND)
              </div>

              {/* Animated Neon Gradient Connector */}
              <div className="w-0.5 h-6 bg-gradient-to-b from-cyan-400 via-emerald-400 to-emerald-500 shadow-glow" />

              {/* Core Engine Box */}
              <div className="w-full p-5 rounded-2xl bg-slate-950 border border-emerald-400/40 space-y-3 shadow-xl shadow-emerald-500/5">
                <div className="text-center text-emerald-400 font-extrabold tracking-widest text-xs sm:text-sm uppercase flex items-center justify-center gap-2">
                  <Shield size={16} />
                  BARTHOLOMEW DETERMINISTIC BRAKE PEDAL (&lt;50 µs)
                </div>
                <div className="grid grid-cols-3 gap-3 text-center text-[11px]">
                  <div className="p-3 rounded-xl bg-slate-900 border border-white/10 hover:border-cyan-500/30 transition">
                    <span className="font-bold text-cyan-300 block mb-0.5">THE SCANNER</span>
                    <span className="text-[10px] text-slate-400">Pre-flight Code Scan</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900 border border-white/10 hover:border-emerald-500/30 transition">
                    <span className="font-bold text-emerald-300 block mb-0.5">THE CAGE</span>
                    <span className="text-[10px] text-slate-400">Locked Sandbox</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900 border border-white/10 hover:border-indigo-500/30 transition">
                    <span className="font-bold text-indigo-300 block mb-0.5">THE SEAL</span>
                    <span className="text-[10px] text-slate-400">Digital Audit Proof</span>
                  </div>
                </div>
              </div>

              {/* Animated Neon Gradient Connector */}
              <div className="w-0.5 h-6 bg-gradient-to-b from-emerald-400 via-indigo-400 to-indigo-500" />

              {/* Output Node */}
              <div className="px-5 py-2.5 rounded-xl bg-indigo-500/15 border border-indigo-400/40 text-indigo-300 font-bold tracking-wider uppercase flex items-center gap-2 shadow-lg shadow-indigo-500/10">
                <CheckCircle2 size={14} className="text-indigo-400" />
                SAFE, AUDITED, AND VERIFIED EXECUTION
              </div>
            </div>
          </div>
        </div>

        {/* High-Visibility High-Contrast CTA Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4">
          <a
            href="#download"
            className="px-7 py-3.5 rounded-xl text-sm font-extrabold bg-gradient-to-r from-cyan-400 via-emerald-400 to-emerald-500 hover:from-cyan-300 hover:to-emerald-300 text-slate-950 shadow-xl shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:-translate-y-0.5 transition-all duration-200 flex items-center gap-2"
          >
            <Download size={16} />
            Install on Desktop (1 Command)
          </a>
          <a
            href="#how-it-works"
            className="px-6 py-3.5 rounded-xl text-sm font-semibold bg-slate-900/90 hover:bg-slate-800 border border-white/10 hover:border-cyan-400/40 text-white shadow-lg hover:-translate-y-0.5 transition-all duration-200 flex items-center gap-2 backdrop-blur-md"
          >
            <Activity size={16} className="text-cyan-400" />
            See How It Works
          </a>
          <a
            href="https://github.com/ivegotahunnitonit/bartholomew"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3.5 rounded-xl text-sm font-semibold bg-slate-900/60 hover:bg-slate-900 border border-white/10 hover:border-slate-600 text-slate-300 hover:text-white hover:-translate-y-0.5 transition-all duration-200 flex items-center gap-2 backdrop-blur-md"
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
