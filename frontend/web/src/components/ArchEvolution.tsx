const ERAS = [
  {
    era: 'v1–v4',
    period: '2024 – Early 2025',
    name: 'Origin',
    color: '#38bdf8',
    summary: 'Basic trajectory scanner — flat log, regex credential patterns, single-env.',
    milestones: [
      'Ed25519 trajectory signing',
      'First OWASP LLM01 detection',
      'Python SDK alpha',
    ],
  },
  {
    era: 'v5–v7',
    period: 'Mid 2025',
    name: 'Epistemic Core',
    color: '#34d399',
    summary: 'Epistemic Contradiction Engine introduced. Belief graph, tiered memory, cheap-path budget governor.',
    milestones: [
      'Epistemic Contradiction Engine (ECE)',
      'HOT / WARM / COLD memory tiers',
      'Expected Value Governor (frontier budget)',
      'Evidence provenance tracking (OBSERVED → DISPROVEN)',
    ],
  },
  {
    era: 'v8–v9',
    period: '2026 – Now',
    name: 'Adaptive Memory Engine',
    color: '#a78bfa',
    summary: 'Full DERG graph, async dreaming for offline strategy compression, SHA-256 chain attestation, GCP Cloud Run deployment.',
    milestones: [
      'DERG graph with epistemic node status',
      'Async offline strategy compression ("dreaming")',
      'Cloud Run + Firebase Hosting production deploy',
      'Multi-env policy (dev / staging / prod / air-gap)',
      '11.98M scans/sec benchmark',
    ],
  },
]

export default function ArchEvolution() {
  return (
    <section id="evolution" className="py-24 px-5 sm:px-8">
      <div className="section-divider mb-24" />
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-14">
          <div className="section-label">Architecture Evolution</div>
          <h2 className="section-title mb-4">From scanner to Adaptive Memory Engine</h2>
          <p className="section-subtitle mx-auto text-center">
            Where it started, where it is, and where it's going.
          </p>
        </div>

        {/* Timeline */}
        <div className="relative">
          {/* Vertical line */}
          <div
            className="absolute left-5 top-0 bottom-0 w-px hidden md:block"
            style={{ background: 'linear-gradient(to bottom, rgba(56,189,248,0.4), rgba(139,92,246,0.2), transparent)' }}
          />

          <div className="flex flex-col gap-6">
            {ERAS.map((era, i) => (
              <div key={era.era} className="flex gap-6">
                {/* Timeline dot */}
                <div className="hidden md:flex flex-col items-center" style={{ minWidth: '40px' }}>
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center font-black text-xs z-10 relative"
                    style={{
                      background: `linear-gradient(135deg, ${era.color}22, ${era.color}11)`,
                      border: `2px solid ${era.color}60`,
                      color: era.color,
                      fontFamily: '"JetBrains Mono", monospace',
                    }}
                  >
                    {i + 1}
                  </div>
                </div>

                {/* Card */}
                <div
                  className="card card-hover flex-1 p-6"
                  style={{ borderLeftColor: era.color + '40', borderLeftWidth: '3px' }}
                >
                  <div className="flex flex-wrap items-center gap-2 mb-3">
                    <span className="badge" style={{ background: `${era.color}12`, color: era.color, border: `1px solid ${era.color}35` }}>
                      {era.era}
                    </span>
                    <span className="text-xs" style={{ color: '#475569' }}>{era.period}</span>
                  </div>

                  <h3 className="font-bold text-lg mb-2" style={{ color: '#f1f5f9', fontFamily: '"Plus Jakarta Sans", sans-serif' }}>
                    {era.name}
                  </h3>
                  <p className="text-sm leading-relaxed mb-4" style={{ color: '#94a3b8' }}>
                    {era.summary}
                  </p>

                  <ul className="flex flex-col gap-1.5">
                    {era.milestones.map(m => (
                      <li key={m} className="flex items-start gap-2 text-sm" style={{ color: '#94a3b8' }}>
                        <span className="text-xs mt-0.5" style={{ color: era.color }}></span>
                        {m}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
