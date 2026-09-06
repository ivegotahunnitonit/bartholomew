import type { ReactNode } from 'react'
import { Globe, ShieldCheck, Zap, FileCheck } from 'lucide-react'

interface PartnerLogo {
  name: string
  label: string
  category: string
  badge: string
  color: string
  icon: ReactNode
}

export default function EnterpriseEcosystemBanner() {
  const partners: PartnerLogo[] = [
    {
      name: 'CrewAI',
      label: 'Native BTPTaskGuard & WrapTools',
      category: 'MULTI-AGENT FRAMEWORK',
      badge: 'Drop-In Guard',
      color: '#f59e0b',
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none">
          <path d="M12 3L4 7.5v9L12 21l8-4.5v-9L12 3z" stroke="#f59e0b" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          <circle cx="9" cy="11" r="1.5" fill="#f59e0b" />
          <circle cx="15" cy="11" r="1.5" fill="#f59e0b" />
          <path d="M9 15h6" stroke="#f59e0b" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      )
    },
    {
      name: 'LangGraph & LangChain',
      label: 'StateGraph Invariant Node Gates',
      category: 'GRAPH ORCHESTRATION',
      badge: 'State Interceptor',
      color: '#10b981',
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none">
          <circle cx="6" cy="6" r="3" fill="#10b981" />
          <circle cx="18" cy="6" r="3" fill="#10b981" />
          <circle cx="12" cy="18" r="3" fill="#10b981" />
          <path d="M8.5 7.5l7 0M7.5 8.5l3.5 7M16.5 8.5l-3.5 7" stroke="#10b981" strokeWidth="1.75" strokeLinecap="round" />
        </svg>
      )
    },
    {
      name: 'Microsoft AutoGen',
      label: 'ConversableAgent Wire Interceptor',
      category: 'SWARM CONVERSATION',
      badge: 'Zero Leakage',
      color: '#00a4ef',
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none">
          <rect x="2" y="2" width="9" height="9" fill="#f25022" rx="1" />
          <rect x="13" y="2" width="9" height="9" fill="#7fba00" rx="1" />
          <rect x="2" y="13" width="9" height="9" fill="#00a4ef" rx="1" />
          <rect x="13" y="13" width="9" height="9" fill="#ffb900" rx="1" />
        </svg>
      )
    },
    {
      name: 'Claude Desktop & Cursor',
      label: 'Standard MCP Protocol Proxy',
      category: 'DEVELOPER AGENT IDE',
      badge: 'MCP Compliant',
      color: '#d97706',
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="#d97706">
          <path d="M13.8 2.2a1.8 1.8 0 0 0-3.6 0l-.3 4.8a1 1 0 0 1-.7.9L4.8 9.3a1.8 1.8 0 0 0 0 3.4l4.4 1.4a1 1 0 0 1 .7.9l.3 4.8a1.8 1.8 0 0 0 3.6 0l.3-4.8a1 1 0 0 1 .7-.9l4.4-1.4a1.8 1.8 0 0 0 0-3.4l-4.4-1.4a1 1 0 0 1-.7-.9l-.3-4.8z" />
        </svg>
      )
    },
    {
      name: 'OpenAI Swarms & GPT-4o',
      label: 'Function Calling AST Inspector',
      category: 'FUNCTION EXECUTION',
      badge: 'Tool Calling Gate',
      color: '#10b981',
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2a4 4 0 0 1 3.5 2.1l.5.9a4 4 0 0 1 1.5 5.5l-.5.9a4 4 0 0 1-2 5.3l-.9.5a4 4 0 0 1-5.6-1.5l-.5-.9a4 4 0 0 1-1.5-5.5l.5-.9a4 4 0 0 1 2-5.3l.9-.5A4 4 0 0 1 12 2z"/>
          <path d="M12 8v8m-4-6l8 4m-8 0l8-4"/>
        </svg>
      )
    },
    {
      name: 'Docker & Kubernetes',
      label: 'In-Process Container & Pod Isolation',
      category: 'CONTAINER DEFENSE',
      badge: 'Defense-in-Depth',
      color: '#2496ed',
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="#2496ed">
          <path d="M2.5 13.5c.3-1.6 1.4-2.8 2.8-3.2.3-.1.6-.1.9-.1h1.3V8.7h2.2v1.5h1.5V8.7h2.2v1.5h1.5V8.7h2.2v1.5h1.2c2.8 0 5.1 1.9 5.6 4.7.5 2.6-.8 5.1-3.2 6.1-3.6 1.5-7.7 1.3-11.2-.5-3.3-1.7-5.9-4.8-6.8-8.5z"/>
          <rect x="7" y="6" width="2.2" height="2" rx="0.3" fill="#2496ed"/>
          <rect x="10.2" y="6" width="2.2" height="2" rx="0.3" fill="#2496ed"/>
        </svg>
      )
    },
    {
      name: 'LlamaIndex Workflows',
      label: 'Event-Driven Pipeline AST Guard',
      category: 'RAG & WORKFLOWS',
      badge: 'Pipeline Gate',
      color: '#a855f7',
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="#a855f7" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <path d="M8 22v-6l-2-2V8a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2h2a2 2 0 0 1 2 2v2l-2 2v6" />
          <circle cx="10" cy="9" r="1.2" fill="#a855f7"/>
          <path d="M8 4l2 2m4-2l-2 2" />
        </svg>
      )
    },
    {
      name: 'LiteLLM & Local Models',
      label: 'Universal Model Wire Gateway',
      category: 'MODEL GATEWAY',
      badge: 'Zero Leakage',
      color: '#ec4899',
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="#ec4899" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
        </svg>
      )
    },
    {
      name: 'Google Gemini & Vertex AI',
      label: 'Gemini 2.0 Function Declaration Guard',
      category: 'FRONTIER MULTIMODAL',
      badge: 'Vertex AI Compatible',
      color: '#4285f4',
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M23.7 12.3c0-.8-.1-1.7-.2-2.3H12v4.6h6.6c-.3 1.5-1.1 2.8-2.4 3.7v3h3.9c2.3-2.1 3.6-5.2 3.6-9z"/>
          <path fill="#34A853" d="M12 24c3.2 0 6-1.1 8-3l-3.9-3c-1.1.7-2.5 1.2-4.1 1.2-3.1 0-5.8-2.1-6.7-4.9H1.3v3.1C3.3 21.4 7.4 24 12 24z"/>
          <path fill="#FBBC05" d="M5.3 14.3c-.2-.7-.4-1.5-.4-2.3s.2-1.6.4-2.3V6.6H1.3C.5 8.2 0 10 0 12s.5 3.8 1.3 5.4l4-3.1z"/>
          <path fill="#EA4335" d="M12 4.8c1.8 0 3.3.6 4.6 1.8l3.4-3.4C18 1.2 15.2 0 12 0 7.4 0 3.3 2.6 1.3 6.6l4 3.1c.9-2.8 3.6-4.9 6.7-4.9z"/>
        </svg>
      )
    },
    {
      name: 'AWS Bedrock & Containers',
      label: 'Runtime Invariant Attestation',
      category: 'CLOUD RUNTIME',
      badge: 'Enterprise Secured',
      color: '#ff9900',
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none">
          <path d="M4 16.5c3.5 2.5 8.5 2.8 12.5.5.5-.3 1.2.2 1 .8-.5 1.5-3.5 3.7-8 3.7-4.2 0-7.2-2.2-8-3.5-.3-.5.3-1.2.8-.9l1.7-.6z" fill="#ff9900"/>
          <path d="M18.8 16.2l1.7 1.8-2.5.4.8-2.2z" fill="#ff9900"/>
          <path d="M7 6l5-3 5 3v6l-5 3-5-3V6z" stroke="#ff9900" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      )
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
            <span>[ UNIVERSAL AGENT FRAMEWORKS &amp; RUNTIMES ]</span>
          </div>
          <p className="text-xs text-zinc-400 font-sans max-w-2xl mx-auto">
            Zero-friction interoperability. Protects CrewAI, LangGraph, AutoGen, Claude, and OpenAI tool dispatches with deterministic in-process AST invariant gating before execution hits the operating system or database.
          </p>
        </div>

        {/* Dynamic Animated Marquee Row */}
        <div className="relative w-full overflow-hidden mask-[linear-gradient(to_right,transparent,black_10%,black_90%,transparent)]">
          <div className="flex items-center gap-4 py-2 w-max animate-[marquee_34s_linear_infinite] hover:pause-animation">
            {[...partners, ...partners].map((p, idx) => (
              <div
                key={`${p.name}-${idx}`}
                className="flex items-center gap-3 px-4 py-2.5 bg-gradient-to-b from-zinc-900/90 to-black/90 backdrop-blur-md border border-zinc-800/80 hover:border-emerald-500/50 hover:shadow-[0_0_20px_rgba(16,185,129,0.15)] transition-all duration-300 rounded-xl group shrink-0 cursor-default"
              >
                {/* Dedicated SVG Company Logo Container */}
                <div 
                  className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0 bg-black/80 border border-zinc-800/80 group-hover:border-zinc-700 transition-all shadow-inner"
                  style={{ boxShadow: `0 0 12px ${p.color}15` }}
                >
                  {p.icon}
                </div>
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
            <span>SOC 2-Ready Control Framework</span>
          </span>
          <span>•</span>
          <span className="inline-flex items-center gap-1.5 text-cyan-300">
            <FileCheck size={13} />
            <span>EU AI Act Art. 14 &amp; 15 Circuit Breaker</span>
          </span>
          <span>•</span>
          <span className="inline-flex items-center gap-1.5 text-amber-300">
            <Zap size={13} />
            <span>Fastest &amp; Most Reliable AST Gating</span>
          </span>
          <span>•</span>
          <span className="inline-flex items-center gap-1.5 text-purple-300">
            <ShieldCheck size={13} />
            <span>Docker &amp; Container In-Process Defense</span>
          </span>
        </div>
      </div>
    </section>
  )
}
