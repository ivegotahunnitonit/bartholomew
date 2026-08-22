import { useState } from 'react'
import { Shield, Check, Copy, CheckCircle2, FileCode, Cpu, Download, Lock } from 'lucide-react'

export default function DesktopInstallerSection() {
  const [activeTab, setActiveTab] = useState<'pip' | 'npm' | 'vscode' | 'source'>('pip')
  const [copied, setCopied] = useState<string | null>(null)

  const commands = {
    pip: 'pip install git+https://github.com/ivegotahunnitonit/bartholomew.git',
    npm: 'npm install git+https://github.com/ivegotahunnitonit/bartholomew.git',
    vscode: 'code --install-extension https://bartholomew.info/bartholomew.vsix',
    source: 'git clone https://github.com/ivegotahunnitonit/bartholomew.git && cd bartholomew && pip install -e .'
  }

  const tabLabels = {
    pip: '[PYTHON PIP (GIT)]',
    npm: '[NODE.JS (GIT)]',
    vscode: '[VS CODE / CURSOR VSIX]',
    source: '[SOURCE REPO]'
  }

  const directDownloadFiles = {
    pip: { filename: 'btp_guard-latest.whl', href: '/btp_guard-latest.whl', label: 'DOWNLOAD WHEEL' },
    npm: { filename: 'bartholomew-npm.tgz', href: 'https://github.com/ivegotahunnitonit/bartholomew', label: 'VIEW NPM PACKAGE' },
    vscode: { filename: 'bartholomew.vsix', href: '/bartholomew.vsix', label: 'DOWNLOAD .VSIX' },
    source: { filename: 'bartholomew-desktop.zip', href: '/bartholomew-desktop.zip', label: 'DOWNLOAD SOURCE ZIP' }
  }

  const handleCopy = (tab: keyof typeof commands) => {
    navigator.clipboard.writeText(commands[tab])
    setCopied(tab)
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <section id="download" className="py-24 bg-black border-t border-[#1c1c1c] text-white relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#0a0a0a] border border-[#222222] text-[#f59e0b] text-xs font-mono font-bold uppercase tracking-wider mb-4">
            <Lock size={13} className="text-[#f59e0b]" />
            <span>[ VERIFIED PACKAGE DISTRIBUTION &amp; OFFLINE INSPECTION ]</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white font-sans">
            Install via Standard Package Managers
          </h2>
          <p className="mt-4 text-base text-[#a1a1aa] font-sans">
            Bartholomew is 100% open source. Install directly via PyPI, NPM, VS Code VSIX, or clone the repository to run the 16-suite CI security gate on your own machine with zero remote script execution.
          </p>
        </div>

        {/* OS Selector & Terminal Card */}
        <div className="max-w-4xl mx-auto bg-[#0a0a0a] border border-[#222222] shadow-2xl overflow-hidden">
          {/* Terminal Window Header */}
          <div className="flex items-center justify-between px-4 py-2.5 bg-[#000000] border-b border-[#222222]">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 bg-[#ef4444]" />
              <div className="w-2.5 h-2.5 bg-[#f59e0b]" />
              <div className="w-2.5 h-2.5 bg-[#10b981]" />
            </div>
            <span className="text-[11px] font-mono text-[#71717a]">terminal — verified-install-channel</span>
            <div className="w-12" />
          </div>

          {/* Selector Tabs */}
          <div className="flex border-b border-[#222222] bg-[#000000] p-2 gap-2">
            {(['pip', 'npm', 'vscode', 'source'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-2.5 px-3 text-xs font-mono font-bold transition flex items-center justify-center gap-2 border ${
                  activeTab === tab
                    ? 'bg-[#f59e0b] text-[#000000] border-[#f59e0b]'
                    : 'bg-[#0a0a0a] text-[#a1a1aa] border-[#222222] hover:text-[#ffffff]'
                }`}
              >
                <span>{tabLabels[tab]}</span>
              </button>
            ))}
          </div>

          {/* Terminal Command Display & Action */}
          <div className="p-6 sm:p-8">
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-[#000000] border border-[#222222] p-4 font-mono text-xs sm:text-sm text-[#f59e0b]">
              <span className="truncate flex-1">$ {commands[activeTab]}</span>
              <div className="flex items-center gap-2 shrink-0">
                <a
                  href={directDownloadFiles[activeTab].href}
                  download={directDownloadFiles[activeTab].filename}
                  className="px-3.5 py-2 text-xs font-mono font-bold bg-[#f59e0b] hover:bg-[#d97706] text-[#000000] transition flex items-center gap-1.5"
                >
                  <Download size={12} />
                  <span>[{directDownloadFiles[activeTab].label}]</span>
                </a>
                <button
                  onClick={() => handleCopy(activeTab)}
                  className={`px-3.5 py-2 text-xs font-mono font-bold transition flex items-center gap-1.5 border ${
                    copied === activeTab
                      ? 'bg-[#10b981] text-[#000000] border-[#10b981]'
                      : 'bg-[#0a0a0a] hover:bg-[#141414] text-[#ffffff] border-[#333333]'
                  }`}
                >
                  {copied === activeTab ? (
                    <>
                      <Check size={12} />
                      <span>COPIED</span>
                    </>
                  ) : (
                    <>
                      <Copy size={12} />
                      <span>COPY</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* In-Process Library Highlight Banner */}
            <div className="mt-6 p-4 bg-[#050505] border border-[#222222] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 font-mono text-xs text-[#a1a1aa]">
              <div className="space-y-1">
                <div className="text-white font-bold flex items-center gap-2">
                  <Shield size={14} className="text-[#10b981]" />
                  <span>EMBEDDED IN-PROCESS MODE (ZERO DAEMON REQUIRED)</span>
                </div>
                <p className="text-[#71717a] font-sans">
                  Run directly in your Python or Node.js script. Evaluates AST invariants in &lt;5.0 microseconds with zero IPC, zero background daemons, and zero network sockets.
                </p>
              </div>
              <a
                href="#sdk"
                className="px-3 py-1.5 bg-[#141414] hover:bg-[#222222] text-[#f59e0b] border border-[#333333] transition shrink-0 font-bold"
              >
                [VIEW 1-LINE CODE]
              </a>
            </div>

            {/* Verification Features Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
              <div className="p-4 bg-[#000000] border border-[#222222]">
                <div className="flex items-center gap-2 text-xs font-mono font-bold text-white mb-2">
                  <CheckCircle2 size={14} className="text-[#10b981]" />
                  <span>AUDITABLE CODEBASE</span>
                </div>
                <p className="text-xs text-[#71717a] font-sans leading-relaxed">
                  Every parser, invariant checker, and cryptographic signing routine is readable in 35-line reference files.
                </p>
              </div>

              <div className="p-4 bg-[#000000] border border-[#222222]">
                <div className="flex items-center gap-2 text-xs font-mono font-bold text-white mb-2">
                  <FileCode size={14} className="text-[#f59e0b]" />
                  <span>RFC 8785 DETERMINISM</span>
                </div>
                <p className="text-xs text-[#71717a] font-sans leading-relaxed">
                  JSON Canonicalization Scheme ensures identical byte-level hash determinism across Python, Go, and C.
                </p>
              </div>

              <div className="p-4 bg-[#000000] border border-[#222222]">
                <div className="flex items-center gap-2 text-xs font-mono font-bold text-white mb-2">
                  <Cpu size={14} className="text-[#38bdf8]" />
                  <span>NO PROXY BOTTLENECK</span>
                </div>
                <p className="text-xs text-[#71717a] font-sans leading-relaxed">
                  Compiled pure-C FFI executes in &lt;5 µs, avoiding the latency and failure modes of remote webhooks.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
