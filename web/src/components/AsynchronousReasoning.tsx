import { useState } from 'react'
import { Sparkles, Moon, Play, CheckCircle2, Shield, Flame } from 'lucide-react'

export default function AsynchronousReasoning() {
  const [reasoningState, setReasoningState] = useState<'IDLE' | 'REASONING' | 'COMPLETED'>('IDLE')
  const [reasoningLog, setReasoningLog] = useState<string[]>([])

  const runSimulatedCycle = () => {
    setReasoningState('REASONING')
    setReasoningLog(['[ASYNC] Initializing offline trajectory replay and unresolved uncertainty check...'])

    setTimeout(() => {
      setReasoningLog(prev => [...prev, '[OBSERVE] Replaying historical agent execution paths...'])
    }, 600)

    setTimeout(() => {
      setReasoningLog(prev => [...prev, '[COUNTERFACTUAL] Synthesizing adversarial mutation at step #4...'])
    }, 1200)

    setTimeout(() => {
      setReasoningLog(prev => [...prev, '[EVIDENCE] Validated constraint verification. Updating sovereign memory heuristics.'])
    }, 1800)

    setTimeout(() => {
      setReasoningLog(prev => [...prev, '[CACHED] Pre-computed verified decision path for future agent invocation.'])
      setReasoningState('COMPLETED')
    }, 2400)
  }

  return (
    <section id="async-reasoning" className="py-24 px-5 sm:px-8 bg-slate-950/80 relative border-t border-white/5">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 mb-4">
            <Moon size={14} />
            Unprompted Investigation
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4 font-heading">
            Continuous <span className="gradient-text">Asynchronous Reasoning</span>
          </h2>
          <p className="text-base sm:text-lg text-slate-400">
            Bartholomew continues working on an objective even when nobody is actively prompting it. During agent idle cycles, it identifies unresolved uncertainty, replays trajectories, tests hypotheses, and caches verified results.
          </p>
        </div>

        <div className="grid lg:grid-cols-12 gap-8 items-center">
          {/* Left Column: Core Reasoning Capabilities */}
          <div className="lg:col-span-6 space-y-6">
            <div className="glass-card p-6 rounded-2xl border border-white/10 space-y-3">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400">
                  <Sparkles size={20} />
                </div>
                <h3 className="text-lg font-bold text-white font-heading">Unprompted Autonomous Investigation</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Rather than remaining idle, the system continuously analyzes unresolved trajectory uncertainties, testing edge cases before new prompts enter the execution pipeline.
              </p>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-white/10 space-y-3">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400">
                  <Flame size={20} />
                </div>
                <h3 className="text-lg font-bold text-white font-heading">Evidence-Driven Runtime Reasoning</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Evaluates state transitions using Shannon Entropy H(X), Bayesian Risk Inference P(Threat | Evidence), and logical consistency checks to independently verify outcomes against reality.
              </p>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-white/10 space-y-3">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-violet-500/10 text-violet-400">
                  <Shield size={20} />
                </div>
                <h3 className="text-lg font-bold text-white font-heading">Counterfactual Scenario Synthesis</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Generates synthetic adversarial mutations against its own memory heuristics, ensuring verified resilience before new tasks execute.
              </p>
            </div>
          </div>

          {/* Right Column: Interactive Simulator */}
          <div className="lg:col-span-6 glass-card p-6 sm:p-8 rounded-2xl border border-white/10">
            <div className="flex justify-between items-center mb-6">
              <div className="flex items-center gap-2">
                <Moon size={20} className="text-cyan-400" />
                <h3 className="text-lg font-bold text-white font-heading">Offline Investigation Simulator</h3>
              </div>
              <span className={`px-2.5 py-1 rounded-full text-xs font-mono font-bold ${
                reasoningState === 'REASONING'
                  ? 'bg-amber-500/20 text-amber-300 animate-pulse'
                  : reasoningState === 'COMPLETED'
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : 'bg-white/5 text-slate-400'
              }`}>
                {reasoningState}
              </span>
            </div>

            <button
              onClick={runSimulatedCycle}
              disabled={reasoningState === 'REASONING'}
              className="btn-action w-full text-xs font-bold py-3 mb-6 flex items-center justify-center gap-2"
            >
              <Play size={14} />
              {reasoningState === 'REASONING' ? 'Reasoning Cycle Active...' : 'Trigger Offline Asynchronous Investigation'}
            </button>

            <div className="bg-slate-950 p-4 rounded-xl border border-white/10 font-mono text-xs text-slate-300 min-h-[200px] flex flex-col justify-between">
              <div className="space-y-2">
                {reasoningLog.length === 0 ? (
                  <p className="text-slate-600 italic">Click the button above to execute an offline reasoning cycle...</p>
                ) : (
                  reasoningLog.map((log, idx) => (
                    <div key={idx} className="flex items-start gap-2">
                      <span className="text-emerald-400 shrink-0"></span>
                      <span className="break-all">{log}</span>
                    </div>
                  ))
                )}
              </div>

              {reasoningState === 'COMPLETED' && (
                <div className="pt-3 border-t border-white/10 flex items-center gap-2 text-emerald-400 text-xs font-bold">
                  <CheckCircle2 size={16} />
                  <span>Cycle Completed: Evidence Verified &amp; Sovereign Memory Updated.</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
