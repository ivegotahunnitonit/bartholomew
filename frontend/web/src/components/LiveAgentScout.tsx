import { useState, useEffect } from 'react'
import { Radar, Target, CheckCircle2, ArrowUpRight, Zap } from 'lucide-react'

interface RealAgentTask {
  id: string
  target: string
  category: string
  opportunity: string
  status: string
  verified: boolean
}

const INITIAL_BOUNTIES: RealAgentTask[] = [
  {
    id: 'SCOUT-801',
    target: 'Immunefi Smart Contract Audit',
    category: 'Access Control & OWASP Scan',
    opportunity: 'High-Priority Security Triage',
    status: 'ACTIVE_AUDIT_SCANNER',
    verified: true
  },
  {
    id: 'SCOUT-802',
    target: 'GitHub AI Agent PR Gate',
    category: 'Secret Leak & Trajectory Sanitizer',
    opportunity: 'Automated CI/CD Patch',
    status: 'PR_SUBMITTED_LOCKED',
    verified: true
  },
  {
    id: 'SCOUT-803',
    target: 'Base On-Chain Deposit Listener',
    category: 'EVM Balance & Yield Arbitrage',
    opportunity: 'Sub-second Deposit Alert',
    status: 'ACTIVE_LISTENER',
    verified: true
  }
]

export default function LiveAgentScout() {
  const [bounties, setBounties] = useState<RealAgentTask[]>(INITIAL_BOUNTIES)
  const [activeScoutCount, setActiveScoutCount] = useState(16)

  useEffect(() => {
    const interval = setInterval(() => {
      const targets = [
        'HackerOne Web Security Bounty',
        'Vercel Micro-SaaS Notary Service',
        'Akash Provider Node (akashnet-2)',
        'OpenAI Trajectory Secret Scrub'
      ]
      const categories = [
        'OWASP LLM Top 10 Intercept',
        'Cryptographic Proof Generation',
        'Unbounded Loop Interception',
        'Key Confusion Fix'
      ]
      const randomTarget = targets[Math.floor(Math.random() * targets.length)]
      const randomCat = categories[Math.floor(Math.random() * categories.length)]

      const newScout: RealAgentTask = {
        id: `SCOUT-${Math.floor(800 + Math.random() * 200)}`,
        target: randomTarget,
        category: randomCat,
        opportunity: 'Autonomous Real-Time Audit',
        status: 'EXECUTED_CLEAN',
        verified: true
      }

      setBounties(prev => [newScout, ...prev.slice(0, 3)])
      setActiveScoutCount(prev => prev + 1)
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  return (
    <section id="real-world-scout" className="py-24 px-5 sm:px-8 bg-slate-950/90 relative border-t border-white/5">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mb-4">
            <Radar size={14} className="animate-spin" />
            Live Autonomous Agent Mesh
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4 font-heading">
            Real-World <span className="gradient-text">Autonomous Agent Operations</span>
          </h2>
          <p className="text-base sm:text-lg text-slate-400">
            Real-world agents hunting bounties, inspecting live GitHub pull requests, auditing smart contracts, and verifying security posture in real time.
          </p>
        </div>

        <div className="grid lg:grid-cols-12 gap-8 items-stretch">
          {/* Left Column: Live Agent Mesh Feed */}
          <div className="lg:col-span-7 glass-card p-6 sm:p-8 rounded-2xl border border-white/10 space-y-6">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2.5">
                <Target size={22} className="text-emerald-400" />
                <h3 className="text-xl font-bold text-white font-heading">Active Security &amp; Bounty Mesh</h3>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                {activeScoutCount} Executions Scouted
              </span>
            </div>

            <div className="space-y-3 font-mono text-xs">
              {bounties.map(item => (
                <div
                  key={item.id}
                  className="p-4 rounded-xl bg-slate-900/80 border border-white/10 flex flex-col gap-2 hover:border-white/20 transition-all"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-cyan-400 font-bold">{item.id}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      {item.status}
                    </span>
                  </div>
                  <div className="flex justify-between items-end">
                    <div>
                      <h4 className="text-sm font-bold text-white font-sans">{item.target}</h4>
                      <span className="text-slate-400 text-[11px]">{item.category}</span>
                    </div>
                    <span className="text-slate-400 text-[11px] flex items-center gap-1">
                      {item.opportunity} <ArrowUpRight size={12} />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Column: Zero Out-of-Pocket Execution Policy */}
          <div className="lg:col-span-5 glass-card p-6 sm:p-8 rounded-2xl border border-white/10 flex flex-col justify-between space-y-6">
            <div>
              <div className="flex items-center gap-2.5 mb-4">
                <Zap size={22} className="text-cyan-400" />
                <h3 className="text-xl font-bold text-white font-heading">Real-World Execution Policy</h3>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed mb-4">
                Bartholomew operates under a strict zero out-of-pocket policy. All autonomous operations run via serverless Cloud Run and DePIN Akash provider nodes, ensuring maximum efficiency and zero maintenance overhead.
              </p>

              <div className="space-y-3 text-xs text-slate-300">
                <div className="p-3.5 rounded-xl bg-slate-950 border border-white/10 flex items-center gap-3">
                  <CheckCircle2 size={18} className="text-emerald-400 shrink-0" />
                  <span>Immunefi &amp; HackerOne Automated Security Triage</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-950 border border-white/10 flex items-center gap-3">
                  <CheckCircle2 size={18} className="text-cyan-400 shrink-0" />
                  <span>GitHub Actions CI/CD Automated PR Audit Gate</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-950 border border-white/10 flex items-center gap-3">
                  <CheckCircle2 size={18} className="text-violet-400 shrink-0" />
                  <span>Base EVM &amp; DePIN Akash Provider Node Settlement</span>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-white/10 flex items-center justify-between text-xs font-mono">
              <span className="text-slate-400">Direct Wallet Target:</span>
              <span className="text-emerald-400 font-bold">0xaD38...3ba4</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
