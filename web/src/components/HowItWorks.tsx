import { Zap, Shield, FileText } from 'lucide-react'

const STEPS = [
  {
    step: '01',
    icon: Zap,
    color: '#38bdf8',
    title: 'Intercept',
    subtitle: 'Before execution',
    desc: 'Your agent produces a thought or tool call. Bartholomew intercepts the payload in-process via a <1KB SDK wrapper — no proxy, no sidecar required.',
    code: `# FastAPI middleware (1 line)
app.add_middleware(BartholomewMiddleware)

# Or Python decorator
@guard(policy="strict")
async def agent_step(trajectory):
    ...`,
  },
  {
    step: '02',
    icon: Shield,
    color: '#34d399',
    title: 'Evaluate',
    subtitle: 'In 1.44 microseconds',
    desc: 'The Go daemon runs 7 OWASP threat classes, 40+ credential patterns, and the Epistemic Contradiction Engine in parallel. All compiled — no inference.',
    code: `{
  "owasp_class": "LLM02",
  "credential_leak": true,
  "keys_found": ["sk-proj-..."],
  "contradiction_score": 0.0,
  "scan_ns": 1440,
  "action": "BLOCK"
}`,
  },
  {
    step: '03',
    icon: FileText,
    color: '#a78bfa',
    title: 'Attest',
    subtitle: 'Immutable proof',
    desc: 'A SHA-256 hash of the cleaned trajectory is chained to the previous record and optionally synced to Firestore. Full compliance trail, zero extra latency.',
    code: `{
  "attestation_hash":
    "sha256:3a4b2c...",
  "chain_index": 1847,
  "prev_hash": "sha256:9f1e3d...",
  "status": "CLEAN",
  "compliance": "SOC2_PASSED"
}`,
  },
]

export default function HowItWorks() {
  return (
    <section id="how" className="py-24 px-5 sm:px-8">
      <div className="section-divider mb-24" />
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-14">
          <div className="section-label">How it works</div>
          <h2 className="section-title mb-4">Three steps. Under two microseconds.</h2>
          <p className="section-subtitle mx-auto text-center">
            No LLM inference. No cloud round-trips. Pure compiled Go running inline with your agent.
          </p>
        </div>

        <div className="flex flex-col lg:flex-row gap-6">
          {STEPS.map((step, i) => {
            const Icon = step.icon
            return (
              <div key={step.step} className="card p-6 flex-1 relative overflow-hidden">
                {/* Step number watermark */}
                <div
                  className="absolute top-4 right-5 font-black select-none"
                  style={{
                    fontSize: '4.5rem',
                    color: `${step.color}08`,
                    fontFamily: '"JetBrains Mono", monospace',
                    lineHeight: 1,
                  }}
                >
                  {step.step}
                </div>

                {/* Connector dots */}
                {i < STEPS.length - 1 && (
                  <div className="hidden lg:flex absolute -right-3.5 top-1/2 -translate-y-1/2 z-10 flex-col gap-0.5">
                    {[...Array(3)].map((_, j) => (
                      <div key={j} className="w-1.5 h-1.5 rounded-full" style={{ background: step.color, opacity: 0.4 + j * 0.2 }} />
                    ))}
                  </div>
                )}

                <div className="relative">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center mb-4"
                    style={{ background: `${step.color}18`, border: `1px solid ${step.color}35` }}
                  >
                    <Icon size={20} style={{ color: step.color }} strokeWidth={2} />
                  </div>

                  <div className="text-xs font-mono mb-1" style={{ color: step.color, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                    {step.subtitle}
                  </div>
                  <h3 className="font-bold text-xl mb-3" style={{ color: '#f1f5f9', fontFamily: '"Plus Jakarta Sans", sans-serif' }}>
                    {step.title}
                  </h3>
                  <p className="text-sm leading-relaxed mb-4" style={{ color: '#94a3b8' }}>
                    {step.desc}
                  </p>

                  <pre className="code-block text-xs">
                    <code style={{ color: '#94a3b8' }}>{step.code}</code>
                  </pre>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
