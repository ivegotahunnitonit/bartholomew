import { useState } from 'react'

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
    <section id="download" className="py-20 bg-slate-900 border-y border-slate-800 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-4">
            ⚡ Official Desktop Distribution
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            Install Bartholomew on Your Desktop
          </h2>
          <p className="mt-4 text-lg text-slate-400">
            One command to install the sub-millisecond BTP cryptographic guardrail engine directly onto your terminal.
          </p>
        </div>

        {/* OS Selector Tabs */}
        <div className="max-w-4xl mx-auto bg-slate-950 rounded-2xl border border-slate-800 shadow-2xl overflow-hidden">
          <div className="flex border-b border-slate-800 bg-slate-900/50 p-2 gap-2">
            {(['windows', 'mac', 'linux', 'pip'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-3 px-4 rounded-xl text-sm font-semibold transition-all flex items-center justify-center gap-2 ${
                  activeTab === tab
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                {tab === 'windows' && '🪟 Windows (PowerShell)'}
                {tab === 'mac' && '🍎 macOS (Terminal)'}
                {tab === 'linux' && '🐧 Linux (Bash)'}
                {tab === 'pip' && '🐍 Python (pip)'}
              </button>
            ))}
          </div>

          {/* Terminal Command Display */}
          <div className="p-6 sm:p-8">
            <div className="flex items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-xl p-4 font-mono text-sm sm:text-base text-emerald-400">
              <span className="truncate">{commands[activeTab]}</span>
              <button
                onClick={() => handleCopy(activeTab)}
                className="shrink-0 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-bold transition flex items-center gap-1.5 border border-slate-700"
              >
                {copied === activeTab ? '✅ Copied!' : '📋 Copy Command'}
              </button>
            </div>

            {/* Quickstart Command Cheatsheet */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800/80">
                <div className="text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-1">Step 1</div>
                <div className="font-mono text-sm text-slate-200">bartholomew version</div>
                <p className="text-xs text-slate-400 mt-1">Verify BTP/2.2 protocol and target latency (&lt;50 µs).</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800/80">
                <div className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-1">Step 2</div>
                <div className="font-mono text-sm text-slate-200">bartholomew init</div>
                <p className="text-xs text-slate-400 mt-1">Generates local Ed25519 keypair and project security policy.</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800/80">
                <div className="text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-1">Step 3</div>
                <div className="font-mono text-sm text-slate-200">bartholomew audit .</div>
                <p className="text-xs text-slate-400 mt-1">Performs compiler-grade AST security scan with zero cloud overhead.</p>
              </div>
            </div>

            {/* Source / GitHub Direct Link */}
            <div className="mt-6 pt-6 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-3">
              <div>
                <span>Source Code & Security Audits available at </span>
                <a
                  href="https://github.com/ivegotahunnitonit/bartholomew"
                  target="_blank"
                  rel="noreferrer"
                  className="text-indigo-400 hover:underline font-semibold"
                >
                  github.com/ivegotahunnitonit/bartholomew
                </a>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-emerald-400">● 100% Offline Compatible</span>
                <span>● Zero Telemetry / Airgap Ready</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
