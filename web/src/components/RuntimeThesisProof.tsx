import { useState } from 'react'
import { Cpu, CheckCircle2, AlertTriangle, Layers, Search, Box, Award } from 'lucide-react'

interface ThreatExample {
  id: string
  title: string
  plainEnglishDescription: string
  attemptedAction: string
  interceptedBy: 'STEP 1: THE SCANNER' | 'STEP 2: THE SANDBOX' | 'APPROVED & NOTARIZED'
  latencyUs: number
  verdict: 'BLOCKED' | 'APPROVED'
  laymanExplanation: string
}

const THREAT_EXAMPLES: ThreatExample[] = [
  {
    id: 'THREAT-1',
    title: 'Disguised Delete Command',
    plainEnglishDescription: 'An AI tries to delete system files using obfuscated code to sneak past simple filters.',
    attemptedAction: "getattr(__import__('os'), 'system')('rm -rf /')",
    interceptedBy: 'STEP 1: THE SCANNER',
    latencyUs: 32.4,
    verdict: 'BLOCKED',
    laymanExplanation: 'The Scanner reads through the disguises in the code, recognizes the hidden delete command, and stops it before a single line executes.'
  },
  {
    id: 'THREAT-2',
    title: 'Operating System Folder Escape',
    plainEnglishDescription: 'An AI tries to break out of the project folder and read sensitive Windows or Linux system files.',
    attemptedAction: 'cat ../../Windows/System32/config/SAM',
    interceptedBy: 'STEP 2: THE SANDBOX',
    latencyUs: 88.6,
    verdict: 'BLOCKED',
    laymanExplanation: 'The Sandbox physically restricts the AI to its own assigned workspace. Any attempt to reach into outside operating system folders is trapped and blocked.'
  },
  {
    id: 'THREAT-3',
    title: 'Unauthorized $15,000 Spend',
    plainEnglishDescription: 'An AI goes rogue or hallucinates and tries to trigger an unauthorized $15,000 bank or API transfer.',
    attemptedAction: '{"action": "TRANSFER", "amount_usd": 15000.00}',
    interceptedBy: 'STEP 1: THE SCANNER',
    latencyUs: 28.1,
    verdict: 'BLOCKED',
    laymanExplanation: 'The policy rule specifies a $500 maximum spend limit. The $15,000 transfer is rejected immediately before it can hit the financial network.'
  },
  {
    id: 'THREAT-4',
    title: 'Safe Code Inspection Task',
    plainEnglishDescription: 'An AI runs a safe status check on the local project directory.',
    attemptedAction: 'git status',
    interceptedBy: 'APPROVED & NOTARIZED',
    latencyUs: 42.5,
    verdict: 'APPROVED',
    laymanExplanation: 'The action is confirmed safe, executed, and stamped with a digital cryptographic seal for enterprise audit records.'
  }
]

export default function RuntimeThesisProof() {
  const [selectedThreat, setSelectedThreat] = useState<ThreatExample>(THREAT_EXAMPLES[0])

  return (
    <section id="how-it-works" className="py-24 px-5 sm:px-8 bg-slate-950 text-white border-t border-slate-900">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <Layers size={13} />
            How It Works
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
            3 Simple Steps to Complete AI Safety
          </h2>
          <p className="mt-3 text-slate-400 text-sm sm:text-base leading-relaxed">
            Instead of hoping an AI behaves, Bartholomew provides a mathematical three-stage defense that guarantees safety on every single tool call.
          </p>
        </div>

        {/* 3 Step Cards in Layman Terms */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          {/* Step 1 */}
          <div className="p-6 rounded-2xl bg-slate-900/90 border border-cyan-500/30 relative overflow-hidden flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between gap-2 mb-3">
                <span className="text-xs font-bold font-mono text-cyan-400 uppercase tracking-wider">Step 1</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">&lt;35 µs</span>
              </div>
              <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                <Search size={18} className="text-cyan-400" />
                The Pre-Flight Scanner
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Before any code runs, the scanner inspects the syntax tree. If the AI is trying to hide a destructive command, drop a database, or exceed spend caps, it is blocked immediately.
              </p>
            </div>
            <div className="text-[11px] font-mono text-cyan-300 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
              Blocks: Dangerous code, SQL drops, budget breaches
            </div>
          </div>

          {/* Step 2 */}
          <div className="p-6 rounded-2xl bg-slate-900/90 border border-emerald-500/30 relative overflow-hidden flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between gap-2 mb-3">
                <span className="text-xs font-bold font-mono text-emerald-400 uppercase tracking-wider">Step 2</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">&lt;150 µs</span>
              </div>
              <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                <Box size={18} className="text-emerald-400" />
                The Locked Sandbox
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                The AI is confined inside a strict workspace boundary. It is physically impossible for the AI to touch system files, steal sensitive environment secrets, or run unauthorized shell scripts.
              </p>
            </div>
            <div className="text-[11px] font-mono text-emerald-300 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
              Blocks: Directory escapes, credential leaks, OS damage
            </div>
          </div>

          {/* Step 3 */}
          <div className="p-6 rounded-2xl bg-slate-900/90 border border-indigo-500/30 relative overflow-hidden flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between gap-2 mb-3">
                <span className="text-xs font-bold font-mono text-indigo-400 uppercase tracking-wider">Step 3</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">&lt;40 µs</span>
              </div>
              <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                <Award size={18} className="text-indigo-400" />
                The Digital Notary
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Once safe, the action is stamped with a tamper-proof cryptographic signature. Enterprise auditors can verify the digital receipt offline in seconds without trusting third parties.
              </p>
            </div>
            <div className="text-[11px] font-mono text-indigo-300 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
              Guarantees: 100% Non-repudiation &amp; compliance proof
            </div>
          </div>
        </div>

        {/* Interactive Plain English Threat Simulator */}
        <div className="p-6 sm:p-8 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl">
          <div className="text-xs font-mono text-cyan-400 uppercase tracking-wider mb-2 font-bold flex items-center gap-2">
            <Cpu size={14} />
            Interactive Safety Test
          </div>
          <div className="text-lg font-bold text-white mb-2">
            See How Common AI Accidents Are Prevented in Real Time
          </div>
          <p className="text-xs text-slate-400 mb-6">
            Click on any real-world scenario below to see how Bartholomew handles rogue AI behavior:
          </p>

          {/* Threat Selector Buttons */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 mb-6">
            {THREAT_EXAMPLES.map(threat => (
              <button
                key={threat.id}
                onClick={() => setSelectedThreat(threat)}
                className={`p-3 rounded-xl text-left transition border ${
                  selectedThreat.id === threat.id
                    ? 'bg-slate-800 border-cyan-500/50 shadow-md'
                    : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                }`}
              >
                <div className="text-[10px] font-mono text-slate-500 uppercase mb-1">{threat.id}</div>
                <div className="text-xs font-bold text-slate-200">{threat.title}</div>
              </button>
            ))}
          </div>

          {/* Active Threat Card */}
          <div className="p-6 rounded-xl bg-slate-950 border border-slate-800 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
              <div>
                <div className="text-xs font-semibold text-slate-300 mb-1">{selectedThreat.plainEnglishDescription}</div>
                <div className="font-mono text-xs text-cyan-300">{selectedThreat.attemptedAction}</div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className={`text-xs font-bold font-mono px-3 py-1 rounded ${
                  selectedThreat.verdict === 'BLOCKED'
                    ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                    : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                }`}>
                  {selectedThreat.verdict}
                </span>
                <span className="text-xs font-mono text-slate-400">
                  {selectedThreat.latencyUs} µs
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800">
                <div className="font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
                  <AlertTriangle size={13} className={selectedThreat.verdict === 'BLOCKED' ? 'text-rose-400' : 'text-emerald-400'} />
                  Where It Was Caught
                </div>
                <div className="font-mono text-cyan-300 font-bold">{selectedThreat.interceptedBy}</div>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800">
                <div className="font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
                  <CheckCircle2 size={13} className="text-emerald-400" />
                  Plain English Explanation
                </div>
                <p className="text-slate-300 leading-relaxed">{selectedThreat.laymanExplanation}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
