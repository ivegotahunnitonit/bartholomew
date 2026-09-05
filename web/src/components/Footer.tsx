import { CheckCircle2, Code2, ExternalLink, ShieldCheck, Lock, FileCheck2, Cpu } from 'lucide-react'
import Logo from './Logo'

export default function Footer() {
  return (
    <footer className="py-16 px-5 sm:px-8 bg-[#020204] text-[#a1a1aa] border-t border-[#27272a]/70 relative overflow-hidden">
      {/* Top ambient glowing accent line */}
      <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#10b981]/70 to-transparent pointer-events-none" />

      {/* Subtle background glow */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[800px] h-[250px] bg-gradient-to-t from-[#10b981]/5 to-transparent blur-[140px] pointer-events-none" />

      <div className="max-w-6xl mx-auto space-y-12 relative z-10">
        {/* Visual Certification Seals Banner */}
        <div className="p-6 sm:p-7 bg-gradient-to-b from-[#0e0e14]/95 via-[#09090d]/95 to-[#050507] border border-[#27272a]/80 rounded-2xl shadow-2xl relative backdrop-blur-xl">
          <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#10b981]/50 to-transparent pointer-events-none" />

          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="space-y-1 text-center md:text-left">
              <div className="text-xs font-mono font-bold uppercase tracking-wider text-[#10b981] flex items-center justify-center md:justify-start gap-2">
                <ShieldCheck size={16} className="text-[#10b981]" />
                <span>[ VERIFIED COMPLIANCE &amp; SECURITY SEALS ]</span>
              </div>
              <p className="text-xs text-[#a1a1aa] font-sans">
                Independently verifiable open-source security baselines, deterministic cryptography, and formal audit standards.
              </p>
            </div>

            {/* Seals Badges Grid */}
            <div className="flex flex-wrap items-center justify-center gap-3">
              {/* 31/31 CI Gate Seal */}
              <div className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-[#050508] border border-[#10b981]/40 text-[11px] font-mono text-[#d4d4d8] rounded-xl shadow-sm">
                <Cpu size={13} className="text-[#10b981]" />
                <span className="text-[#10b981] font-bold">31/31 CI GATES</span>
              </div>

              {/* FIPS 186-5 Cryptographic Seal */}
              <div className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-[#050508] border border-[#f59e0b]/40 text-[11px] font-mono text-[#d4d4d8] rounded-xl shadow-sm">
                <Lock size={13} className="text-[#f59e0b]" />
                <span>FIPS 186-5 ED25519</span>
              </div>

              {/* RFC 8785 Canonical Seal */}
              <div className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-[#050508] border border-[#38bdf8]/40 text-[11px] font-mono text-[#d4d4d8] rounded-xl shadow-sm">
                <FileCheck2 size={13} className="text-[#38bdf8]" />
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
            <p className="text-xs text-[#a1a1aa] max-w-sm leading-relaxed font-sans">
              Sub-50 microsecond cryptographic safety infrastructure and deterministic invariant guardrails for autonomous AI agents.
            </p>
            <div className="flex items-center gap-2 text-xs text-[#10b981] font-mono pt-1">
              <CheckCircle2 size={14} />
              <span>[PROTOCOL ACTIVE: BTP v2.8.0 · APACHE 2.0 / BSL LICENSED]</span>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="md:col-span-3 space-y-3">
            <div className="text-xs font-bold uppercase tracking-wider text-white font-mono">
              [NAVIGATION]
            </div>
            <ul className="space-y-2.5 text-xs font-mono">
              <li>
                <a href="#how-it-works" className="hover:text-white transition">
                  [HOW IT WORKS]
                </a>
              </li>
              <li>
                <a href="#threat-simulator" className="hover:text-white transition">
                  [THREAT DEMOS]
                </a>
              </li>
              <li>
                <a href="#policy-editor" className="hover:text-white transition">
                  [IN-BROWSER TESTER]
                </a>
              </li>
              <li>
                <a href="#sdk" className="hover:text-white transition">
                  [PYTHON / JS SDK]
                </a>
              </li>
              <li>
                <a href="#download" className="hover:text-white transition">
                  [GET STARTED]
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
                  className="text-[#f59e0b] hover:text-white transition inline-flex items-center gap-1 font-bold"
                >
                  <span>[ARCHITECTURE WHITE PAPER]</span>
                  <ExternalLink size={10} className="text-[#f59e0b]" />
                </a>
              </li>
              <li>
                <a
                  href="/SECURITY_WHITE_PAPER_AND_THREAT_MODEL.md"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-white transition inline-flex items-center gap-1"
                >
                  <span>[THREAT MODEL SPEC (.MD)]</span>
                  <ExternalLink size={10} className="text-[#71717a]" />
                </a>
              </li>
              <li>
                <a
                  href="https://www.bestpractices.dev/projects/14198"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-white transition inline-flex items-center gap-1.5"
                >
                  <ShieldCheck size={12} className="text-[#10b981]" />
                  <span>[OPENSSF BEST PRACTICES]</span>
                  <ExternalLink size={10} className="text-[#71717a]" />
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
                  <span>GITHUB REPO</span>
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
          <div>© 2026 BARTHOLOMEW TRUST PROTOCOL · OPEN STANDARDS</div>
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
