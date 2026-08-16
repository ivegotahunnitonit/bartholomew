import {
  ShieldCheck,
  TrendingUp,
  FileCheck,
  Zap,
  Server,
  Layers,
  CheckCircle2,
  Cpu
} from 'lucide-react'

export default function ExecutiveSummary() {
  return (
    <section id="executive-summary" className="py-24 px-5 sm:px-8 bg-slate-950/60 relative border-t border-white/5">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 mb-4">
            <FileCheck size={14} />
            Institutional Briefing
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4 font-heading">
            Executive Summary & <span className="gradient-text">Real-World ROI</span>
          </h2>
          <p className="text-base sm:text-lg text-slate-400">
            A defining breakdown of Bartholomew's enterprise security architecture, proactive dreaming capabilities, zero-infrastructure unit cost policy, and actionable deployment pathways.
          </p>
        </div>

        {/* 4 Core Pillars Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          <div className="glass-card p-6 rounded-2xl border border-white/10 space-y-3">
            <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 w-fit">
              <Zap size={22} />
            </div>
            <h3 className="text-lg font-bold text-white font-heading">Sub-Microsecond Speed</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              1.14 μs latency intercept guarantees zero impact on agent throughput while stopping OWASP LLM threats before LLM API invocation.
            </p>
          </div>

          <div className="glass-card p-6 rounded-2xl border border-white/10 space-y-3">
            <div className="p-3 rounded-xl bg-cyan-500/10 text-cyan-400 w-fit">
              <ShieldCheck size={22} />
            </div>
            <h3 className="text-lg font-bold text-white font-heading">SOC2 & OWASP Compliant</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Ed25519 signed JSON Evidence Artifacts establish audit compliance for enterprise insurance, SOC2, and ISO27001 requirements.
            </p>
          </div>

          <div className="glass-card p-6 rounded-2xl border border-white/10 space-y-3">
            <div className="p-3 rounded-xl bg-violet-500/10 text-violet-400 w-fit">
              <TrendingUp size={22} />
            </div>
            <h3 className="text-lg font-bold text-white font-heading">Exponential Scale Path</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Modular integration across local Python services, multi-agent frameworks, enterprise CI/CD gates, and sovereign cloud enclaves.
            </p>
          </div>

          <div className="glass-card p-6 rounded-2xl border border-white/10 space-y-3">
            <div className="p-3 rounded-xl bg-amber-500/10 text-amber-400 w-fit">
              <Server size={22} />
            </div>
            <h3 className="text-lg font-bold text-white font-heading">Zero-Cost Unit Economics</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Serverless Cloud Run + DePIN Akash provider nodes ensure zero out-of-pocket overhead while maintaining 99.99% uptime.
            </p>
          </div>
        </div>

        {/* Detailed Strategic Breakdown */}
        <div className="grid lg:grid-cols-12 gap-8 items-stretch">
          {/* Left Column: Business & Security Roadmap */}
          <div className="lg:col-span-7 glass-card p-8 rounded-2xl border border-white/10 space-y-6">
            <h3 className="text-2xl font-bold text-white font-heading flex items-center gap-2">
              <Layers size={22} className="text-emerald-400" />
              Strategic Implementation & Business Value
            </h3>

            <div className="space-y-4 text-xs text-slate-300">
              <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-1.5">
                <div className="flex justify-between font-bold text-sm text-white">
                  <span>1. Instant Developer Integration</span>
                  <span className="text-emerald-400 font-mono">Ready Today</span>
                </div>
                <p className="text-slate-400">
                  Engineers add <code className="text-emerald-400 font-mono">pip install bartholomew-eval</code> to Python services or import the TypeScript SDK for sub-microsecond prompt sanitization and token budget limits.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-1.5">
                <div className="flex justify-between font-bold text-sm text-white">
                  <span>2. Enterprise Security Audit & Certification</span>
                  <span className="text-cyan-400 font-mono">Automated CI/CD</span>
                </div>
                <p className="text-slate-400">
                  Enterprise client codebases are scanned for SAST, SCA, and IaC secrets. Automated PDF & HTML verification certificates are generated for institutional compliance.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-1.5">
                <div className="flex justify-between font-bold text-sm text-white">
                  <span>3. Autonomous Swarm Governance</span>
                  <span className="text-violet-400 font-mono">Sovereign Consensus</span>
                </div>
                <p className="text-slate-400">
                  Multi-agent teams (LangChain, CrewAI, AutoGen) run through Bayesian risk scoring to reach cryptographic consensus before executing financial or system-level transactions.
                </p>
              </div>
            </div>
          </div>

          {/* Right Column: Deployment Capability Matrix */}
          <div className="lg:col-span-5 glass-card p-8 rounded-2xl border border-white/10 space-y-6 flex flex-col justify-between">
            <div>
              <h3 className="text-2xl font-bold text-white font-heading flex items-center gap-2 mb-4">
                <Cpu size={22} className="text-cyan-400" />
                Operational Deployment Tiers
              </h3>

              <div className="space-y-3 font-mono text-xs">
                <div className="p-3.5 rounded-xl bg-slate-950 border border-white/10 flex justify-between items-center">
                  <div>
                    <span className="text-white font-bold block">Developer Engine</span>
                    <span className="text-slate-500 text-[11px]">PyPI Package &amp; Zero-Dependency Engine</span>
                  </div>
                  <span className="text-emerald-400 font-bold text-xs uppercase tracking-wider">Sub-Microsecond</span>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950 border border-white/10 flex justify-between items-center">
                  <div>
                    <span className="text-white font-bold block">Team Telemetry Suite</span>
                    <span className="text-slate-500 text-[11px]">Real-Time Dashboards &amp; Alert Routing</span>
                  </div>
                  <span className="text-cyan-400 font-bold text-xs uppercase tracking-wider">Live Telemetry</span>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950 border border-white/10 flex justify-between items-center">
                  <div>
                    <span className="text-white font-bold block">Institutional Audit Certifier</span>
                    <span className="text-slate-500 text-[11px]">Full SAST / SCA / Secret Verification</span>
                  </div>
                  <span className="text-violet-400 font-bold text-xs uppercase tracking-wider">Ed25519 Signed</span>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950 border border-white/10 flex justify-between items-center">
                  <div>
                    <span className="text-white font-bold block">Sovereign Enclave</span>
                    <span className="text-slate-500 text-[11px]">Air-Gapped On-Prem &amp; Private Cloud Node</span>
                  </div>
                  <span className="text-amber-400 font-bold text-xs uppercase tracking-wider">Air-Gapped</span>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 flex items-center gap-3">
              <CheckCircle2 size={20} className="shrink-0" />
              <span>Full compliance verified on Google Cloud Run + Firebase Hosting.</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
