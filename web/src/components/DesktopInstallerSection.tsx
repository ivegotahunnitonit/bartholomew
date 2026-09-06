import { useState } from 'react'
import { Shield, Check, Copy, CheckCircle2, FileCode, Cpu } from 'lucide-react'

export default function DesktopInstallerSection() {
  const [activeTab, setActiveTab] = useState<'pip' | 'cli' | 'vscode' | 'source'>('pip')
  const [copied, setCopied] = useState<string | null>(null)

  const commands = {
    pip: 'pip install btp-guard',
    cli: 'pip install btp-guard && btp-guard init',
    vscode: 'code --install-extension bartholomew.vsix',
    source: 'git clone https://github.com/ivegotahunnitonit/bartholomew.git && cd bartholomew && pip install -e .'
  }

  const tabLabels = {
    pip: '[PYTHON PIP (PYPI)]',
    cli: '[BTP-GUARD CLI INIT]',
    vscode: '[VS CODE / CURSOR VSIX]',
    source: '[SOURCE REPO]'
  }

  const directDownloadFiles = {
    pip: { filename: 'pypi-btp-guard', href: 'https://pypi.org/project/btp-guard/', label: 'VIEW PYPI PACKAGE' },
    cli: { filename: 'pypi-btp-guard', href: 'https://pypi.org/project/btp-guard/', label: 'VIEW PYPI DOCUMENTATION' },
    vscode: { filename: 'bartholomew.vsix', href: 'https://bartholomew.info/bartholomew.vsix', label: 'DOWNLOAD .VSIX' },
    source: { filename: 'source-main.zip', href: 'https://github.com/ivegotahunnitonit/bartholomew/archive/refs/heads/main.zip', label: 'DOWNLOAD SOURCE ZIP' }
  }

  const handleCopy = (tab: keyof typeof commands) => {
    navigator.clipboard.writeText(commands[tab])
    setCopied(tab)
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <section id="quickstart" className="py-24 bg-gradient-to-b from-[#040406] via-[#08080c] to-[#040406] border-t border-[#1f1f23] text-white relative overflow-hidden">
      <div id="download" className="absolute -top-24" />
      {/* Ambient background glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-[#10b981]/5 blur-[140px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#10b981]/10 border border-[#10b981]/30 text-[#10b981] text-xs font-mono font-bold uppercase tracking-wider mb-4 rounded-full">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse" />
            <span>[ VERIFIED SOURCE INSTALLATION &amp; OFFLINE INSPECTION ]</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white font-sans">
            Install Directly from Verified Registries
          </h2>
          <p className="mt-4 text-base text-[#a1a1aa] font-sans">
            Bartholomew is 100% open source. Install directly via pip, btp-guard CLI, VS Code extension, or clone the repository to run the 31-suite security gate on your own machine with zero remote script execution.
          </p>
        </div>

        {/* OS Selector & Terminal Card - Frontier Glassmorphism */}
        <div className="max-w-4xl mx-auto rounded-2xl border border-[#27272a] bg-gradient-to-b from-[#0e0e11] via-[#09090b] to-[#040405] shadow-[0_20px_50px_-20px_rgba(16,185,129,0.15)] relative overflow-hidden">
          {/* Top Glowing Ambient Highlight */}
          <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#10b981]/70 to-transparent pointer-events-none" />

          {/* Terminal Window Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-[#08080a] border-b border-[#1f1f23]">
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#ef4444] inline-block shadow-[0_0_8px_rgba(239,68,68,0.4)]" />
                <span className="w-2.5 h-2.5 rounded-full bg-[#f59e0b] inline-block shadow-[0_0_8px_rgba(245,158,11,0.4)]" />
                <span className="w-2.5 h-2.5 rounded-full bg-[#10b981] inline-block shadow-[0_0_8px_rgba(16,185,129,0.4)]" />
              </div>
              <div className="h-3.5 w-[1px] bg-[#27272a] mx-1" />
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#10b981]/10 border border-[#10b981]/30 text-[10px] font-mono text-[#10b981] font-bold uppercase">
                verified-install-channel
              </div>
            </div>
            <div className="text-[11px] font-mono text-[#71717a] hidden sm:block">FIPS 186-5 &bull; RFC 8785</div>
          </div>

          {/* Selector Tabs — 2 col grid on mobile, 4 col on sm+ */}
          <div className="grid grid-cols-2 sm:grid-cols-4 border-b border-[#1f1f23] bg-[#060608] p-2 gap-2">
            {(['pip', 'cli', 'vscode', 'source'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-2 px-3 text-[11px] sm:text-xs font-mono font-bold transition flex items-center justify-center gap-1.5 border rounded-lg min-h-[42px] ${
                  activeTab === tab
                    ? 'bg-[#10b981]/15 text-white border-[#10b981] shadow-[0_0_15px_rgba(16,185,129,0.2)]'
                    : 'bg-[#0b0b0e] text-[#a1a1aa] border-[#222226] hover:text-white hover:border-[#38383f]'
                }`}
              >
                <span className="text-center leading-tight">{tabLabels[tab]}</span>
              </button>
            ))}
          </div>

          {/* Terminal Command Display & Action */}
          <div className="p-4 sm:p-8">
            {/* Command string + action buttons */}
            <div className="flex flex-col gap-3 bg-[#030304] border border-[#1f1f23] rounded-xl p-4 font-mono text-xs shadow-inner">
              {/* Scrollable command line */}
              <div className="overflow-x-auto whitespace-nowrap flex items-center gap-2">
                <span className="text-[#10b981] font-bold text-sm">❯</span>
                <span className="text-[#f59e0b]">$ {commands[activeTab]}</span>
              </div>
              {/* Action buttons */}
              <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#1a1a1e]">
                <a
                  href={directDownloadFiles[activeTab].href}
                  target="_blank"
                  rel="noreferrer"
                  className="flex-1 min-w-[120px] px-3.5 py-2 text-xs font-mono font-bold bg-[#10b981]/15 hover:bg-[#10b981]/25 text-[#10b981] border border-[#10b981]/40 transition flex items-center justify-center gap-1.5 rounded-lg shadow-sm"
                >
                  <span>[{directDownloadFiles[activeTab].label}]</span>
                </a>
                <button
                  onClick={() => handleCopy(activeTab)}
                  className={`flex-1 min-w-[80px] px-3.5 py-2 text-xs font-mono font-bold transition flex items-center justify-center gap-1.5 border rounded-lg ${
                    copied === activeTab
                      ? 'bg-[#10b981] text-black border-[#10b981] shadow-[0_0_15px_rgba(16,185,129,0.3)]'
                      : 'bg-[#111115] hover:bg-[#18181c] text-white border-[#27272a]'
                  }`}
                >
                  {copied === activeTab ? (
                    <>
                      <Check size={12} className="stroke-[3]" />
                      <span>COPIED!</span>
                    </>
                  ) : (
                    <>
                      <Copy size={12} />
                      <span>COPY COMMAND</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* In-Process Library Highlight Banner */}
            <div className="mt-6 p-4.5 bg-gradient-to-r from-[#10b981]/10 via-[#0a0a0d] to-[#0a0a0d] border border-[#10b981]/30 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 font-mono text-xs">
              <div className="space-y-1">
                <div className="text-white font-bold flex items-center gap-2">
                  <Shield size={15} className="text-[#10b981]" />
                  <span>EMBEDDED IN-PROCESS MODE (ZERO DAEMONS REQUIRED)</span>
                </div>
                <p className="text-[#a1a1aa] font-sans text-xs">
                  Runs directly in your process memory. Evaluates AST invariants with the fastest and most reliable local gating, with zero IPC, zero background daemons, and zero network telemetry.
                </p>
              </div>
              <a
                href="#sdk"
                className="px-3.5 py-1.5 bg-[#10b981]/15 hover:bg-[#10b981]/25 text-[#10b981] border border-[#10b981]/40 rounded-lg transition shrink-0 font-bold"
              >
                [VIEW 1-LINE CODE]
              </a>
            </div>

            {/* Verification Features Grid — 1 col mobile, 3 col md+ */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 mt-6">
              <div className="p-4 bg-gradient-to-b from-[#0e0e12]/80 to-[#070709]/90 border border-[#27272a]/70 rounded-xl hover:border-[#10b981]/40 transition">
                <div className="flex items-center gap-2 text-xs font-mono font-bold text-white mb-2">
                  <CheckCircle2 size={14} className="text-[#10b981]" />
                  <span>AUDITABLE CODEBASE</span>
                </div>
                <p className="text-xs text-[#a1a1aa] font-sans leading-relaxed">
                  Every parser, invariant checker, and cryptographic signing routine is readable in clean, audited reference files.
                </p>
              </div>

              <div className="p-4 bg-gradient-to-b from-[#0e0e12]/80 to-[#070709]/90 border border-[#27272a]/70 rounded-xl hover:border-[#10b981]/40 transition">
                <div className="flex items-center gap-2 text-xs font-mono font-bold text-white mb-2">
                  <FileCode size={14} className="text-[#f59e0b]" />
                  <span>RFC 8785 DETERMINISM</span>
                </div>
                <p className="text-xs text-[#a1a1aa] font-sans leading-relaxed">
                  JSON Canonicalization Scheme ensures identical byte-level hash determinism across Python, Go, and C.
                </p>
              </div>

              <div className="p-4 bg-gradient-to-b from-[#0e0e12]/80 to-[#070709]/90 border border-[#27272a]/70 rounded-xl hover:border-[#10b981]/40 transition">
                <div className="flex items-center gap-2 text-xs font-mono font-bold text-white mb-2">
                  <Cpu size={14} className="text-[#10b981]" />
                  <span>NO PROXY BOTTLENECK</span>
                </div>
                <p className="text-xs text-[#a1a1aa] font-sans leading-relaxed">
                  Pure local in-process gating provides the fastest and most reliable AST inspection, avoiding the latency and network failure modes of remote webhooks.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
