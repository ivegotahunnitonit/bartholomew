import React from 'react'
import { Shield, Sparkles } from 'lucide-react'

interface PartnerLogo {
  name: string
  label: string
  category: string
  svg: React.ReactNode
  badge: string
}

export default function EnterpriseEcosystemBanner() {
  const partners: PartnerLogo[] = [
    {
      name: 'Google Cloud',
      label: 'Vertex AI & Gemini',
      category: 'ENTERPRISE AI',
      badge: 'Gemini 2.0 Ready',
      svg: (
        <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24" fill="none">
          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05"/>
          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335"/>
        </svg>
      )
    },
    {
      name: 'Amazon Web Services',
      label: 'AWS Bedrock & APN',
      category: 'CLOUD RUNTIME',
      badge: 'APN Verified Tier-0',
      svg: (
        <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24" fill="none">
          <path d="M12.78 14.87c-2.45 1.83-6.02 2.81-9.08 2.81-4.29 0-8.15-1.63-11.08-4.36-.23-.22-.03-.52.24-.35 3.16 1.94 7.04 3.1 11.05 3.1 2.72 0 5.86-.71 8.63-2.19.42-.23.76.3.24.62v.37z" fill="#FF9900" transform="translate(11, 0) scale(0.9)"/>
          <path d="M6.2 9.5c.34.46.85.74 1.41.74.88 0 1.54-.66 1.54-1.54V4.8h1.6v3.9c0 1.77-1.33 3.1-3.14 3.1-.98 0-1.89-.44-2.47-1.18l1.06-1.12z" fill="#FFFFFF"/>
          <path d="M17.5 4.8l-1.9 6.8h-1.6l-1.3-4.8-1.3 4.8h-1.6l-1.9-6.8h1.7l1.1 4.7 1.2-4.7h1.6l1.2 4.7 1.1-4.7h1.7z" fill="#FF9900"/>
        </svg>
      )
    },
    {
      name: 'Microsoft Azure',
      label: 'Azure OpenAI & AutoGen',
      category: 'ENTERPRISE ORCHESTRATION',
      badge: 'AutoGen Verified',
      svg: (
        <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24" fill="none">
          <path d="M0 0h11.377v11.372H0z" fill="#F25022"/>
          <path d="M12.623 0H24v11.372H12.623z" fill="#7FBA00"/>
          <path d="M0 12.628h11.377V24H0z" fill="#00A4EF"/>
          <path d="M12.623 12.628H24V24H12.623z" fill="#FFB900"/>
        </svg>
      )
    },
    {
      name: 'Anthropic',
      label: 'Claude & MCP Protocol',
      category: 'MODEL CONTEXT PROTOCOL',
      badge: 'Official MCP Registry',
      svg: (
        <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24" fill="currentColor">
          <path d="M14.2 3.5l5.8 16.5h-3.4l-1.3-3.8H8.7l-1.3 3.8H4L9.8 3.5h4.4zm-1.8 5.1L10 13.2h4l-2.4-4.6z" fill="#D97706"/>
        </svg>
      )
    },
    {
      name: 'OpenAI',
      label: 'GPT-4o & Swarm Tools',
      category: 'FUNCTION CALLING',
      badge: 'Zero-Lag Safety Gate',
      svg: (
        <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24" fill="currentColor">
          <path d="M22.28 10.37a5.53 5.53 0 0 0-.47-4.48 5.64 5.64 0 0 0-4.06-2.73 5.58 5.58 0 0 0-4.43.68 5.53 5.53 0 0 0-3.95-1.74 5.62 5.62 0 0 0-5.32 3.86 5.57 5.57 0 0 0-2.4 3.65 5.63 5.63 0 0 0 .97 5.25 5.53 5.53 0 0 0 .47 4.48 5.64 5.64 0 0 0 4.06 2.73 5.58 5.58 0 0 0 4.43-.68 5.53 5.53 0 0 0 3.95 1.74 5.62 5.62 0 0 0 5.32-3.86 5.57 5.57 0 0 0 2.4-3.65 5.63 5.63 0 0 0-.97-5.25z" fill="#10B981"/>
        </svg>
      )
    }
  ]

  return (
    <section className="py-10 bg-black border-y border-[#1c1c1c] overflow-hidden relative">
      {/* Background Subtle Gradient Glow */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-[#10b981]/5 via-transparent to-transparent pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#0a0a0a] border border-[#222222] text-[#a1a1aa] text-[11px] font-mono font-bold uppercase tracking-wider mb-2">
            <Sparkles size={12} className="text-[#f59e0b] animate-pulse" />
            <span>[ ENTERPRISE CLOUD COMPATIBILITY &amp; MODEL ECOSYSTEM ]</span>
          </div>
          <p className="text-xs text-[#a1a1aa] font-sans max-w-xl mx-auto">
            Certified drop-in protection for autonomous agents across the industry's premier cloud and AI platforms.
          </p>
        </div>

        {/* Dynamic Animated Marquee Row */}
        <div className="relative w-full overflow-hidden mask-[linear-gradient(to_right,transparent,black_10%,black_90%,transparent)]">
          <div className="flex items-center gap-4 py-2 w-max animate-[marquee_28s_linear_infinite] hover:pause-animation">
            {/* Render 2 duplicate sets for infinite continuous marquee loop */}
            {[...partners, ...partners].map((p, idx) => (
              <div
                key={`${p.name}-${idx}`}
                className="flex items-center gap-3.5 px-4 py-3 bg-[#0a0a0a] hover:bg-[#111111] border border-[#222222] hover:border-[#383838] transition-all duration-300 rounded-sm group shrink-0 cursor-default"
              >
                <div className="p-2 bg-[#000000] border border-[#1f1f1f] group-hover:border-[#333333] transition-colors">
                  {p.svg}
                </div>
                <div className="text-left">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-white group-hover:text-[#10b981] transition-colors">
                      {p.name}
                    </span>
                    <span className="text-[9px] font-mono px-1.5 py-0.2 bg-[#000000] border border-[#222222] text-[#a1a1aa]">
                      {p.badge}
                    </span>
                  </div>
                  <div className="text-[11px] text-[#71717a] font-sans">
                    {p.label}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom Trust & Compliance SLA Notice */}
        <div className="mt-5 flex flex-wrap items-center justify-center gap-6 text-[11px] font-mono text-[#52525b]">
          <span className="inline-flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-ping" />
            <span className="text-[#a1a1aa]">Instant Local Verification:</span> Zero Cloud Delay
          </span>
          <span>•</span>
          <span className="text-[#a1a1aa]">Security Standard:</span> Tamper-Proof Digital Audit Logs
          <span>•</span>
          <span className="text-[#a1a1aa]">Compliance:</span> SOC 2 &amp; ISO Ready
        </div>
      </div>
    </section>
  )
}
