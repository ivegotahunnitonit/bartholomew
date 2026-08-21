import { useState } from 'react'
import { Terminal, Shield, Check, Copy, CheckCircle2, FileCode, Cpu, ArrowRight } from 'lucide-react'

export default function DesktopInstallerSection() {
  const [activeTab, setActiveTab] = useState<'windows' | 'mac' | 'linux' | 'pip'>('windows')
  const [copied, setCopied] = useState<string | null>(null)

  const commands = {
    windows: 'irm https://raw.githubusercontent.com/ivegotahunnitonit/bartholomew/main/install.ps1 | iex',
    mac: 'curl -fsSL https://raw.githubusercontent.com/ivegotahunnitonit/bartholomew/main/install.sh | bash',
    linux: 'curl -fsSL https://raw.githubusercontent.com/ivegotahunnitonit/bartholomew/main/install.sh | bash',
    pip: 'pip install git+https://github.com/ivegotahunnitonit/bartholomew.git'
  }

  const handleCopy = (tab: keyof typeof commands) => {
    navigator.clipboard.writeText(commands[tab])
    setCopied(tab)
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <section id="download" className="py-24 bg-slate-950 border-t border-slate-900 text-white relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-400/30 text-cyan-300 text-xs font-mono font-bold uppercase tracking-wider mb-4 shadow-sm">
            <Shield size={13} className="text-cyan-400" />
            1-Click Desktop Distribution
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white font-sans">
            Install Bartholomew on Your Desktop
          </h2>
          <p className="mt-4 text-base sm:text-lg text-slate-300">
            One command to install the sub-millisecond BTP cryptographic guardrail engine directly onto your terminal.
          </p>
        </div>

        {/* OS Selector & Terminal Card with macOS Styling */}
        <div className="max-w-4xl mx-auto bg-slate-900/90 rounded-2xl border border-white/10 shadow-2xl overflow-hidden backdrop-blur-xl hover:border-cyan-500/30 transition-all duration-200">
          {/* macOS Titlebar */}
          <div className="flex items-center justify-between px-4 py-3 bg-slate-950/80 border-b border-white/10">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-rose-500/80" />
              <div className="w-3 h-3 rounded-full bg-amber-500/80" />
              <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
            </div>
            <span className="text-[11px] font-mono text-slate-400">terminal — install-bartholomew</span>
            <div className="w-12" />
          </div>

          {/* OS Selector Tabs */}
          <div className="flex border-b border-white/10 bg-slate-950/60 p-2 gap-2">
            {(['windows', 'mac', 'linux', 'pip'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-3 px-4 rounded-xl text-xs sm:text-sm font-semibold transition-all flex items-center justify-center gap-2 ${
                  activeTab === tab
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/40 shadow-lg shadow-cyan-500/10'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                {tab === 'windows' && (
                  <>
                    <Terminal size={14} />
                    <span>Windows (PowerShell)</span>
                  </>
                )}
                {tab === 'mac' && (
                  <>
                    <Terminal size={14} />
                    <span>macOS (Terminal)</span>
                  </>
                )}
                {tab === 'linux' && (
                  <>
                    <Terminal size={14} />
                    <span>Linux (Bash)</span>
                  </>
                )}
                {tab === 'pip' && (
                  <>
                    <FileCode size={14} />
                    <span>Python (pip)</span>
                  </>
                )}
              </button>
            ))}
          </div>

          {/* Terminal Command Display */}
          <div className="p-6 sm:p-8">
            <div className="flex items-center justify-between gap-4 bg-slate-950 border border-white/10 rounded-xl p-4 font-mono text-xs sm:text-sm text-cyan-300 shadow-inner">
              <span className="truncate">{commands[activeTab]}</span>
              <button
                onClick={() => handleCopy(activeTab)}
                className={`shrink-0 px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-1.5 border shadow-sm ${
                  copied === activeTab
                    ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300'
                    : 'bg-slate-800 hover:bg-slate-700 text-white border-slate-700 hover:border-cyan-400/50'
                }`}
              >
                {copied === activeTab ? (
                  <>
                    <Check size={13} className="text-emerald-400" />
                    <span className="text-emerald-300">Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy size={13} />
                    <span>Copy Command</span>
                  </>
                )}
              </button>
            </div>

            {/* Quickstart Command Cheatsheet with Hover Transforms */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-5 rounded-xl bg-slate-950/70 border border-white/10 hover:-translate-y-1 hover:border-cyan-500/30 transition-all duration-200">
                <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider mb-2">
                  <Cpu size={13} />
                  <span>Step 1</span>
                </div>
                <div className="font-mono text-xs sm:text-sm text-slate-200 bg-slate-900 px-3 py-2 rounded border border-white/5">
                  bartholomew version
                </div>
                <p className="text-xs text-slate-400 mt-2">Verify BTP/2.2 protocol active state and sub-50 µs latency.</p>
              </div>

              <div className="p-5 rounded-xl bg-slate-950/70 border border-white/10 hover:-translate-y-1 hover:border-emerald-500/30 transition-all duration-200">
                <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider mb-2">
                  <Shield size={13} />
                  <span>Step 2</span>
                </div>
                <div className="font-mono text-xs sm:text-sm text-slate-200 bg-slate-900 px-3 py-2 rounded border border-white/5">
                  bartholomew init
                </div>
                <p className="text-xs text-slate-400 mt-2">Generates sovereign Ed25519 keypair and project security policy.</p>
              </div>

              <div className="p-5 rounded-xl bg-slate-950/70 border border-white/10 hover:-translate-y-1 hover:border-indigo-500/30 transition-all duration-200">
                <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-indigo-400 uppercase tracking-wider mb-2">
                  <FileCode size={13} />
                  <span>Step 3</span>
                </div>
                <div className="font-mono text-xs sm:text-sm text-slate-200 bg-slate-900 px-3 py-2 rounded border border-white/5">
                  bartholomew audit .
                </div>
                <p className="text-xs text-slate-400 mt-2">Performs compiler-grade AST security scan with zero cloud overhead.</p>
              </div>
            </div>

            {/* Source / GitHub Direct Link */}
            <div className="mt-8 pt-6 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-3 font-mono">
              <div>
                <span>Source: </span>
                <a
                  href="https://github.com/ivegotahunnitonit/bartholomew"
                  target="_blank"
                  rel="noreferrer"
                  className="text-cyan-400 hover:underline font-semibold inline-flex items-center gap-1"
                >
                  github.com/ivegotahunnitonit/bartholomew
                  <ArrowRight size={11} />
                </a>
              </div>
              <div className="flex items-center gap-4 text-slate-400">
                <span className="flex items-center gap-1 text-emerald-400">
                  <CheckCircle2 size={12} />
                  100% Offline Compatible
                </span>
                <span className="flex items-center gap-1 text-cyan-400">
                  <CheckCircle2 size={12} />
                  Zero Cloud Telemetry
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
