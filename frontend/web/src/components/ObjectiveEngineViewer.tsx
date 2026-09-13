import { useState } from 'react'
import { Target, AlertTriangle, RefreshCw, BarChart2, ShieldCheck } from 'lucide-react'

interface EvaluationResult {
  decision: string
  objective_id: string
  selected_action: {
    action_id: string
    description: string
    expected_value: number
    expected_cost: number
    risk_score: number
    net_expected_utility: number
  }
  ranked_candidates_count: number
  verification_status: string
}

interface OutcomeRecord {
  action_id: string
  predicted_outcome: string
  actual_outcome: string
  success: boolean
  prediction_variance: number
  evidence_refs: string[]
}

const SAMPLE_EVALUATION: EvaluationResult = {
  decision: 'EXECUTE_NEXT_BEST_ACTION',
  objective_id: 'obj_reduce_cloud_cost_01',
  selected_action: {
    action_id: 'act_downscale_idle_nodes',
    description: 'Downscale idle worker nodes during off-peak hours (01:00-05:00 UTC)',
    expected_value: 120.0,
    expected_cost: 5.0,
    risk_score: 0.10,
    net_expected_utility: 114.0
  },
  ranked_candidates_count: 2,
  verification_status: 'CONSTRAINTS_VERIFIED'
}

const SAMPLE_OUTCOMES: OutcomeRecord[] = [
  {
    action_id: 'act_downscale_idle_nodes',
    predicted_outcome: '22% cost reduction with 100% uptime',
    actual_outcome: '24% cost reduction with 100% uptime verified',
    success: true,
    prediction_variance: 0.02,
    evidence_refs: ['ev_billing_audit_202']
  }
]

export default function ObjectiveEngineViewer() {
  const [evalResult] = useState<EvaluationResult>(SAMPLE_EVALUATION)
  const [outcomes, setOutcomes] = useState<OutcomeRecord[]>(SAMPLE_OUTCOMES)
  const [isEvaluating, setIsEvaluating] = useState(false)

  const handleEvaluate = () => {
    setIsEvaluating(true)
    setTimeout(() => {
      const newOutcome: OutcomeRecord = {
        action_id: `act_opt_${Math.floor(100 + Math.random() * 900)}`,
        predicted_outcome: 'Optimal query execution path caching',
        actual_outcome: '1.14 μs latency reduction verified',
        success: true,
        prediction_variance: 0.01,
        evidence_refs: [`ev_outcome_${Math.floor(100 + Math.random() * 900)}`]
      }
      setOutcomes(prev => [newOutcome, ...prev])
      setIsEvaluating(false)
    }, 600)
  }

  return (
    <section id="objective-engine" className="py-24 px-5 sm:px-8 bg-slate-950/80 relative border-t border-white/5">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mb-4">
            <Target size={14} />
            Closed Decision-Control Loop
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4 font-heading">
            Objective Engine &amp; <span className="gradient-text">Outcome Memory</span>
          </h2>
          <p className="text-base sm:text-lg text-slate-400">
            AI agents generate intentions. Bartholomew evaluates constraints, ranks expected utility vs. risk, and verifies real-world outcomes against predictions to build a compounding proprietary outcome memory.
          </p>
        </div>

        {/* Closed Loop Architecture Flow */}
        <div className="glass-card p-6 sm:p-8 rounded-2xl border border-white/10 mb-12 bg-slate-950/90">
          <div className="text-xs font-mono text-center text-slate-500 mb-4 uppercase tracking-widest">
            THE CLOSED DECISION-CONTROL LOOP
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2 text-center text-xs font-mono">
            <div className="p-3 rounded-xl bg-slate-900 border border-white/10 text-cyan-300">
              <span className="font-bold block text-[11px]">1. OBJECTIVE</span>
              <span className="text-[10px] text-slate-400">Goal &amp; Limits</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900 border border-white/10 text-emerald-300">
              <span className="font-bold block text-[11px]">2. PERCEIVE</span>
              <span className="text-[10px] text-slate-400">Observe State</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900 border border-white/10 text-violet-300">
              <span className="font-bold block text-[11px]">3. REASON</span>
              <span className="text-[10px] text-slate-400">Utility vs Risk</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900 border border-white/10 text-cyan-300">
              <span className="font-bold block text-[11px]">4. VERIFY</span>
              <span className="text-[10px] text-slate-400">Constraints</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900 border border-white/10 text-amber-300">
              <span className="font-bold block text-[11px]">5. ACT</span>
              <span className="text-[10px] text-slate-400">Execute</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900 border border-white/10 text-rose-300">
              <span className="font-bold block text-[11px]">6. OUTCOME</span>
              <span className="text-[10px] text-slate-400">Real World</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900 border border-white/10 text-emerald-300">
              <span className="font-bold block text-[11px]">7. LEARN</span>
              <span className="text-[10px] text-slate-400">Store Memory</span>
            </div>
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              <span className="font-bold block text-[11px]">8. RE-EVALUATE</span>
              <span className="text-[10px] text-slate-400">Closed Loop</span>
            </div>
          </div>
        </div>

        {/* Evaluation & Outcome History Grid */}
        <div className="grid lg:grid-cols-12 gap-8 items-stretch">
          {/* Left Column: Selected Action & Utility Ranking */}
          <div className="lg:col-span-6 glass-card p-6 sm:p-8 rounded-2xl border border-white/10 space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-xl font-bold text-white font-heading flex items-center gap-2">
                <ShieldCheck size={22} className="text-emerald-400" />
                Selected Action &amp; Utility Evaluation
              </h3>
              <button
                onClick={handleEvaluate}
                disabled={isEvaluating}
                className="btn-action text-xs font-bold py-2 px-4 flex items-center gap-1.5"
              >
                <RefreshCw size={14} className={isEvaluating ? 'animate-spin' : ''} />
                {isEvaluating ? 'Evaluating...' : 'Evaluate Action'}
              </button>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-emerald-500/30 space-y-3 font-mono text-xs">
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Objective ID:</span>
                <span className="text-cyan-400 font-bold">{evalResult.objective_id}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Decision:</span>
                <span className="text-emerald-400 font-bold">{evalResult.decision}</span>
              </div>
              <div className="pt-2 border-t border-white/10 space-y-2">
                <span className="text-slate-400 block">Selected Action Description:</span>
                <p className="text-white bg-slate-900 p-2.5 rounded border border-white/5 font-sans">
                  {evalResult.selected_action.description}
                </p>
              </div>
              <div className="grid grid-cols-3 gap-2 pt-2 text-center">
                <div className="p-2 rounded bg-slate-900 border border-white/5">
                  <span className="text-slate-500 text-[10px] block">Expected Value</span>
                  <span className="text-emerald-400 font-bold">${evalResult.selected_action.expected_value}</span>
                </div>
                <div className="p-2 rounded bg-slate-900 border border-white/5">
                  <span className="text-slate-500 text-[10px] block">Expected Cost</span>
                  <span className="text-amber-400 font-bold">${evalResult.selected_action.expected_cost}</span>
                </div>
                <div className="p-2 rounded bg-slate-900 border border-white/5">
                  <span className="text-slate-500 text-[10px] block">Net Utility</span>
                  <span className="text-cyan-400 font-bold">+{evalResult.selected_action.net_expected_utility}</span>
                </div>
              </div>
            </div>

            {/* Constraint Violation Rejection Note */}
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-white/5 text-xs text-slate-400 flex items-start gap-2.5">
              <AlertTriangle size={16} className="text-amber-400 shrink-0 mt-0.5" />
              <span>
                Candidate <code className="text-slate-200 font-mono">act_migrate_to_spot_instances</code> was rejected because it violated the <code className="text-amber-300 font-mono">zero_downtime_guarantee</code> constraint.
              </span>
            </div>
          </div>

          {/* Right Column: Persistent Outcome Memory */}
          <div className="lg:col-span-6 glass-card p-6 sm:p-8 rounded-2xl border border-white/10 space-y-6 flex flex-col justify-between">
            <div>
              <h3 className="text-xl font-bold text-white font-heading flex items-center gap-2 mb-4">
                <BarChart2 size={22} className="text-cyan-400" />
                Proprietary Outcome Memory (Predicted vs. Actual)
              </h3>

              <div className="space-y-3 font-mono text-xs max-h-[300px] overflow-y-auto pr-1">
                {outcomes.map((rec, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-slate-950 border border-white/10 space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-cyan-400 font-bold">{rec.action_id}</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                        VERIFIED_MATCH
                      </span>
                    </div>
                    <div className="space-y-1 text-[11px]">
                      <div className="text-slate-400 flex justify-between">
                        <span>Predicted:</span>
                        <span className="text-slate-300">{rec.predicted_outcome}</span>
                      </div>
                      <div className="text-slate-400 flex justify-between">
                        <span>Actual Outcome:</span>
                        <span className="text-emerald-400 font-bold">{rec.actual_outcome}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-white/10 text-xs text-slate-400 flex items-center justify-between">
              <span>Decision-Outcome Memory Size:</span>
              <strong className="text-emerald-400 font-mono font-bold">{outcomes.length} Verified Records</strong>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
