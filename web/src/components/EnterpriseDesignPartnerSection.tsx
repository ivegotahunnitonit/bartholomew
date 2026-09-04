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
    <section id="enterprise" className="py-24 bg-[#040406] border-t border-[#27272a]/70 text-white relative overflow-hidden">
      {/* Top ambient glowing accent line */}
      <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#10b981]/70 to-transparent pointer-events-none" />

      {/* Subtle radial ambient glow */}
      <div className="absolute top-1/2 right-1/4 -translate-y-1/2 w-[600px] h-[300px] bg-gradient-to-b from-[#10b981]/10 to-transparent blur-[140px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Pill & Title */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-14 gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-[#10b981]/10 border border-[#10b981]/30 text-xs font-mono font-bold text-[#10b981] rounded-full mb-4 shadow-[0_0_15px_rgba(16,185,129,0.15)]">
              <span className="w-2 h-2 rounded-full bg-[#10b981] animate-ping" />
              <span>[ENTERPRISE DESIGN PARTNER PROGRAM]</span>
            </div>
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold font-sans tracking-tight text-white">
              Deterministic Security &amp; Compliance for Agent Workflows
            </h2>
            <p className="text-[#a1a1aa] text-sm sm:text-base mt-3 max-w-3xl font-sans leading-relaxed">
              Replace secondary LLM judge latency (800ms–2500ms) with sub-100 microsecond deterministic AST enforcement, Ed25519 cryptographic execution receipts, and automated SOC 2 / ISO 27001 audit streams.
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <a
              href="mailto:enterprise@bartholomew.info?subject=Bartholomew%20Enterprise%20Design%20Partner%20Inquiry&body=Hi%20Bartholomew%20Team%2C%0A%0AWe%20are%20building%20autonomous%20agentic%20workflows%20using%20%5BLangChain%20%2F%20CrewAI%20%2F%20AutoGen%5D%20and%20would%20like%20to%20apply%20for%20the%2014-day%20assisted%20enterprise%20pilot.%0A%0AOrganization%3A%20%0ATeam%20Size%3A%20%0APrimary%20Use%20Case%3A%20%0A"
              className="px-5 py-3 bg-gradient-to-r from-[#10b981] to-[#059669] hover:from-[#059669] hover:to-[#047857] text-black font-mono font-bold text-xs rounded-xl transition-all duration-200 flex items-center gap-2 shadow-[0_0_25px_rgba(16,185,129,0.3)] active:scale-95"
            >
              <span>APPLY FOR 14-DAY PILOT</span>
              <ArrowRight size={14} />
            </a>
          </div>
        </div>

        {/* 4 Feature Pillars Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          
          <div className="p-6 bg-gradient-to-b from-[#0e0e14]/90 via-[#09090d]/90 to-[#040406] border border-[#27272a]/75 hover:border-[#10b981]/50 rounded-2xl flex flex-col justify-between transition-all duration-300 shadow-xl hover:shadow-[0_15px_35px_-10px_rgba(16,185,129,0.15)] group backdrop-blur-md">
            <div>
              <div className="w-10 h-10 rounded-xl bg-[#10b981]/10 border border-[#10b981]/30 flex items-center justify-center text-[#10b981] mb-5 group-hover:scale-110 transition-transform">
                <Terminal size={20} />
              </div>
              <h3 className="font-mono text-sm font-bold text-white mb-2.5 group-hover:text-[#10b981] transition-colors">Native Framework Adapters</h3>
              <p className="text-xs text-[#a1a1aa] leading-relaxed font-sans">
                Drop-in wrappers for LangChain (<code className="text-[#10b981] bg-[#10b981]/10 px-1 py-0.5 rounded">BartholomewLangChainTool</code>), CrewAI (<code className="text-[#10b981] bg-[#10b981]/10 px-1 py-0.5 rounded">@btp_crewai_tool</code>), AutoGen, and LlamaIndex. Enforce security without re-architecting your agents.
              </p>
            </div>
            <div className="mt-5 pt-3.5 border-t border-[#27272a]/60 text-[11px] font-mono text-[#10b981] flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]" />
              <span>Zero-instrumentation hook</span>
            </div>
          </div>

          <div className="p-6 bg-gradient-to-b from-[#0e0e14]/90 via-[#09090d]/90 to-[#040406] border border-[#27272a]/75 hover:border-[#f59e0b]/50 rounded-2xl flex flex-col justify-between transition-all duration-300 shadow-xl hover:shadow-[0_15px_35px_-10px_rgba(245,158,11,0.15)] group backdrop-blur-md">
            <div>
              <div className="w-10 h-10 rounded-xl bg-[#f59e0b]/10 border border-[#f59e0b]/30 flex items-center justify-center text-[#f59e0b] mb-5 group-hover:scale-110 transition-transform">
                <Lock size={20} />
              </div>
              <h3 className="font-mono text-sm font-bold text-white mb-2.5 group-hover:text-[#f59e0b] transition-colors">Non-Human Identity (NHI)</h3>
              <p className="text-xs text-[#a1a1aa] leading-relaxed font-sans">
                Provisions sovereign Ed25519 identity keypairs per agent worker with granular capability tiers (<code className="text-[#f59e0b] bg-[#f59e0b]/10 px-1 py-0.5 rounded">ANALYST</code>, <code className="text-[#f59e0b] bg-[#f59e0b]/10 px-1 py-0.5 rounded">OPERATOR</code>, <code className="text-[#f59e0b] bg-[#f59e0b]/10 px-1 py-0.5 rounded">ADMIN</code>) and automated revocation.
              </p>
            </div>
            <div className="mt-5 pt-3.5 border-t border-[#27272a]/60 text-[11px] font-mono text-[#f59e0b] flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#f59e0b]" />
              <span>RFC 8785 canonical receipts</span>
            </div>
          </div>

          <div className="p-6 bg-gradient-to-b from-[#0e0e14]/90 via-[#09090d]/90 to-[#040406] border border-[#27272a]/75 hover:border-[#3b82f6]/50 rounded-2xl flex flex-col justify-between transition-all duration-300 shadow-xl hover:shadow-[0_15px_35px_-10px_rgba(59,130,246,0.15)] group backdrop-blur-md">
            <div>
              <div className="w-10 h-10 rounded-xl bg-[#3b82f6]/10 border border-[#3b82f6]/30 flex items-center justify-center text-[#3b82f6] mb-5 group-hover:scale-110 transition-transform">
                <Server size={20} />
              </div>
              <h3 className="font-mono text-sm font-bold text-white mb-2.5 group-hover:text-[#38bdf8] transition-colors">Asynchronous SIEM Streaming</h3>
              <p className="text-xs text-[#a1a1aa] leading-relaxed font-sans">
                High-throughput background batch export to Datadog Logs (v2), Splunk HEC, AWS CloudWatch, and encrypted local spool storage without blocking execution.
              </p>
            </div>
            <div className="mt-5 pt-3.5 border-t border-[#27272a]/60 text-[11px] font-mono text-[#38bdf8] flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#38bdf8]" />
              <span>Sub-5ms queue dispatch</span>
            </div>
          </div>

          <div className="p-6 bg-gradient-to-b from-[#0e0e14]/90 via-[#09090d]/90 to-[#040406] border border-[#27272a]/75 hover:border-[#a855f7]/50 rounded-2xl flex flex-col justify-between transition-all duration-300 shadow-xl hover:shadow-[0_15px_35px_-10px_rgba(168,85,247,0.15)] group backdrop-blur-md">
            <div>
              <div className="w-10 h-10 rounded-xl bg-[#a855f7]/10 border border-[#a855f7]/30 flex items-center justify-center text-[#a855f7] mb-5 group-hover:scale-110 transition-transform">
                <Shield size={20} />
              </div>
              <h3 className="font-mono text-sm font-bold text-white mb-2.5 group-hover:text-[#c084fc] transition-colors">Automated Compliance</h3>
              <p className="text-xs text-[#a1a1aa] leading-relaxed font-sans">
                Turnkey alignment with SOC 2 Type II (CC6.1, CC6.8, CC7.2) and ISO/IEC 27001:2022 (A.8.15, A.8.16, A.8.24) with offline-verifiable cryptographic receipts.
              </p>
            </div>
            <div className="mt-5 pt-3.5 border-t border-[#27272a]/60 text-[11px] font-mono text-[#c084fc] flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#c084fc]" />
              <span>Auditor-ready reports</span>
            </div>
          </div>

        </div>

        {/* Pilot Overview Banner */}
        <div className="bg-gradient-to-b from-[#0f0f16]/95 via-[#0a0a0f]/95 to-[#050508] border border-[#27272a]/80 rounded-2xl p-7 sm:p-9 shadow-2xl relative overflow-hidden backdrop-blur-xl">
          {/* Glowing line on top of banner */}
          <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#f59e0b]/60 to-transparent pointer-events-none" />

          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 relative z-10">
            <div className="space-y-2.5">
              <div className="flex items-center gap-2.5">
                <span className="px-2.5 py-1 bg-[#f59e0b]/15 text-[#f59e0b] border border-[#f59e0b]/40 text-[10px] font-mono font-bold rounded-full">
                  LIMITED ENROLLMENT (5 TEAMS)
                </span>
                <span className="text-xs font-mono text-[#a1a1aa]">14-Day Assisted Engineering Pilot</span>
              </div>
              <h3 className="text-xl sm:text-2xl font-bold font-sans text-white tracking-tight">
                Integrate BTP into your staging agent cluster with dedicated architectural support.
              </h3>
              <p className="text-xs sm:text-sm text-[#a1a1aa] font-sans max-w-2xl leading-relaxed">
                Includes custom policy generation, synthetic adversarial stress-testing (10k fuzz iterations), and an auditor-certified SOC 2 compliance evidence package.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3 shrink-0">
              <a
                href="https://github.com/ivegotahunnitonit/bartholomew/blob/main/docs/ENTERPRISE_PILOT_OUTREACH_KIT.md"
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2.5 bg-[#14141a] hover:bg-[#1f1f28] border border-[#33333e] hover:border-[#666677] text-xs font-mono text-white rounded-xl transition flex items-center gap-2"
              >
                <FileText size={14} className="text-[#10b981]" />
                <span>PILOT SPECIFICATION</span>
                <ExternalLink size={12} className="text-[#71717a]" />
              </a>
              <button
                onClick={handleCopyEmail}
                className="px-4 py-2.5 bg-[#08080c] border border-[#27272a] hover:border-[#10b981] text-xs font-mono text-[#d4d4d8] hover:text-white rounded-xl transition cursor-pointer"
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
