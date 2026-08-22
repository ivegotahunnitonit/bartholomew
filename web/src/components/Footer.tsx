import { CheckCircle2, Code2, ExternalLink } from 'lucide-react'
import Logo from './Logo'

export default function Footer() {
  return (
    <footer className="py-14 px-5 sm:px-8 bg-black text-[#a1a1aa] border-t border-[#1c1c1c]">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-10 pb-10 border-b border-[#222222]">
          {/* Brand Info */}
          <div className="md:col-span-6 space-y-3">
            <div className="flex items-center">
              <Logo size={28} showText={true} />
            </div>
            <p className="text-xs text-[#a1a1aa] max-w-sm leading-relaxed font-sans">
              Sub-millisecond cryptographic safety infrastructure and deterministic guardrails for autonomous AI agents.
            </p>
            <div className="flex items-center gap-2 text-xs text-[#10b981] font-mono pt-1">
              <CheckCircle2 size={13} />
              <span>[PROTOCOL ACTIVE: BTP v2.2.0 · MIT LICENSED]</span>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="md:col-span-3 space-y-3">
            <div className="text-xs font-bold uppercase tracking-wider text-white font-mono">
              [NAVIGATION]
            </div>
            <ul className="space-y-2 text-xs font-mono">
              <li>
                <a href="#how-it-works" className="hover:text-white transition">
                  [HOW IT WORKS]
                </a>
              </li>
              <li>
                <a href="#download" className="hover:text-white transition">
                  [INSTALL CLI]
                </a>
              </li>
              <li>
                <a href="#policy-editor" className="hover:text-white transition">
                  [RULE BUILDER]
                </a>
              </li>
              <li>
                <a href="#sdk" className="hover:text-white transition">
                  [1-LINE SDKS]
                </a>
              </li>
              <li>
                <a href="#live-api" className="hover:text-white transition">
                  [GATEWAY API]
                </a>
              </li>
            </ul>
          </div>

          {/* Standards & Open Source */}
          <div className="md:col-span-3 space-y-3">
            <div className="text-xs font-bold uppercase tracking-wider text-white font-mono">
              [SPECIFICATIONS]
            </div>
            <ul className="space-y-2 text-xs font-mono">
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
          <div>© 2026 OPEN SOURCE UNDER MIT LICENSE</div>
          <div className="flex items-center gap-4">
            <a href="https://bartholomew.info" className="text-[#a1a1aa] hover:text-white transition">
              bartholomew.info
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
