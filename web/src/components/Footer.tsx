import { CheckCircle2, Code2, ExternalLink } from 'lucide-react'
import Logo from './Logo'

export default function Footer() {
  return (
    <footer className="py-14 px-5 sm:px-8 bg-slate-950 text-slate-400 border-t border-slate-900">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-10 pb-10 border-b border-slate-900">
          {/* Brand Info */}
          <div className="md:col-span-6 space-y-3">
            <div className="flex items-center gap-2.5">
              <Logo size={28} />
              <span className="font-extrabold text-base tracking-tight text-white font-mono">
                BARTHOLOMEW
              </span>
            </div>
            <p className="text-xs text-slate-400 max-w-sm leading-relaxed">
              Sub-millisecond cryptographic safety infrastructure and deterministic guardrails for autonomous AI agents.
            </p>
            <div className="flex items-center gap-2 text-xs text-emerald-400 font-mono pt-1">
              <CheckCircle2 size={13} />
              <span>Protocol Active: BTP v2.2.0 (MIT Licensed)</span>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="md:col-span-3 space-y-3">
            <div className="text-xs font-bold uppercase tracking-wider text-slate-300 font-mono">
              Navigation
            </div>
            <ul className="space-y-2 text-xs">
              <li>
                <a href="#how-it-works" className="hover:text-cyan-400 transition">
                  How It Works
                </a>
              </li>
              <li>
                <a href="#download" className="hover:text-cyan-400 transition">
                  Install Desktop CLI
                </a>
              </li>
              <li>
                <a href="#policy-editor" className="hover:text-cyan-400 transition">
                  Rule Builder
                </a>
              </li>
              <li>
                <a href="#sdk" className="hover:text-cyan-400 transition">
                  1-Line SDKs
                </a>
              </li>
              <li>
                <a href="#live-api" className="hover:text-cyan-400 transition">
                  Gateway API
                </a>
              </li>
            </ul>
          </div>

          {/* Standards & Open Source */}
          <div className="md:col-span-3 space-y-3">
            <div className="text-xs font-bold uppercase tracking-wider text-slate-300 font-mono">
              Open Standards
            </div>
            <ul className="space-y-2 text-xs">
              <li>
                <a
                  href="https://github.com/ivegotahunnitonit/bartholomew"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-cyan-400 transition inline-flex items-center gap-1"
                >
                  <Code2 size={12} />
                  <span>GitHub Repository</span>
                  <ExternalLink size={10} className="text-slate-500" />
                </a>
              </li>
              <li>
                <a
                  href="https://www.rfc-editor.org/rfc/rfc8785"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-cyan-400 transition inline-flex items-center gap-1"
                >
                  <span>RFC 8785 Canonical JSON</span>
                  <ExternalLink size={10} className="text-slate-500" />
                </a>
              </li>
              <li>
                <a
                  href="https://csrc.nist.gov/pubs/fips/186-5/final"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-cyan-400 transition inline-flex items-center gap-1"
                >
                  <span>FIPS 186-5 Ed25519</span>
                  <ExternalLink size={10} className="text-slate-500" />
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
          <div>© 2026 Bartholomew Protocol · Open Source</div>
          <div className="flex items-center gap-4">
            <a href="https://bartholomew.info" className="text-slate-400 hover:text-white transition">
              bartholomew.info
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
