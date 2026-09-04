import { useState } from 'react'
import { Shield, ArrowRight, Server, Terminal, Lock, ExternalLink, FileText } from 'lucide-react'

export default function EnterpriseDesignPartnerSection() {
  const [copiedEmail, setCopiedEmail] = useState(false)

  const handleCopyEmail = () => {
    navigator.clipboard.writeText('enterprise@bartholomew.info')
    setCopiedEmail(true)
    setTimeout(() => setCopiedEmail(false), 2000)
  }

  return (
    <section id="enterprise" className="py-20 bg-[#000000] border-t border-[#222222] text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Pill & Title */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#0a0a0a] border border-[#222222] text-xs font-mono font-bold text-[#10b981] mb-3">
              <span className="w-2 h-2 bg-[#10b981] animate-pulse" />
              <span>[ENTERPRISE DESIGN PARTNER PROGRAM]</span>
            </div>
            <h2 className="text-2xl sm:text-4xl font-bold font-sans tracking-tight text-white">
              Deterministic Security &amp; Compliance for Agent Workflows
            </h2>
            <p className="text-[#a1a1aa] text-sm sm:text-base mt-2 max-w-3xl font-sans">
              Replace secondary LLM judge latency (800ms-2500ms) with sub-100 microsecond deterministic AST enforcement, Ed25519 cryptographic execution receipts, and automated SOC 2 / ISO 27001 audit streams.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <a
              href="mailto:enterprise@bartholomew.info?subject=Bartholomew%20Enterprise%20Design%20Partner%20Inquiry&body=Hi%20Bartholomew%20Team%2C%0A%0AWe%20are%20building%20autonomous%20agentic%20workflows%20using%20%5BLangChain%20%2F%20CrewAI%20%2F%20AutoGen%5D%20and%20would%20like%20to%20apply%20for%20the%2014-day%20assisted%20enterprise%20pilot.%0A%0AOrganization%3A%20%0ATeam%20Size%3A%20%0APrimary%20Use%20Case%3A%20%0A"
              className="px-4 py-2 bg-[#10b981] hover:bg-[#059669] text-black font-mono font-bold text-xs transition flex items-center gap-2 shadow-lg"
            >
              <span>APPLY FOR 14-DAY PILOT</span>
              <ArrowRight size={13} />
            </a>
          </div>
        </div>

        {/* 4 Feature Pillars Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          
          <div className="p-5 bg-[#0a0a0a] border border-[#222222] flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded bg-[#10b981]/10 border border-[#10b981]/30 flex items-center justify-center text-[#10b981] mb-4">
                <Terminal size={18} />
              </div>
              <h3 className="font-mono text-sm font-bold text-white mb-2">Native Framework Adapters</h3>
              <p className="text-xs text-[#a1a1aa] leading-relaxed">
                Drop-in wrappers for LangChain (<code className="text-[#10b981]">BartholomewLangChainTool</code>), CrewAI (<code className="text-[#10b981]">@btp_crewai_tool</code>), AutoGen, and LlamaIndex. Enforce security without re-architecting your agents.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-[#1a1a1a] text-[11px] font-mono text-[#71717a]">
              Zero-instrumentation hook
            </div>
          </div>

          <div className="p-5 bg-[#0a0a0a] border border-[#222222] flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded bg-[#f59e0b]/10 border border-[#f59e0b]/30 flex items-center justify-center text-[#f59e0b] mb-4">
                <Lock size={18} />
              </div>
              <h3 className="font-mono text-sm font-bold text-white mb-2">Non-Human Identity (NHI)</h3>
              <p className="text-xs text-[#a1a1aa] leading-relaxed">
                Provisions sovereign Ed25519 identity keypairs per agent worker with granular capability tiers (<code className="text-[#f59e0b]">ANALYST</code>, <code className="text-[#f59e0b]">OPERATOR</code>, <code className="text-[#f59e0b]">ADMIN</code>) and automated revocation.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-[#1a1a1a] text-[11px] font-mono text-[#71717a]">
              RFC 8785 canonical receipts
            </div>
          </div>

          <div className="p-5 bg-[#0a0a0a] border border-[#222222] flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded bg-[#3b82f6]/10 border border-[#3b82f6]/30 flex items-center justify-center text-[#3b82f6] mb-4">
                <Server size={18} />
              </div>
              <h3 className="font-mono text-sm font-bold text-white mb-2">Asynchronous SIEM Streaming</h3>
              <p className="text-xs text-[#a1a1aa] leading-relaxed">
                High-throughput background batch export to Datadog Logs (v2), Splunk HEC, AWS CloudWatch, and encrypted local spool storage without blocking execution.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-[#1a1a1a] text-[11px] font-mono text-[#71717a]">
              Sub-5ms queue dispatch
            </div>
          </div>

          <div className="p-5 bg-[#0a0a0a] border border-[#222222] flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded bg-[#a855f7]/10 border border-[#a855f7]/30 flex items-center justify-center text-[#a855f7] mb-4">
                <Shield size={18} />
              </div>
              <h3 className="font-mono text-sm font-bold text-white mb-2">Automated Compliance</h3>
              <p className="text-xs text-[#a1a1aa] leading-relaxed">
                Turnkey alignment with SOC 2 Type II (CC6.1, CC6.8, CC7.2) and ISO/IEC 27001:2022 (A.8.15, A.8.16, A.8.24) with offline-verifiable cryptographic receipts.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-[#1a1a1a] text-[11px] font-mono text-[#71717a]">
              Auditor-ready reports
            </div>
          </div>

        </div>

        {/* Pilot Overview Banner */}
        <div className="bg-[#0a0a0a] border border-[#222222] p-6 sm:p-8">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 bg-[#f59e0b]/20 text-[#f59e0b] border border-[#f59e0b]/40 text-[10px] font-mono font-bold">
                  LIMITED ENROLLMENT (5 TEAMS)
                </span>
                <span className="text-xs font-mono text-[#a1a1aa]">14-Day Assisted Engineering Pilot</span>
              </div>
              <h3 className="text-xl font-bold font-sans text-white">
                Integrate BTP into your staging agent cluster with dedicated architectural support.
              </h3>
              <p className="text-xs sm:text-sm text-[#71717a] font-sans max-w-2xl">
                Includes custom policy generation, synthetic adversarial stress-testing (10k fuzz iterations), and an auditor-certified SOC 2 compliance evidence package.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <a
                href="https://github.com/ivegotahunnitonit/bartholomew/blob/main/docs/ENTERPRISE_PILOT_OUTREACH_KIT.md"
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 bg-[#121212] border border-[#333333] hover:border-[#666666] text-xs font-mono text-white transition flex items-center gap-1.5"
              >
                <FileText size={13} />
                <span>PILOT SPECIFICATION</span>
                <ExternalLink size={11} className="text-[#71717a]" />
              </a>
              <button
                onClick={handleCopyEmail}
                className="px-4 py-2 bg-[#000000] border border-[#222222] hover:border-[#10b981] text-xs font-mono text-[#d4d4d8] hover:text-white transition"
              >
                {copiedEmail ? '[COPIED EMAIL]' : '[COPY CONTACT EMAIL]'}
              </button>
            </div>
          </div>
        </div>

      </div>
    </section>
  )
}
