import { Shield, Eye, Key, RefreshCw, FileCheck } from 'lucide-react'

const ITEMS = [
  {
    icon: Eye,
    color: '#34d399',
    title: 'Trajectory scanning',
    body: 'Every thought and tool call your agent generates is intercepted in-process. Nothing executes before Bartholomew has read it.',
  },
  {
    icon: Key,
    color: '#38bdf8',
    title: 'Credential masking',
    body: 'API keys, tokens, and secrets matching 40+ regex patterns are automatically scrubbed and replaced with [REDACTED] before they can leak.',
  },
  {
    icon: Shield,
    color: '#a78bfa',
    title: 'OWASP LLM threat detection',
    body: '7-class OWASP threat model runs as compiled Go — prompt injection, denial-of-wallet, training-data poisoning and more, with <2 μs latency.',
  },
  {
    icon: RefreshCw,
    color: '#fbbf24',
    title: 'Epistemic Contradiction Engine',
    body: 'Detects logical contradictions across multi-step reasoning chains. Stops agents from acting on beliefs they have already disproved.',
  },
  {
    icon: FileCheck,
    color: '#fb7185',
    title: 'SHA-256 attestation',
    body: 'Every scanned trajectory gets a cryptographic proof — signed, chained, and optionally synced to Firestore. Immutable audit trail.',
  },
]

export default function WhatIsBartholomew() {
  return (
    <section id="what" className="py-24 px-5 sm:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-14">
          <div className="section-label">What is Bartholomew?</div>
          <h2 className="section-title mb-4">
            An always-on security layer<br className="hidden md:block" />
            {' '}for every AI agent you run
          </h2>
          <p className="section-subtitle mx-auto text-center">
            Most AI security tools check logs after the fact. Bartholomew runs <em style={{ color: '#34d399', fontStyle: 'normal' }}>inline</em>, 
            before execution — so threats are stopped, not just reported.
          </p>
        </div>

        {/* Cards */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {ITEMS.map((item) => {
            const Icon = item.icon
            return (
              <div key={item.title} className="card card-hover p-6">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center mb-4"
                  style={{ background: `${item.color}18`, border: `1px solid ${item.color}35` }}
                >
                  <Icon size={20} style={{ color: item.color }} strokeWidth={2} />
                </div>
                <h3
                  className="font-bold mb-2 text-base"
                  style={{ color: '#f1f5f9', fontFamily: '"Plus Jakarta Sans", sans-serif' }}
                >
                  {item.title}
                </h3>
                <p className="text-sm leading-relaxed" style={{ color: '#94a3b8' }}>
                  {item.body}
                </p>
              </div>
            )
          })}

          {/* Pitch card */}
          <div
            className="card-hover p-6 sm:col-span-2 lg:col-span-1 flex flex-col justify-between rounded-2xl"
            style={{
              background: 'linear-gradient(135deg, rgba(16,185,129,0.12), rgba(6,182,212,0.08))',
              border: '1px solid rgba(52,211,153,0.25)',
            }}
          >
            <div>
              <div className="badge badge-emerald mb-4">Zero-dependency</div>
              <h3 className="font-bold text-lg mb-2" style={{ color: '#f1f5f9', fontFamily: '"Plus Jakarta Sans", sans-serif' }}>
                Runs everywhere — including air-gapped
              </h3>
              <p className="text-sm leading-relaxed" style={{ color: '#94a3b8' }}>
                Single Go binary. No Python, no npm, no cloud API calls required. 
                Deploy to SCIF networks, K8s, Docker, or bare metal.
              </p>
            </div>
            <a
              href="/dashboard/admin.html"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary mt-5 self-start"
              style={{ fontSize: '0.85rem', padding: '0.55rem 1.2rem' }}
            >
              Open Command Center
            </a>
          </div>
        </div>
      </div>
    </section>
  )
}
