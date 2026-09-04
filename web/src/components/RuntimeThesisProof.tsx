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
    ruleHit: 'RULE_AST_OBFUSCATED_DYNAMIC_IMPORT [CRITICAL]',
    terminalLog: `[00:00:00.032] INTERCEPTED by Bartholomew AST Engine
[00:00:00.032] AST Node: Call -> Attribute(Name='getattr', attr='system')
[00:00:00.032] Constant Folding: 'o' + 's' => 'os'
[00:00:00.032] Invariant Verdict: [DENY] (Destructive OS call blocked)
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
    ruleHit: 'RULE_PATH_CONTAINMENT_BREACH [CRITICAL]',
    terminalLog: `[00:00:00.088] INTERCEPTED by Hermetic Sandbox Boundary
[00:00:00.088] Root Boundary: C:\\Users\\User\\.bartholomew\\workspace
[00:00:00.088] Target Path: C:\\Windows\\System32\\config\\SAM
[00:00:00.088] commonpath Check: [FAILED] (Escaped sandbox root)
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
    ruleHit: 'RULE_SPEND_CAP_EXCEEDED [MAX: $500.00, REQ: $15,000.00]',
    terminalLog: `[00:00:00.028] INTERCEPTED by Policy-as-Code Engine
[00:00:00.028] Policy File: policies/default_security_policy.yaml
[00:00:00.028] Invariant: amount_usd <= 500.00 (Requested: 15000.00)
[00:00:00.028] Verdict: [DENY] (Requires Ed25519 co-signer co-authorization)
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
    ruleHit: 'RULE_ALLOWLISTED_BINARY [ALLOW]',
    terminalLog: `[00:00:00.042] VERIFIED by Bartholomew Invariant Engine
[00:00:00.042] AST Gate: [CLEAN] | Sandbox: [CONTAINED]
[00:00:00.042] RFC 8785 Canonical JSON: Deterministic Hash Generated
[00:00:00.042] Ed25519 Signature: 7e5bf4b7db8fe0a94ac299ec3263d53e...
[00:00:00.042] Execution Status: [SUCCESS] (42.5 µs)`
  }
]

export default function RuntimeThesisProof() {
  const [selectedThreat, setSelectedThreat] = useState<ThreatExample>(THREAT_EXAMPLES[0])

  return (
    <section id="threat-simulator" className="py-24 px-5 sm:px-8 bg-[#040406] text-white border-t border-[#27272a]/70 relative overflow-hidden">
      {/* Top ambient glowing accent line */}
      <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#f59e0b]/70 to-transparent pointer-events-none" />

      {/* Background glow accents */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[700px] h-[300px] bg-gradient-to-b from-[#f59e0b]/10 via-[#10b981]/5 to-transparent blur-[140px] pointer-events-none" />

      <div className="max-w-6xl mx-auto relative z-10">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-[#f59e0b]/10 border border-[#f59e0b]/30 text-[#f59e0b] rounded-full text-xs font-mono font-bold tracking-wider mb-4 shadow-[0_0_15px_rgba(245,158,11,0.15)]">
            <Layers size={13} />
            <span>[ DETERMINISTIC DEFENSE MODEL ]</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white font-sans">
            3 Simple Steps to Complete AI Safety
          </h2>
          <p className="mt-4 text-[#a1a1aa] text-sm sm:text-base leading-relaxed font-sans">
            Instead of hoping an AI behaves, Bartholomew provides a mathematical three-stage defense that guarantees safety on every single tool call.
          </p>
        </div>

        {/* 3 Step Box Cards */}
        <div id="how-it-works" className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <div className="p-7 bg-gradient-to-b from-[#0e0e14]/90 via-[#09090d]/90 to-[#040406] border border-[#27272a]/75 hover:border-[#f59e0b]/50 rounded-2xl flex flex-col justify-between transition-all duration-300 shadow-xl hover:shadow-[0_15px_35px_-10px_rgba(245,158,11,0.15)] group backdrop-blur-md">
            <div>
              <div className="flex items-center justify-between gap-2 mb-4">
                <span className="text-xs font-bold font-mono text-[#f59e0b] uppercase tracking-wider">[STEP 1]</span>
                <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-[#f59e0b]/10 text-[#f59e0b] border border-[#f59e0b]/40">&lt;35 µs</span>
              </div>
              <h3 className="text-lg font-bold text-white mb-2.5 flex items-center gap-2 font-sans group-hover:text-[#f59e0b] transition-colors">
                <Search size={18} className="text-[#f59e0b]" />
                The Pre-Flight Scanner
              </h3>
              <p className="text-xs text-[#a1a1aa] leading-relaxed mb-5 font-sans">
                Before any code runs, the scanner inspects the syntax tree. If the AI is trying to hide a destructive command, drop a database, or exceed spend caps, it is blocked immediately.
              </p>
            </div>
            <div className="text-[11px] font-mono text-[#f59e0b] bg-[#050508] p-3 rounded-xl border border-[#27272a]/70">
              [BLOCKS: DANGEROUS CODE · SQL DROPS · SPEND BREACHES]
            </div>
          </div>

          <div className="p-7 bg-gradient-to-b from-[#0e0e14]/90 via-[#09090d]/90 to-[#040406] border border-[#27272a]/75 hover:border-[#10b981]/50 rounded-2xl flex flex-col justify-between transition-all duration-300 shadow-xl hover:shadow-[0_15px_35px_-10px_rgba(16,185,129,0.15)] group backdrop-blur-md">
            <div>
              <div className="flex items-center justify-between gap-2 mb-4">
                <span className="text-xs font-bold font-mono text-[#10b981] uppercase tracking-wider">[STEP 2]</span>
                <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-[#10b981]/10 text-[#10b981] border border-[#10b981]/40">&lt;150 µs</span>
              </div>
              <h3 className="text-lg font-bold text-white mb-2.5 flex items-center gap-2 font-sans group-hover:text-[#10b981] transition-colors">
                <Box size={18} className="text-[#10b981]" />
                The Locked Sandbox
              </h3>
              <p className="text-xs text-[#a1a1aa] leading-relaxed mb-5 font-sans">
                The AI is confined inside a strict workspace boundary. It is physically impossible for the AI to touch system files, steal sensitive environment secrets, or run unauthorized shell scripts.
              </p>
            </div>
            <div className="text-[11px] font-mono text-[#10b981] bg-[#050508] p-3 rounded-xl border border-[#27272a]/70">
              [BLOCKS: DIRECTORY ESCAPES · CREDENTIAL LEAKS · OS DAMAGE]
            </div>
          </div>

          <div className="p-7 bg-gradient-to-b from-[#0e0e14]/90 via-[#09090d]/90 to-[#040406] border border-[#27272a]/75 hover:border-emerald-400/50 rounded-2xl flex flex-col justify-between transition-all duration-300 shadow-xl hover:shadow-[0_15px_35px_-10px_rgba(16,185,129,0.15)] group backdrop-blur-md">
            <div>
              <div className="flex items-center justify-between gap-2 mb-4">
                <span className="text-xs font-bold font-mono text-[#ffffff] uppercase tracking-wider">[STEP 3]</span>
                <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-[#10b981]/10 text-[#10b981] border border-[#10b981]/40">&lt;40 µs</span>
              </div>
              <h3 className="text-lg font-bold text-white mb-2.5 flex items-center gap-2 font-sans group-hover:text-[#10b981] transition-colors">
                <Award size={18} className="text-[#10b981]" />
                The Digital Notary
              </h3>
              <p className="text-xs text-[#a1a1aa] leading-relaxed mb-5 font-sans">
                Once safe, the action is stamped with a tamper-proof cryptographic signature. Enterprise auditors can verify the digital receipt offline in seconds without trusting third parties.
              </p>
            </div>
            <div className="text-[11px] font-mono text-[#10b981] bg-[#050508] p-3 rounded-xl border border-[#27272a]/70">
              [GUARANTEES: 100% NON-REPUDIATION · COMPLIANCE PROOF]
            </div>
          </div>
        </div>

        {/* Interactive Threat Simulator Split-Pane IDE Preview */}
        <div className="bg-gradient-to-b from-[#0e0e14]/95 via-[#09090d]/95 to-[#050507] border border-[#27272a]/80 rounded-2xl shadow-2xl overflow-hidden relative backdrop-blur-xl">
          <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#f59e0b]/60 to-transparent pointer-events-none" />

          {/* Header Bar */}
          <div className="px-6 py-4 bg-[#111118]/80 border-b border-[#27272a]/70 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="text-xs font-mono text-[#f59e0b] uppercase tracking-wider font-bold flex items-center gap-2">
                <Cpu size={14} />
                <span>[LIVE THREAT SIMULATOR]</span>
              </div>
              <div className="text-sm font-bold text-white mt-1 font-sans">
                Select an attack scenario to watch Bartholomew intercept it in real time:
              </div>
            </div>
          </div>

          {/* Scenario Tabs with Box Borders */}
          <div className="p-3 bg-[#08080c] border-b border-[#27272a]/70 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
            {THREAT_EXAMPLES.map(threat => (
              <button
                key={threat.id}
                onClick={() => setSelectedThreat(threat)}
                className={`p-3.5 text-left transition-all duration-200 font-mono rounded-xl border cursor-pointer ${
                  selectedThreat.id === threat.id
                    ? 'bg-gradient-to-b from-[#1c1c24] to-[#121218] border-[#f59e0b] text-white shadow-[0_0_20px_rgba(245,158,11,0.2)] ring-1 ring-[#f59e0b]/50'
                    : 'bg-[#0a0a0f]/80 border-[#27272a]/60 text-[#a1a1aa] hover:text-[#ffffff] hover:border-[#444455]'
                }`}
              >
                <div className="text-[10px] text-[#f59e0b] uppercase mb-1 font-bold">[{threat.id}]</div>
                <div className="text-xs font-semibold">{threat.title}</div>
              </button>
            ))}
          </div>

          {/* Split-Pane Layout */}
          <div className="p-6 sm:p-8 grid grid-cols-1 lg:grid-cols-12 gap-6 bg-[#060609]">
            {/* Left Pane: Incoming Agent Payload */}
            <div className="lg:col-span-6 bg-[#020204] border border-[#27272a]/80 rounded-xl overflow-hidden flex flex-col shadow-lg">
              <div className="flex items-center justify-between px-4 py-2.5 bg-[#0a0a10] border-b border-[#27272a]/70">
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#ef4444]" />
                  <div className="w-2.5 h-2.5 rounded-full bg-[#f59e0b]" />
                  <div className="w-2.5 h-2.5 rounded-full bg-[#10b981]" />
                </div>
                <span className="text-[11px] font-mono text-[#a1a1aa]">incoming_agent_payload.json</span>
                <span className="text-[10px] font-mono text-[#71717a]">[RAW PAYLOAD]</span>
              </div>
              <div className="p-4 flex-grow">
                <pre className="font-mono text-xs text-[#d4d4d8] leading-relaxed overflow-x-auto whitespace-pre-wrap">
                  {selectedThreat.rawPayload}
                </pre>
              </div>
              <div className="p-3 bg-[#0a0a10] border-t border-[#27272a]/70 text-[11px] text-[#a1a1aa] font-sans">
                {selectedThreat.plainEnglishDescription}
              </div>
            </div>

            {/* Right Pane: BTP Interception Terminal Output */}
            <div className="lg:col-span-6 bg-[#020204] border border-[#27272a]/80 rounded-xl overflow-hidden flex flex-col shadow-lg">
              <div className="flex items-center justify-between px-4 py-2.5 bg-[#0a0a10] border-b border-[#27272a]/70">
                <div className="flex items-center gap-2">
                  <Terminal size={13} className="text-[#f59e0b]" />
                  <span className="text-[11px] font-mono text-[#d4d4d8]">btp-engine-interception.log</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${
                    selectedThreat.verdict === 'BLOCKED'
                      ? 'bg-[#ef4444]/20 text-[#ef4444] border-[#ef4444]/40'
                      : 'bg-[#10b981]/20 text-[#10b981] border-[#10b981]/40'
                  }`}>
                    [{selectedThreat.verdict}]
                  </span>
                  <span className="text-[10px] font-mono text-[#f59e0b]">{selectedThreat.latencyUs} µs</span>
                </div>
              </div>
              <div className="p-4 flex-grow font-mono text-xs leading-relaxed overflow-x-auto">
                <div className={`font-bold mb-2 ${selectedThreat.verdict === 'BLOCKED' ? 'text-[#ef4444]' : 'text-[#10b981]'}`}>
                  {selectedThreat.ruleHit}
                </div>
                <pre className="text-[#a1a1aa] whitespace-pre-wrap">
                  {selectedThreat.terminalLog}
                </pre>
              </div>
              <div className="p-3 bg-[#0a0a10] border-t border-[#27272a]/70 text-[11px] font-mono flex items-center justify-between text-[#a1a1aa]">
                <span>GUARD: <strong className="text-[#ffffff]">{selectedThreat.interceptedBy}</strong></span>
                <span className="text-[#10b981]">[100% IN-PROCESS]</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
