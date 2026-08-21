import { CheckCircle2 } from 'lucide-react'
import Logo from './Logo'

const LINKS = {
  Architecture: [
    { label: 'Download Desktop CLI', href: '#download', ext: false },
    { label: '3-Tier Invariant Defense', href: '#runtime-proof', ext: false },
    { label: 'Interactive Policy Editor', href: '#policy-editor', ext: false },
    { label: 'Multi-Language SDKs', href: '#sdk', ext: false },
    { label: 'Gateway API', href: '#live-api', ext: false },
  ],
  Resources: [
    { label: 'GitHub Repository', href: 'https://github.com/ivegotahunnitonit/bartholomew', ext: true },
    { label: 'RFC 8785 Canonical JSON', href: 'https://www.rfc-editor.org/rfc/rfc8785', ext: true },
    { label: 'FIPS 186-5 Ed25519 Spec', href: 'https://csrc.nist.gov/pubs/fips/186-5/final', ext: true },
  ],
  Security: [
    { label: 'Zero Cloud Telemetry', href: '#download', ext: false },
    { label: 'Hermetic Sandbox Boundary', href: '#runtime-proof', ext: false },
    { label: 'Compiler-Grade AST Static Gate', href: '#runtime-proof', ext: false },
  ],
}

export default function Footer() {
  return (
    <footer className="py-16 px-5 sm:px-8 bg-slate-950 text-slate-400 border-t border-slate-900">
      <div className="max-w-6xl mx-auto">
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-10 mb-12">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2.5 mb-4">
              <Logo size={32} />
              <span className="font-extrabold text-base tracking-tight text-white font-mono">
                BARTHOLOMEW
              </span>
            </div>
            <p className="text-xs leading-relaxed mb-4 text-slate-400 max-w-[240px]">
              Sub-millisecond cryptographic invariant and safety guardrail engine for autonomous AI agents.
            </p>
            <div className="flex items-center gap-2 text-xs text-emerald-400 font-mono">
              <CheckCircle2 size={13} />
              <span>Protocol Active: BTP/2.2</span>
            </div>
          </div>

          {/* Link Groups */}
          {Object.entries(LINKS).map(([group, items]) => (
            <div key={group}>
              <div className="text-xs font-bold uppercase tracking-widest mb-4 text-slate-500 font-mono">
                {group}
              </div>
              <ul className="flex flex-col gap-2.5">
                {items.map(item => (
                  <li key={item.label}>
                    <a
                      href={item.href}
                      target={item.ext ? '_blank' : undefined}
                      rel={item.ext ? 'noopener noreferrer' : undefined}
                      className="text-xs text-slate-400 hover:text-cyan-400 transition"
                    >
                      {item.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-8 text-xs border-t border-slate-900 text-slate-500">
          <div>© 2026 Bartholomew Protocol · Open Source under MIT License</div>
          <div className="flex items-center gap-4">
            <span className="text-cyan-400 font-mono">BTP v2.2.0</span>
            <a href="https://bartholomew.info" className="text-slate-400 hover:text-white transition">
              bartholomew.info
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
