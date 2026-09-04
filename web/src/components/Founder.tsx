import { useState } from 'react'
import { ExternalLink, Code2, Mail, ShieldCheck, FileText, Globe, Layers } from 'lucide-react'

interface VersionMilestone {
  version: string
  timeline: string
  title: string
  status: 'LIVE' | 'IN DEVELOPMENT' | 'PLANNED'
  highlights: string[]
}

const UPCOMING_MILESTONES: VersionMilestone[] = [
  {
    version: 'BTP v2.5.0',
    timeline: 'CURRENT RELEASE',
    status: 'LIVE',
    title: 'Framework Interoperability & Stateful Guard',
    highlights: [
      'Native adapters for LangChain, CrewAI, AutoGen, and LlamaIndex.',
      'Stateful multi-turn session guard tracking fragmented prompt injection across turns.',
      'Non-Human Identity (NHI) Ed25519 governance with automated revocation certificates.',
      'Asynchronous batch SIEM export (Datadog v2, Splunk HEC, AWS CloudWatch).'
    ]
  },
  {
    version: 'BTP v2.6.0',
    timeline: 'Q4 2026',
    status: 'IN DEVELOPMENT',
    title: 'Kernel eBPF Sandboxing & Confidential Enclaves',
    highlights: [
      'Linux eBPF kernel probes trapping agent file/network mutations with zero userspace context-switch overhead.',
      'Hardware-attested confidential computing deployment for AWS Nitro and GCP Confidential VMs.',
      'Dynamic memory bounds preventing Denial-of-Memory agent heap exhaustion attacks.'
    ]
  },
  {
    version: 'BTP v2.7.0',
    timeline: 'Q1 2027',
    status: 'PLANNED',
    title: 'Cross-Cloud Swarm Byzantine Quorum',
    highlights: [
      'Byzantine Fault Tolerant (BFT) consensus protocol for autonomous multi-agent swarm fleets.',
      'Cross-organization capability negotiation and multi-signature authorization thresholds.',
      'Global privacy-preserving threat intelligence federation via k-anonymity hash synchronization.'
    ]
  },
  {
    version: 'BTP v3.0.0',
    timeline: '2027 FRONTIER',
    status: 'PLANNED',
    title: 'Zero-Knowledge Compliance Proofs (zk-SNARK)',
    highlights: [
      'Generate succinct zk-SNARK cryptographic proofs of policy adherence without exposing proprietary prompt context.',
      'Auditors and regulators verify complete regulatory compliance without viewing confidential enterprise data.',
      'Autonomous on-chain and off-chain execution receipt verification with sub-millisecond check times.'
    ]
  }
]

export default function Founder() {
  const [selectedMilestone, setSelectedMilestone] = useState<number>(0)

  return (
    <section id="founder" className="py-24 px-5 sm:px-8 bg-black text-white border-t border-[#1c1c1c]">
      <div className="max-w-6xl mx-auto">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#0a0a0a] border border-[#222222] text-[#10b981] text-xs font-mono font-bold uppercase tracking-wider mb-3">
            <ShieldCheck size={13} />
            <span>[ OPERATIONAL TRANSPARENCY &amp; ROADMAP ]</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white font-sans">
            Founder Perspective &amp; Architectural Roadmap
          </h2>
          <p className="mt-3 text-[#a1a1aa] text-sm sm:text-base font-sans">
            Bartholomew is engineered from first principles as an independent, deterministic execution substrate. Here is our thesis for BTP v2.5.0 and our roadmap for future agent runtimes.
          </p>
        </div>

        {/* Founder Card */}
        <div className="rounded-xl p-8 md:p-10 bg-[#0a0a0a] border border-[#222222] shadow-2xl relative overflow-hidden flex flex-col md:flex-row items-center md:items-start gap-8 mb-12">
          
          {/* Avatar with fallback */}
          <div className="shrink-0">
            <div className="relative inline-block">
              <img
                src="/founder_avatar.jpg"
                alt="Itsub Alemayehu - Founder & Lead Architect"
                className="w-32 h-32 rounded-full object-cover border-2 border-[#10b981] shadow-[0_0_25px_rgba(16,185,129,0.25)] cursor-pointer"
                onClick={() => window.open('/founder_avatar.jpg', '_blank')}
                onError={(e) => {
                  const img = e.target as HTMLImageElement
                  img.onerror = null
                  img.src = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='128' height='128' viewBox='0 0 24 24' fill='none' stroke='%2310b981' stroke-width='1.5'%3E%3Ccircle cx='12' cy='8' r='5'/%3E%3Cpath d='M20 21a8 8 0 0 0-16 0'/%3E%3C/svg%3E`
                }}
              />
              <span className="absolute bottom-1 right-1 w-4 h-4 bg-[#10b981] border-2 border-black rounded-full" title="Active Core Engineer" />
            </div>
          </div>

          {/* Details & Founder Statement */}
          <div className="flex-1 text-center md:text-left space-y-4">
            <div>
              <div className="flex flex-wrap items-center justify-center md:justify-start gap-2.5 mb-1">
                <h3 className="text-2xl font-bold text-white font-sans">Itsub Alemayehu</h3>
                <span className="px-2 py-0.5 bg-[#10b981]/10 text-[#10b981] border border-[#10b981]/30 font-mono text-[11px] font-bold">
                  FOUNDER &amp; LEAD ARCHITECT
                </span>
              </div>
              <p className="text-xs font-mono text-[#f59e0b]">
                Autonomous Systems Laboratory &bull; Bartholomew Trust Protocol Lead
              </p>
            </div>

            <div className="space-y-3 text-sm text-[#d4d4d8] leading-relaxed font-sans text-left">
              <p>
                "When autonomous AI agents transition from passive assistants into active enterprise participants with direct authority over production databases, cloud infrastructure, and financial transfers, probabilistic safety models fundamentally fail. An LLM judge that evaluates actions after the fact introduces seconds of latency and remains vulnerable to the exact same prompt confusion it seeks to prevent."
              </p>
              <p>
                "With <strong>BTP v2.5.0</strong>, we have proven that enterprise security does not require sacrificing performance. By executing deterministic Abstract Syntax Tree (AST) validation and constant folding in CPU memory, Bartholomew gates destructive commands in under 100 microseconds—over 10,000 times faster than secondary LLM guardrails. With our native framework adapters for LangChain, CrewAI, AutoGen, and LlamaIndex, developers can enforce hard mathematical guarantees and emit auditor-certified SOC 2 receipts with zero changes to their underlying model."
              </p>
              <p className="text-xs text-[#a1a1aa] font-mono">
                "Our commitment is uncompromising: local execution, zero mandatory cloud telemetry, sub-5 microsecond rollbacks, and complete mathematical reproducibility."
              </p>
            </div>

            <div className="pt-2 border-t border-[#1c1c1c] grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
              <div className="flex items-center gap-2 text-[#a1a1aa]">
                <Globe size={13} className="text-[#38bdf8]" />
                <span>Domain: <a href="https://bartholomew.info" className="text-white hover:underline">bartholomew.info</a></span>
              </div>
              <div className="flex items-center gap-2 text-[#a1a1aa]">
                <Mail size={13} className="text-[#f59e0b]" />
                <span>Contact: <a href="mailto:itsub@bartholomew.info" className="text-white hover:underline">itsub@bartholomew.info</a></span>
              </div>
            </div>

            {/* Verifiable Third-Party Public Links */}
            <div className="pt-3 flex flex-wrap gap-2.5 justify-center md:justify-start">
              <a
                href="https://github.com/ivegotahunnitonit"
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 bg-[#000000] border border-[#222222] text-xs font-mono text-[#d4d4d8] hover:text-white hover:border-[#444444] transition inline-flex items-center gap-1.5"
              >
                <Code2 size={13} className="text-[#10b981]" />
                <span>GitHub Profile</span>
                <ExternalLink size={10} className="text-[#71717a]" />
              </a>

              <a
                href="https://doi.org/10.5281/zenodo.18843719"
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 bg-[#000000] border border-[#222222] text-xs font-mono text-[#d4d4d8] hover:text-white hover:border-[#444444] transition inline-flex items-center gap-1.5"
              >
                <FileText size={13} className="text-[#f59e0b]" />
                <span>Zenodo Academic DOI (v2.5)</span>
                <ExternalLink size={10} className="text-[#71717a]" />
              </a>

              <a
                href="/dashboard/admin.html"
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 bg-[#f59e0b] text-black font-bold text-xs font-mono transition inline-flex items-center gap-1.5 hover:bg-[#d97706]"
              >
                <ShieldCheck size={13} />
                <span>Live Admin Command Center</span>
              </a>
            </div>

          </div>
        </div>

        {/* Future Architecture Roadmap & Continuous Improvement */}
        <div className="bg-[#0a0a0a] border border-[#222222] p-6 sm:p-8 rounded-xl">
          <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Layers size={15} className="text-[#10b981]" />
                <span className="text-xs font-mono font-bold text-[#10b981]">[PROTOCOL EVOLUTION]</span>
              </div>
              <h3 className="text-xl sm:text-2xl font-bold text-white font-sans">
                Upcoming Versions &amp; Continuous Improvement Strategy
              </h3>
            </div>
            <span className="text-xs font-mono text-[#71717a]">
              Formal Verification &bull; Kernel Hardening &bull; Zero-Knowledge
            </span>
          </div>

          {/* Version Selector Tabs */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 mb-6">
            {UPCOMING_MILESTONES.map((m, idx) => (
              <button
                key={m.version}
                onClick={() => setSelectedMilestone(idx)}
                className={`p-3 text-left border transition font-mono ${
                  selectedMilestone === idx
                    ? 'bg-[#121212] border-[#10b981] text-white shadow-lg'
                    : 'bg-[#050505] border-[#222222] text-[#71717a] hover:text-[#d4d4d8]'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-[#f59e0b]">{m.version}</span>
                  <span className={`text-[10px] px-1.5 py-0.2 font-bold ${
                    m.status === 'LIVE'
                      ? 'bg-[#10b981]/20 text-[#10b981]'
                      : m.status === 'IN DEVELOPMENT'
                      ? 'bg-[#3b82f6]/20 text-[#3b82f6]'
                      : 'bg-[#71717a]/20 text-[#a1a1aa]'
                  }`}>
                    {m.status}
                  </span>
                </div>
                <div className="text-[11px] text-[#a1a1aa] truncate">{m.title}</div>
                <div className="text-[10px] text-[#52525b] mt-1">{m.timeline}</div>
              </button>
            ))}
          </div>

          {/* Active Version Feature Deep Dive */}
          <div className="bg-[#000000] border border-[#1c1c1c] p-5 sm:p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-[#1c1c1c] gap-2">
              <div>
                <span className="text-xs font-mono text-[#10b981] font-bold">
                  {UPCOMING_MILESTONES[selectedMilestone].timeline} &bull; {UPCOMING_MILESTONES[selectedMilestone].status}
                </span>
                <h4 className="text-lg font-bold text-white font-sans mt-0.5">
                  {UPCOMING_MILESTONES[selectedMilestone].version}: {UPCOMING_MILESTONES[selectedMilestone].title}
                </h4>
              </div>
              <div className="text-xs font-mono text-[#a1a1aa]">
                Milestone {selectedMilestone + 1} of 4
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {UPCOMING_MILESTONES[selectedMilestone].highlights.map((highlight, hIdx) => (
                <div key={hIdx} className="flex items-start gap-2.5 text-xs sm:text-sm text-[#d4d4d8] font-sans">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#10b981] mt-1.5 shrink-0" />
                  <span>{highlight}</span>
                </div>
              ))}
            </div>
          </div>

          {/* How We Improve: Continuous Engineering Discipline */}
          <div className="mt-6 pt-6 border-t border-[#1c1c1c] grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-sans">
            <div className="p-3 bg-[#050505] border border-[#1a1a1a]">
              <div className="font-mono font-bold text-[#10b981] mb-1">[10k ADVERSARIAL FUZZING]</div>
              <p className="text-[#a1a1aa]">
                Every git commit triggers automated AST fuzzing across 10,000 permutations of obfuscated shell and SQL attacks to eliminate false negatives.
              </p>
            </div>
            <div className="p-3 bg-[#050505] border border-[#1a1a1a]">
              <div className="font-mono font-bold text-[#f59e0b] mb-1">[SUB-5µS LATENCY BUDGET]</div>
              <p className="text-[#a1a1aa]">
                Strict memory and execution limits: zero cloud calls on the critical path and micro-rollbacks executed in under 3 milliseconds.
              </p>
            </div>
            <div className="p-3 bg-[#050505] border border-[#1a1a1a]">
              <div className="font-mono font-bold text-[#38bdf8] mb-1">[PRIVACY-FIRST INTEL]</div>
              <p className="text-[#a1a1aa]">
                Emerging injection signatures are federated using 24-bit k-anonymity prefixes, protecting enterprise prompt privacy while immunizing the ecosystem.
              </p>
            </div>
          </div>

        </div>

      </div>
    </section>
  )
}
