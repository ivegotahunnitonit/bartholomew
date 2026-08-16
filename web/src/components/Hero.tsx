import { ArrowRight, Terminal, Shield, Cpu, Activity } from 'lucide-react'

const PILLARS = [
  { label: 'Security', desc: 'OWASP LLM Intercept & Secret Masking' },
  { label: 'Research', desc: 'Hypothesis Verification & Evidence' },
  { label: 'Automation', desc: 'Constraint Enforcement & Control' },
  { label: 'Economic Intelligence', desc: 'Opportunity Discovery & Resource Allocation' },
]

export default function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col justify-center pt-28 pb-20 px-5 sm:px-8 bg-bg overflow-hidden">
      {/* Background radial ambient light */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] bg-gradient-to-r from-emerald-500/10 via-cyan-500/10 to-violet-500/10 rounded-full blur-[140px] pointer-events-none" />

      <div className="max-w-5xl mx-auto w-full relative z-10">
        {/* Badge */}
        <div className="flex items-center justify-center mb-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <Cpu size={14} className="animate-pulse" />
            Autonomous Decision-Control Protocol
          </div>
        </div>

        {/* Primary Headline */}
        <h1
          className="text-center font-extrabold leading-tight mb-6 tracking-tight text-white font-heading"
          style={{ fontSize: 'clamp(2.4rem, 6vw, 4.2rem)', letterSpacing: '-0.03em' }}
        >
          An Autonomous Decision-Control &amp;{' '}
          <span className="gradient-text">Verification Layer</span>
          <br className="hidden sm:block" />
          {' '}for AI Agents.
        </h1>

        {/* Subtitle */}
        <p
          className="text-center mx-auto mb-10 text-slate-300 leading-relaxed max-w-2xl text-base sm:text-lg"
        >
          Bartholomew evaluates state, evidence, constraints, and outcomes in real time. Natively proficient as a <strong>Master of Linux</strong> environments, it enables autonomous agents to operate safely and effectively against reality rather than endlessly generating unverified responses.
        </p>

        {/* Central Architecture Flow Visual */}
        <div className="glass-card p-6 sm:p-8 rounded-2xl border border-white/10 max-w-3xl mx-auto mb-12 relative overflow-hidden bg-slate-950/80">
          <div className="flex flex-col items-center space-y-4 font-mono text-xs">
            {/* Top Node */}
            <div className="px-4 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-bold tracking-wider uppercase">
              AI AGENT INTENT &amp; DECISION
            </div>

            <div className="w-px h-6 bg-gradient-to-b from-cyan-500/50 to-emerald-500/50" />

            {/* Bartholomew Core Box */}
            <div className="w-full p-4 rounded-xl bg-slate-900/90 border border-emerald-500/30 space-y-3">
              <div className="text-center text-emerald-400 font-extrabold tracking-widest text-sm uppercase">
                BARTHOLOMEW VERIFICATION ENGINE
              </div>
              <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
                <div className="p-2 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-300">
                  <span className="font-bold block">REASON</span>
                  <span className="text-[10px] text-slate-400">Entropy &amp; Logic</span>
                </div>
                <div className="p-2 rounded bg-cyan-500/10 border border-cyan-500/20 text-cyan-300">
                  <span className="font-bold block">VERIFY</span>
                  <span className="text-[10px] text-slate-400">Ed25519 Evidence</span>
                </div>
                <div className="p-2 rounded bg-violet-500/10 border border-violet-500/20 text-violet-300">
                  <span className="font-bold block">MEMORY</span>
                  <span className="text-[10px] text-slate-400">Sovereign State</span>
                </div>
              </div>
            </div>

            <div className="w-px h-6 bg-gradient-to-b from-emerald-500/50 to-violet-500/50" />

            {/* Outcome Node */}
            <div className="px-4 py-2 rounded-lg bg-violet-500/10 border border-violet-500/30 text-violet-300 font-bold tracking-wider uppercase">
              REAL-WORLD ACTION &amp; VERIFIED OUTCOME
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 mb-16">
          <a href="#primitives" className="btn-action text-sm font-bold py-3 px-7 flex items-center gap-2">
            <Activity size={16} />
            Explore Core Primitives
          </a>
          <a href="#applications" className="btn-secondary text-sm font-medium py-3 px-6 flex items-center gap-2">
            <Shield size={16} className="text-cyan-400" />
            View Applications
            <ArrowRight size={16} />
          </a>
          <a
            href="https://pypi.org/project/bartholomew-eval/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-xs font-mono text-slate-500 hover:text-slate-300 transition-colors"
          >
            <Terminal size={14} />
            pip install bartholomew-eval
          </a>
        </div>

        {/* 4 Pillars Underneath */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
          {PILLARS.map((p) => (
            <div key={p.label} className="glass-card p-4 rounded-xl border border-white/10 text-center space-y-1">
              <span className="text-sm font-bold text-white font-heading block">{p.label}</span>
              <span className="text-[11px] text-slate-400 block">{p.desc}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
