import Logo from './Logo'

interface NavLink { label: string; href: string; ext: boolean }
const LINKS: Record<string, NavLink[]> = {
  Product: [
    { label: 'Simulator', href: '#simulator', ext: false },
    { label: 'Command Center', href: '#command-center', ext: false },
    { label: 'Epistemic Engines', href: '#engines', ext: false },
    { label: 'SDK', href: '#sdk', ext: false },
    { label: 'Live API', href: '#live-api', ext: false },
  ],
  Resources: [
    { label: 'GitHub', href: 'https://github.com/ivegotahunnitonit/bartholomew', ext: true },
    { label: 'PyPI Package', href: 'https://pypi.org/project/bartholomew-eval/', ext: true },
    { label: 'BTP Test Vectors', href: '/api/v1/btp/test-vectors', ext: true },
    { label: 'Architecture', href: '/PITCH_DECK.html', ext: false },
    { label: 'Security', href: '/operations', ext: false },
  ],
  Company: [
    { label: 'Executive Summary', href: '#executive-summary', ext: false },
    { label: 'Pitch Deck', href: '/PITCH_DECK.html', ext: false },
    { label: 'Operations Workspace', href: '/operations', ext: false },
    { label: 'Contact Security Team', href: 'mailto:itsub@bartholomew.info', ext: true },
  ],
}

export default function Footer() {
  return (
    <footer
      className="py-16 px-5 sm:px-8"
      style={{ borderTop: '1px solid rgba(255,255,255,0.07)' }}
    >
      <div className="max-w-6xl mx-auto">
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-10 mb-12">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2.5 mb-4">
              <Logo size={32} />
            </div>
            <p className="text-sm leading-relaxed mb-4" style={{ color: '#475569', maxWidth: '220px' }}>
              Verifiable agent trust &amp; identity protocol. Live on GCP Cloud Run.
            </p>
            <div className="flex items-center gap-1.5">
              <span className="pulse-dot" />
              <span className="text-xs font-mono" style={{ color: '#34d399' }}>All systems operational</span>
            </div>
          </div>

          {/* Link groups */}
          {Object.entries(LINKS).map(([group, items]) => (
            <div key={group}>
              <div className="text-xs font-bold uppercase tracking-widest mb-4" style={{ color: '#475569', letterSpacing: '0.1em' }}>
                {group}
              </div>
              <ul className="flex flex-col gap-2.5">
                {items.map(item => (
                  <li key={item.label}>
                    <a
                      href={item.href}
                      target={item.ext ? '_blank' : undefined}
                      rel={item.ext ? 'noopener noreferrer' : undefined}
                      className="text-sm transition-colors duration-150 no-underline"
                      style={{ color: '#94a3b8' }}
                      onMouseEnter={e => (e.target as HTMLElement).style.color = '#f1f5f9'}
                      onMouseLeave={e => (e.target as HTMLElement).style.color = '#94a3b8'}
                    >
                      {item.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div
          className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-8 text-xs"
          style={{ borderTop: '1px solid rgba(255,255,255,0.06)', color: '#475569' }}
        >
          <div>© 2025 Bartholomew · Independently owned and operated</div>
          <div className="flex items-center gap-4">
            <span>v9.1 · Ed25519 Verified</span>
            <a href="https://bartholomew.info" className="no-underline" style={{ color: '#475569' }}>bartholomew.info</a>
          </div>
        </div>
      </div>
    </footer>
  )
}
