import { CheckCircle2, Code2, ExternalLink, ShieldCheck, Lock, FileCheck2, Cpu } from 'lucide-react'
import Logo from './Logo'

export default function Footer() {
  return (
    <footer className="py-16 px-5 sm:px-8 bg-[#020204] text-[#a1a1aa] border-t border-[#27272a]/70 relative overflow-hidden">
      {/* Top ambient glowing accent line */}
      <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-emerald-500/70 to-transparent pointer-events-none" />

      {/* Subtle background glow */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[800px] h-[250px] bg-gradient-to-t from-emerald-500/5 to-transparent blur-[140px] pointer-events-none" />

      <div className="max-w-6xl mx-auto space-y-12 relative z-10">
        {/* Visual Certification Seals Banner */}
        <div className="p-6 sm:p-7 bg-gradient-to-b from-zinc-900/95 via-[#09090d]/95 to-[#050507] border border-zinc-800 rounded-2xl shadow-2xl relative backdrop-blur-xl">
          <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent pointer-events-none" />

          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="space-y-1 text-center md:text-left">
              <div className="text-xs font-mono font-bold uppercase tracking-wider text-emerald-400 flex items-center justify-center md:justify-start gap-2">
                <ShieldCheck size={16} className="text-emerald-400" />
                <span>[ VERIFIED COMPLIANCE &amp; SECURITY SEALS ]</span>
              </div>
              <p className="text-xs text-zinc-400 font-sans">
                Independently verifiable open-source security baselines, deterministic cryptography, and formal audit standards.
              </p>
            </div>

            {/* Seals Badges Grid */}
            <div className="flex flex-wrap items-center justify-center gap-3">
              {/* 2,791 Clean Tests Seal */}
              <div className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-[#050508] border border-emerald-500/40 text-[11px] font-mono text-[#d4d4d8] rounded-xl shadow-sm">
                <Cpu size={13} className="text-emerald-400" />
                <span className="text-emerald-400 font-bold">2,791 / 2,791 TESTS PASSING (100%)</span>
              </div>

              {/* FIPS 186-5 Cryptographic Seal */}
              <div className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-[#050508] border border-amber-500/40 text-[11px] font-mono text-[#d4d4d8] rounded-xl shadow-sm">
                <Lock size={13} className="text-amber-400" />
                <span>FIPS 186-5 ED25519</span>
              </div>

              {/* RFC 8785 Canonical Seal */}
              <div className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-[#050508] border border-cyan-500/40 text-[11px] font-mono text-[#d4d4d8] rounded-xl shadow-sm">
                <FileCheck2 size={13} className="text-cyan-400" />
                <span>RFC 8785 CANONICAL</span>
              </div>

              {/* Apache 2.0 Open Source */}
              <div className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-[#050508] border border-[#27272a] text-[11px] font-mono text-[#d4d4d8] rounded-xl shadow-sm">
                <Code2 size={13} className="text-[#a1a1aa]" />
                <span>APACHE-2.0</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Footer Links */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-10 pb-10 border-b border-[#27272a]/70">
          {/* Brand Info */}
          <div className="md:col-span-6 space-y-3.5">
            <div className="flex items-center">
              <Logo size={28} showText={true} />
            </div>
            <div className="flex items-center gap-2 text-xs text-emerald-400 font-mono pt-1">
              <CheckCircle2 size={14} />
              <span>[PROTOCOL ACTIVE: BTP v5.4.0 · SOVEREIGN TRUST &amp; SETTLEMENT RUNTIME]</span>
            </div>
            <p className="text-xs text-zinc-400 max-w-md font-sans">
              The fastest and most reliable local AST safety gating, zero prompt leakage, cryptographic agent passports, and trustless multi-chain escrow bridging for autonomous AI agents.
            </p>
          </div>

          {/* Navigation Links */}
          <div className="md:col-span-3 space-y-3">
            <div className="text-xs font-bold uppercase tracking-wider text-white font-mono">
              [PLATFORM]
            </div>
            <ul className="space-y-2.5 text-xs font-mono">
              <li>
                <a href="#swarm-arena" className="hover:text-white transition">
                  [SWARM ARENA]
                </a>
              </li>
              <li>
                <a href="#marketplace" className="hover:text-white transition">
                  [AGENT MARKETPLACE]
                </a>
              </li>
              <li>
                <a href="#p2p-mesh" className="text-cyan-400 hover:text-cyan-300 transition">
                  [P2P MESH &amp; BRIDGE]
                </a>
              </li>
              <li>
                <a href="#compliance" className="hover:text-white transition">
                  [COMPLIANCE DOSSIER]
                </a>
              </li>
              <li>
                <a href="#quickstart" className="text-emerald-400 hover:text-emerald-300 transition">
                  [10s QUICKSTART]
                </a>
              </li>
            </ul>
          </div>

          {/* Standards & Open Source */}
          <div className="md:col-span-3 space-y-3">
            <div className="text-xs font-bold uppercase tracking-wider text-white font-mono">
              [SPECIFICATIONS]
            </div>
            <ul className="space-y-2.5 text-xs font-mono">
              <li>
                <a
                  href="/SECURITY_WHITE_PAPER_AND_THREAT_MODEL.html"
                  target="_blank"
                  rel="noreferrer"
                  className="text-amber-400 hover:text-white transition inline-flex items-center gap-1 font-bold"
                >
                  <span>[ARCHITECTURE SPEC]</span>
                  <ExternalLink size={10} className="text-amber-400" />
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/ivegotahunnitonit/bartholomew"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-white transition inline-flex items-center gap-1"
                >
                  <Code2 size={12} />
                  <span>GITHUB SOURCE</span>
                  <ExternalLink size={10} className="text-[#71717a]" />
                </a>
              </li>
              <li>
                <a
                  href="https://www.rfc-editor.org/rfc/rfc8785"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-white transition inline-flex items-center gap-1"
                >
                  <span>RFC 8785 CANONICAL</span>
                  <ExternalLink size={10} className="text-[#71717a]" />
                </a>
              </li>
              <li>
                <a
                  href="https://csrc.nist.gov/pubs/fips/186-5/final"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-white transition inline-flex items-center gap-1"
                >
                  <span>FIPS 186-5 ED25519</span>
                  <ExternalLink size={10} className="text-[#71717a]" />
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-[#71717a] font-mono">
          <div>© 2026 BARTHOLOMEW TRUST PROTOCOL · SOVEREIGN OPEN STANDARDS</div>
          <div className="flex items-center gap-4">
            <a href="https://bartholomew.info" className="text-[#a1a1aa] hover:text-white transition">
              bartholomew.info
            </a>
            <span>·</span>
            <a
              href="https://github.com/ivegotahunnitonit/bartholomew/blob/main/LICENSE"
              target="_blank"
              rel="noreferrer"
              className="text-[#a1a1aa] hover:text-white transition"
            >
              [APACHE 2.0 LICENSE]
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
