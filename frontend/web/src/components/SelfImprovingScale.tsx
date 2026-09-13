import { RefreshCw, Cpu, Layers, GitMerge, ArrowRight, ShieldCheck } from 'lucide-react'

const STAGES = [
  {
    step: '01',
    title: 'Trajectory Fuzzer',
    desc: 'Continuously generates adversarial inputs, prompt mutations, and structural stress vectors.',
    icon: Cpu,
    color: 'text-rose-400'
  },
  {
    step: '02',
    title: 'Self-Healing Engine',
    desc: 'Automatically rewrites broken logic and applies security patches without human intervention.',
    icon: RefreshCw,
    color: 'text-amber-400'
  },
  {
    step: '03',
    title: 'Sovereign Local Memory',
    desc: 'Stores consolidated heuristics in isolated SQLite vector enclaves for sub-nanosecond lookups.',
    icon: Layers,
    color: 'text-emerald-400'
  },
  {
    step: '04',
    title: 'Autonomous Threat Discoverer',
    desc: 'Discovers zero-day OWASP attack vectors and synthesizes real-time mitigation rules.',
    icon: ShieldCheck,
    color: 'text-cyan-400'
  },
  {
    step: '05',
    title: 'Universal Swarm Scaling',
    desc: 'Scales seamlessly from single agent nodes to multi-agent swarms with cryptographic consensus.',
    icon: GitMerge,
    color: 'text-violet-400'
  }
]

export default function SelfImprovingScale() {
  return (
    <section id="scaling" className="py-24 px-5 sm:px-8 bg-bg relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mb-4">
            <RefreshCw size={14} className="animate-spin" />
            Continuous Self-Healing Loop
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4 font-heading">
            Autonomous <span className="gradient-text">Self-Improvement &amp; Scaling</span>
          </h2>
          <p className="text-base sm:text-lg text-slate-400">
            A clear architectural scope of how Bartholomew continuously adapts, patches vulnerabilities, and scales from local developer environments to multi-node sovereign swarms.
          </p>
        </div>

        {/* Stage Workflow Pipeline */}
        <div className="grid md:grid-cols-5 gap-4">
          {STAGES.map((s, idx) => {
            const IconComp = s.icon
            return (
              <div key={s.step} className="glass-card p-5 rounded-2xl border border-white/10 relative flex flex-col justify-between hover:border-white/20 transition-all group">
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-xs font-mono font-bold text-slate-500">{s.step}</span>
                    <IconComp size={20} className={`${s.color} group-hover:scale-110 transition-transform`} />
                  </div>
                  <h3 className="text-base font-bold text-white font-heading mb-2">{s.title}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">{s.desc}</p>
                </div>

                {idx < STAGES.length - 1 && (
                  <div className="hidden md:block absolute -right-3 top-1/2 -translate-y-1/2 z-20 text-slate-600">
                    <ArrowRight size={14} />
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
