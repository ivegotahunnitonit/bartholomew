import { Shield, Search, TrendingUp, Layers } from 'lucide-react'

const APPLICATIONS = [
  {
    title: 'Security & Threat Mitigation',
    pipeline: 'PERCEIVE → REASON → VERIFY → BLOCK',
    desc: 'Sub-microsecond OWASP threat interception, secret credential scrubbing, token budget caps, and air-gapped enclave protection.',
    icon: Shield,
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10'
  },
  {
    title: 'Autonomous Research & Investigation',
    pipeline: 'PERCEIVE → REASON → INVESTIGATE → VERIFY → LEARN',
    desc: 'Continuous offline trajectory replay, counterfactual scenario synthesis, evidence collection, and hypothesis testing during idle cycles.',
    icon: Search,
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10'
  },
  {
    title: 'Economic Intelligence & Resource Matching',
    pipeline: 'PERCEIVE → FIND OPPORTUNITY → MODEL → EXPERIMENT → VERIFY → LEARN',
    desc: 'Discovers persistent market inefficiencies, evaluates resource capacity, matches underutilized assets, and verifies economic value before allocation.',
    icon: TrendingUp,
    color: 'text-violet-400',
    bg: 'bg-violet-500/10'
  },
  {
    title: 'Multi-Agent Swarm Orchestration',
    pipeline: 'PERCEIVE → PLAN → EXECUTE → VERIFY → ADAPT',
    desc: 'Governs multi-agent teams (LangChain, AutoGen, CrewAI) with Bayesian risk scoring and Ed25519 cryptographic consensus before state transitions.',
    icon: Layers,
    color: 'text-amber-400',
    bg: 'bg-amber-500/10'
  }
]

export default function Applications() {
  return (
    <section id="applications" className="py-24 px-5 sm:px-8 bg-bg relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 mb-4">
            <Layers size={14} />
            Extensible Applications
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4 font-heading">
            Applications Built on <span className="gradient-text">the Core Machine</span>
          </h2>
          <p className="text-base sm:text-lg text-slate-400">
            Security is one application. Bartholomew's decision-control primitives extend seamlessly across research, economic intelligence, and multi-agent orchestration.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {APPLICATIONS.map((app) => {
            const IconComp = app.icon
            return (
              <div key={app.title} className="glass-card p-6 rounded-2xl border border-white/10 space-y-4 hover:border-white/20 transition-all">
                <div className="flex items-center gap-3">
                  <div className={`p-3 rounded-xl ${app.bg} ${app.color}`}>
                    <IconComp size={22} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white font-heading">{app.title}</h3>
                    <span className="text-[11px] font-mono text-slate-400">{app.pipeline}</span>
                  </div>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{app.desc}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
