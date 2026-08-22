import { useState } from 'react'
import { Shield, Lock, ChevronDown, ChevronUp, FileCode, Layers } from 'lucide-react'

interface FAQItem {
  question: string
  category: 'SUPPLY_CHAIN' | 'ARCHITECTURE' | 'COMPLIANCE' | 'COMPARISON'
  shortAnswer: string
  detailedAnswer: string
}

const FAQS: FAQItem[] = [
  {
    question: 'Why avoid piped shell installer scripts (curl | bash or irm | iex)?',
    category: 'SUPPLY_CHAIN',
    shortAnswer: 'Piped shell execution is a supply-chain anti-pattern. We distribute exclusively through standard package registries.',
    detailedAnswer: 'Piping remote scripts directly into a shell execution engine bypasses static scanning and hash verification. Bartholomew is distributed through auditable source repositories: Python Git install (pip install git+https://github.com/ivegotahunnitonit/bartholomew.git), standard VS Code VSIX, or direct source clones (git clone) with reproducible CI test gates.'
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
    question: 'How does Bartholomew compare to Docker containers and VM sandboxing?',
    category: 'ARCHITECTURE',
    shortAnswer: 'Bartholomew complements Docker by providing fine-grained semantic invariant gating inside containers.',
    detailedAnswer: 'Docker and virtual machines provide coarse OS-level isolation (filesystem namespaces and cgroups), but cannot inspect the semantic intent of tool payloads (e.g. distinguishing a safe SQL SELECT from a destructive DROP TABLE, or detecting an exponential retry loop). Bartholomew runs natively inside Docker containers and Kubernetes pods (via our official Helm Chart) to provide sub-50 µs pre-flight invariant gating before commands touch the container filesystem.'
  },
  {
    question: 'How can developers independently verify the cryptographic and performance claims?',
    category: 'COMPLIANCE',
    shortAnswer: 'Through our open 35-line reference verifier and reproducible 16-suite CI test battery.',
    detailedAnswer: 'Every claim is backed by transparent, open-source code: (1) FIPS 186-5 / RFC 8785 attestation is verifiable via standalone_btp_verifier.py (35 lines, zero dependencies). (2) Sub-50 µs latency is benchmarked in pure C (btp_fast_engine.c) in tests/test_native_core.py. (3) The entire 2,500+ test fuzzing battery is publicly runnable via python ci_security_gate.py.'
  }
]

export default function SecurityThreatModelSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0)

  const toggleFAQ = (idx: number) => {
    setOpenIndex(openIndex === idx ? null : idx)
  }

  return (
    <section id="security-threat-model" className="py-24 bg-[#000000] text-white border-t border-[#1c1c1c]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 bg-[#0a0a0a] border border-[#222222] text-[#38bdf8] text-xs font-mono font-bold uppercase tracking-wider mb-4">
            <Lock size={13} className="text-[#38bdf8]" />
            <span>[ FORMAL THREAT MODEL &amp; SECURITY ARCHITECTURE ]</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white font-sans">
            Direct Answers to Security &amp; Supply-Chain Concerns
          </h2>
          <p className="mt-4 text-base text-[#a1a1aa] font-sans">
            We built Bartholomew on the principle of transparent, zero-trust systems engineering. Here is our formal threat model, privilege architecture, and technical justifications.
          </p>
        </div>

        {/* 3 Core Pillars Banner */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <div className="p-6 bg-[#0a0a0a] border border-[#222222] shadow-xl">
            <div className="flex items-center gap-2.5 text-sm font-mono font-bold text-white mb-2">
              <Shield size={16} className="text-[#10b981]" />
              <span>ZERO-DAEMON ARCHITECTURE</span>
            </div>
            <p className="text-xs text-[#a1a1aa] font-sans leading-relaxed">
              Runs 100% in-process as an embedded library. Zero background daemons, zero open network sockets, and zero IPC attack surface.
            </p>
          </div>

          <div className="p-6 bg-[#0a0a0a] border border-[#222222] shadow-xl">
            <div className="flex items-center gap-2.5 text-sm font-mono font-bold text-white mb-2">
              <FileCode size={16} className="text-[#f59e0b]" />
              <span>VERIFIED PACKAGE REGISTRIES</span>
            </div>
            <p className="text-xs text-[#a1a1aa] font-sans leading-relaxed">
              Distributed exclusively via auditable GitHub repositories (pip install git+https://github.com/ivegotahunnitonit/bartholomew.git) and source clones. No raw shell script piping.
            </p>
          </div>

          <div className="p-6 bg-[#0a0a0a] border border-[#222222] shadow-xl">
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
        <div className="space-y-4 max-w-4xl mx-auto">
          {FAQS.map((item, index) => {
            const isOpen = openIndex === index
            return (
              <div
                key={index}
                className="bg-[#0a0a0a] border border-[#222222] overflow-hidden transition"
              >
                <button
                  onClick={() => toggleFAQ(index)}
                  className="w-full p-5 text-left flex items-center justify-between gap-4 hover:bg-[#111111] transition"
                >
                  <div className="flex items-start sm:items-center gap-3">
                    <span className="text-xs font-mono font-bold text-[#f59e0b] px-2 py-0.5 bg-black border border-[#222222] shrink-0">
                      [{item.category}]
                    </span>
                    <span className="text-sm sm:text-base font-bold text-white font-sans">
                      {item.question}
                    </span>
                  </div>
                  <div className="text-[#a1a1aa] shrink-0">
                    {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                  </div>
                </button>

                {isOpen && (
                  <div className="px-5 pb-6 pt-2 border-t border-[#1c1c1c] bg-[#050505] space-y-3">
                    <div className="p-3 bg-[#0a0a0a] border border-[#222222] font-mono text-xs text-[#10b981]">
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

        {/* Direct Links to Standalone White Paper and Markdown Spec */}
        <div className="mt-14 flex flex-wrap items-center justify-center gap-4">
          <a
            href="/SECURITY_WHITE_PAPER_AND_THREAT_MODEL.html"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#f59e0b] hover:bg-[#d97706] text-[#000000] font-mono text-xs font-bold transition border border-[#f59e0b]"
          >
            <FileCode size={14} />
            <span>[ OPEN WHITE PAPER (STANDALONE HTML) ]</span>
          </a>
          <a
            href="/SECURITY_WHITE_PAPER_AND_THREAT_MODEL.md"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#0a0a0a] hover:bg-[#141414] text-[#a1a1aa] hover:text-white border border-[#333333] font-mono text-xs font-bold transition"
          >
            <FileCode size={14} />
            <span>[ VIEW RAW SPECIFICATION (.MD) ]</span>
          </a>
        </div>
      </div>
    </section>
  )
}
