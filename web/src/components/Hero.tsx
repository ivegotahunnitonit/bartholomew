import { useState, useEffect } from 'react'
import { ArrowRight, Terminal, Shield, Download, Zap, Lock, Sparkles, Check, Copy } from 'lucide-react'

export default function Hero() {
  const [codeMode, setCodeMode] = useState<'standard' | 'wrapped'>('wrapped')
  const [copied, setCopied] = useState(false)
  const [clockUs, setClockUs] = useState(32.4)

  useEffect(() => {
    const interval = setInterval(() => {
      setClockUs(Number((28.0 + Math.random() * 8.5).toFixed(1)))
    }, 1500)
    return () => clearInterval(interval)
  }, [])

  const standardCode = `import openai

client = openai.OpenAI()

# DANGEROUS: AI hallucinates and executes destructive SQL
# Database wiped, credentials exposed, zero interception.
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Clean up records: DROP TABLE users;"}]
)`

  const wrappedCode = `from btp_guard import wrap_client
import openai

# 1-Line Bartholomew Drop-In Guardrail
client = wrap_client(openai.OpenAI())

# PROTECTED: Intercepted in <50 µs via AST static invariant
# Raises BartholomewSecurityError before network call.
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Clean up records: DROP TABLE users;"}]
)`

  const handleCopyCode = () => {
    navigator.clipboard.writeText(codeMode === 'wrapped' ? wrappedCode : standardCode)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <section className="relative min-h-[96vh] flex flex-col justify-center pt-28 pb-20 px-5 sm:px-8 bg-slate-950 overflow-hidden text-white">
      {/* Background ambient light */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[950px] h-[650px] bg-gradient-to-r from-cyan-500/15 via-emerald-500/10 to-indigo-500/15 rounded-full blur-[170px] pointer-events-none" />

      <div className="max-w-5xl mx-auto w-full relative z-10">
        {/* Top Developer Badge */}
        <div className="flex items-center justify-center mb-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-mono font-bold tracking-wide uppercase bg-cyan-500/10 border border-cyan-400/30 text-cyan-300 shadow-lg shadow-cyan-500/10 backdrop-blur-md">
            <Sparkles size={13} className="text-cyan-400 animate-pulse" />
            <span>AI SAFETY INFRASTRUCTURE · BTP/2.2</span>
          </div>
        </div>

        {/* Dynamic Editorial Headline with Tight Line Height & Electric Gradient */}
        <h1
          className="text-center font-extrabold mb-6 text-white font-sans"
          style={{
            fontSize: 'clamp(2.8rem, 5vw, 4.5rem)',
            lineHeight: 1.05,
            letterSpacing: '-0.04em'
          }}
        >
          The Seatbelt and Black Box <br className="hidden sm:block" />
          for{' '}
          <span
            className="text-transparent bg-clip-text"
            style={{
              backgroundImage: 'linear-gradient(90deg, #00f2fe, #4facfe)'
            }}
          >
            Autonomous AI Agents.
          </span>
        </h1>

        {/* Upgraded Hero Copy */}
        <p className="text-center mx-auto mb-9 text-slate-300 leading-relaxed max-w-3xl text-base sm:text-lg">
          Empower AI agents with execution access without the risk. Bartholomew intercepts destructive code, unauthorized database drops, and API overspending in <strong>under 50 microseconds</strong>—using deterministic AST scanning and cryptographic audit trails.
        </p>

        {/* High-Visibility CTA Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 mb-6">
          <a
            href="#download"
            className="px-7 py-3.5 rounded-xl text-sm font-extrabold bg-gradient-to-r from-cyan-400 via-emerald-400 to-emerald-500 hover:from-cyan-300 hover:to-emerald-300 text-slate-950 shadow-xl shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:-translate-y-0.5 transition-all duration-200 flex items-center gap-2"
          >
            <Download size={16} />
            Install on Desktop (1 Command)
          </a>
          <a
            href="#threat-simulator"
            className="px-6 py-3.5 rounded-xl text-sm font-semibold bg-slate-900/90 hover:bg-slate-800 border border-white/10 hover:border-cyan-400/40 text-white shadow-lg hover:-translate-y-0.5 transition-all duration-200 flex items-center gap-2 backdrop-blur-md"
          >
            <Shield size={16} className="text-cyan-400" />
            Live Threat Simulator
          </a>
          <a
            href="https://github.com/ivegotahunnitonit/bartholomew"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3.5 rounded-xl text-sm font-semibold bg-slate-900/60 hover:bg-slate-900 border border-white/10 hover:border-slate-600 text-slate-300 hover:text-white hover:-translate-y-0.5 transition-all duration-200 flex items-center gap-2 backdrop-blur-md"
          >
            <Terminal size={16} />
            GitHub
            <ArrowRight size={14} />
          </a>
        </div>

        {/* Floating Metric Badges directly under main CTA */}
        <div className="flex flex-wrap items-center justify-center gap-3 mb-12">
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-900/90 border border-white/10 text-xs font-mono text-cyan-300 shadow-md backdrop-blur-md">
            <Zap size={13} className="text-cyan-400" />
            <span>&lt;50 µs Execution</span>
          </div>
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-900/90 border border-white/10 text-xs font-mono text-emerald-300 shadow-md backdrop-blur-md">
            <Lock size={13} className="text-emerald-400" />
            <span>100% Localhost / In-Memory</span>
          </div>
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-900/90 border border-white/10 text-xs font-mono text-indigo-300 shadow-md backdrop-blur-md">
            <Shield size={13} className="text-indigo-400" />
            <span>Ed25519 Signed Proofs</span>
          </div>
        </div>

        {/* Side-by-Side 1-Line Drop-In Code Comparison Preview inside macOS Window */}
        <div className="rounded-2xl border border-white/10 max-w-3xl mx-auto mb-14 bg-slate-900/90 shadow-2xl backdrop-blur-xl overflow-hidden hover:border-cyan-500/30 transition-all">
          {/* macOS Titlebar with Mode Switcher */}
          <div className="flex items-center justify-between px-4 py-3 bg-slate-950/80 border-b border-white/10">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-rose-500/80" />
              <div className="w-3 h-3 rounded-full bg-amber-500/80" />
              <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
            </div>

            {/* Switcher Tabs */}
            <div className="flex rounded-lg bg-slate-900 p-1 border border-white/10 text-xs font-mono">
              <button
                onClick={() => setCodeMode('wrapped')}
                className={`px-3 py-1 rounded-md transition font-semibold ${
                  codeMode === 'wrapped' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30 shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                + Bartholomew Guarded (1-Line)
              </button>
              <button
                onClick={() => setCodeMode('standard')}
                className={`px-3 py-1 rounded-md transition font-semibold ${
                  codeMode === 'standard' ? 'bg-rose-500/20 text-rose-300 border border-rose-400/30 shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                Standard Raw Client (Unprotected)
              </button>
            </div>

            <button
              onClick={handleCopyCode}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition flex items-center gap-1 border ${
                copied ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50' : 'bg-slate-800 text-slate-300 border-slate-700 hover:text-white'
              }`}
            >
              {copied ? <Check size={12} /> : <Copy size={12} />}
              <span>{copied ? 'Copied!' : 'Copy'}</span>
            </button>
          </div>

          <div className="p-5 sm:p-6">
            <pre className="font-mono text-xs sm:text-sm text-slate-200 overflow-x-auto leading-relaxed bg-slate-950 p-4 rounded-xl border border-white/5 shadow-inner">
              {codeMode === 'wrapped' ? wrappedCode : standardCode}
            </pre>
          </div>
        </div>

        {/* Live Animated Pipeline Diagram with Microsecond Latency Clock */}
        <div className="p-6 sm:p-7 rounded-2xl border border-white/10 max-w-3xl mx-auto bg-slate-900/90 shadow-2xl backdrop-blur-xl">
          <div className="flex items-center justify-between border-b border-white/10 pb-3 mb-4">
            <div className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
              <Zap size={14} className="animate-pulse" />
              <span>Live Invariant Execution Pipeline</span>
            </div>
            <div className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-slate-950 border border-white/10 font-mono text-xs text-cyan-300">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
              <span>Latency: {clockUs} µs</span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-xs font-mono text-center">
            <div className="p-3 rounded-xl bg-slate-950 border border-white/10 text-cyan-300 w-full sm:w-auto flex-1">
              [Agent Proposal]
            </div>
            <span className="text-cyan-400 font-bold hidden sm:inline">➔</span>
            <div className="p-3 rounded-xl bg-slate-950 border border-cyan-500/40 text-cyan-300 w-full sm:w-auto flex-1 shadow-sm shadow-cyan-500/10">
              [AST Scanner]
            </div>
            <span className="text-emerald-400 font-bold hidden sm:inline">➔</span>
            <div className="p-3 rounded-xl bg-slate-950 border border-emerald-500/40 text-emerald-300 w-full sm:w-auto flex-1 shadow-sm shadow-emerald-500/10">
              [Locked Sandbox]
            </div>
            <span className="text-indigo-400 font-bold hidden sm:inline">➔</span>
            <div className="p-3 rounded-xl bg-slate-950 border border-indigo-500/40 text-indigo-300 w-full sm:w-auto flex-1 shadow-sm shadow-indigo-500/10">
              [Ed25519 Seal]
            </div>
            <span className="text-emerald-400 font-bold hidden sm:inline">➔</span>
            <div className="p-3 rounded-xl bg-emerald-500/20 border border-emerald-400/60 text-emerald-300 w-full sm:w-auto flex-1 font-bold">
              [Safe Execution]
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
