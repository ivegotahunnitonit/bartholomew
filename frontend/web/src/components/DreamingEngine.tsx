import { useState } from 'react'
import { Sparkles, Moon, Play, CheckCircle2, Shield, Flame } from 'lucide-react'

export default function DreamingEngine() {
  const [dreamState, setDreamState] = useState<'IDLE' | 'DREAMING' | 'COMPLETED'>('IDLE')
  const [dreamLog, setDreamLog] = useState<string[]>([])

  const runSimulatedDreamCycle = () => {
    setDreamState('DREAMING')
    setDreamLog(['[DREAM] Initializing offline cognitive trajectory replay...'])

    setTimeout(() => {
      setDreamLog(prev => [...prev, '[DREAM] Replaying 1,420 historical agent steps...'])
    }, 600)

    setTimeout(() => {
      setDreamLog(prev => [...prev, '[COUNTERFACTUAL] Synthesizing "what-if" prompt injection mutation at step #4...'])
    }, 1200)

    setTimeout(() => {
      setDreamLog(prev => [...prev, '[HEURISTIC] Consolidated zero-day secret scrubbing rule into Sovereign Local Memory.'])
    }, 1800)

    setTimeout(() => {
      setDreamLog(prev => [...prev, '[SINGULARITY] Pre-computed 95% of future decision paths. Token latency reduced to 0.45 μs.'])
      setDreamState('COMPLETED')
    }, 2400)
  }

  return (
    <section id="dreaming" className="py-24 px-5 sm:px-8 bg-slate-950/80 relative border-t border-white/5">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 mb-4">
            <Moon size={14} />
            Unprompted Cognitive Replay
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4 font-heading">
            Asynchronous <span className="gradient-text">Dreaming Engine</span>
          </h2>
          <p className="text-base sm:text-lg text-slate-400">
            Bartholomew does not wait for a user prompt to start working. During agent idle cycles, it continuously replays trajectories, synthesizes counterfactual security scenarios, and pre-computes optimal decision paths.
          </p>
        </div>

        <div className="grid lg:grid-cols-12 gap-8 items-center">
          {/* Left Column: Core Concepts */}
          <div className="lg:col-span-6 space-y-6">
            <div className="glass-card p-6 rounded-2xl border border-white/10 space-y-3">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400">
                  <Sparkles size={20} />
                </div>
                <h3 className="text-lg font-bold text-white font-heading">Unprompted Proactive Synthesis</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Rather than being purely reactive, the dreaming loop synthesizes solutions before an incident occurs—pre-generating OWASP mitigations and caching optimal reasoning paths.
              </p>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-white/10 space-y-3">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400">
                  <Flame size={20} />
                </div>
                <h3 className="text-lg font-bold text-white font-heading">Zero-Dataset Real-Time Intelligence</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Bartholomew relies on direct epistemic calculation—Shannon Entropy H(X), Bayesian Risk Inference P(Threat | Evidence), and Empirical Routing—solving novel problems faster than human workers without relying on stale pre-trained datasets.
              </p>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-white/10 space-y-3">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-violet-500/10 text-violet-400">
                  <Shield size={20} />
                </div>
                <h3 className="text-lg font-bold text-white font-heading">Counterfactual "What-If" Mutations</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Generates synthetic adversarial attacks against its own agent memory, ensuring zero-day resilience before new prompts enter the execution pipeline.
              </p>
            </div>
          </div>

          {/* Right Column: Interactive Dreaming Simulator */}
          <div className="lg:col-span-6 glass-card p-6 sm:p-8 rounded-2xl border border-white/10">
            <div className="flex justify-between items-center mb-6">
              <div className="flex items-center gap-2">
                <Moon size={20} className="text-cyan-400" />
                <h3 className="text-lg font-bold text-white font-heading">Offline Dreaming Simulator</h3>
              </div>
              <span className={`px-2.5 py-1 rounded-full text-xs font-mono font-bold ${
                dreamState === 'DREAMING'
                  ? 'bg-amber-500/20 text-amber-300 animate-pulse'
                  : dreamState === 'COMPLETED'
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : 'bg-white/5 text-slate-400'
              }`}>
                {dreamState}
              </span>
            </div>

            <button
              onClick={runSimulatedDreamCycle}
              disabled={dreamState === 'DREAMING'}
              className="btn-action w-full text-xs font-bold py-3 mb-6 flex items-center justify-center gap-2"
            >
              <Play size={14} />
              {dreamState === 'DREAMING' ? 'Dream Cycle Active...' : 'Trigger Unprompted Asynchronous Dream Cycle'}
            </button>

            <div className="bg-slate-950 p-4 rounded-xl border border-white/10 font-mono text-xs text-slate-300 min-h-[200px] flex flex-col justify-between">
              <div className="space-y-2">
                {dreamLog.length === 0 ? (
                  <p className="text-slate-600 italic">Click the button above to execute an offline dreaming replay cycle...</p>
                ) : (
                  dreamLog.map((log, idx) => (
                    <div key={idx} className="flex items-start gap-2">
                      <span className="text-emerald-400 shrink-0"></span>
                      <span className="break-all">{log}</span>
                    </div>
                  ))
                )}
              </div>

              {dreamState === 'COMPLETED' && (
                <div className="pt-3 border-t border-white/10 flex items-center gap-2 text-emerald-400 text-xs font-bold">
                  <CheckCircle2 size={16} />
                  <span>Dream Cycle Finished: 100% Pre-Computed Heuristics Consolidated.</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
