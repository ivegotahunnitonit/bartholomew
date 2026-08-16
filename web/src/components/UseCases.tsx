import { Building2, Heart, Globe2, Cpu } from 'lucide-react'

const CASES = [
  {
    icon: Building2,
    color: '#38bdf8',
    sector: 'FinTech',
    title: 'Autonomous trading agents',
    desc: 'Stop an agent from exfiltrating API keys, executing runaway trades, or logging PII. Sub-microsecond kill-switch before any order reaches the exchange.',
    tags: ['LLM02 credential leak', 'LLM04 denial-of-wallet', 'PII masking'],
  },
  {
    icon: Heart,
    color: '#fb7185',
    sector: 'Healthcare',
    title: 'Clinical AI workflows',
    desc: 'HIPAA-grade trajectory attestation. Every agent thought log is immutably signed and archived. Block any step that attempts to export PHI beyond its authorized scope.',
    tags: ['HIPAA audit trail', 'PHI exfiltration prevention', 'SHA-256 attestation'],
  },
  {
    icon: Globe2,
    color: '#a78bfa',
    sector: 'Defense / GovTech',
    title: 'SCIF & air-gapped deployments',
    desc: 'Single binary, no internet required. Deploy to classified networks. Sovereign mode: all detection on-device, local append-only attestation log, zero cloud dependencies.',
    tags: ['Air-gap binary', 'FedRAMP (Q4 2026)', 'Sovereign mode'],
  },
  {
    icon: Cpu,
    color: '#34d399',
    sector: 'SaaS / AI Infrastructure',
    title: 'Multi-tenant agent platforms',
    desc: 'Per-tenant policy isolation, environment-aware kill-switches (dev/staging/prod), and SIEM integration for Splunk/Datadog. Scale to millions of scans per day.',
    tags: ['Multi-env policy', 'SIEM integration', 'SOC 2 Type II'],
  },
]

export default function UseCases() {
  return (
    <section id="use-cases" className="py-24 px-5 sm:px-8">
      <div className="section-divider mb-24" />
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-14">
          <div className="section-label">Use Cases</div>
          <h2 className="section-title mb-4">Built for the industries that can't afford a breach</h2>
          <p className="section-subtitle mx-auto text-center">
            Any team running autonomous AI agents on sensitive data is a target. Bartholomew is the kill-switch.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 gap-5">
          {CASES.map(c => {
            const Icon = c.icon
            return (
              <div key={c.title} className="card card-hover p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center"
                    style={{ background: `${c.color}18`, border: `1px solid ${c.color}35` }}
                  >
                    <Icon size={20} style={{ color: c.color }} strokeWidth={2} />
                  </div>
                  <span className="badge" style={{ background: `${c.color}12`, color: c.color, border: `1px solid ${c.color}35` }}>
                    {c.sector}
                  </span>
                </div>

                <h3 className="font-bold text-base mb-2" style={{ color: '#f1f5f9', fontFamily: '"Plus Jakarta Sans", sans-serif' }}>
                  {c.title}
                </h3>
                <p className="text-sm leading-relaxed mb-4" style={{ color: '#94a3b8' }}>
                  {c.desc}
                </p>

                <div className="flex flex-wrap gap-1.5">
                  {c.tags.map(tag => (
                    <span
                      key={tag}
                      className="text-xs px-2.5 py-1 rounded-lg"
                      style={{
                        background: 'rgba(255,255,255,0.04)',
                        border: '1px solid rgba(255,255,255,0.08)',
                        color: '#94a3b8',
                        fontFamily: '"JetBrains Mono", monospace',
                      }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
