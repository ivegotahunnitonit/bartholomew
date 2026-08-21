import { useState } from 'react'
import { Shield, Check, Copy, CheckCircle2, FileCode, Cpu, ArrowRight, Download } from 'lucide-react'

export default function DesktopInstallerSection() {
  const [activeTab, setActiveTab] = useState<'windows' | 'mac' | 'linux' | 'pip'>('windows')
  const [copied, setCopied] = useState<string | null>(null)

  const commands = {
    windows: 'irm https://bartholomew.info/install.ps1 | iex',
    mac: 'curl -fsSL https://bartholomew.info/install.sh | bash',
    linux: 'curl -fsSL https://bartholomew.info/install.sh | bash',
    pip: 'pip install git+https://github.com/ivegotahunnitonit/bartholomew.git'
  }

  const directDownloadFiles = {
    windows: { filename: 'install.bat', href: '/install.bat', label: 'DOWNLOAD INSTALL.BAT' },
    mac: { filename: 'install.sh', href: '/install.sh', label: 'DOWNLOAD INSTALL.SH' },
    linux: { filename: 'install.sh', href: '/install.sh', label: 'DOWNLOAD INSTALL.SH' },
    pip: { filename: 'install.ps1', href: '/install.ps1', label: 'DOWNLOAD SCRIPT' }
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
            <Shield size={13} className="text-[#f59e0b]" />
            <span>[ 1-CLICK DESKTOP DISTRIBUTION ]</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white font-sans">
            Install Bartholomew on Your Desktop
          </h2>
          <p className="mt-4 text-base text-[#a1a1aa] font-sans">
            One click to download the direct installer, or one command to run the sub-millisecond BTP cryptographic guardrail engine directly in your terminal.
          </p>
        </div>

        {/* OS Selector & Terminal Card with Cyber-Terminal Styling */}
        <div className="max-w-4xl mx-auto bg-[#0a0a0a] border border-[#222222] shadow-2xl overflow-hidden">
          {/* Terminal Window Header */}
          <div className="flex items-center justify-between px-4 py-2.5 bg-[#000000] border-b border-[#222222]">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 bg-[#ef4444]" />
              <div className="w-2.5 h-2.5 bg-[#f59e0b]" />
              <div className="w-2.5 h-2.5 bg-[#10b981]" />
            </div>
            <span className="text-[11px] font-mono text-[#71717a]">terminal — install-bartholomew</span>
            <div className="w-12" />
          </div>

          {/* OS Selector Tabs */}
          <div className="flex border-b border-[#222222] bg-[#000000] p-2 gap-2">
            {(['windows', 'mac', 'linux', 'pip'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-2.5 px-3 text-xs font-mono font-bold transition flex items-center justify-center gap-2 border ${
                  activeTab === tab
                    ? 'bg-[#f59e0b] text-[#000000] border-[#f59e0b]'
                    : 'bg-[#0a0a0a] text-[#a1a1aa] border-[#222222] hover:text-[#ffffff]'
                }`}
              >
                {tab === 'windows' && <span>[WINDOWS]</span>}
                {tab === 'mac' && <span>[MACOS]</span>}
                {tab === 'linux' && <span>[LINUX]</span>}
                {tab === 'pip' && <span>[PYTHON PIP]</span>}
              </button>
            ))}
          </div>

          {/* Terminal Command Display & 1-Click Direct Download Action */}
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
                  <span>[DOWNLOAD FILE]</span>
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
                      <span>[COPIED]</span>
                    </>
                  ) : (
                    <>
                      <Copy size={12} />
                      <span>[COPY]</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Quickstart Command Cheatsheet with Square Cards */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-[#000000] border border-[#222222]">
                <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-[#f59e0b] uppercase tracking-wider mb-2">
                  <Cpu size={13} />
                  <span>[STEP 1]</span>
                </div>
                <div className="font-mono text-xs text-[#ffffff] bg-[#0a0a0a] px-2.5 py-1.5 border border-[#1a1a1a]">
                  bartholomew version
                </div>
                <p className="text-xs text-[#a1a1aa] mt-2 font-sans">Verify BTP/2.2 protocol active state and sub-50 µs latency.</p>
              </div>

              <div className="p-4 bg-[#000000] border border-[#222222]">
                <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-[#10b981] uppercase tracking-wider mb-2">
                  <Shield size={13} />
                  <span>[STEP 2]</span>
                </div>
                <div className="font-mono text-xs text-[#ffffff] bg-[#0a0a0a] px-2.5 py-1.5 border border-[#1a1a1a]">
                  bartholomew init
                </div>
                <p className="text-xs text-[#a1a1aa] mt-2 font-sans">Generates sovereign Ed25519 keypair and project security policy.</p>
              </div>

              <div className="p-4 bg-[#000000] border border-[#222222]">
                <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-[#ffffff] uppercase tracking-wider mb-2">
                  <FileCode size={13} />
                  <span>[STEP 3]</span>
                </div>
                <div className="font-mono text-xs text-[#ffffff] bg-[#0a0a0a] px-2.5 py-1.5 border border-[#1a1a1a]">
                  bartholomew daemon start
                </div>
                <p className="text-xs text-[#a1a1aa] mt-2 font-sans">Starts background guard daemon on localhost with desktop alerts.</p>
              </div>
            </div>

            {/* Source / GitHub Direct Link */}
            <div className="mt-8 pt-6 border-t border-[#222222] flex flex-col sm:flex-row items-center justify-between text-xs text-[#a1a1aa] gap-3 font-mono">
              <div>
                <span>Source repository: </span>
                <a
                  href="https://github.com/ivegotahunnitonit/bartholomew"
                  target="_blank"
                  rel="noreferrer"
                  className="text-[#f59e0b] hover:underline font-semibold inline-flex items-center gap-1"
                >
                  github.com/ivegotahunnitonit/bartholomew
                  <ArrowRight size={11} />
                </a>
              </div>
              <div className="flex items-center gap-4 text-[#a1a1aa]">
                <span className="flex items-center gap-1 text-[#10b981]">
                  <CheckCircle2 size={12} />
                  100% Offline Compatible
                </span>
                <span className="flex items-center gap-1 text-[#ffffff]">
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
