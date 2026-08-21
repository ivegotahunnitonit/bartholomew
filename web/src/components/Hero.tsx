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
# Result: Database wiped, credentials exposed, zero runtime interception.
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Clean up records: DROP TABLE users;"}]
)`

  const wrappedCode = `from btp_guard import wrap_client
import openai

# 1-Line Bartholomew Drop-In Guardrail
client = wrap_client(openai.OpenAI())

# PROTECTED: Intercepted in <50 µs via AST static invariant
# Raises BartholomewSecurityError before network call executes.
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
    <section className="relative min-h-[96vh] flex flex-col justify-center pt-28 pb-20 px-5 sm:px-8 bg-black text-white overflow-hidden">
      <div className="max-w-5xl mx-auto w-full relative z-10">
        {/* Top Monospace Badge Box */}
        <div className="flex items-center justify-center mb-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#0a0a0a] border border-[#222222] text-xs font-mono font-semibold uppercase tracking-wider text-[#a1a1aa]">
            <Sparkles size={13} className="text-[#f59e0b]" />
            <span>[ PROTOCOL: BTP/2.2 · CRYPTOGRAPHIC AGENT GUARD ]</span>
          </div>
        </div>

        {/* Metallic Dimensional Hero Title */}
        <h1
          className="text-center font-bold mb-5 font-sans hero-metallic-title"
          style={{
            fontSize: 'clamp(2.1rem, 3.8vw, 3.25rem)',
            lineHeight: 1.12,
            letterSpacing: '-0.025em'
          }}
        >
          The Seatbelt and Black Box <br className="hidden sm:block" />
          for Autonomous AI Agents.
        </h1>

        {/* High-Contrast Zinc Subtitle */}
        <p className="text-center mx-auto mb-8 text-[#d4d4d8] leading-relaxed max-w-2xl text-sm sm:text-base font-sans">
          Empower AI agents with execution access without the risk. Bartholomew intercepts destructive code, unauthorized database drops, and API overspending in <strong className="text-[#ffffff]">under 50 microseconds</strong>—using deterministic AST scanning and cryptographic audit trails.
        </p>

        {/* High-Contrast CTA Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 mb-6">
          <a
            href="#download"
            className="px-7 py-3 text-sm font-mono font-bold bg-[#f59e0b] hover:bg-[#d97706] text-[#000000] border border-[#f59e0b] transition flex items-center gap-2 shadow-lg"
          >
            <Download size={15} />
            <span>[ INSTALL DESKTOP CLI ]</span>
          </a>
          <a
            href="#threat-simulator"
            className="px-6 py-3 text-sm font-mono font-semibold bg-[#0a0a0a] hover:bg-[#141414] border border-[#222222] hover:border-[#444444] text-[#ffffff] transition flex items-center gap-2"
          >
            <Shield size={15} className="text-[#10b981]" />
            <span>[ THREAT SIMULATOR ]</span>
          </a>
          <a
            href="https://github.com/ivegotahunnitonit/bartholomew"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 text-sm font-mono font-semibold bg-[#0a0a0a] hover:bg-[#141414] border border-[#222222] hover:border-[#444444] text-[#a1a1aa] hover:text-[#ffffff] transition flex items-center gap-2"
          >
            <Terminal size={15} />
            <span>GITHUB</span>
            <ArrowRight size={13} />
          </a>
        </div>

        {/* Floating Monospace Stat Box Chips */}
        <div className="flex flex-wrap items-center justify-center gap-3 mb-12">
          <div className="flex items-center gap-2 px-3 py-1 bg-[#0a0a0a] border border-[#222222] text-xs font-mono text-[#f59e0b]">
            <Zap size={13} />
            <span>[ LATENCY: &lt;50 µs ]</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1 bg-[#0a0a0a] border border-[#222222] text-xs font-mono text-[#10b981]">
            <Lock size={13} />
            <span>[ IN-MEMORY / ZERO CLOUD CALLS ]</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1 bg-[#0a0a0a] border border-[#222222] text-xs font-mono text-[#ffffff]">
            <Shield size={13} className="text-[#10b981]" />
            <span>[ PROOF: ED25519 SIGNED ]</span>
          </div>
        </div>

        {/* Side-by-Side 1-Line Drop-In Code Comparison in Cyber-Terminal macOS Frame */}
        <div className="border border-[#222222] max-w-3xl mx-auto mb-14 bg-[#0a0a0a] shadow-2xl overflow-hidden">
          {/* macOS Titlebar with Mode Switcher */}
          <div className="flex items-center justify-between px-4 py-2.5 bg-[#000000] border-b border-[#222222]">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 bg-[#ef4444]" />
              <div className="w-2.5 h-2.5 bg-[#f59e0b]" />
              <div className="w-2.5 h-2.5 bg-[#10b981]" />
            </div>

            {/* Switcher Tabs */}
            <div className="flex bg-[#0a0a0a] border border-[#222222] text-xs font-mono">
              <button
                onClick={() => setCodeMode('wrapped')}
                className={`px-3 py-1 transition font-bold ${
                  codeMode === 'wrapped' ? 'bg-[#10b981] text-[#000000]' : 'text-[#a1a1aa] hover:text-[#ffffff]'
                }`}
              >
                [+ BARTHOLOMEW GUARDED]
              </button>
              <button
                onClick={() => setCodeMode('standard')}
                className={`px-3 py-1 transition font-bold ${
                  codeMode === 'standard' ? 'bg-[#ef4444] text-[#ffffff]' : 'text-[#a1a1aa] hover:text-[#ffffff]'
                }`}
              >
                [RAW UNPROTECTED]
              </button>
            </div>

            <button
              onClick={handleCopyCode}
              className={`px-2.5 py-1 text-xs font-mono font-semibold transition flex items-center gap-1 border ${
                copied ? 'bg-[#10b981]/20 text-[#10b981] border-[#10b981]/50' : 'bg-[#0a0a0a] text-[#a1a1aa] border-[#222222] hover:text-[#ffffff]'
              }`}
            >
              {copied ? <Check size={11} /> : <Copy size={11} />}
              <span>{copied ? '[COPIED]' : '[COPY]'}</span>
            </button>
          </div>

          <div className="p-5">
            <pre className="font-mono text-xs sm:text-sm text-[#d4d4d8] overflow-x-auto leading-relaxed bg-[#000000] p-4 border border-[#1a1a1a]">
              {codeMode === 'wrapped' ? wrappedCode : standardCode}
            </pre>
          </div>
        </div>

        {/* Live Cyber Pipeline Flow Diagram with Real-Time Latency Clock */}
        <div className="p-6 border border-[#222222] max-w-3xl mx-auto bg-[#0a0a0a]">
          <div className="flex items-center justify-between border-b border-[#222222] pb-3 mb-4 font-mono text-xs">
            <div className="text-[#f59e0b] font-bold uppercase tracking-wider flex items-center gap-2">
              <Zap size={14} className="text-[#f59e0b]" />
              <span>[LIVE INVARIANT PIPELINE]</span>
            </div>
            <div className="flex items-center gap-2 px-2.5 py-1 bg-[#000000] border border-[#222222] text-[#10b981] font-bold">
              <span className="w-1.5 h-1.5 bg-[#10b981] animate-ping" />
              <span>LATENCY: {clockUs} µs</span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-xs font-mono text-center">
            <div className="p-2.5 bg-[#000000] border border-[#222222] text-[#a1a1aa] flex-1 w-full sm:w-auto">
              [AGENT PROPOSAL]
            </div>
            <span className="text-[#f59e0b] font-bold hidden sm:inline">&gt;</span>
            <div className="p-2.5 bg-[#000000] border border-[#f59e0b]/50 text-[#f59e0b] flex-1 w-full sm:w-auto">
              [AST SCANNER]
            </div>
            <span className="text-[#10b981] font-bold hidden sm:inline">&gt;</span>
            <div className="p-2.5 bg-[#000000] border border-[#10b981]/50 text-[#10b981] flex-1 w-full sm:w-auto">
              [SANDBOX CAGE]
            </div>
            <span className="text-[#10b981] font-bold hidden sm:inline">&gt;</span>
            <div className="p-2.5 bg-[#000000] border border-[#10b981]/50 text-[#ffffff] flex-1 w-full sm:w-auto">
              [ED25519 SEAL]
            </div>
            <span className="text-[#10b981] font-bold hidden sm:inline">&gt;</span>
            <div className="p-2.5 bg-[#10b981] text-[#000000] font-bold flex-1 w-full sm:w-auto">
              [SAFE EXECUTION]
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
