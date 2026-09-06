import { useState } from 'react'
import { ExternalLink, Code2, Mail, ShieldCheck, Globe, Layers, Award } from 'lucide-react'

interface VersionMilestone {
  version: string
  timeline: string
  title: string
  status: 'LIVE' | 'IN DEVELOPMENT' | 'PLANNED'
  highlights: string[]
}

const UPCOMING_MILESTONES: VersionMilestone[] = [
  {
    version: 'BTP v5.0.0',
    timeline: 'MULTI-TENANCY',
    status: 'LIVE',
    title: 'Enterprise Workspaces & Cryptographic Isolation',
    highlights: [
      'Multi-tenant workspace isolation across enterprise boundaries with scoped API keys (btp_live / btp_test).',
      'Cryptographic cross-tenant escrow slashing firewalls preventing unauthorized data or capital leakage.',
      'Sovereign digital agent passports providing non-human workers with verified Ed25519 identity.',
      'Interactive dashboard project switcher supporting instantaneous live tenant context changes.'
    ]
  },
  {
    version: 'BTP v5.1.0',
    timeline: 'SECOPS AUTOMATION',
    status: 'LIVE',
    title: 'Real-Time Incident Webhooks & SecOps Alerting',
    highlights: [
      'Automated security incident dispatch with HMAC-SHA256 signatures for zero-tamper audit trails.',
      'Native adapters for Slack Block Kit, Discord webhooks, PagerDuty incidents, and enterprise SIEM pipelines.',
      'Instantaneous alerting on blocked prompt injections, secret exfiltrations, and runaway execution loops.',
      'Multi-tenant isolation ensuring security events never cross enterprise organizational boundaries.'
    ]
  },
  {
    version: 'BTP v5.2.0',
    timeline: 'SELF-HEALING',
    status: 'LIVE',
    title: 'Autonomous Red-Teaming & Policy Auto-Immunity',
    highlights: [
      'Continuous adversarial mutation engine probing agent environments for evasive attack vectors.',
      'Automated policy synthesis: discovers novel attack patterns and generates hardened AST rules on the fly.',
      'Golden regression verification: rigorously tests synthesized rules to guarantee zero false positives.',
      'Atomic hot-reloading updating security policies in real time without restarting active agent workers.'
    ]
  },
  {
    version: 'BTP v5.3.0',
    timeline: 'SLA MARKETPLACE',
    status: 'LIVE',
    title: 'Cross-Tenant Agent Marketplace & Two-Sided SLA Escrows',
    highlights: [
      'Decentralized marketplace enabling enterprises to hire specialized autonomous agents across organizations.',
      'Two-sided conditional micro-escrows simultaneously locking client budgets and provider performance bonds.',
      'Zero-Knowledge Task Completion Proofs (zk-TCP) mathematically proving task success with 0 bytes of prompt leaked.',
      'Trustless atomic settlement automatically disbursing payments and returning performance bonds upon verified completion.'
    ]
  },
  {
    version: 'BTP v5.4.0',
    timeline: 'CURRENT RUNTIME',
    status: 'LIVE',
    title: 'Decentralized P2P Reputation Gossip & Cross-Chain Bridge',
    highlights: [
      'Decentralized peer reputation gossip mesh with EigenTrust damping (alpha = 0.85) resisting Sybil collusion.',
      'Fast-path slashing propagation across peer nodes immediately upon detected Byzantine fault or SLA breach.',
      'HTLC-style hash-locked cross-chain bridge relay connecting Base (EVM), Arbitrum (EVM), and Bitcoin Lightning (L402).',
      'Unified multi-framework protection supporting CrewAI, LangGraph, AutoGen, and Claude Desktop MCP.'
    ]
  },
  {
    version: 'BTP v5.5.0',
    timeline: 'UPCOMING',
    status: 'IN DEVELOPMENT',
    title: 'Global Autonomous Agent Clearinghouse & Liquidity Mesh',
    highlights: [
      'Autonomous high-frequency liquidity routing across decentralized exchanges and Lightning nodes.',
      'Universal non-human identity federation standardizing cross-cloud agent authorization.',
      'Self-reconciling decentralized credit facilities for autonomous corporate entities and DAOs.',
      'Zero-human-intervention commercial operations delivering continuous 24/7 autonomous economic output.'
    ]
  }
]

export default function Founder() {
  const [selectedMilestone, setSelectedMilestone] = useState<number>(4)

  return (
    <section id="founder" className="py-24 px-5 sm:px-8 bg-[#040406] text-white border-t border-[#27272a]/70 relative overflow-hidden">
      {/* Top ambient glowing accent line */}
      <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-emerald-500/70 to-transparent pointer-events-none" />

      {/* Background glow accents */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[700px] h-[300px] bg-gradient-to-b from-emerald-500/10 to-transparent blur-[140px] pointer-events-none" />

      <div className="max-w-6xl mx-auto relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-full text-xs font-mono font-bold tracking-wider mb-4 shadow-[0_0_15px_rgba(16,185,129,0.15)]">
            <ShieldCheck size={13} />
            <span>[ OPERATIONAL TRANSPARENCY &amp; ROADMAP ]</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white font-sans">
            Founder Perspective &amp; Architectural Roadmap
          </h2>
          <p className="mt-4 text-zinc-400 text-sm sm:text-base font-sans leading-relaxed">
            Why we built Bartholomew, how our deterministic trust runtime protects autonomous agent workflows, and where we are heading next.
          </p>
        </div>

        {/* Founder Card */}
        <div className="rounded-2xl p-8 md:p-10 bg-gradient-to-b from-zinc-900/95 via-[#09090d]/95 to-[#050507] border border-zinc-800 shadow-2xl relative overflow-hidden flex flex-col md:flex-row items-center md:items-start gap-8 mb-12 backdrop-blur-xl">
          <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent pointer-events-none" />

          {/* Avatar with fallback */}
          <div className="shrink-0">
            <div className="relative inline-block">
              <img
                src="/founder_avatar.jpg"
                alt="Itsub Alemayehu - Founder & Lead Architect"
                className="w-32 h-32 rounded-full object-cover border-2 border-emerald-500 shadow-[0_0_25px_rgba(16,185,129,0.25)] cursor-pointer"
                onClick={() => window.open('/founder_avatar.jpg', '_blank')}
                onError={(e) => {
                  const img = e.target as HTMLImageElement
                  img.onerror = null
                  img.src = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='128' height='128' viewBox='0 0 24 24' fill='none' stroke='%2310b981' stroke-width='1.5'%3E%3Ccircle cx='12' cy='8' r='5'/%3E%3Cpath d='M20 21a8 8 0 0 0-16 0'/%3E%3C/svg%3E`
                }}
              />
              <span className="absolute bottom-1 right-1 w-4 h-4 bg-emerald-500 border-2 border-black rounded-full" title="Active Core Engineer" />
            </div>
          </div>

          {/* Details & Founder Statement */}
          <div className="flex-1 text-center md:text-left space-y-4">
            <div>
              <div className="flex flex-wrap items-center justify-center md:justify-start gap-2.5 mb-1.5">
                <h3 className="text-2xl sm:text-3xl font-bold text-white font-sans">Itsub Alemayehu</h3>
                <span className="px-2.5 py-0.5 bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-mono text-[11px] font-bold rounded-full">
                  FOUNDER &amp; LEAD ARCHITECT
                </span>
              </div>
              <p className="text-xs font-mono text-amber-400">
                Autonomous Systems Laboratory &bull; Bartholomew Trust Protocol Lead
              </p>
            </div>

            <div className="space-y-3.5 text-sm text-zinc-300 leading-relaxed font-sans text-left">
              {/* Where We Started */}
              <div className="p-3.5 rounded-xl bg-black/60 border border-zinc-800">
                <span className="text-[11px] font-mono font-bold text-amber-400 block uppercase tracking-wider mb-1">
                  [ 01 &middot; Where We Started ]
                </span>
                <p className="text-xs sm:text-sm text-zinc-400 leading-relaxed">
                  Prompt engineering and secondary observer LLMs broke down the moment autonomous agents started executing terminal commands, touching production data, and moving capital. We founded Bartholomew on a fundamental engineering principle: autonomous agent safety requires deterministic boundaries in local memory and compiler-grade AST inspection before commands ever touch the operating system.
                </p>
              </div>

              {/* Where We Are (v5.4) */}
              <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/40 shadow-[0_0_20px_rgba(16,185,129,0.08)]">
                <span className="text-[11px] font-mono font-bold text-emerald-400 block uppercase tracking-wider mb-1 flex items-center justify-between">
                  <span>[ 02 &middot; Where We Are &middot; BTP v5.4 ]</span>
                  <span className="text-[10px] bg-emerald-500/20 px-2 py-0.5 rounded border border-emerald-500/30 font-mono font-bold">CURRENT PRODUCTION RUNTIME</span>
                </span>
                <p className="text-xs sm:text-sm text-zinc-200 leading-relaxed">
                  With <strong>BTP v5.4</strong>, we delivered a comprehensive sovereign trust protocol. We unified the fastest and most reliable in-memory local AST safety gating, zero prompt leakage, cryptographic agent passports, and cross-tenant SLA escrows with Zero-Knowledge Task Completion Proofs (zk-TCP). Autonomous agents can now collaborate across enterprise borders, build decentralized reputation via EigenTrust, and bridge capital atomically across Base, Arbitrum, and Bitcoin Lightning—with <strong>100% clean test passes across 2,791 automated regression suites</strong>.
                </p>
              </div>

              {/* Where We're Headed */}
              <div className="p-3.5 rounded-xl bg-black/60 border border-zinc-800">
                <span className="text-[11px] font-mono font-bold text-cyan-400 block uppercase tracking-wider mb-1">
                  [ 03 &middot; Where We're Headed &middot; Planetary Agent Economy ]
                </span>
                <p className="text-xs sm:text-sm text-zinc-400 leading-relaxed">
                  We are building the <strong>Autonomous Circularity Network (ACN)</strong>—a decentralized, self-healing substrate where millions of specialized AI agents discover peers, negotiate zero-knowledge tool delegations, and settle commercial tasks with mathematical finality and zero human friction.
                </p>
              </div>

              <p className="text-xs text-zinc-500 font-mono pt-1">
                "When your agents build the future, Bartholomew makes sure they don't break the present."
              </p>
            </div>

            <div className="pt-2 border-t border-zinc-800 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
              <div className="flex items-center gap-2 text-zinc-400">
                <Globe size={13} className="text-cyan-400" />
                <span>Domain: <a href="https://bartholomew.info" className="text-white hover:underline">bartholomew.info</a></span>
              </div>
              <div className="flex items-center gap-2 text-zinc-400">
                <Mail size={13} className="text-amber-400" />
                <span>Contact: <a href="mailto:itsub@bartholomew.info" className="text-white hover:underline">itsub@bartholomew.info</a></span>
              </div>
            </div>

            {/* Verifiable Links */}
            <div className="pt-3 flex flex-wrap gap-2.5 justify-center md:justify-start">
              <a
                href="https://github.com/ivegotahunnitonit"
                target="_blank"
                rel="noopener noreferrer"
                className="px-3.5 py-2 bg-black border border-zinc-800 hover:border-emerald-500 text-xs font-mono text-zinc-300 hover:text-white rounded-xl transition inline-flex items-center gap-2 shadow-sm"
              >
                <Code2 size={14} className="text-emerald-400" />
                <span>GitHub Profile</span>
                <ExternalLink size={11} className="text-zinc-500" />
              </a>

              <a
                href="https://doi.org/10.5281/zenodo.18843719"
                target="_blank"
                rel="noopener noreferrer"
                className="px-3.5 py-2 bg-black border border-zinc-800 hover:border-emerald-500 text-xs font-mono text-zinc-300 hover:text-white rounded-xl transition inline-flex items-center gap-2 shadow-sm"
              >
                <Award size={14} className="text-cyan-400" />
                <span>Zenodo Academic Archive</span>
                <ExternalLink size={11} className="text-zinc-500" />
              </a>
            </div>
          </div>
        </div>

        {/* Protocol Evolution Timeline Showcase */}
        <div className="rounded-2xl p-6 sm:p-8 bg-black/60 border border-zinc-800 shadow-xl backdrop-blur-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-zinc-800 mb-6">
            <div>
              <div className="text-xs font-mono font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-2 mb-1">
                <Layers size={14} className="text-emerald-400" />
                <span>[ PROTOCOL RELEASE EVOLUTION &amp; ROADMAP ]</span>
              </div>
              <h3 className="text-xl sm:text-2xl font-bold text-white font-sans">
                Progressive Sovereign Capability Delivery
              </h3>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-bold">
                2,791 Automated Tests Passing
              </span>
            </div>
          </div>

          {/* Timeline Selector Buttons */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 mb-6">
            {UPCOMING_MILESTONES.map((m, idx) => {
              const isSelected = selectedMilestone === idx
              return (
                <button
                  key={m.version}
                  onClick={() => setSelectedMilestone(idx)}
                  className={`p-3 rounded-xl text-left border transition-all ${
                    isSelected
                      ? 'bg-emerald-500/15 border-emerald-500/80 text-white shadow-[0_0_15px_rgba(16,185,129,0.15)]'
                      : 'bg-zinc-900/60 border-zinc-800 text-zinc-400 hover:text-white hover:border-zinc-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono text-xs font-bold text-white">{m.version}</span>
                    <span className={`text-[8px] font-mono font-bold px-1.5 py-0.2 rounded ${
                      m.status === 'LIVE' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'
                    }`}>
                      {m.status}
                    </span>
                  </div>
                  <div className="text-[10px] font-mono text-zinc-500 truncate">{m.timeline}</div>
                </button>
              )
            })}
          </div>

          {/* Selected Milestone Detail Pane */}
          {UPCOMING_MILESTONES[selectedMilestone] && (
            <div className="p-5 rounded-xl bg-zinc-900/80 border border-zinc-800 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    {UPCOMING_MILESTONES[selectedMilestone].version}
                  </span>
                  <h4 className="text-base font-bold text-white">
                    {UPCOMING_MILESTONES[selectedMilestone].title}
                  </h4>
                </div>
                <span className="text-xs font-mono text-zinc-400">
                  {UPCOMING_MILESTONES[selectedMilestone].timeline}
                </span>
              </div>

              <ul className="grid grid-cols-1 md:grid-cols-2 gap-2.5 pt-2">
                {UPCOMING_MILESTONES[selectedMilestone].highlights.map((h, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-zinc-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                    <span>{h}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

      </div>
    </section>
  )
}
