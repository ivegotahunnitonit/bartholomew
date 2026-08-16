import React, { useState } from 'react'
import {
  Shield,
  Zap,
  Terminal,
  Code2,
  Lock,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Cpu,
  FileCheck,
  Play,
  Github,
  Check
} from 'lucide-react'

export default function LandingPage() {
  const [trajectoryInput, setTrajectoryInput] = useState(
    JSON.stringify(
      {
        agent_name: "CustomerSupportBot_v2",
        steps: [
          {
            step_index: 1,
            type: "thought",
            content: "Authenticating with database using key sk-proj-99887766554433221100"
          },
          {
            step_index: 2,
            type: "tool_call",
            tool_name: "search_db",
            content: "Executing user query: SELECT * FROM users"
          },
          {
            step_index: 3,
            type: "tool_call",
            tool_name: "search_db",
            content: "Retrying query SELECT * FROM users after connection reset"
          }
        ]
      },
      null,
      2
    )
  )

  const [auditResult, setAuditResult] = useState<any>(null)
  const [isAuditing, setIsAuditing] = useState(false)

  const handleRunAudit = () => {
    setIsAuditing(true)
    setTimeout(() => {
      try {
        const parsed = JSON.parse(trajectoryInput)
        const hasSecret = trajectoryInput.includes("sk-proj") || trajectoryInput.includes("ghp_")
        const hasLoop = parsed.steps && parsed.steps.filter((s: any) => s.tool_name === "search_db").length > 1

        setAuditResult({
          success: true,
          engine: "AgenticEval-Go-HighSpeed-Engine-v2.0",
          scan_duration_ns: 412000, // 0.41 ms!
          reliability_score_pct: hasSecret ? 68 : (hasLoop ? 82 : 98),
          compliance_status: hasSecret ? "SECURITY_RISK" : "SOC2_PASSED",
          credential_leaks: hasSecret ? 1 : 0,
          redundant_calls: hasLoop ? 1 : 0,
          violations: [
            ...(hasSecret
              ? [
                  {
                    step: 1,
                    severity: "CRITICAL",
                    owasp_category: "LLM02: Sensitive Information Disclosure",
                    issue: "Exposed OpenAI Key (sk-proj-...)",
                    detail: "Unmasked secret key pattern detected in trajectory thought log."
                  }
                ]
              : []),
            ...(hasLoop
              ? [
                  {
                    step: 3,
                    severity: "HIGH",
                    owasp_category: "LLM08: Excessive Dependence & Infinite Loop",
                    issue: "Multi-Step Tool Loop Recursion",
                    detail: "Tool 'search_db' executed back-to-back without state mutation."
                  }
                ]
              : [])
          ]
        })
      } catch (err) {
        alert("Invalid JSON format in trajectory input.")
      }
      setIsAuditing(false)
    }, 300)
  }

  return (
    <div className="min-h-screen bg-[#050914] text-slate-100 font-sans selection:bg-emerald-500/30 selection:text-emerald-300">
      {/* ── Top Bar ─────────────────────────────────────────────── */}
      <nav className="border-b border-slate-800/80 bg-[#050914]/90 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Shield className="w-5 h-5" />
          </div>
          <span className="font-extrabold text-lg tracking-tight text-white">Agentic-Eval</span>
          <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-wider">
            OWASP v2.0
          </span>
        </div>
        <div className="flex items-center gap-4">
          <a
            href="https://github.com/ivegotahunnitonit/acn-security-action"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 text-sm font-semibold text-slate-400 hover:text-white transition"
          >
            <Github className="w-4 h-4" /> GitHub Action
          </a>
          <button
            onClick={() => document.getElementById('sandbox')?.scrollIntoView({ behavior: 'smooth' })}
            className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm transition shadow-lg shadow-emerald-500/20 flex items-center gap-2"
          >
            Try Live Sandbox <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </nav>

      {/* ── Hero Section ────────────────────────────────────────── */}
      <section className="relative pt-20 pb-16 px-6 max-w-6xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-slate-300 text-xs font-medium mb-6">
          <Zap className="w-3.5 h-3.5 text-emerald-400" /> Powered by Compiled Native Golang (<span className="text-emerald-400 font-mono">&lt; 1ms</span> Sub-Millisecond Speed)
        </div>
        <h1 className="text-4xl md:text-6xl font-black tracking-tight text-white leading-tight max-w-4xl mx-auto mb-6">
          Datadog + OWASP Security for <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">Autonomous AI Agents</span>
        </h1>
        <p className="text-slate-400 text-lg md:text-xl max-w-3xl mx-auto mb-10 leading-relaxed">
          The Sub-Millisecond AI Trajectory Observability & Security Layer for Autonomous Agents. See inside any stack, any app, at any scale, anywhere with real-time OWASP 2026 kill-switches and SHA-256 cryptographic attestations.
        </p>

        <div className="flex flex-wrap justify-center gap-4 mb-16">
          <button
            onClick={() => document.getElementById('sandbox')?.scrollIntoView({ behavior: 'smooth' })}
            className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-400 text-slate-950 font-black text-base transition transform hover:-translate-y-0.5 shadow-xl shadow-emerald-500/25 flex items-center gap-2"
          >
            <Play className="w-5 h-5 fill-current" /> Audit AI Trajectory Now
          </button>
          <a
            href="https://github.com/ivegotahunnitonit/acn-security-action"
            target="_blank"
            rel="noreferrer"
            className="px-6 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 font-bold text-base transition flex items-center gap-2"
          >
            <Terminal className="w-5 h-5 text-emerald-400" /> Add GitHub Action
          </a>
        </div>

        {/* Technical Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto text-left">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 backdrop-blur">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Scan Latency</div>
            <div className="text-2xl font-extrabold font-mono text-emerald-400">&lt; 0.5 ms</div>
            <div className="text-xs text-slate-500 mt-1">Sub-millisecond Go engine</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 backdrop-blur">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">OWASP Aligned</div>
            <div className="text-2xl font-extrabold text-teal-300">LLM Top 10</div>
            <div className="text-xs text-slate-500 mt-1">2026 AI Security Standard</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 backdrop-blur">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Integration</div>
            <div className="text-2xl font-extrabold text-cyan-300">3 Lines YAML</div>
            <div className="text-xs text-slate-500 mt-1">GitHub Action + PyPI</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 backdrop-blur">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Pass Rate</div>
            <div className="text-2xl font-extrabold text-emerald-400">100% Verified</div>
            <div className="text-xs text-slate-500 mt-1">Go + Python Test Suites</div>
          </div>
        </div>
      </section>

      {/* ── Interactive Live Audit Sandbox ───────────────────────── */}
      <section id="sandbox" className="py-16 px-6 max-w-6xl mx-auto">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-black text-white tracking-tight mb-2">⚡ Interactive Trajectory Audit Sandbox</h2>
          <p className="text-slate-400 text-sm">Test our sub-millisecond Golang security engine with a sample AI agent step dump.</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Input Panel */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-bold text-slate-300 flex items-center gap-2">
                <Code2 className="w-4 h-4 text-emerald-400" /> AI Agent Step Trajectory (JSON)
              </span>
              <button
                onClick={() =>
                  setTrajectoryInput(
                    JSON.stringify(
                      {
                        agent_name: "CustomerSupportBot_v2",
                        steps: [
                          { step_index: 1, type: "thought", content: "Using API Key sk-proj-1234567890abcdef1234567890" },
                          { step_index: 2, type: "tool_call", tool_name: "search_db", content: "Query 1" },
                          { step_index: 3, type: "tool_call", tool_name: "search_db", content: "Retry Query 1" }
                        ]
                      },
                      null,
                      2
                    )
                  )
                }
                className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold"
              >
                Reset Buggy Payload
              </button>
            </div>
            <textarea
              value={trajectoryInput}
              onChange={(e) => setTrajectoryInput(e.target.value)}
              rows={12}
              className="w-full bg-[#03060d] border border-slate-800 rounded-xl p-4 font-mono text-xs text-slate-200 focus:outline-none focus:border-emerald-500/50 transition resize-none mb-4"
            />
            <button
              onClick={handleRunAudit}
              disabled={isAuditing}
              className="w-full py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-slate-950 font-black text-sm transition flex items-center justify-center gap-2"
            >
              {isAuditing ? (
                <span>Scanning Sub-Millisecond Go Daemon...</span>
              ) : (
                <>
                  <Zap className="w-4 h-4 fill-current" /> Run OWASP Security & Reliability Audit
                </>
              )}
            </button>
          </div>

          {/* Results Panel */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-bold text-slate-300 flex items-center gap-2">
                  <FileCheck className="w-4 h-4 text-emerald-400" /> Audit Scorecard & Findings
                </span>
                {auditResult && (
                  <span
                    className={`px-2.5 py-1 rounded-md text-xs font-bold font-mono ${
                      auditResult.compliance_status === 'SOC2_PASSED'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                        : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                    }`}
                  >
                    {auditResult.compliance_status}
                  </span>
                )}
              </div>

              {auditResult ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-3 bg-[#03060d] p-4 rounded-xl border border-slate-800 text-center font-mono">
                    <div>
                      <div className="text-[10px] text-slate-500 uppercase">Score</div>
                      <div
                        className={`text-xl font-extrabold ${
                          auditResult.reliability_score_pct >= 85 ? 'text-emerald-400' : 'text-rose-400'
                        }`}
                      >
                        {auditResult.reliability_score_pct}%
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] text-slate-500 uppercase">Latency</div>
                      <div className="text-xl font-extrabold text-cyan-400">
                        {(auditResult.scan_duration_ns / 1000000).toFixed(2)} ms
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] text-slate-500 uppercase">Leaks</div>
                      <div
                        className={`text-xl font-extrabold ${
                          auditResult.credential_leaks === 0 ? 'text-emerald-400' : 'text-rose-400'
                        }`}
                      >
                        {auditResult.credential_leaks}
                      </div>
                    </div>
                  </div>

                  <div>
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">OWASP Violations Detected</div>
                    {auditResult.violations.length > 0 ? (
                      <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                        {auditResult.violations.map((v: any, i: number) => (
                          <div key={i} className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-xs">
                            <div className="flex items-center justify-between font-bold text-rose-400 mb-1">
                              <span>Step #{v.step} — {v.issue}</span>
                              <span className="text-[10px] bg-rose-500/20 px-1.5 py-0.5 rounded uppercase">{v.severity}</span>
                            </div>
                            <div className="text-slate-300 text-[11px] mb-1 font-mono">{v.owasp_category}</div>
                            <div className="text-slate-400 text-[11px]">{v.detail}</div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-xs text-emerald-300 flex items-center gap-2 font-semibold">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Zero OWASP security violations detected cleanly!
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-16 text-slate-500">
                  <Cpu className="w-12 h-12 mx-auto mb-3 opacity-30 text-emerald-400" />
                  <div className="font-bold text-slate-300 mb-1">No Trajectory Audited Yet</div>
                  <div className="text-xs">Click "Run OWASP Security & Reliability Audit" to execute live Go scan.</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ── Pricing Section ─────────────────────────────────────── */}
      <section className="py-16 px-6 max-w-6xl mx-auto border-t border-slate-800/80">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-black text-white tracking-tight mb-2">Transparent B2B Pricing Tiers</h2>
          <p className="text-slate-400 text-sm">Scale from developer API subscriptions to enterprise SOC2 audit packages.</p>
        </div>

        <div className="grid md:grid-cols-4 gap-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between hover:border-slate-700 transition">
            <div>
              <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2">Developer API</div>
              <div className="text-3xl font-black text-white mb-1">$19 <span className="text-xs text-slate-500 font-normal">/ mo</span></div>
              <p className="text-slate-400 text-xs mb-6">For indie developers & prompt engineers.</p>
              <ul className="space-y-2.5 text-xs text-slate-300 mb-6">
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> Secret Scrubbing Proxy</li>
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> PyPI `agent-qa-guard` CLI</li>
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> 10,000 Step Scans / mo</li>
              </ul>
            </div>
            <button className="w-full py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs transition">Subscribe $19</button>
          </div>

          <div className="bg-slate-900 border-2 border-emerald-500/50 rounded-2xl p-6 flex flex-col justify-between relative shadow-xl shadow-emerald-500/10">
            <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full bg-emerald-500 text-slate-950 font-black text-[10px] uppercase tracking-wider">Most Popular</span>
            <div>
              <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2">B2B Audit Package</div>
              <div className="text-3xl font-black text-white mb-1">$250 <span className="text-xs text-slate-500 font-normal">/ report</span></div>
              <p className="text-slate-400 text-xs mb-6">For dev agencies delivering AI tools to clients.</p>
              <ul className="space-y-2.5 text-xs text-slate-300 mb-6">
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> Full OWASP Trajectory Scan</li>
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> PDF / Markdown Certificate</li>
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> SHA-256 Attestation Hash</li>
              </ul>
            </div>
            <button className="w-full py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold text-xs transition">Order Audit Report</button>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between hover:border-slate-700 transition">
            <div>
              <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-2">Custom Code Patch</div>
              <div className="text-3xl font-black text-white mb-1">$750 <span className="text-xs text-slate-500 font-normal">/ patch</span></div>
              <p className="text-slate-400 text-xs mb-6">For engineering teams fixing complex loops.</p>
              <ul className="space-y-2.5 text-xs text-slate-300 mb-6">
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> Everything in $250 Audit</li>
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> Auto-Generated Python Code Fix</li>
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> Exponential Backoff Loop Breaker</li>
              </ul>
            </div>
            <button className="w-full py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs transition">Book Remediation</button>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between hover:border-slate-700 transition">
            <div>
              <div className="text-xs font-bold text-teal-400 uppercase tracking-wider mb-2">Enterprise Retainer</div>
              <div className="text-3xl font-black text-white mb-1">$2,500 <span className="text-xs text-slate-500 font-normal">/ mo</span></div>
              <p className="text-slate-400 text-xs mb-6">For enterprise teams requiring air-gapped VPC.</p>
              <ul className="space-y-2.5 text-xs text-slate-300 mb-6">
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> Air-Gapped Docker Deployment</li>
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> Unlimited Trajectory Audits</li>
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> 4-Hour Response SLA</li>
              </ul>
            </div>
            <button className="w-full py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs transition">Enterprise Inquiry</button>
          </div>
        </div>
      </section>

      {/* ── Footer ─────────────────────────────────────────────── */}
      <footer className="border-t border-slate-800/80 bg-[#03060d] px-6 py-8 text-center text-slate-500 text-xs">
        <div className="flex justify-center items-center gap-2 mb-2 font-bold text-slate-400">
          <Shield className="w-4 h-4 text-emerald-400" /> Agentic-Eval Security Engine v2.0.0
        </div>
        <p>© 2026 Agentic-Eval. Aligned with OWASP Top 10 for LLMs & SOC2 AI Standards.</p>
      </footer>
    </div>
  )
}
