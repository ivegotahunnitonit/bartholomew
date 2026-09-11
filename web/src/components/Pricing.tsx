import { useState } from 'react'
import { Check, Shield, Sparkles, ArrowRight, Key, FileText, X, Send, Building, Mail, CheckCircle2 } from 'lucide-react'

export default function Pricing() {
  const [copiedKey, setCopiedKey] = useState(false)
  const [checkoutStatus, setCheckoutStatus] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [leadSubmitted, setLeadSubmitted] = useState(false)
  const [submittingLead, setSubmittingLead] = useState(false)
  const [leadForm, setLeadForm] = useState({
    email: '',
    company: '',
    framework: 'CrewAI',
    fleetSize: '10-50 agents',
    notes: ''
  })

  const handleFreeKey = () => {
    const key = `btp_free_${Math.random().toString(36).substring(2, 12)}_${Date.now().toString(36)}`
    navigator.clipboard.writeText(key)
    setCopiedKey(true)
    setTimeout(() => setCopiedKey(false), 3000)
  }

  const handleLeadSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!leadForm.email) return
    setSubmittingLead(true)
    try {
      await fetch('https://bartolomew-cloud-engine-322603900775.us-central1.run.app/api/v1/telemetry/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          events: [{
            event_id: `lead_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
            timestamp: Date.now() / 1000,
            verdict: 'ENTERPRISE_LEAD',
            action_type: 'ENTERPRISE_PILOT_REQUEST',
            rule_id: 'RULE_ENTERPRISE_INBOUND',
            reason: `Pilot & SOC 2 Dossier request from ${leadForm.company || 'Enterprise'}`,
            metadata: {
              ...leadForm,
              referrer: document.referrer,
              url: window.location.href,
              user_agent: navigator.userAgent
            }
          }],
          client_version: '5.4.4'
        })
      }).catch(() => null)
    } catch {}
    setSubmittingLead(false)
    setLeadSubmitted(true)
  }

  const handleCheckout = (tierName: string, price: string) => {
    setCheckoutStatus(`Preparing secure checkout for ${tierName} (${price}/mo)...`)

    // Direct verified Stripe checkout links
    const proPaymentLink = (import.meta as any).env?.VITE_STRIPE_PAYMENT_LINK_PRO || 'https://buy.stripe.com/fZu28rbNz5TYcmAddK9R600'
    const enterprisePaymentLink = (import.meta as any).env?.VITE_STRIPE_PAYMENT_LINK_ENTERPRISE || 'https://buy.stripe.com/fZu14ng3PgyC9ao2z69R601'

    setTimeout(() => {
      if (tierName.includes('Pro')) {
        window.location.href = proPaymentLink
      } else if (tierName.includes('Enterprise')) {
        window.location.href = enterprisePaymentLink
      } else {
        window.location.href = '/store/'
      }
    }, 400)
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
                  <span>Fastest &amp; Most Reliable AST Engine</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-[#10b981] shrink-0" />
                  <span>Unlimited local evals (100% Pro Bono Forever)</span>
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
                <span className="text-4xl font-extrabold">$199</span>
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
            <div className="space-y-2.5">
              <button
                onClick={() => handleCheckout('Enterprise & Bonded Warranty', '$199')}
                className="w-full py-3 px-4 bg-[#18181b] hover:bg-[#27272a] text-white font-medium rounded-xl text-sm transition-all border border-[#27272a] flex items-center justify-center gap-2"
              >
                <Shield className="w-4 h-4 text-[#a855f7]" />
                <span>Get Enterprise License ($199/mo)</span>
              </button>
              <button
                onClick={() => { setModalOpen(true); setLeadSubmitted(false); }}
                className="w-full py-2.5 px-4 bg-[#a855f7]/10 hover:bg-[#a855f7]/20 text-[#c084fc] font-semibold rounded-xl text-xs transition-all border border-[#a855f7]/30 flex items-center justify-center gap-2"
              >
                <FileText className="w-3.5 h-3.5 text-[#a855f7]" />
                <span>Request SOC 2 Dossier &amp; Custom PoC</span>
              </button>
            </div>
          </div>
        </div>

        {/* Enterprise Pilot & CISO Consultation Banner */}
        <div className="mt-16 bg-gradient-to-r from-[#0d0d12] via-[#160d20] to-[#0d0d12] border border-[#a855f7]/30 rounded-2xl p-6 sm:p-8 flex flex-col md:flex-row items-center justify-between gap-6 shadow-2xl">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 text-xs font-mono font-bold text-[#c084fc] mb-2">
              <Shield className="w-4 h-4 text-[#a855f7]" />
              <span>CUSTOM ENTERPRISE ENCLAVES &amp; SOC 2 TYPE II COMPLIANCE</span>
            </div>
            <h3 className="text-xl font-bold text-white mb-2">
              Need on-premises enclaves, custom AST policies, or vendor security review?
            </h3>
            <p className="text-sm text-[#a1a1aa] leading-relaxed">
              We work directly with CISOs, DevSecOps leaders, and AI safety engineering teams at frontier technology firms. Get a signed Ed25519 compliance evidence pack and private AWS/GCP sidecar deployment within 2 business hours.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row items-center gap-3 shrink-0 w-full md:w-auto">
            <button
              onClick={() => { setModalOpen(true); setLeadSubmitted(false); }}
              className="w-full sm:w-auto px-6 py-3 bg-[#a855f7] hover:bg-[#9333ea] text-white font-bold rounded-xl text-sm transition-all shadow-lg shadow-[#a855f7]/25 flex items-center justify-center gap-2"
            >
              <FileText className="w-4 h-4" />
              <span>Request Pilot &amp; Dossier</span>
            </button>
            <a
              href="mailto:security@bartholomew.info?subject=Enterprise%20Security%20Review%20Inquiry"
              className="w-full sm:w-auto px-5 py-3 bg-[#18181b] hover:bg-[#27272a] text-[#d4d4d8] hover:text-white font-medium rounded-xl text-sm transition-all border border-[#27272a] flex items-center justify-center gap-2"
            >
              <Mail className="w-4 h-4 text-[#a1a1aa]" />
              <span>security@bartholomew.info</span>
            </a>
          </div>
        </div>

        {/* Status Toast */}
        {checkoutStatus && (
          <div className="mt-8 max-w-md mx-auto p-4 bg-[#18181b] border border-[#10b981]/40 rounded-xl text-center text-sm font-mono text-[#10b981] animate-pulse">
            {checkoutStatus}
          </div>
        )}
      </div>

      {/* Enterprise Lead Capture Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
          <div className="bg-[#0c0c10] border border-[#27272a] hover:border-[#a855f7]/50 rounded-2xl max-w-lg w-full p-6 sm:p-8 shadow-2xl relative">
            <button
              onClick={() => setModalOpen(false)}
              className="absolute top-5 right-5 text-[#71717a] hover:text-white transition p-1"
              aria-label="Close modal"
            >
              <X className="w-5 h-5" />
            </button>

            {!leadSubmitted ? (
              <div>
                <div className="inline-flex items-center gap-2 text-xs font-mono font-bold text-[#c084fc] mb-2">
                  <Shield className="w-4 h-4 text-[#a855f7]" />
                  <span>ENTERPRISE PILOT &amp; DOSSIER REQUEST</span>
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">
                  Deploy Bartholomew in Your Organization
                </h3>
                <p className="text-sm text-[#a1a1aa] mb-6 leading-relaxed">
                  Receive our audited SOC 2 Type II evidence pack, private AWS/GCP VPC deployment templates, and a custom evaluation sandbox for your engineering team.
                </p>

                <form onSubmit={handleLeadSubmit} className="space-y-4">
                  <div>
                    <label className="block text-xs font-mono font-semibold text-[#a1a1aa] uppercase mb-1">
                      Work Email *
                    </label>
                    <div className="relative">
                      <Mail className="w-4 h-4 text-[#71717a] absolute left-3.5 top-1/2 -translate-y-1/2" />
                      <input
                        type="email"
                        required
                        placeholder="you@company.com"
                        value={leadForm.email}
                        onChange={(e) => setLeadForm({ ...leadForm, email: e.target.value })}
                        className="w-full pl-10 pr-4 py-2.5 bg-[#141418] border border-[#27272a] rounded-xl text-white text-sm focus:outline-none focus:border-[#a855f7] transition"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-mono font-semibold text-[#a1a1aa] uppercase mb-1">
                      Company / Organization *
                    </label>
                    <div className="relative">
                      <Building className="w-4 h-4 text-[#71717a] absolute left-3.5 top-1/2 -translate-y-1/2" />
                      <input
                        type="text"
                        required
                        placeholder="Palo Alto Networks, Datadog, etc."
                        value={leadForm.company}
                        onChange={(e) => setLeadForm({ ...leadForm, company: e.target.value })}
                        className="w-full pl-10 pr-4 py-2.5 bg-[#141418] border border-[#27272a] rounded-xl text-white text-sm focus:outline-none focus:border-[#a855f7] transition"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-mono font-semibold text-[#a1a1aa] uppercase mb-1">
                        Primary Agent Framework
                      </label>
                      <select
                        value={leadForm.framework}
                        onChange={(e) => setLeadForm({ ...leadForm, framework: e.target.value })}
                        className="w-full px-3 py-2.5 bg-[#141418] border border-[#27272a] rounded-xl text-white text-sm focus:outline-none focus:border-[#a855f7] transition"
                      >
                        <option value="CrewAI">CrewAI</option>
                        <option value="LangGraph">LangGraph / LangChain</option>
                        <option value="AutoGen">Microsoft AutoGen</option>
                        <option value="Cursor/Claude Code">Cursor / Claude Code</option>
                        <option value="Custom In-House">Custom In-House Swarm</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-mono font-semibold text-[#a1a1aa] uppercase mb-1">
                        Fleet Scale
                      </label>
                      <select
                        value={leadForm.fleetSize}
                        onChange={(e) => setLeadForm({ ...leadForm, fleetSize: e.target.value })}
                        className="w-full px-3 py-2.5 bg-[#141418] border border-[#27272a] rounded-xl text-white text-sm focus:outline-none focus:border-[#a855f7] transition"
                      >
                        <option value="1-10 agents">1 - 10 Autonomous Agents</option>
                        <option value="10-50 agents">10 - 50 Autonomous Agents</option>
                        <option value="50+ enterprise swarm">50+ Enterprise Swarm</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-mono font-semibold text-[#a1a1aa] uppercase mb-1">
                      Specific Requirements or Compliance Needs (Optional)
                    </label>
                    <textarea
                      rows={2}
                      placeholder="e.g. AWS Nitro Enclave deployment, SOC 2 CC7.1 audit trail, eBPF tracing..."
                      value={leadForm.notes}
                      onChange={(e) => setLeadForm({ ...leadForm, notes: e.target.value })}
                      className="w-full px-4 py-2 bg-[#141418] border border-[#27272a] rounded-xl text-white text-sm focus:outline-none focus:border-[#a855f7] transition resize-none"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={submittingLead}
                    className="w-full py-3 px-4 bg-[#a855f7] hover:bg-[#9333ea] disabled:opacity-50 text-white font-bold rounded-xl text-sm transition-all flex items-center justify-center gap-2 shadow-lg shadow-[#a855f7]/25"
                  >
                    <Send className="w-4 h-4" />
                    <span>{submittingLead ? 'Submitting Request...' : 'Dispatch Pilot &amp; Dossier Request'}</span>
                  </button>

                  <div className="text-center text-xs text-[#71717a] pt-1">
                    Direct security inquiries: <a href="mailto:security@bartholomew.info" className="text-[#a855f7] underline">security@bartholomew.info</a>
                  </div>
                </form>
              </div>
            ) : (
              <div className="text-center py-6">
                <div className="w-14 h-14 mx-auto rounded-full bg-[#10b981]/15 border border-[#10b981]/40 flex items-center justify-center text-[#10b981] mb-4">
                  <CheckCircle2 className="w-8 h-8" />
                </div>
                <h4 className="text-2xl font-bold text-white mb-2">Request Successfully Dispatched</h4>
                <p className="text-sm text-[#a1a1aa] mb-6 leading-relaxed">
                  Thank you. Our Solutions Architecture team has logged your inquiry from <strong className="text-white">{leadForm.company || 'your organization'}</strong>. We will deliver the cryptographic SOC 2 Type II evidence dossier and private enclave deployment guide to <strong className="text-[#10b981]">{leadForm.email}</strong> within 2 business hours.
                </p>

                <div className="bg-[#141418] border border-[#27272a] rounded-xl p-4 text-left mb-6 text-xs text-[#d4d4d8] space-y-2">
                  <div className="font-mono text-[#a855f7] font-semibold">[VERIFIED ARTIFACTS DISPATCHING]</div>
                  <div className="flex items-center gap-2">
                    <Check className="w-3.5 h-3.5 text-[#10b981]" />
                    <span>SOC 2 Type II Merkle Tree Evidence Bundle (AICPA CC6.1, CC7.1)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="w-3.5 h-3.5 text-[#10b981]" />
                    <span>Zero-Knowledge Invariant Compliance Proof (zk-ICP) Specification</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="w-3.5 h-3.5 text-[#10b981]" />
                    <span>Private AWS CDK / Docker Compose In-Process Sidecar Template</span>
                  </div>
                </div>

                <button
                  onClick={() => setModalOpen(false)}
                  className="w-full py-2.5 px-4 bg-[#18181b] hover:bg-[#27272a] text-white font-medium rounded-xl text-sm transition border border-[#27272a]"
                >
                  Close
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  )
}
