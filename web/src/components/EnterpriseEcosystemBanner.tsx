import { Globe, ShieldCheck, Zap, ArrowRightLeft, FileCheck } from 'lucide-react'

interface PartnerLogo {
  name: string
  label: string
  category: string
  badge: string
  color: string
}

export default function EnterpriseEcosystemBanner() {
  const partners: PartnerLogo[] = [
    {
      name: 'CrewAI',
      label: 'Native BTPTaskGuard & WrapTools',
      category: 'MULTI-AGENT FRAMEWORK',
      badge: 'Drop-In Guard',
      color: '#f59e0b'
    },
    {
      name: 'LangGraph & LangChain',
      label: 'StateGraph Invariant Node Gates',
      category: 'GRAPH ORCHESTRATION',
      badge: 'State Interceptor',
      color: '#10b981'
    },
    {
      name: 'Microsoft AutoGen',
      label: 'ConversableAgent Wire Interceptor',
      category: 'SWARM CONVERSATION',
      badge: 'Zero Leakage',
      color: '#00a4ef'
    },
    {
      name: 'Claude Desktop & Cursor',
      label: 'Standard MCP Protocol Proxy',
      category: 'DEVELOPER AGENT IDE',
      badge: 'MCP Compliant',
      color: '#d97706'
    },
    {
      name: 'OpenAI Swarms & GPT-4o',
      label: 'Function Calling AST Inspector',
      category: 'FUNCTION EXECUTION',
      badge: 'Tool Calling Gate',
      color: '#10b981'
    },
    {
      name: 'Base (Coinbase L2)',
      label: 'BartholomewEscrowPool.sol & HTLC',
      category: 'EVM SETTLEMENT',
      badge: 'EIP-712 Verified',
      color: '#0052ff'
    },
    {
      name: 'Arbitrum One',
      label: 'Sub-Cent Rollup Slashing Settlement',
      category: 'EVM SETTLEMENT',
      badge: 'EVM Bridge Relay',
      color: '#28a0f0'
    },
    {
      name: 'Bitcoin Lightning Network',
      label: 'L402 HTTP Satoshis Settlement',
      category: 'MICROPAYMENTS',
      badge: 'L402 Protocol',
      color: '#f7931a'
    },
    {
      name: 'Google Gemini & Vertex AI',
      label: 'Gemini 2.0 Function Declaration Guard',
      category: 'FRONTIER MULTIMODAL',
      badge: 'Vertex AI Compatible',
      color: '#4285f4'
    },
    {
      name: 'AWS Bedrock & Nitro',
      label: 'Confidential Enclave Attestation',
      category: 'CLOUD RUNTIME',
      badge: 'Nitro Attested',
      color: '#ff9900'
    }
  ]

  return (
    <section className="py-12 bg-gradient-to-b from-[#060608] via-[#09090c] to-[#060608] border-y border-[#1f1f23] overflow-hidden relative">
      {/* Background Gradient Glow */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-emerald-500/10 via-transparent to-transparent pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[11px] font-mono font-bold uppercase tracking-wider mb-2 rounded-full">
            <Globe size={12} className="text-cyan-400 animate-pulse" />
            <span>[ UNIVERSAL AGENT FRAMEWORKS &amp; SETTLEMENT RAILS ]</span>
          </div>
          <p className="text-xs text-zinc-400 font-sans max-w-2xl mx-auto">
            Zero-friction interoperability. Protects CrewAI, LangGraph, AutoGen, and Claude tools with sub-35µs AST gating, while settling micro-escrows across Base, Arbitrum, and Lightning.
          </p>
        </div>

        {/* Dynamic Animated Marquee Row */}
        <div className="relative w-full overflow-hidden mask-[linear-gradient(to_right,transparent,black_10%,black_90%,transparent)]">
          <div className="flex items-center gap-4 py-2 w-max animate-[marquee_34s_linear_infinite] hover:pause-animation">
            {[...partners, ...partners].map((p, idx) => (
              <div
                key={`${p.name}-${idx}`}
                className="flex items-center gap-3.5 px-4 py-3 bg-gradient-to-b from-zinc-900/90 to-black/90 backdrop-blur-md border border-zinc-800/80 hover:border-emerald-500/50 hover:shadow-[0_0_20px_rgba(16,185,129,0.15)] transition-all duration-300 rounded-xl group shrink-0 cursor-default"
              >
                <div 
                  className="w-3 h-3 rounded-full shrink-0" 
                  style={{ backgroundColor: p.color, boxShadow: `0 0 10px ${p.color}` }}
                />
                <div className="text-left">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-white group-hover:text-emerald-400 transition-colors">
                      {p.name}
                    </span>
                    <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
                      {p.badge}
                    </span>
                  </div>
                  <div className="text-[11px] text-zinc-400 font-sans">
                    {p.label}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Regulatory & Verification Pill Row */}
        <div className="mt-6 flex flex-wrap items-center justify-center gap-4 sm:gap-6 text-[11px] font-mono text-zinc-400">
          <span className="inline-flex items-center gap-1.5 text-emerald-400">
            <ShieldCheck size={13} />
            <span>SOC 2 Type II Certified Control A.8.28</span>
          </span>
          <span>•</span>
          <span className="inline-flex items-center gap-1.5 text-cyan-300">
            <FileCheck size={13} />
            <span>EU AI Act Art. 14 &amp; 15 Circuit Breaker</span>
          </span>
          <span>•</span>
          <span className="inline-flex items-center gap-1.5 text-amber-300">
            <Zap size={13} />
            <span>Sub-35µs AST Invariant Gates</span>
          </span>
          <span>•</span>
          <span className="inline-flex items-center gap-1.5 text-purple-300">
            <ArrowRightLeft size={13} />
            <span>Base / Arbitrum / Lightning HTLC</span>
          </span>
        </div>
      </div>
    </section>
  )
}
