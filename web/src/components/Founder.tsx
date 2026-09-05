import { useState } from 'react'
import { ExternalLink, Code2, Mail, ShieldCheck, FileText, Globe, Layers } from 'lucide-react'

interface VersionMilestone {
  version: string
  timeline: string
  title: string
  status: 'LIVE' | 'IN DEVELOPMENT' | 'PLANNED'
  highlights: string[]
  paperPdf?: string
  zenodoDoi?: string
}

const UPCOMING_MILESTONES: VersionMilestone[] = [
  {
    version: 'BTP v2.9.0',
    timeline: 'FOUNDATION BEDROCK',
    status: 'LIVE',
    title: 'Post-Quantum Envelopes & MuSig2 Pre-Computed Rounds',
    paperPdf: '/paper_v2_9.pdf',
    zenodoDoi: '10.5281/zenodo.22076540',
    highlights: [
      'Dual-layer post-quantum hybrid envelope binding FROST RFC 9591 with Winternitz One-Time Signatures (WOTS+).',
      'Two-round adaptive state machines dynamically reconfiguring threshold parameters without centralized coordinators.',
      'Quantum-safe non-repudiation ensuring immutable multi-agent audit trails resist Shor\'s algorithm.',
      'Sub-5ms signing budget (2.42 ms median for 3-of-5 quorums) maintaining high agent throughput.'
    ]
  },
  {
    version: 'BTP v3.0.0',
    timeline: 'CURRENT RUNTIME',
    status: 'LIVE',
    title: 'Zero-Knowledge Invariant Compliance Proofs (zk-ICP)',
    paperPdf: '/paper_v3_0.pdf',
    zenodoDoi: '10.5281/zenodo.22076541',
    highlights: [
      'Mathematical zero-knowledge receipts proving an agent obeyed all rules with exactly 0 bytes of plaintext prompt leaked.',
      'Pedersen commitments over RFC 3526 1024-bit safe primes combined with non-interactive Fiat-Shamir challenges.',
      'Sub-millisecond verification (0.42 ms) with fixed 512-byte cryptographic receipt payloads.',
      'Integrated CLI (btp-guard zk-prove, zk-verify) and Model Context Protocol (btp_verify_safety_proof) tooling.'
    ]
  },
  {
    version: 'BTP v3.1.0',
    timeline: 'Q2 2026 &bull; IN ACTIVE CORE',
    status: 'IN DEVELOPMENT',
    title: 'Autonomous Circularity Network (ACN) & Peer Discovery',
    paperPdf: '/WHITEPAPER.md',
    highlights: [
      'Decentralized agent peer discovery and automated capability negotiation using signed cryptographic manifests.',
      'Sovereign digital passports for non-human agent workers with cryptographically verifiable reputation vectors.',
      'Zero-knowledge inter-agent delegation protocols preventing lateral privilege escalation across autonomous swarms.',
      'Self-reconciling circuit breakers preventing multi-swarm cascading failures and cross-organization deadlocks.'
    ]
  },
  {
    version: 'BTP v3.2.0',
    timeline: 'Q3 2026 &bull; KERNEL EXPANSION',
    status: 'IN DEVELOPMENT',
    title: 'Ring-0 eBPF Memory Hooks & Hot-Pluggable Invariants',
    highlights: [
      'Native Linux Ring-0 eBPF kernel traps executing deterministic invariant checks in sub-microsecond latency (<0.18µs).',
      'Hot-reloading invariant rulesets without requiring agent process restart or context reconstruction.',
      'Dynamic threshold rebalancing automatically adjusting quorum sizes based on real-time threat entropy metrics.',
      'Hardware-assisted cryptographic acceleration using AVX-512 and ARM NEON vectorized field operations.'
    ]
  },
  {
    version: 'BTP v3.5.0',
    timeline: 'Q4 2026 &bull; DISTRIBUTED SWARM',
    status: 'PLANNED',
    title: 'Cross-Cloud Hardware Enclave Attestation & zk-Rollups',
    highlights: [
      'Multi-cloud secure enclave attestation bridging AWS Nitro, Intel SGX, and Apple Secure Enclaves under unified proofs.',
      'Recursive zk-Rollup batching 10,000 agent state transitions into a single verifiable 256-byte on-chain anchor.',
      'Automated formal verification engine synthesizing provably sound safety invariants directly from plain-language policies.',
      'Universal Model Context Protocol (MCP) hypervisor securing arbitrary third-party agent tools with zero configuration.'
    ]
  },
  {
    version: 'BTP v4.0.0',
    timeline: '2027 &bull; FUTURE HORIZON',
    status: 'PLANNED',
    title: 'Sovereign Agent Clearinghouse & Global Invariant Mesh',
    highlights: [
      'Autonomous micro-settlement layer enabling non-human agents to exchange compute, data, and tools with mathematical finality.',
      'Global cryptographic invariant mesh guaranteeing planetary-scale AI safety without centralized single points of failure.',
      'Autonomous fault isolation and self-healing memory architectures for fully autonomous self-replicating workflows.',
      'Universal verification primitives standardizing safe AI-to-AI interaction across all architectures and runtimes.'
    ]
  }
]

export default function Founder() {
  const [selectedMilestone, setSelectedMilestone] = useState<number>(1)

  return (
    <section id="founder" className="py-24 px-5 sm:px-8 bg-[#040406] text-white border-t border-[#27272a]/70 relative overflow-hidden">
      {/* Top ambient glowing accent line */}
      <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#10b981]/70 to-transparent pointer-events-none" />

      {/* Background glow accents */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[700px] h-[300px] bg-gradient-to-b from-[#10b981]/10 to-transparent blur-[140px] pointer-events-none" />

      <div className="max-w-6xl mx-auto relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-[#10b981]/10 border border-[#10b981]/30 text-[#10b981] rounded-full text-xs font-mono font-bold tracking-wider mb-4 shadow-[0_0_15px_rgba(16,185,129,0.15)]">
            <ShieldCheck size={13} />
            <span>[ OPERATIONAL TRANSPARENCY &amp; ROADMAP ]</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white font-sans">
            Founder Perspective &amp; Architectural Roadmap
          </h2>
          <p className="mt-4 text-[#a1a1aa] text-sm sm:text-base font-sans leading-relaxed">
            Why we built Bartholomew, how our deterministic invariant runtime protects autonomous agent workflows, and where we are heading next.
          </p>
        </div>

        {/* Founder Card */}
        <div className="rounded-2xl p-8 md:p-10 bg-gradient-to-b from-[#0e0e14]/95 via-[#09090d]/95 to-[#050507] border border-[#27272a]/80 shadow-2xl relative overflow-hidden flex flex-col md:flex-row items-center md:items-start gap-8 mb-12 backdrop-blur-xl">
          <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#10b981]/50 to-transparent pointer-events-none" />

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
              <div className="flex flex-wrap items-center justify-center md:justify-start gap-2.5 mb-1.5">
                <h3 className="text-2xl sm:text-3xl font-bold text-white font-sans">Itsub Alemayehu</h3>
                <span className="px-2.5 py-0.5 bg-[#10b981]/15 text-[#10b981] border border-[#10b981]/30 font-mono text-[11px] font-bold rounded-full">
                  FOUNDER &amp; LEAD ARCHITECT
                </span>
              </div>
              <p className="text-xs font-mono text-[#f59e0b]">
                Autonomous Systems Laboratory &bull; Bartholomew Trust Protocol Lead
              </p>
            </div>

            <div className="space-y-3.5 text-sm text-[#d4d4d8] leading-relaxed font-sans text-left">
              {/* Where We Were */}
              <div className="p-3.5 rounded-xl bg-[#08080c] border border-[#1c1c22]">
                <span className="text-[11px] font-mono font-bold text-[#f59e0b] block uppercase tracking-wider mb-1">
                  [ 01 &middot; Where We Started ]
                </span>
                <p className="text-xs sm:text-sm text-[#a1a1aa] leading-relaxed">
                  Prompt engineering and secondary observer LLMs broke down the moment agents started executing terminal commands, touching production data, and moving capital. We founded Bartholomew on a strict engineering law: autonomous agent safety requires deterministic memory boundaries and compiler-grade AST invariants.
                </p>
              </div>

              {/* Where We Are (v3.0) */}
              <div className="p-3.5 rounded-xl bg-[#080d0b] border border-[#10b981]/30 shadow-[0_0_20px_rgba(16,185,129,0.06)]">
                <span className="text-[11px] font-mono font-bold text-[#10b981] block uppercase tracking-wider mb-1 flex items-center justify-between">
                  <span>[ 02 &middot; Where We Are &middot; BTP v3.0 ]</span>
                  <span className="text-[10px] bg-[#10b981]/15 px-2 py-0.5 rounded border border-[#10b981]/30">ACTIVE RUNTIME</span>
                </span>
                <p className="text-xs sm:text-sm text-[#e4e4e7] leading-relaxed">
                  With <strong>BTP v3.0</strong>, we delivered a 100% offline cryptographic trust kernel. We unified in-process memory gating, Zero-Knowledge Invariant Compliance Proofs (zk-ICP), FROST RFC 9591 multi-agent threshold consensus, and post-quantum envelopes across every foundation model, open-source weight, and distributed agent swarm—proving an agent adhered to all constraints with <strong>0 bytes of prompt or payload leaked</strong>, accessible to everyone, everywhere.
                </p>
              </div>

              {/* Where We're Headed */}
              <div className="p-3.5 rounded-xl bg-[#08080c] border border-[#1c1c22]">
                <span className="text-[11px] font-mono font-bold text-[#38bdf8] block uppercase tracking-wider mb-1">
                  [ 03 &middot; Where We're Headed &middot; Sovereign Agent Infrastructure ]
                </span>
                <p className="text-xs sm:text-sm text-[#a1a1aa] leading-relaxed">
                  We are building the <strong>Autonomous Circularity Network (ACN)</strong>—a sovereign, self-healing substrate where distributed agents discover peers, negotiate zero-knowledge tool delegations, and settle commercial tasks with mathematical finality and zero human friction.
                </p>
              </div>

              <p className="text-xs text-[#71717a] font-mono pt-1">
                "When your agents build the future, Bartholomew makes sure they don't break the present."
              </p>
            </div>

            <div className="pt-2 border-t border-[#27272a]/70 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
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
                className="px-3.5 py-2 bg-[#050508] border border-[#27272a] hover:border-[#10b981] text-xs font-mono text-[#d4d4d8] hover:text-white rounded-xl transition inline-flex items-center gap-2 shadow-sm"
              >
                <Code2 size={14} className="text-[#10b981]" />
                <span>GitHub Profile</span>
                <ExternalLink size={11} className="text-[#71717a]" />
              </a>

              <a
                href="https://doi.org/10.5281/zenodo.18843719"
                target="_blank"
                rel="noopener noreferrer"
                className="px-3.5 py-2 bg-[#050508] border border-[#27272a] hover:border-[#f59e0b] text-xs font-mono text-[#d4d4d8] hover:text-white rounded-xl transition inline-flex items-center gap-2 shadow-sm"
              >
                <FileText size={14} className="text-[#f59e0b]" />
                <span>Zenodo Academic DOI (v2.5)</span>
                <ExternalLink size={11} className="text-[#71717a]" />
              </a>

              <a
                href="/dashboard/admin.html"
                target="_blank"
                rel="noopener noreferrer"
                className="px-3.5 py-2 bg-gradient-to-r from-[#f59e0b] to-[#d97706] hover:from-[#d97706] hover:to-[#b45309] text-black font-bold text-xs font-mono rounded-xl transition inline-flex items-center gap-2 shadow-[0_0_15px_rgba(245,158,11,0.25)]"
              >
                <ShieldCheck size={14} />
                <span>Live Admin Command Center</span>
              </a>
            </div>

          </div>
        </div>

        {/* Future Architecture Roadmap & Continuous Improvement */}
        <div className="bg-gradient-to-b from-[#0e0e14]/95 via-[#09090d]/95 to-[#050507] border border-[#27272a]/80 p-7 sm:p-9 rounded-2xl shadow-2xl relative overflow-hidden backdrop-blur-xl">
          <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#10b981]/50 to-transparent pointer-events-none" />

          <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1.5">
                <Layers size={15} className="text-[#10b981]" />
                <span className="text-xs font-mono font-bold text-[#10b981]">[PROTOCOL EVOLUTION]</span>
              </div>
              <h3 className="text-2xl sm:text-3xl font-bold text-white font-sans tracking-tight">
                Upcoming Versions &amp; Continuous Improvement Strategy
              </h3>
            </div>
            <span className="text-xs font-mono text-[#a1a1aa] bg-[#050508] px-3 py-1 rounded-lg border border-[#27272a]">
              Formal Verification &bull; Kernel Hardening &bull; Zero-Knowledge Proofs
            </span>
          </div>

          {/* Version Selector Tabs */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 mb-6">
            {UPCOMING_MILESTONES.map((m, idx) => (
              <button
                key={m.version}
                onClick={() => setSelectedMilestone(idx)}
                className={`p-3.5 text-left border rounded-xl transition-all duration-200 font-mono cursor-pointer ${
                  selectedMilestone === idx
                    ? 'bg-gradient-to-b from-[#14141c] to-[#0d0d12] border-[#10b981] text-white shadow-[0_0_20px_rgba(16,185,129,0.2)] ring-1 ring-[#10b981]'
                    : 'bg-[#050508] border-[#27272a]/70 text-[#71717a] hover:text-[#d4d4d8] hover:border-[#444455]'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-bold text-[#f59e0b]">{m.version}</span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
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
          <div className="bg-[#030305] border border-[#27272a]/80 rounded-xl p-6 sm:p-7 shadow-inner">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-[#27272a]/70 gap-2">
              <div>
                <span className="text-xs font-mono text-[#10b981] font-bold">
                  {UPCOMING_MILESTONES[selectedMilestone].timeline} &bull; {UPCOMING_MILESTONES[selectedMilestone].status}
                </span>
                <h4 className="text-lg font-bold text-white font-sans mt-1">
                  {UPCOMING_MILESTONES[selectedMilestone].version}: {UPCOMING_MILESTONES[selectedMilestone].title}
                </h4>
              </div>
              <div className="text-xs font-mono text-[#a1a1aa]">
                Milestone {selectedMilestone + 1} of {UPCOMING_MILESTONES.length}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {UPCOMING_MILESTONES[selectedMilestone].highlights.map((highlight, hIdx) => (
                <div key={hIdx} className="flex items-start gap-3 text-xs sm:text-sm text-[#d4d4d8] font-sans">
                  <div className="w-2 h-2 rounded-full bg-[#10b981] mt-1.5 shrink-0" />
                  <span className="leading-relaxed">{highlight}</span>
                </div>
              ))}
            </div>

            {/* Academic Paper & Zenodo Public Reference */}
            {UPCOMING_MILESTONES[selectedMilestone].paperPdf && (
              <div className="mt-5 pt-4 border-t border-[#27272a]/70 flex flex-wrap items-center gap-3">
                <a
                  href={UPCOMING_MILESTONES[selectedMilestone].paperPdf}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3.5 py-2 bg-[#10b981]/15 hover:bg-[#10b981]/25 border border-[#10b981]/50 text-[#10b981] hover:text-white font-mono text-xs rounded-xl transition inline-flex items-center gap-2 shadow-sm font-semibold"
                >
                  <FileText size={14} />
                  <span>Download Academic Paper PDF ({UPCOMING_MILESTONES[selectedMilestone].version})</span>
                  <ExternalLink size={11} />
                </a>
                {UPCOMING_MILESTONES[selectedMilestone].zenodoDoi && (
                  <a
                    href={`https://doi.org/${UPCOMING_MILESTONES[selectedMilestone].zenodoDoi}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3.5 py-2 bg-[#050508] border border-[#27272a] hover:border-[#f59e0b] text-xs font-mono text-[#a1a1aa] hover:text-white rounded-xl transition inline-flex items-center gap-2"
                  >
                    <span>Zenodo DOI: {UPCOMING_MILESTONES[selectedMilestone].zenodoDoi}</span>
                    <ExternalLink size={11} className="text-[#71717a]" />
                  </a>
                )}
              </div>
            )}
          </div>

          {/* How We Improve: Continuous Engineering Discipline */}
          <div className="mt-6 pt-6 border-t border-[#27272a]/70 grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-sans">
            <div className="p-4 bg-[#08080c]/80 border border-[#27272a]/70 rounded-xl">
              <div className="font-mono font-bold text-[#10b981] mb-1.5 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]" />
                <span>[10k ADVERSARIAL FUZZING]</span>
              </div>
              <p className="text-[#a1a1aa] leading-relaxed">
                Every code release runs automated stress tests across 10,000 permutations of disguised attacks and shell tricks to ensure zero security gaps.
              </p>
            </div>
            <div className="p-4 bg-[#08080c]/80 border border-[#27272a]/70 rounded-xl">
              <div className="font-mono font-bold text-[#f59e0b] mb-1.5 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#f59e0b]" />
                <span>[SUB-5µS LATENCY BUDGET]</span>
              </div>
              <p className="text-[#a1a1aa] leading-relaxed">
                Strict speed limits: zero cloud calls on the critical decision path and immediate state restoration executed in under 3 milliseconds.
              </p>
            </div>
            <div className="p-4 bg-[#08080c]/80 border border-[#27272a]/70 rounded-xl">
              <div className="font-mono font-bold text-[#38bdf8] mb-1.5 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#38bdf8]" />
                <span>[PRIVACY-FIRST THREAT INTEL]</span>
              </div>
              <p className="text-[#a1a1aa] leading-relaxed">
                New security patterns are shared using mathematical privacy hashes, protecting user confidentiality while keeping the entire network protected.
              </p>
            </div>
          </div>

        </div>

      </div>
    </section>
  )
}
