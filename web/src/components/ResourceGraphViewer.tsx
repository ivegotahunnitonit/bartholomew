import { useState } from 'react'
import { GitMerge, ArrowRight, CheckCircle2, ShieldCheck, Cpu, RefreshCw, FileText } from 'lucide-react'

interface CycleStep {
  from_entity: string
  to_entity: string
  capability_transferred: string
  capacity: string
}

interface SimulatedCycle {
  cycle_length: number
  participants: string[]
  viability_score: number
  observed_facts: string[]
  estimates: string[]
  evidence_refs: string[]
  exchange_sequence: CycleStep[]
}

const SAMPLE_CYCLE: SimulatedCycle = {
  cycle_length: 4,
  participants: [
    'Entity_A_Developer',
    'Entity_B_Accountant',
    'Entity_C_EquipmentOwner',
    'Entity_D_Landscaper'
  ],
  viability_score: 0.92,
  observed_facts: [
    'Closed loop established across 4 distinct entities: A -> B -> C -> D -> A',
    '100% resource-to-need structural alignment verified.',
    'All entity capabilities verified via signed cryptographic evidence artifacts.'
  ],
  estimates: [
    'Cycle execution assumes synchronous participant commitment without transaction friction.',
    'Estimated completion window: August 15 - August 30, 2026.'
  ],
  evidence_refs: [
    'ev_github_audit_101',
    'ev_cpa_cert_202',
    'ev_serial_inspect_303',
    'ev_license_bond_404'
  ],
  exchange_sequence: [
    {
      from_entity: 'Entity_A_Developer',
      to_entity: 'Entity_B_Accountant',
      capability_transferred: 'Web Development',
      capacity: '20 Hours'
    },
    {
      from_entity: 'Entity_B_Accountant',
      to_entity: 'Entity_C_EquipmentOwner',
      capability_transferred: 'Accounting & Tax Review',
      capacity: '10 Hours'
    },
    {
      from_entity: 'Entity_C_EquipmentOwner',
      to_entity: 'Entity_D_Landscaper',
      capability_transferred: 'Equipment Rental (Skidsteer)',
      capacity: '1 Unit'
    },
    {
      from_entity: 'Entity_D_Landscaper',
      to_entity: 'Entity_A_Developer',
      capability_transferred: 'Landscaping & Grading',
      capacity: '15 Hours'
    }
  ]
}

export default function ResourceGraphViewer() {
  const [activeCycle] = useState<SimulatedCycle>(SAMPLE_CYCLE)
  const [isMatching, setIsMatching] = useState(false)

  const runGraphMatching = () => {
    setIsMatching(true)
    setTimeout(() => {
      setIsMatching(false)
    }, 600)
  }

  return (
    <section id="resource-graph" className="py-24 px-5 sm:px-8 bg-slate-950/90 relative border-t border-white/5">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mb-4">
            <GitMerge size={14} />
            Resource Graph Capability Layer
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4 font-heading">
            Deterministic <span className="gradient-text">Resource Graph &amp; Cycle Discovery</span>
          </h2>
          <p className="text-base sm:text-lg text-slate-400">
            Bartholomew models resources, needs, capabilities, constraints, and verified outcomes—discovering multi-party exchange cycles (A → B → C → D → A) without money, tokens, or public marketplaces.
          </p>
        </div>

        {/* Top Control Bar */}
        <div className="glass-card p-6 sm:p-8 rounded-2xl border border-white/10 mb-8 space-y-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h3 className="text-xl font-bold text-white font-heading flex items-center gap-2">
                <Cpu size={22} className="text-emerald-400" />
                Multi-Party Exchange Graph (Simulated Model)
              </h3>
              <p className="text-xs text-slate-400">
                Discovers compatible resources across non-cash barter cycles and validates evidence.
              </p>
            </div>
            <button
              onClick={runGraphMatching}
              disabled={isMatching}
              className="btn-action text-xs font-bold py-2.5 px-5 flex items-center gap-2 shrink-0"
            >
              <RefreshCw size={14} className={isMatching ? 'animate-spin' : ''} />
              {isMatching ? 'Matching Cycle Graph...' : 'Re-Run Deterministic Cycle Discovery'}
            </button>
          </div>

          {/* Sequence Cycle Diagram */}
          <div className="grid md:grid-cols-4 gap-4 pt-4">
            {activeCycle.exchange_sequence.map((step, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-900/90 border border-white/10 space-y-2 relative">
                <div className="flex justify-between items-center text-xs font-mono text-slate-500">
                  <span>STEP 0{idx + 1}</span>
                  <span className="text-cyan-400 font-bold">MATCHED</span>
                </div>
                <div className="text-xs font-bold text-emerald-400 font-mono truncate">{step.from_entity}</div>
                <div className="text-xs text-slate-300 font-sans font-semibold flex items-center gap-1">
                  <span>Transfers:</span>
                  <span className="text-white">{step.capability_transferred}</span>
                </div>
                <div className="text-[11px] text-slate-400">Capacity: {step.capacity}</div>
                <div className="text-[11px] text-violet-400 font-mono flex items-center gap-1">
                  <span>Receiver:</span>
                  <span className="truncate">{step.to_entity}</span>
                </div>

                {idx < activeCycle.exchange_sequence.length - 1 && (
                  <div className="hidden md:block absolute -right-3 top-1/2 -translate-y-1/2 z-20 text-slate-600">
                    <ArrowRight size={14} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Breakdown: Facts vs Estimates & Verified Evidence */}
        <div className="grid lg:grid-cols-12 gap-8 items-stretch">
          {/* Left Column: Facts vs Estimates */}
          <div className="lg:col-span-7 glass-card p-6 sm:p-8 rounded-2xl border border-white/10 space-y-6">
            <h4 className="text-lg font-bold text-white font-heading flex items-center gap-2">
              <FileText size={20} className="text-cyan-400" />
              Observed Facts vs. Estimated Projections
            </h4>

            <div className="space-y-4 text-xs font-mono">
              <div className="p-4 rounded-xl bg-slate-950 border border-emerald-500/30 space-y-2">
                <span className="text-emerald-400 font-bold block uppercase tracking-wider text-[11px]">
                  ✓ Verified Observed Facts:
                </span>
                <ul className="space-y-1.5 text-slate-300">
                  {activeCycle.observed_facts.map((fact, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-emerald-400 shrink-0">❯</span>
                      <span>{fact}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-xl bg-slate-950 border border-amber-500/30 space-y-2">
                <span className="text-amber-400 font-bold block uppercase tracking-wider text-[11px]">
                  ⚠ Explicit Estimates &amp; Hypotheses:
                </span>
                <ul className="space-y-1.5 text-slate-300">
                  {activeCycle.estimates.map((est, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-amber-400 shrink-0">❯</span>
                      <span>{est}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Right Column: Evidence References */}
          <div className="lg:col-span-5 glass-card p-6 sm:p-8 rounded-2xl border border-white/10 space-y-6 flex flex-col justify-between">
            <div>
              <h4 className="text-lg font-bold text-white font-heading flex items-center gap-2 mb-4">
                <ShieldCheck size={20} className="text-violet-400" />
                Supporting Cryptographic Evidence
              </h4>

              <div className="space-y-2.5 font-mono text-xs">
                {activeCycle.evidence_refs.map((ref, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-950 border border-white/10 flex justify-between items-center">
                    <span className="text-slate-300">{ref}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-violet-500/20 text-violet-300 border border-violet-500/30">
                      VERIFIED
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-white/10 text-xs text-slate-400 flex items-center gap-3">
              <CheckCircle2 size={18} className="text-emerald-400 shrink-0" />
              <span>Deterministic Graph Viability Score: <strong className="text-white font-mono font-bold">92%</strong></span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
