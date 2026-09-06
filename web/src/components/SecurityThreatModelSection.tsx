import { useState } from 'react'
import { ShieldAlert, ShieldCheck, Cpu, ChevronDown, ChevronUp, FileCode, Layers, BookOpen, X, CheckCircle2, Lock, Terminal } from 'lucide-react'

interface FAQItem {
  question: string
  category: 'SUPPLY_CHAIN' | 'ARCHITECTURE' | 'COMPLIANCE' | 'COMPARISON' | 'INTEGRITY'
  shortAnswer: string
  detailedAnswer: string
}

const FAQS: FAQItem[] = [
  {
    question: 'Why avoid piped shell installer scripts (curl | bash or irm | iex)?',
    category: 'SUPPLY_CHAIN',
    shortAnswer: 'Piped shell execution is a supply-chain anti-pattern. We distribute exclusively through standard package registries.',
    detailedAnswer: 'Piping remote scripts directly into a shell execution engine bypasses static scanning and hash verification. Bartholomew is distributed through official package registries: PyPI (pip install btp-guard), npm (npm install btp-guard), standard VS Code VSIX, or direct source clones (git clone) with reproducible CI test gates.'
  },
  {
    question: 'Does Bartholomew require a background proxy daemon (Confused Deputy Risk)?',
    category: 'ARCHITECTURE',
    shortAnswer: 'No. Bartholomew runs 100% in-process as an embedded library with zero daemons, zero sockets, and zero IPC.',
    detailedAnswer: 'Running a local background proxy daemon creates a potential attack surface. Bartholomew is designed as an embedded in-process library. When integrated with LangGraph, CrewAI, or Python scripts, the invariant evaluator executes directly in caller memory in <5.0 microseconds with zero inter-process communication, zero open network sockets, and zero background daemons.'
  },
  {
    question: 'Why not rely solely on Claude Desktop native human confirmation popups?',
    category: 'COMPARISON',
    shortAnswer: 'Native popups fail under alert fatigue, cannot run in unattended swarms, and provide zero cryptographic proof.',
    detailedAnswer: 'Native dialog popups are useful for casual desktop exploration, but break down in production for 4 reasons: (1) Alert Fatigue: Humans blindly click "Allow" after dozens of prompts, missing destructive payloads. (2) Unattended Swarms: High-velocity autonomous agents (LangGraph, AutoGen, CI/CD bots) run thousands of actions/hour where manual clicking is impossible. (3) Absence of Invariant Mathematics: Popups cannot enforce exponential loop decay (LDMU), spend caps, or Coulomb concurrency backoffs. (4) Zero Non-Repudiation: Native popups generate no signed Ed25519 receipts for downstream databases or SOC 2 compliance auditors.'
  },
  {
    question: 'How does Bartholomew protect against supply-chain poisoning in agent dependencies?',
    category: 'INTEGRITY',
    shortAnswer: 'Every trajectory, rule evaluation, and AST decision is cryptographically signed using FIPS 186-5 Ed25519 with nonced receipts.',
    detailedAnswer: 'Bartholomew implements RFC 8785 Canonical JSON (JCS) serialization paired with Ed25519 asymmetric signatures. When an agent attempts an action, Bartholomew computes a deterministic hash of the payload, verifies caller authorization against the local policy graph, and stamps the decision with a nonced, unforgeable cryptographic receipt. Downstream execution environments (MCP servers, database gateways, terminal runners) reject any payload lacking a valid cryptographic stamp.'
  },
  {
    question: 'Is Bartholomew an operating system sandbox replacement (Docker, microVMs, gVisor)?',
    category: 'ARCHITECTURE',
    shortAnswer: 'No. Bartholomew is a Layer-7 in-process semantic tool gate. It is designed to be paired with container sandboxes, not replace OS kernel isolation.',
    detailedAnswer: 'Operating system sandboxes (Docker, Firecracker, gVisor) provide essential kernel-level process and hardware isolation. However, an agent running inside a container can still drop its own production database, burn thousands of dollars in runaway API loops, or exfiltrate API keys. Bartholomew operates at the application runtime layer, intercepting tool dispatches in <2.3µs before commands hit the OS. For full production defense-in-depth, always run Bartholomew-protected agents inside isolated container environments.'
  },
  {
    question: 'How does static AST parsing handle dynamic evaluation (eval, exec, reflection) and rule maintenance?',
    category: 'ARCHITECTURE',
    shortAnswer: 'Dynamic evaluation sinks (eval, exec) are blocked as high-entropy invariant violations; policies come with pre-packaged declarative defaults.',
    detailedAnswer: 'Rather than attempting probabilistic guesswork on arbitrary runtime strings, Bartholomew treats un-gated dynamic code execution (eval, exec, runtime __import__ reflection) as an immediate invariant violation. This prevents obfuscated code from evading AST scrutiny. For policy management, Bartholomew ships with pre-configured default rule sets (rules-controller.yaml) covering standard database mutations, secret scrubbing, and loop damping so teams do not need to maintain brittle custom rule sets from scratch.'
  }
]

export default function SecurityThreatModelSection() {
  const [activeFaq, setActiveFaq] = useState<number | null>(0)
  const [showInlineWhitepaper, setShowInlineWhitepaper] = useState<boolean>(false)
  const [activeTab, setActiveTab] = useState<'architecture' | 'threat_model' | 'crypto' | 'enterprise' | 'landscape'>('architecture')

  const toggleFAQ = (idx: number) => {
    setActiveFaq(activeFaq === idx ? null : idx)
  }

  return (
    <section id="threat-model" className="py-24 px-5 sm:px-8 bg-gradient-to-b from-[#040406] via-[#08080c] to-[#040406] text-white border-t border-[#1f1f23] relative overflow-hidden">
      {/* Ambient background glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-[#10b981]/5 blur-[150px] pointer-events-none" />

      <div className="max-w-7xl mx-auto relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 bg-[#10b981]/10 border border-[#10b981]/30 text-xs font-mono font-bold uppercase tracking-wider text-[#10b981] mb-4 rounded-full">
            <ShieldAlert size={14} className="text-[#10b981]" />
            <span>THREAT MODEL &amp; SUPPLY CHAIN GOVERNANCE</span>
          </div>
          <h2 className="text-2xl sm:text-4xl font-bold font-sans tracking-tight mb-4 text-white">
            Designed for Zero-Trust Agent Operations
          </h2>
          <p className="text-sm sm:text-base text-[#a1a1aa] font-sans">
            How Bartholomew addresses supply-chain poisoning, confused deputy risks, and autonomous execution safety.
          </p>
        </div>

        {/* 4 Architectural Pillar Cards - Frontier Glassmorphism */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          <div className="p-6 rounded-2xl bg-gradient-to-b from-[#0e0e12]/90 via-[#08080a]/90 to-[#040405] border border-[#27272a]/70 hover:border-[#10b981]/50 hover:shadow-[0_0_25px_rgba(16,185,129,0.15)] transition-all duration-300 relative overflow-hidden group">
            <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#10b981]/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="flex items-center gap-2.5 text-sm font-mono font-bold text-white mb-2">
              <ShieldCheck size={16} className="text-[#10b981]" />
              <span>ZERO INJECTION ESCAPES</span>
            </div>
            <p className="text-xs text-[#a1a1aa] font-sans leading-relaxed">
              Sub-2.3 µs deterministic AST invariant checking blocks catastrophic shell patterns (rm -rf, DROP TABLE) in-memory before OS dispatch.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-gradient-to-b from-[#0e0e12]/90 via-[#08080a]/90 to-[#040405] border border-[#27272a]/70 hover:border-[#a855f7]/50 hover:shadow-[0_0_25px_rgba(168,85,247,0.15)] transition-all duration-300 relative overflow-hidden group">
            <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#a855f7]/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="flex items-center gap-2.5 text-sm font-mono font-bold text-white mb-2">
              <Cpu size={16} className="text-[#a855f7]" />
              <span>IN-PROCESS ZERO IPC</span>
            </div>
            <p className="text-xs text-[#a1a1aa] font-sans leading-relaxed">
              Direct caller memory execution with zero open sockets, zero daemon vulnerabilities, and zero IPC overhead.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-gradient-to-b from-[#0e0e12]/90 via-[#08080a]/90 to-[#040405] border border-[#27272a]/70 hover:border-[#f59e0b]/50 hover:shadow-[0_0_25px_rgba(245,158,11,0.15)] transition-all duration-300 relative overflow-hidden group">
            <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#f59e0b]/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="flex items-center gap-2.5 text-sm font-mono font-bold text-white mb-2">
              <FileCode size={16} className="text-[#f59e0b]" />
              <span>VERIFIED PACKAGE REGISTRIES</span>
            </div>
            <p className="text-xs text-[#a1a1aa] font-sans leading-relaxed">
              Distributed officially via npm (npm install btp-guard), PyPI, and standard VS Code VSIX. No raw shell script piping.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-gradient-to-b from-[#0e0e12]/90 via-[#08080a]/90 to-[#040405] border border-[#27272a]/70 hover:border-[#38bdf8]/50 hover:shadow-[0_0_25px_rgba(56,189,248,0.15)] transition-all duration-300 relative overflow-hidden group">
            <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#38bdf8]/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="flex items-center gap-2.5 text-sm font-mono font-bold text-white mb-2">
              <Layers size={16} className="text-[#38bdf8]" />
              <span>CONTAINER &amp; K8S NATIVE</span>
            </div>
            <p className="text-xs text-[#a1a1aa] font-sans leading-relaxed">
              Complements Docker and Kubernetes namespaces with fine-grained semantic invariant gating inside container runtimes.
            </p>
          </div>
        </div>

        {/* Accordion FAQ List */}
        <div className="space-y-4 max-w-4xl mx-auto mb-12">
          {FAQS.map((item, index) => {
            const isOpen = activeFaq === index
            return (
              <div
                key={index}
                className={`rounded-xl border transition-all duration-200 overflow-hidden ${
                  isOpen
                    ? 'bg-gradient-to-b from-[#0e0e13] to-[#08080b] border-[#10b981]/50 shadow-[0_0_20px_rgba(16,185,129,0.12)]'
                    : 'bg-[#09090c]/80 border-[#27272a]/70 hover:border-[#3f3f46]'
                }`}
              >
                <button
                  onClick={() => toggleFAQ(index)}
                  className="w-full p-5 text-left flex items-center justify-between gap-4 transition cursor-pointer"
                >
                  <div className="flex items-start sm:items-center gap-3">
                    <span className="text-xs font-mono font-bold text-[#10b981] px-2.5 py-0.5 rounded bg-[#10b981]/10 border border-[#10b981]/30 shrink-0">
                      [{item.category}]
                    </span>
                    <span className="text-sm sm:text-base font-bold text-white font-sans">
                      {item.question}
                    </span>
                  </div>
                  <div className="text-[#a1a1aa] shrink-0">
                    {isOpen ? <ChevronUp size={18} className="text-[#10b981]" /> : <ChevronDown size={18} />}
                  </div>
                </button>

                {isOpen && (
                  <div className="px-5 pb-6 pt-2 border-t border-[#1f1f23] bg-[#040406] space-y-3">
                    <div className="p-3 bg-[#0a0a0d] border border-[#10b981]/30 rounded-lg font-mono text-xs text-[#10b981]">
                      SUMMARY: {item.shortAnswer}
                    </div>
                    <p className="text-xs sm:text-sm text-[#d4d4d8] font-sans leading-relaxed">
                      {item.detailedAnswer}
                    </p>
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* Action Controls: Inline White Paper Viewer & Standalone Specs */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <button
            onClick={() => setShowInlineWhitepaper(!showInlineWhitepaper)}
            className="inline-flex items-center gap-2 px-6 py-3 bg-[#10b981] hover:bg-[#059669] text-black font-mono text-xs font-bold rounded-lg transition shadow-[0_0_20px_rgba(16,185,129,0.3)] cursor-pointer"
          >
            <BookOpen size={15} />
            <span>{showInlineWhitepaper ? '[ HIDE INLINE SPECIFICATION ]' : '[ EXPAND FULL ONLINE WHITE PAPER ]'}</span>
          </button>
          
          <a
            href="/SECURITY_WHITE_PAPER_AND_THREAT_MODEL.html"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 px-5 py-3 bg-[#f59e0b]/10 hover:bg-[#f59e0b]/20 text-[#f59e0b] border border-[#f59e0b]/30 font-mono text-xs font-bold rounded-lg transition"
          >
            <FileCode size={14} />
            <span>[ OPEN STANDALONE HTML ]</span>
          </a>
          
          <a
            href="/SECURITY_WHITE_PAPER_AND_THREAT_MODEL.md"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 px-5 py-3 bg-[#0a0a0a] hover:bg-[#141414] text-[#a1a1aa] hover:text-white border border-[#333333] font-mono text-xs font-bold rounded-lg transition"
          >
            <FileCode size={14} />
            <span>[ RAW SPEC (.MD) ]</span>
          </a>
        </div>

        {/* Expanded Inline White Paper & Threat Model Specification */}
        {showInlineWhitepaper && (
          <div className="mt-10 p-6 sm:p-10 bg-[#0a0a0a] border border-[#10b981]/40 rounded-2xl shadow-2xl relative animate-in fade-in duration-300">
            <div className="flex items-center justify-between pb-6 border-b border-[#222222] mb-6">
              <div className="flex items-center gap-3">
                <BookOpen size={20} className="text-[#10b981]" />
                <div>
                  <h3 className="text-lg sm:text-xl font-bold text-white font-sans">
                    Bartholomew Trust Protocol — Online Architecture &amp; Threat Model Spec
                  </h3>
                  <p className="text-xs font-mono text-[#a1a1aa]">
                    Protocol Version: BTP/5.4.0 &bull; Sovereign Trust &amp; Settlement Protocol &bull; FIPS 186-5 Ed25519 &bull; RFC 8785 JCS
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowInlineWhitepaper(false)}
                className="p-2 text-[#71717a] hover:text-white rounded-lg hover:bg-[#1a1a1a] transition"
              >
                <X size={18} />
              </button>
            </div>

            {/* Spec Tabs */}
            <div className="flex flex-wrap gap-2 mb-8 border-b border-[#1c1c1c] pb-3 font-mono text-xs">
              <button
                onClick={() => setActiveTab('architecture')}
                className={`px-4 py-2 rounded-lg transition font-bold ${activeTab === 'architecture' ? 'bg-[#10b981] text-black' : 'bg-[#111111] text-[#a1a1aa] hover:text-white'}`}
              >
                [1. Kernel Architecture]
              </button>
              <button
                onClick={() => setActiveTab('threat_model')}
                className={`px-4 py-2 rounded-lg transition font-bold ${activeTab === 'threat_model' ? 'bg-[#10b981] text-black' : 'bg-[#111111] text-[#a1a1aa] hover:text-white'}`}
              >
                [2. Adversarial Threat Model]
              </button>
              <button
                onClick={() => setActiveTab('crypto')}
                className={`px-4 py-2 rounded-lg transition font-bold ${activeTab === 'crypto' ? 'bg-[#10b981] text-black' : 'bg-[#111111] text-[#a1a1aa] hover:text-white'}`}
              >
                [3. Cryptographic Receipts]
              </button>
              <button
                onClick={() => setActiveTab('enterprise')}
                className={`px-4 py-2 rounded-lg transition font-bold ${activeTab === 'enterprise' ? 'bg-[#10b981] text-black' : 'bg-[#111111] text-[#a1a1aa] hover:text-white'}`}
              >
                [4. Enterprise &amp; SIEM Roadmap]
              </button>
              <button
                onClick={() => setActiveTab('landscape')}
                className={`px-4 py-2 rounded-lg transition font-bold ${activeTab === 'landscape' ? 'bg-[#10b981] text-black' : 'bg-[#111111] text-[#a1a1aa] hover:text-white'}`}
              >
                [5. Industry Landscape &amp; Defense-in-Depth]
              </button>
            </div>

            {/* Tab Contents */}
            <div className="font-sans text-sm text-[#d4d4d8] leading-relaxed space-y-6">
              {activeTab === 'architecture' && (
                <div className="space-y-4">
                  <h4 className="text-base font-bold text-white font-mono flex items-center gap-2">
                    <Terminal size={16} className="text-[#10b981]" />
                    <span>Three-Step Execution Invariant Pipeline</span>
                  </h4>
                  <p>
                    Bartholomew enforces strict pre-flight transactional safety across three synchronous stages executed entirely in caller memory without subprocess forks:
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
                    <div className="p-4 bg-[#050505] border border-[#222222] rounded-xl space-y-2">
                      <span className="text-[#f59e0b] font-bold block">STEP 1: THE FIREWALL</span>
                      <p className="text-[#a1a1aa]">Deterministic polyglot AST constant folding, secret scrubbing, and prompt injection syntax verification in &lt;1.8 µs.</p>
                    </div>
                    <div className="p-4 bg-[#050505] border border-[#222222] rounded-xl space-y-2">
                      <span className="text-[#06b6d4] font-bold block">STEP 2: THE SANDBOX</span>
                      <p className="text-[#a1a1aa]">Copy-on-Write (CoW) micro-snapshots capturing workspace state, providing instant auto-rollback in &lt;3.8 ms on assertion failure.</p>
                    </div>
                    <div className="p-4 bg-[#050505] border border-[#222222] rounded-xl space-y-2">
                      <span className="text-[#10b981] font-bold block">STEP 3: THE DIGITAL NOTARY</span>
                      <p className="text-[#a1a1aa]">RFC 8785 canonical JSON serialization signed with FIPS 186-5 Ed25519 sovereign keypairs, emitting non-repudiable audit receipts.</p>
                    </div>
                  </div>
                  <p className="text-xs text-[#a1a1aa]">
                    Mathematical throughput benchmark: <strong>854,000 to 1,050,000 evaluations per second</strong> on single-core commodity hardware with sub-5 microsecond p99 latency.
                  </p>
                </div>
              )}

              {activeTab === 'threat_model' && (
                <div className="space-y-4">
                  <h4 className="text-base font-bold text-white font-mono flex items-center gap-2">
                    <Lock size={16} className="text-[#ef4444]" />
                    <span>OWASP Top 10 for Agentic AI Mitigation Matrix</span>
                  </h4>
                  <div className="space-y-3 font-mono text-xs">
                    <div className="p-3 bg-[#050505] border border-[#ef4444]/30 rounded-lg">
                      <span className="text-[#ef4444] font-bold">LLM01: Prompt Injection &amp; Indirect Exfiltration:</span>
                      <p className="text-[#a1a1aa] mt-1 font-sans">
                        Mitigated by invariant AST compilation before tool execution. Even if LLM output instructs a system shell call, constant-folded AST heuristics veto the syscall at the language compiler level.
                      </p>
                    </div>
                    <div className="p-3 bg-[#050505] border border-[#f59e0b]/30 rounded-lg">
                      <span className="text-[#f59e0b] font-bold">LLM06: Excessive Agency &amp; Runaway Loops:</span>
                      <p className="text-[#a1a1aa] mt-1 font-sans">
                        Governed by the Law of Diminishing Marginal Utility: <code>Utility = U₀ &times; (1 - &lambda;)ⁿ</code>. Recursive retries without marginal progress trigger hard execution halts when utility drops below 0.150.
                      </p>
                    </div>
                    <div className="p-3 bg-[#050505] border border-[#a855f7]/30 rounded-lg">
                      <span className="text-[#a855f7] font-bold">LLM07: System Information &amp; Credential Leakage:</span>
                      <p className="text-[#a1a1aa] mt-1 font-sans">
                        In-flight SecretVaultMasker continuously scans outbound tool arguments for API tokens (AWS, GitHub PATs, OpenAI, Slack) and automatically applies zero-copy redactions before network socket dispatch.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'crypto' && (
                <div className="space-y-4">
                  <h4 className="text-base font-bold text-white font-mono flex items-center gap-2">
                    <CheckCircle2 size={16} className="text-[#10b981]" />
                    <span>Deterministic Attestation &amp; Cryptographic Receipts</span>
                  </h4>
                  <p>
                    Every evaluated agent action generates an immutable Merkle receipt conforming to RFC 8785 (JSON Canonicalization Scheme) signed with Ed25519:
                  </p>
                  <pre className="p-4 bg-[#050505] border border-[#222222] rounded-xl font-mono text-xs text-[#10b981] overflow-x-auto">
{`{
  "protocol": "BTP/5.4.0",
  "timestamp": "2026-09-04T02:00:00Z",
  "agent_id": "swe-bench-agent-01",
  "action_type": "POSTGRES_EXECUTE",
  "payload_digest": "sha256:1fecf61c323bb6890bbd778981111b17...",
  "attestation": {
    "verdict": "DENY",
    "rule_id": "BTP-INV-003",
    "reason": "Destructive DDL statement intercepted: DROP TABLE"
  },
  "signature": "ed25519:7a4b89f02c418e99d3e810a9c8f2b740529d8174..."
}`}
                  </pre>
                  <p className="text-xs text-[#a1a1aa]">
                    Any downstream database gateway or MCP server can verify this signature independently in local memory with zero cloud dependencies.
                  </p>
                </div>
              )}

              {activeTab === 'enterprise' && (
                <div className="space-y-4">
                  <h4 className="text-base font-bold text-white font-mono flex items-center gap-2">
                    <Layers size={16} className="text-[#38bdf8]" />
                    <span>Enterprise Key Management, SIEM &amp; Dynamic Sync</span>
                  </h4>
                  <ul className="list-disc pl-5 space-y-2 text-xs text-[#a1a1aa]">
                    <li><strong>Dynamic Policy Synchronization (<code>btp sync</code>)</strong>: Push updated safety rules to running agent fleets without container restarts via atomic in-memory swap.</li>
                    <li><strong>Asynchronous SIEM Streaming</strong>: Zero-blocking batch streaming to Splunk HEC, Datadog Logs, and AWS CloudWatch with local encrypted disk spooling fail-safe.</li>
                    <li><strong>HSM &amp; KMS Delegation</strong>: Support for AWS KMS, GCP Cloud KMS, and HashiCorp Vault for institutional root-of-trust rotation.</li>
                    <li><strong>Kernel-Level Sandbox Containment</strong>: Hard limits enforced via Linux namespaces (<code>unshare</code>), cgroups v2, and eBPF syscall filtering.</li>
                  </ul>
                </div>
              )}

              {activeTab === 'landscape' && (
                <div className="space-y-5">
                  <h4 className="text-base font-bold text-white font-mono flex items-center gap-2">
                    <ShieldCheck size={16} className="text-[#10b981]" />
                    <span>Industry Landscape &amp; Defense-in-Depth Model</span>
                  </h4>
                  <p className="text-xs sm:text-sm text-[#a1a1aa] leading-relaxed">
                    Most security frameworks in the AI industry operate from <em>outside</em> the local runtime process—typically as external HTTP proxies or secondary LLM classification calls. Bartholomew is purpose-built for the sub-50µs in-process tool execution boundary.
                  </p>

                  {/* Comparative Matrix Table */}
                  <div className="overflow-x-auto border border-[#222222] rounded-xl bg-[#050505]">
                    <table className="w-full text-left font-mono text-xs">
                      <thead>
                        <tr className="border-b border-[#222222] bg-[#0c0c10] text-[#a1a1aa]">
                          <th className="p-3">Dimension</th>
                          <th className="p-3">Standard AI Guardrails (NeMo, Guardrails AI, LlamaGuard)</th>
                          <th className="p-3 text-[#10b981]">Bartholomew Protocol (BTP v3.0)</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#1c1c1c] text-[#d4d4d8]">
                        <tr>
                          <td className="p-3 font-bold text-white">Primary Target</td>
                          <td className="p-3 text-[#a1a1aa]">Natural language text, PII, and conversational topics</td>
                          <td className="p-3 text-[#10b981]">Raw tool arguments, local AST structures, and filesystem actions</td>
                        </tr>
                        <tr>
                          <td className="p-3 font-bold text-white">Latency Profile</td>
                          <td className="p-3 text-[#a1a1aa]">~80ms to 2,500ms (secondary LLM classification calls)</td>
                          <td className="p-3 text-[#10b981]">&lt;35 microseconds (in-process static analysis &amp; constant folding)</td>
                        </tr>
                        <tr>
                          <td className="p-3 font-bold text-white">Deployment Mode</td>
                          <td className="p-3 text-[#a1a1aa]">Cloud APIs, HTTP proxy sidecars, or microservices</td>
                          <td className="p-3 text-[#10b981]">In-memory FFI library (<code>pip install btp-guard</code> / <code>npm i btp-guard</code>)</td>
                        </tr>
                        <tr>
                          <td className="p-3 font-bold text-white">Verification</td>
                          <td className="p-3 text-[#a1a1aa]">Mutable text logs and unstructured JSON output</td>
                          <td className="p-3 text-[#10b981]">Cryptographic RFC 8785 Ed25519 signatures and ZK-proof receipts</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  {/* Defense in Depth 3-Layer Stack */}
                  <div className="p-4 bg-[#08080c] border border-[#222222] rounded-xl space-y-2">
                    <span className="font-mono text-xs font-bold text-[#f59e0b] block uppercase tracking-wider">
                      [ The Unified 3-Layer Defense-in-Depth Architecture ]
                    </span>
                    <p className="text-xs text-[#a1a1aa] leading-relaxed">
                      Enterprise AI architectures converge on layered safety:
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs pt-1">
                      <div className="p-3 bg-[#050505] border border-[#1a1a24] rounded-lg">
                        <span className="text-[#38bdf8] font-bold block mb-1">Layer 1: External Dialog</span>
                        <p className="text-[#71717a]">NeMo / LlamaGuard handles conversational tone, user sentiment, and high-level dialogue rules.</p>
                      </div>
                      <div className="p-3 bg-[#050505] border border-[#10b981]/40 rounded-lg">
                        <span className="text-[#10b981] font-bold block mb-1">Layer 2: Local Memory Invariant Gate</span>
                        <p className="text-[#a1a1aa]">Bartholomew provides the fastest and most reliable local AST safety gating against destructive commands (rm -rf, DROP TABLE), API keys, and loops.</p>
                      </div>
                      <div className="p-3 bg-[#050505] border border-[#1a1a24] rounded-lg">
                        <span className="text-[#a855f7] font-bold block mb-1">Layer 3: OS Container</span>
                        <p className="text-[#71717a]">Docker / microVMs provide kernel-level network isolation and host filesystem boundaries.</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

      </div>
    </section>
  )
}
