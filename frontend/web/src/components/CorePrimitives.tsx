import { Eye, Brain, ShieldCheck, Play, Database } from 'lucide-react'

const PRIMITIVES = [
  {
    step: '01',
    name: 'PERCEIVE',
    title: 'Interceptor & Tool Observation',
    desc: 'Observes every thought, tool call, database query, and API payload in real time before execution.',
    icon: Eye,
    color: 'text-emerald-400',
    border: 'border-emerald-500/20',
    bg: 'bg-emerald-500/10'
  },
  {
    step: '02',
    name: 'REASON',
    title: 'Evidence-Driven Inference',
    desc: 'Evaluates trajectory entropy, Bayesian threat probability, and logical consistency without relying on raw model assertions.',
    icon: Brain,
    color: 'text-cyan-400',
    border: 'border-cyan-500/20',
    bg: 'bg-cyan-500/10'
  },
  {
    step: '03',
    name: 'VERIFY',
    title: 'Ed25519 Cryptographic Proof',
    desc: 'Generates tamper-proof JSON evidence artifacts establishing audit compliance and verifiable state constraints.',
    icon: ShieldCheck,
    color: 'text-violet-400',
    border: 'border-violet-500/20',
    bg: 'bg-violet-500/10'
  },
  {
    step: '04',
    name: 'ACT',
    title: 'Controlled Execution & Enforcement',
    desc: 'Executes verified actions within strict token budgets, secret scrubbing guards, and air-gapped security enclaves.',
    icon: Play,
    color: 'text-amber-400',
    border: 'border-amber-500/20',
    bg: 'bg-amber-500/10'
  },
  {
    step: '05',
    name: 'LEARN',
    title: 'Sovereign Memory & Outcome Feedback',
    desc: 'Stores observed outcomes in isolated SQLite vector enclaves to refine decision quality over time.',
    icon: Database,
    color: 'text-rose-400',
    border: 'border-rose-500/20',
    bg: 'bg-rose-500/10'
  }
]

export default function CorePrimitives() {
  return (
    <section id="primitives" className="py-24 px-5 sm:px-8 bg-slate-950/80 relative border-t border-white/5">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mb-4">
            <Brain size={14} />
            Foundational Architecture
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4 font-heading">
            The 5 Core <span className="gradient-text">Primitives</span>
          </h2>
          <p className="text-base sm:text-lg text-slate-400">
            Bartholomew's decision-control layer is built on five explicit primitives that govern how agents interact with reality.
          </p>
        </div>

        <div className="grid md:grid-cols-5 gap-4">
          {PRIMITIVES.map((p) => {
            const IconComp = p.icon
            return (
              <div
                key={p.name}
                className="glass-card p-5 rounded-2xl border border-white/10 flex flex-col justify-between hover:border-white/20 transition-all space-y-4"
              >
                <div>
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-xs font-mono font-bold text-slate-500">{p.step}</span>
                    <div className={`p-2 rounded-xl ${p.bg} ${p.color}`}>
                      <IconComp size={18} />
                    </div>
                  </div>
                  <span className={`text-xs font-mono font-bold uppercase tracking-wider block mb-1 ${p.color}`}>
                    {p.name}
                  </span>
                  <h3 className="text-sm font-bold text-white font-heading mb-2">{p.title}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">{p.desc}</p>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
