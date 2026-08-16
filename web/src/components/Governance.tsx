import { CheckCircle2, AlertCircle } from 'lucide-react'

const TIERS = [
  {
    tier: 'Tier 1',
    name: 'Community',
    price: 'Free',
    color: '#34d399',
    features: ['10,000 scans / month', 'Go daemon binary', '7-class OWASP detection', 'SHA-256 attestation', 'CLI + Python SDK', 'GitHub issues support'],
    missing: ['Firestore sync', 'SIEM integration', 'Multi-env policy', 'SLA'],
    cta: 'Download binary',
    href: 'https://github.com/ivegotahunnitonit/bartholomew',
  },
  {
    tier: 'Tier 2',
    name: 'Professional',
    price: '$299 / mo',
    color: '#38bdf8',
    highlight: true,
    features: ['Unlimited scans', 'Cloud Run managed API', 'Firestore audit sync', 'Slack / email alerts', 'Multi-environment policy', 'Standard SLA (99.5%)'],
    missing: ['SIEM integration', 'Air-gap deploy', 'FedRAMP'],
    cta: 'Start free trial',
    href: '/dashboard/admin.html',
  },
  {
    tier: 'Tier 3',
    name: 'Enterprise',
    price: 'Custom',
    color: '#a78bfa',
    features: ['Everything in Pro', 'Air-gap / SCIF deploy', 'SIEM Splunk / Elastic integration', 'SSO / SAML federation', 'FedRAMP High (Q4 2026)', 'Dedicated SLA (99.99%)', 'SOC 2 Type II attestation'],
    missing: [],
    cta: 'Contact sales',
    href: 'mailto:hello@bartholomew.info',
  },
]

const POLICIES = [
  { label: 'Observe only', desc: 'Log all threats, block nothing', badge: 'DEV', color: '#34d399' },
  { label: 'Warn + log', desc: 'Alert on CRITICAL, log everything', badge: 'STAGING', color: '#38bdf8' },
  { label: 'Hard block', desc: 'Block CRITICAL+HIGH, mask credentials', badge: 'PROD', color: '#a78bfa' },
  { label: 'Sovereign mode', desc: 'Block all, no external calls, local chain', badge: 'AIR-GAP', color: '#fb7185' },
]

export default function Governance() {
  return (
    <section id="governance" className="py-24 px-5 sm:px-8">
      <div className="section-divider mb-24" />
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-14">
          <div className="section-label">Governance & Pricing</div>
          <h2 className="section-title mb-4">Four policy tiers. One binary.</h2>
          <p className="section-subtitle mx-auto text-center">
            Same Bartholomew daemon across dev, staging, production, and air-gapped — with per-environment policy configuration.
          </p>
        </div>

        {/* Policy tiers */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
          {POLICIES.map(p => (
            <div key={p.badge} className="card card-hover p-5 flex flex-col gap-2">
              <span className="badge" style={{ background: `${p.color}12`, color: p.color, border: `1px solid ${p.color}35`, alignSelf: 'flex-start' }}>
                {p.badge}
              </span>
              <div className="font-bold text-sm" style={{ color: '#f1f5f9' }}>{p.label}</div>
              <div className="text-xs" style={{ color: '#94a3b8' }}>{p.desc}</div>
            </div>
          ))}
        </div>

        {/* Pricing cards */}
        <div className="grid md:grid-cols-3 gap-5">
          {TIERS.map(tier => (
            <div
              key={tier.name}
              className="card-hover p-6 flex flex-col rounded-2xl"
              style={{
                background: tier.highlight
                  ? 'linear-gradient(160deg, rgba(6,182,212,0.1), rgba(56,189,248,0.05))'
                  : 'rgba(10,22,40,0.8)',
                border: tier.highlight ? `1px solid ${tier.color}40` : '1px solid rgba(255,255,255,0.07)',
                boxShadow: tier.highlight ? `0 0 40px ${tier.color}10` : 'none',
                transition: 'all 0.2s ease',
              }}
            >
              {tier.highlight && (
                <div className="badge badge-cyan self-start mb-4" style={{ fontSize: '0.68rem' }}>Most popular</div>
              )}
              <div className="text-xs font-mono mb-1" style={{ color: tier.color, textTransform: 'uppercase', letterSpacing: '0.08em' }}>{tier.tier}</div>
              <div className="font-bold text-xl mb-1" style={{ color: '#f1f5f9', fontFamily: '"Plus Jakarta Sans", sans-serif' }}>{tier.name}</div>
              <div className="font-black mb-6" style={{ fontSize: '1.75rem', color: tier.color, fontFamily: '"JetBrains Mono", monospace' }}>{tier.price}</div>

              <div className="flex flex-col gap-2 flex-1">
                {tier.features.map(f => (
                  <div key={f} className="flex items-start gap-2.5 text-sm" style={{ color: '#94a3b8' }}>
                    <CheckCircle2 size={14} style={{ color: tier.color, flexShrink: 0, marginTop: '2px' }} />
                    {f}
                  </div>
                ))}
                {tier.missing.map(f => (
                  <div key={f} className="flex items-start gap-2.5 text-sm" style={{ color: '#2d3f55' }}>
                    <AlertCircle size={14} style={{ color: '#2d3f55', flexShrink: 0, marginTop: '2px' }} />
                    {f}
                  </div>
                ))}
              </div>

              <a
                href={tier.href}
                target={tier.href.startsWith('http') || tier.href.startsWith('mailto') ? '_blank' : undefined}
                rel="noopener noreferrer"
                className={tier.highlight ? 'btn-primary mt-6 justify-center' : 'btn-secondary mt-6 justify-center'}
              >
                {tier.cta}
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
