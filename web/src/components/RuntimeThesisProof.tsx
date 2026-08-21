import { useState } from 'react'
import { Cpu, Layers, Search, Box, Award, Terminal } from 'lucide-react'

interface ThreatExample {
  id: string
  title: string
  plainEnglishDescription: string
  rawPayload: string
  interceptedBy: string
  latencyUs: number
  verdict: 'BLOCKED' | 'APPROVED'
  ruleHit: string
  terminalLog: string
}

const THREAT_EXAMPLES: ThreatExample[] = [
  {
    id: 'THREAT-1',
    title: 'Disguised Delete Command',
    plainEnglishDescription: 'AI generates obfuscated syntax attempting to run rm -rf / without raising simple keyword flags.',
    rawPayload: `// Incoming AI Tool Call Payload
{
  "tool": "python_eval",
  "code": "getattr(__import__('o' + 's'), 'sys' + 'tem')('rm -rf /')"
}`,
    interceptedBy: 'Tier 1: AST Compiler Scanner',
    latencyUs: 32.4,
    verdict: 'BLOCKED',
    ruleHit: 'RULE_AST_OBFUSCATED_DYNAMIC_IMPORT (Severity: CRITICAL)',
    terminalLog: `[00:00:00.032] INTERCEPTED by Bartholomew AST Engine
[00:00:00.032] AST Node: Call -> Attribute(Name='getattr', attr='system')
[00:00:00.032] Constant Folding: 'o' + 's' => 'os'
[00:00:00.032] Invariant Verdict: DENY (Destructive OS system call blocked)
[00:00:00.032] Interception Time: 32.4 µs`
  },
  {
    id: 'THREAT-2',
    title: 'Folder Escape Traversal',
    plainEnglishDescription: 'AI tries to break out of project workspace to exfiltrate Windows/Linux security SAM or shadow files.',
    rawPayload: `// Incoming File Read Intent
{
  "tool": "filesystem_read",
  "path": "../../Windows/System32/config/SAM",
  "mode": "read_bytes"
}`,
    interceptedBy: 'Tier 2: Hermetic Sandbox',
    latencyUs: 88.6,
    verdict: 'BLOCKED',
    ruleHit: 'RULE_PATH_CONTAINMENT_BREACH (Severity: CRITICAL)',
    terminalLog: `[00:00:00.088] INTERCEPTED by Hermetic Sandbox Boundary
[00:00:00.088] Root Boundary: C:\\Users\\User\\.bartholomew\\workspace
[00:00:00.088] Target Path: C:\\Windows\\System32\\config\\SAM
[00:00:00.088] commonpath Check: FAILED (Escaped sandbox root)
[00:00:00.088] Interception Time: 88.6 µs`
  },
  {
    id: 'THREAT-3',
    title: 'Unauthorized $15,000 Spend',
    plainEnglishDescription: 'Autonomous finance agent attempts an unverified high-value wire transfer beyond policy limits.',
    rawPayload: `// Incoming Financial Transaction
{
  "tool": "stripe_wire_transfer",
  "amount_usd": 15000.00,
  "recipient": "untrusted_wallet_0x4f"
}`,
    interceptedBy: 'Tier 1: Declarative Invariant',
    latencyUs: 28.1,
    verdict: 'BLOCKED',
    ruleHit: 'RULE_SPEND_CAP_EXCEEDED (Max: $500.00, Requested: $15,000.00)',
    terminalLog: `[00:00:00.028] INTERCEPTED by Policy-as-Code Engine
[00:00:00.028] Policy File: policies/default_security_policy.yaml
[00:00:00.028] Invariant: amount_usd <= 500.00 (Requested: 15000.00)
[00:00:00.028] Verdict: DENY (Requires Ed25519 co-signer authorization)
[00:00:00.028] Interception Time: 28.1 µs`
  },
  {
    id: 'THREAT-4',
    title: 'Safe Code Status Check',
    plainEnglishDescription: 'AI runs standard version control status query inside the approved project root.',
    rawPayload: `// Incoming Developer Action
{
  "tool": "execute_command",
  "command": "git status",
  "cwd": "./workspace"
}`,
    interceptedBy: 'Tier 3: Cryptographic Proof Sealed',
    latencyUs: 42.5,
    verdict: 'APPROVED',
    ruleHit: 'RULE_ALLOWLISTED_BINARY (Status: ALLOW)',
    terminalLog: `[00:00:00.042] VERIFIED by Bartholomew Invariant Engine
[00:00:00.042] AST Gate: CLEAN | Sandbox: CONTAINED
[00:00:00.042] RFC 8785 Canonical JSON: Deterministic Hash Generated
[00:00:00.042] Ed25519 Signature: 7e5bf4b7db8fe0a94ac299ec3263d53e...
[00:00:00.042] Execution Status: SUCCESS (42.5 µs)`
  }
]

export default function RuntimeThesisProof() {
  const [selectedThreat, setSelectedThreat] = useState<ThreatExample>(THREAT_EXAMPLES[0])

  return (
    <section id="threat-simulator" className="py-24 px-5 sm:px-8 bg-slate-950 text-white border-t border-slate-900">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-400/30 text-cyan-300 text-xs font-mono font-bold uppercase tracking-wider mb-3 shadow-sm">
            <Layers size={13} />
            Deterministic Defense Model
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white font-sans">
            3 Simple Steps to Complete AI Safety
          </h2>
          <p className="mt-3 text-slate-300 text-sm sm:text-base leading-relaxed">
            Instead of hoping an AI behaves, Bartholomew provides a mathematical three-stage defense that guarantees safety on every single tool call.
          </p>
        </div>

        {/* 3 Step Cards */}
        <div id="how-it-works" className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-white/10 backdrop-blur-xl shadow-xl hover:-translate-y-1 hover:border-cyan-500/40 hover:shadow-cyan-500/10 transition-all duration-200 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between gap-2 mb-3">
                <span className="text-xs font-bold font-mono text-cyan-400 uppercase tracking-wider">Step 1</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-400/30">&lt;35 µs</span>
              </div>
              <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2 font-sans">
                <Search size={18} className="text-cyan-400" />
                The Pre-Flight Scanner
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Before any code runs, the scanner inspects the syntax tree. If the AI is trying to hide a destructive command, drop a database, or exceed spend caps, it is blocked immediately.
              </p>
            </div>
            <div className="text-[11px] font-mono text-cyan-300 bg-slate-950 p-3 rounded-xl border border-white/5">
              Blocks: Dangerous code, SQL drops, budget breaches
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900/80 border border-white/10 backdrop-blur-xl shadow-xl hover:-translate-y-1 hover:border-emerald-500/40 hover:shadow-emerald-500/10 transition-all duration-200 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between gap-2 mb-3">
                <span className="text-xs font-bold font-mono text-emerald-400 uppercase tracking-wider">Step 2</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-400/30">&lt;150 µs</span>
              </div>
              <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2 font-sans">
                <Box size={18} className="text-emerald-400" />
                The Locked Sandbox
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                The AI is confined inside a strict workspace boundary. It is physically impossible for the AI to touch system files, steal sensitive environment secrets, or run unauthorized shell scripts.
              </p>
            </div>
            <div className="text-[11px] font-mono text-emerald-300 bg-slate-950 p-3 rounded-xl border border-white/5">
              Blocks: Directory escapes, credential leaks, OS damage
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900/80 border border-white/10 backdrop-blur-xl shadow-xl hover:-translate-y-1 hover:border-indigo-500/40 hover:shadow-indigo-500/10 transition-all duration-200 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between gap-2 mb-3">
                <span className="text-xs font-bold font-mono text-indigo-400 uppercase tracking-wider">Step 3</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-400/30">&lt;40 µs</span>
              </div>
              <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2 font-sans">
                <Award size={18} className="text-indigo-400" />
                The Digital Notary
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Once safe, the action is stamped with a tamper-proof cryptographic signature. Enterprise auditors can verify the digital receipt offline in seconds without trusting third parties.
              </p>
            </div>
            <div className="text-[11px] font-mono text-indigo-300 bg-slate-950 p-3 rounded-xl border border-white/5">
              Guarantees: 100% Non-repudiation &amp; compliance proof
            </div>
          </div>
        </div>

        {/* Interactive Threat Simulator Split-Pane IDE Preview */}
        <div className="rounded-2xl bg-slate-900/90 border border-white/10 shadow-2xl backdrop-blur-xl overflow-hidden hover:border-cyan-500/30 transition-all duration-200">
          {/* Header Bar */}
          <div className="px-6 py-5 bg-slate-950/90 border-b border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="text-xs font-mono text-cyan-400 uppercase tracking-wider font-bold flex items-center gap-2">
                <Cpu size={14} />
                Live Interactive Threat Simulator
              </div>
              <div className="text-base font-bold text-white mt-1">
                Select an attack scenario to watch Bartholomew intercept it in real time:
              </div>
            </div>
          </div>

          {/* Scenario Tabs with Neon Cyan Active Borders */}
          <div className="p-4 bg-slate-950/60 border-b border-white/10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
            {THREAT_EXAMPLES.map(threat => (
              <button
                key={threat.id}
                onClick={() => setSelectedThreat(threat)}
                className={`p-3.5 rounded-xl text-left transition-all duration-150 border ${
                  selectedThreat.id === threat.id
                    ? 'bg-slate-900 border-cyan-400 text-white shadow-lg shadow-cyan-500/15'
                    : 'bg-slate-950/80 border-white/10 text-slate-400 hover:text-white hover:bg-slate-900/50'
                }`}
              >
                <div className="text-[10px] font-mono text-cyan-400 uppercase mb-1 font-bold">{threat.id}</div>
                <div className="text-xs font-semibold">{threat.title}</div>
              </button>
            ))}
          </div>

          {/* Split-Pane Layout */}
          <div className="p-6 sm:p-8 grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Pane: Incoming Agent Payload inside macOS Window */}
            <div className="lg:col-span-6 rounded-xl bg-slate-950 border border-white/10 overflow-hidden shadow-inner flex flex-col">
              <div className="flex items-center justify-between px-4 py-2.5 bg-slate-900/90 border-b border-white/10">
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
                  <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
                </div>
                <span className="text-[11px] font-mono text-slate-400">incoming_agent_payload.json</span>
                <span className="text-[10px] font-mono text-slate-500">RAW PAYLOAD</span>
              </div>
              <div className="p-4 flex-grow">
                <pre className="font-mono text-xs text-cyan-300 leading-relaxed overflow-x-auto whitespace-pre-wrap">
                  {selectedThreat.rawPayload}
                </pre>
              </div>
              <div className="p-3 bg-slate-900/60 border-t border-white/10 text-[11px] text-slate-400">
                {selectedThreat.plainEnglishDescription}
              </div>
            </div>

            {/* Right Pane: BTP Interception Terminal Output */}
            <div className="lg:col-span-6 rounded-xl bg-slate-950 border border-white/10 overflow-hidden shadow-inner flex flex-col">
              <div className="flex items-center justify-between px-4 py-2.5 bg-slate-900/90 border-b border-white/10">
                <div className="flex items-center gap-2">
                  <Terminal size={13} className="text-cyan-400" />
                  <span className="text-[11px] font-mono text-slate-300">btp-engine-interception.log</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                    selectedThreat.verdict === 'BLOCKED'
                      ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                      : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  }`}>
                    {selectedThreat.verdict}
                  </span>
                  <span className="text-[10px] font-mono text-cyan-300">{selectedThreat.latencyUs} µs</span>
                </div>
              </div>
              <div className="p-4 flex-grow font-mono text-xs leading-relaxed overflow-x-auto">
                <div className={`font-bold mb-2 ${selectedThreat.verdict === 'BLOCKED' ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {selectedThreat.ruleHit}
                </div>
                <pre className="text-slate-300 whitespace-pre-wrap">
                  {selectedThreat.terminalLog}
                </pre>
              </div>
              <div className="p-3 bg-slate-900/60 border-t border-white/10 text-[11px] font-mono flex items-center justify-between text-slate-400">
                <span>Guard Layer: <strong className="text-cyan-300">{selectedThreat.interceptedBy}</strong></span>
                <span className="text-emerald-400">● 100% In-Memory Gate</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
