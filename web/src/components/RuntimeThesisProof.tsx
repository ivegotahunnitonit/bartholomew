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
    <section id="threat-simulator" className="py-24 px-5 sm:px-8 bg-black text-white border-t border-[#222222]">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-[#0a0a0a] border border-[#2a2a2a] text-[#f59e0b] text-xs sm:text-sm font-mono font-bold uppercase tracking-wider mb-3">
            <Layers size={14} />
            <span>[ DETERMINISTIC DEFENSE MODEL ]</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white font-sans">
            3 Simple Steps to Complete AI Safety
          </h2>
          <p className="mt-3 text-[#d4d4d8] text-base leading-relaxed font-sans">
            Instead of hoping an AI behaves, Bartholomew provides a mathematical three-stage defense that guarantees safety on every single tool call.
          </p>
        </div>

        {/* 3 Step Box Cards */}
        <div id="how-it-works" className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <div className="p-6 bg-[#0a0a0a] border border-[#262626] flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between gap-2 mb-3">
                <span className="text-xs sm:text-sm font-bold font-mono text-[#f59e0b] uppercase tracking-wider">[STEP 1]</span>
                <span className="text-xs font-mono px-2 py-0.5 bg-[#000000] text-[#f59e0b] border border-[#f59e0b]/40">&lt;35 µs</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-2 font-sans">
                <Search size={18} className="text-[#f59e0b]" />
                The Pre-Flight Scanner
              </h3>
              <p className="text-sm text-[#d4d4d8] leading-relaxed mb-4 font-sans">
                Before any code runs, the scanner inspects the syntax tree. If the AI is trying to hide a destructive command, drop a database, or exceed spend caps, it is blocked immediately.
              </p>
            </div>
            <div className="text-xs font-mono text-[#f59e0b] bg-[#000000] p-3 border border-[#202020] font-semibold">
              [BLOCKS: DANGEROUS CODE · SQL DROPS · SPEND BREACHES]
            </div>
          </div>

          <div className="p-6 bg-[#0a0a0a] border border-[#262626] flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between gap-2 mb-3">
                <span className="text-xs sm:text-sm font-bold font-mono text-[#10b981] uppercase tracking-wider">[STEP 2]</span>
                <span className="text-xs font-mono px-2 py-0.5 bg-[#000000] text-[#10b981] border border-[#10b981]/40">&lt;150 µs</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-2 font-sans">
                <Box size={18} className="text-[#10b981]" />
                The Locked Sandbox
              </h3>
              <p className="text-sm text-[#d4d4d8] leading-relaxed mb-4 font-sans">
                The AI is confined inside a strict workspace boundary. It is physically impossible for the AI to touch system files, steal sensitive environment secrets, or run unauthorized shell scripts.
              </p>
            </div>
            <div className="text-xs font-mono text-[#10b981] bg-[#000000] p-3 border border-[#202020] font-semibold">
              [BLOCKS: DIRECTORY ESCAPES · CREDENTIAL LEAKS · OS DAMAGE]
            </div>
          </div>

          <div className="p-6 bg-[#0a0a0a] border border-[#262626] flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between gap-2 mb-3">
                <span className="text-xs sm:text-sm font-bold font-mono text-[#ffffff] uppercase tracking-wider">[STEP 3]</span>
                <span className="text-xs font-mono px-2 py-0.5 bg-[#000000] text-[#ffffff] border border-[#ffffff]/40">&lt;40 µs</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-2 font-sans">
                <Award size={18} className="text-[#10b981]" />
                The Digital Notary
              </h3>
              <p className="text-sm text-[#d4d4d8] leading-relaxed mb-4 font-sans">
                Once safe, the action is stamped with a tamper-proof cryptographic signature. Enterprise auditors can verify the digital receipt offline in seconds without trusting third parties.
              </p>
            </div>
            <div className="text-xs font-mono text-[#10b981] bg-[#000000] p-3 border border-[#202020] font-semibold">
              [GUARANTEES: 100% NON-REPUDIATION · COMPLIANCE PROOF]
            </div>
          </div>
        </div>

        {/* Interactive Threat Simulator Split-Pane IDE Preview */}
        <div className="bg-[#0a0a0a] border border-[#262626] shadow-2xl overflow-hidden">
          {/* Header Bar */}
          <div className="px-6 py-4 bg-[#000000] border-b border-[#262626] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="text-xs sm:text-sm font-mono text-[#f59e0b] uppercase tracking-wider font-bold flex items-center gap-2">
                <Cpu size={15} />
                <span>[LIVE THREAT SIMULATOR]</span>
              </div>
              <div className="text-base font-bold text-white mt-1 font-sans">
                Select an attack scenario to watch Bartholomew intercept it in real time:
              </div>
            </div>
          </div>

          {/* Scenario Tabs with Box Borders */}
          <div className="p-3.5 bg-[#000000] border-b border-[#262626] grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
            {THREAT_EXAMPLES.map(threat => (
              <button
                key={threat.id}
                onClick={() => setSelectedThreat(threat)}
                className={`p-3.5 text-left transition font-mono border ${
                  selectedThreat.id === threat.id
                    ? 'bg-[#161616] border-[#f59e0b] text-white shadow-md'
                    : 'bg-[#0a0a0a] border-[#262626] text-[#c4c4cc] hover:text-[#ffffff] hover:border-[#444444]'
                }`}
              >
                <div className="text-xs text-[#f59e0b] uppercase mb-1 font-bold">[{threat.id}]</div>
                <div className="text-xs sm:text-sm font-semibold">{threat.title}</div>
              </button>
            ))}
          </div>

          {/* Split-Pane Layout */}
          <div className="p-6 sm:p-8 grid grid-cols-1 lg:grid-cols-12 gap-6 bg-[#0a0a0a]">
            {/* Left Pane: Incoming Agent Payload */}
            <div className="lg:col-span-6 bg-[#000000] border border-[#262626] overflow-hidden flex flex-col">
              <div className="flex items-center justify-between px-4 py-2.5 bg-[#0a0a0a] border-b border-[#262626]">
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 bg-[#ef4444]" />
                  <div className="w-2.5 h-2.5 bg-[#f59e0b]" />
                  <div className="w-2.5 h-2.5 bg-[#10b981]" />
                </div>
                <span className="text-xs font-mono text-[#d4d4d8] font-semibold">incoming_agent_payload.json</span>
                <span className="text-xs font-mono text-[#9ca3af]">[RAW PAYLOAD]</span>
              </div>
              <div className="p-4 sm:p-5 flex-grow">
                <pre className="font-mono text-xs sm:text-sm text-[#e4e4e7] leading-relaxed overflow-x-auto whitespace-pre-wrap">
                  {selectedThreat.rawPayload}
                </pre>
              </div>
              <div className="p-3.5 bg-[#0a0a0a] border-t border-[#262626] text-xs sm:text-sm text-[#d4d4d8] font-sans">
                {selectedThreat.plainEnglishDescription}
              </div>
            </div>

            {/* Right Pane: BTP Interception Terminal Output */}
            <div className="lg:col-span-6 bg-[#000000] border border-[#262626] overflow-hidden flex flex-col">
              <div className="flex items-center justify-between px-4 py-2.5 bg-[#0a0a0a] border-b border-[#262626]">
                <div className="flex items-center gap-2">
                  <Terminal size={14} className="text-[#f59e0b]" />
                  <span className="text-xs font-mono text-[#e4e4e7] font-semibold">btp-engine-interception.log</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-mono font-bold px-2 py-0.5 border ${
                    selectedThreat.verdict === 'BLOCKED'
                      ? 'bg-[#ef4444]/20 text-[#ef4444] border-[#ef4444]/40'
                      : 'bg-[#10b981]/20 text-[#10b981] border-[#10b981]/40'
                  }`}>
                    [{selectedThreat.verdict}]
                  </span>
                  <span className="text-xs font-mono text-[#f59e0b] font-semibold">{selectedThreat.latencyUs} µs</span>
                </div>
              </div>
              <div className="p-4 sm:p-5 flex-grow font-mono text-xs sm:text-sm leading-relaxed overflow-x-auto">
                <div className={`font-bold mb-2.5 ${selectedThreat.verdict === 'BLOCKED' ? 'text-[#ef4444]' : 'text-[#10b981]'}`}>
                  {selectedThreat.ruleHit}
                </div>
                <pre className="text-[#d4d4d8] whitespace-pre-wrap">
                  {selectedThreat.terminalLog}
                </pre>
              </div>
              <div className="p-3.5 bg-[#0a0a0a] border-t border-[#262626] text-xs sm:text-sm font-mono flex items-center justify-between text-[#d4d4d8]">
                <span>GUARD: <strong className="text-[#ffffff]">{selectedThreat.interceptedBy}</strong></span>
                <span className="text-[#10b981] font-semibold">[100% IN-PROCESS]</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
