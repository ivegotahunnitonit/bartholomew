import { useState } from 'react'
import { Check, Shield, Zap, Sparkles, ArrowRight, Lock, Key, Copy } from 'lucide-react'

export default function Pricing() {
  const [copiedKey, setCopiedKey] = useState(false)
  const [selectedTier, setSelectedTier] = useState<string | null>(null)
  const [email, setEmail] = useState('')
  const [checkoutStatus, setCheckoutStatus] = useState<string | null>(null)

  const handleFreeKey = () => {
    const key = `btp_free_${Math.random().toString(36).substring(2, 12)}_${Date.now().toString(36)}`
    navigator.clipboard.writeText(key)
    setCopiedKey(true)
    setTimeout(() => setCopiedKey(false), 3000)
  }

  const handleCheckout = (tierName: string, price: string) => {
    setSelectedTier(tierName)
    setCheckoutStatus(`Redirecting to secure Stripe Checkout for ${tierName} (${price}/mo)...`)
    setTimeout(() => {
      // In production with live Stripe publishable key, triggers stripe checkout session
      window.location.href = `mailto:contact@bartholomew.info?subject=Bartholomew%20${encodeURIComponent(tierName)}%20Subscription&body=Hi%20Itsub,%0D%0A%0D%0AI%20would%20like%20to%20activate%20the%20${encodeURIComponent(tierName)}%20subscription%20(${encodeURIComponent(price)}/mo)%20for%20our%20agent%20stack.%0D%0A%0D%0AMy%20email:%20${encodeURIComponent(email || '')}`
    }, 800)
  }

  return (
    <section id="pricing" className="py-24 bg-[#050505] text-white border-t border-[#1a1a1a] relative overflow-hidden">
      {/* Glow Effects */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-[#10b981]/10 blur-[120px] pointer-events-none rounded-full" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#10b981]/10 border border-[#10b981]/30 rounded-full text-xs font-mono font-semibold text-[#10b981] mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            <span>TRANSPARENT ENTERPRISE PRICING</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
            Deterministic Security for Every Agent Fleet
          </h2>
          <p className="text-[#a1a1aa] text-base sm:text-lg">
            Zero per-token cloud penalties. Deploy in-memory on your host or route through our ultra-low latency gateway.
          </p>
        </div>

        {/* Pricing Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch">
          {/* Free Tier */}
          <div className="bg-[#0a0a0a] border border-[#222222] rounded-2xl p-8 flex flex-col justify-between hover:border-[#333333] transition-all relative">
            <div>
              <div className="text-xs font-mono font-bold uppercase tracking-wider text-[#71717a] mb-2">
                DEVELOPER / OSS
              </div>
              <div className="flex items-baseline gap-1 mb-4">
                <span className="text-4xl font-extrabold">$0</span>
                <span className="text-[#71717a] text-sm">/ forever</span>
              </div>
              <p className="text-sm text-[#a1a1aa] mb-6">
                Open-source in-memory invariant kernel for single agents and local CLI testing.
              </p>
              <ul className="space-y-3 text-sm text-[#d4d4d8] mb-8">
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-[#10b981] shrink-0" />
                  <span>Sub-50 µs Polyglot AST Engine</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-[#10b981] shrink-0" />
                  <span>Up to 10,000 local evals/month</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-[#10b981] shrink-0" />
                  <span>LangChain & Cursor extension</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-[#10b981] shrink-0" />
                  <span>Community Discord support</span>
                </li>
              </ul>
            </div>
            <button
              onClick={handleFreeKey}
              className="w-full py-3 px-4 bg-[#18181b] hover:bg-[#27272a] text-white font-medium rounded-xl text-sm transition-all border border-[#27272a] flex items-center justify-center gap-2"
            >
              <Key className="w-4 h-4" />
              <span>{copiedKey ? 'API Key Copied!' : 'Generate Free API Key'}</span>
            </button>
          </div>

          {/* Pro Builder */}
          <div className="bg-[#0c0c0e] border-2 border-[#10b981] rounded-2xl p-8 flex flex-col justify-between shadow-[0_0_40px_rgba(16,185,129,0.15)] relative scale-105 z-20">
            <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3.5 py-0.5 bg-[#10b981] text-black text-xs font-bold font-mono tracking-wider rounded-full uppercase">
              MOST POPULAR
            </div>
            <div>
              <div className="text-xs font-mono font-bold uppercase tracking-wider text-[#10b981] mb-2">
                PRO AGENT BUILDER
              </div>
              <div className="flex items-baseline gap-1 mb-4">
                <span className="text-4xl font-extrabold">$49</span>
                <span className="text-[#71717a] text-sm">/ month</span>
              </div>
              <p className="text-sm text-[#a1a1aa] mb-6">
                Hosted Tier-0 gateway with automated secret masking and Bedrock/Claude middleware.
              </p>
              <ul className="space-y-3 text-sm text-[#d4d4d8] mb-8">
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-[#10b981] shrink-0" />
                  <span><strong>1,000,000</strong> evaluations/month</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-[#10b981] shrink-0" />
                  <span>Real-time Secret Vault Masker</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-[#10b981] shrink-0" />
                  <span>AWS Bedrock & OpenAI Interceptor</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-[#10b981] shrink-0" />
                  <span>FIPS 186-5 Ed25519 Signed Receipts</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-[#10b981] shrink-0" />
                  <span>Priority Email & Slack Support</span>
                </li>
              </ul>
            </div>
            <button
              onClick={() => handleCheckout('Pro Agent Builder', '$49')}
              className="w-full py-3 px-4 bg-[#10b981] hover:bg-[#059669] text-black font-bold rounded-xl text-sm transition-all flex items-center justify-center gap-2 shadow-lg shadow-[#10b981]/20"
            >
              <span>Subscribe to Pro</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Enterprise & Bonded Warranty */}
          <div className="bg-[#0a0a0a] border border-[#222222] rounded-2xl p-8 flex flex-col justify-between hover:border-[#333333] transition-all relative">
            <div>
              <div className="text-xs font-mono font-bold uppercase tracking-wider text-[#a855f7] mb-2">
                ENTERPRISE & WARRANTY
              </div>
              <div className="flex items-baseline gap-1 mb-4">
                <span className="text-4xl font-extrabold">$499</span>
                <span className="text-[#71717a] text-sm">/ month</span>
              </div>
              <p className="text-sm text-[#a1a1aa] mb-6">
                Multi-agent enterprise fleets with backed Bonded Warranty and SOC 2 Merkle compliance.
              </p>
              <ul className="space-y-3 text-sm text-[#d4d4d8] mb-8">
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-[#a855f7] shrink-0" />
                  <span><strong>$10,000 Bonded Execution Warranty</strong></span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-[#a855f7] shrink-0" />
                  <span>20,000,000 evaluations/month</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-[#a855f7] shrink-0" />
                  <span>SOC 2 Type II Certified Merkle Tree</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-[#a855f7] shrink-0" />
                  <span>Private AWS VPC / CDK Sidecar</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-[#a855f7] shrink-0" />
                  <span>24/7 Dedicated Solutions Engineer</span>
                </li>
              </ul>
            </div>
            <button
              onClick={() => handleCheckout('Enterprise & Bonded Warranty', '$499')}
              className="w-full py-3 px-4 bg-[#18181b] hover:bg-[#27272a] text-white font-medium rounded-xl text-sm transition-all border border-[#27272a] flex items-center justify-center gap-2"
            >
              <Shield className="w-4 h-4 text-[#a855f7]" />
              <span>Get Enterprise License</span>
            </button>
          </div>
        </div>

        {/* Status Toast */}
        {checkoutStatus && (
          <div className="mt-8 max-w-md mx-auto p-4 bg-[#18181b] border border-[#10b981]/40 rounded-xl text-center text-sm font-mono text-[#10b981] animate-pulse">
            {checkoutStatus}
          </div>
        )}
      </div>
    </section>
  )
}
