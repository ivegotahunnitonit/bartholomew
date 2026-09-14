import { useState } from 'react'
import { Link } from 'react-router-dom'
import { 
  Check, 
  Copy, 
  Terminal, 
  ShieldCheck, 
  Zap, 
  ChevronDown, 
  ChevronUp, 
  Sparkles, 
  ArrowRight, 
  ExternalLink,
  Lock,
  FileCheck
} from 'lucide-react'

type ConsoleTab = 'quickstart' | 'claude' | 'openai' | 'gemini' | 'cloudflare' | 'docker'

interface ConsoleItem {
  tab: ConsoleTab
  label: string
  pill: string
  filename: string
  command?: string
  code: string
  explanation: string
  latency: string
}

const CONSOLE_ITEMS: Record<ConsoleTab, ConsoleItem> = {
  quickstart: {
    tab: 'quickstart',
    label: 'Auto-Patch',
    pill: 'Zero-Touch',
    filename: 'main.py — zero-touch runtime gate',
    command: 'pip install btp-guard',
    code: `import btp_guard

# 1-Line Universal Interceptor: In-flight AST gating for all agent tool calls
btp_guard.auto_patch()

# Sub-35µs AST gate, spend-cap governor, & secret scrubbing are now active.
# Destructive syscalls (rm -rf, DROP TABLE, mkfs) and secret leaks are vetoed in memory.`,
    explanation: 'Zero-touch global auto-patcher. Intercepts OpenAI, Anthropic, Gemini, and tool call dispatches in-flight with zero refactoring.',
    latency: 'Sub-35µs AST SLA'
  },
  claude: {
    tab: 'claude',
    label: 'Claude Tools',
    pill: 'Anthropic Wire',
    filename: 'claude_computer_use_guard.py',
    command: 'pip install btp-guard anthropic',
    code: `import anthropic
from btp_guard import Guard

guard = Guard(spend_cap=150.0, strict=True)
client = anthropic.Anthropic()

# Intercept Claude 3.7 tool use & computer use actions before execution
def safe_tool_executor(tool_name: str, tool_input: dict):
    verdict = guard.check(str(tool_input))
    if not verdict["allowed"]:
        return {"error": f"Bartholomew Security Veto: {verdict['reason']}"}
    return execute_action(tool_name, tool_input)`,
    explanation: 'Native Anthropic tool use & computer use gatekeeper. Blocks destructive OS commands and prompts before hitting runtime shells.',
    latency: 'In-Process Gate (<30µs)'
  },
  openai: {
    tab: 'openai',
    label: 'OpenAI Agents',
    pill: 'Agents SDK',
    filename: 'openai_agents_sdk_guard.py',
    command: 'pip install btp-guard openai',
    code: `from openai import OpenAI
from btp_guard import Guard

client = OpenAI()
guard = Guard(workspace_id="prod-agents", spend_cap=250.0)

# Pre-dispatch validation for GPT-4o / GPT-Astra tool dispatches
for tool_call in response.choices[0].message.tool_calls:
    check = guard.check(tool_call.function.arguments)
    if not check["allowed"]:
        raise PermissionError(f"BTP Veto: {check['reason']}")
    execute_internal_tool(tool_call)`,
    explanation: 'Pre-dispatch validation for OpenAI function calling & Agents SDK. Drops malicious SQL, shell calls, or secret leaks in caller RAM.',
    latency: 'In-Memory Inspection (<25µs)'
  },
  gemini: {
    tab: 'gemini',
    label: 'Gemini 3.8',
    pill: 'Vertex AI',
    filename: 'vertex_ai_agent_guard.py',
    command: 'pip install btp-guard google-generativeai',
    code: `import google.generativeai as genai
from btp_guard import Guard

guard = Guard(workspace_id="gemini-prod")

def safe_gemini_dispatcher(tool_call):
    # Evaluates function call arguments against BTP AST security policies
    res = guard.check(str(tool_call.args))
    if not res["allowed"]:
        return {"status": "vetoed", "reason": res["reason"]}
    return execute_gemini_tool(tool_call)`,
    explanation: 'Multimodal function declaration gate for Google Gemini 3.8 and Vertex AI. Prevents runaway tool loops and credential exfiltration.',
    latency: 'Sub-35µs Gate'
  },
  cloudflare: {
    tab: 'cloudflare',
    label: 'Cloudflare AI',
    pill: 'Edge Runtime',
    filename: 'cloudflare_workers_guard.ts',
    command: 'npm install btp-guard',
    code: `import { evaluateIntent, scrubSensitiveCredentials } from 'btp-guard';

export default {
  async fetch(request, env) {
    const payload = await request.json();
    
    // Sub-35us edge AST evaluation before running serverless tool action
    const verdict = evaluateIntent({
      agentId: 'worker-edge-01',
      actionType: 'EXECUTE',
      payload
    });

    if (!verdict.allowed) {
      return new Response(JSON.stringify({ error: verdict.reason }), { status: 403 });
    }
    return runAgentTool(payload);
  }
};`,
    explanation: 'Zero-cold-start Edge Gateway for Cloudflare Workers AI. Runs deterministic microsecond gating natively at the global CDN edge.',
    latency: 'Edge Native (<35µs)'
  },
  docker: {
    tab: 'docker',
    label: 'Container Pods',
    pill: 'Defense-in-Depth',
    filename: 'container_sandbox_defense.py',
    command: 'pip install btp-guard',
    code: `from btp_guard.sandbox import ContainerGuardPolicy

# Layer-7 Invariant Gating paired with OS Container Sandboxing
policy = ContainerGuardPolicy(
    container_runtime="docker",
    block_dynamic_exec=True,        # Vetoes eval, exec, base64 decoding sinks
    allowed_egress_domains=["api.github.com", "pypi.org"]
)
# AST gating intercepts tool dispatches inside isolated container namespaces`,
    explanation: 'Production defense-in-depth model. Pairs Layer-7 semantic AST invariant gating with OS-level Docker and Kubernetes namespaces.',
    latency: 'Hermetic Sandbox Safe'
  }
}

export default function Hero() {
  const [activeTab, setActiveTab] = useState<ConsoleTab>('quickstart')
  const [copiedCode, setCopiedCode] = useState(false)
  const [copiedCmd, setCopiedCmd] = useState(false)
  const [showChecksums, setShowChecksums] = useState(false)
  const current = CONSOLE_ITEMS[activeTab]

  const handleCopyCode = () => {
    navigator.clipboard.writeText(current.code)
    setCopiedCode(true)
    setTimeout(() => setCopiedCode(false), 2000)
  }

  return (
    <section className="relative min-h-[90vh] flex flex-col justify-center pt-32 pb-20 px-4 sm:px-6 lg:px-8 bg-[#040406] text-white overflow-hidden">
      {/* Dynamic Background Glow Radial */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[760px] h-[440px] bg-gradient-to-r from-emerald-500/15 via-cyan-500/10 to-purple-500/10 blur-[150px] rounded-full pointer-events-none" />

      <div className="max-w-5xl mx-auto w-full relative z-10 text-center">

        {/* Category Pill */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-xs font-semibold mb-5 shadow-[0_0_15px_rgba(16,185,129,0.1)]">
          <Sparkles className="w-3.5 h-3.5" />
          <span>AUTONOMOUS EXECUTION FIREWALL &bull; BTP v5.4.12</span>
        </div>

        {/* Impactful Headline */}
        <h1 
          className="font-extrabold font-sans tracking-tight text-white mb-6 mx-auto max-w-4xl"
          style={{
            fontSize: 'clamp(2.1rem, 5.2vw, 3.8rem)',
            lineHeight: 1.12,
            letterSpacing: '-0.035em'
          }}
        >
          The Sovereign Security Runtime &amp; Firewall for AI Agents.
        </h1>

        {/* Subtitle with softened contrast */}
        <p className="text-center mx-auto mb-10 text-zinc-300 leading-relaxed max-w-3xl text-sm sm:text-base font-sans">
          Zero cloud lag. Zero prompt leakage. Deterministic in-memory AST safety gating stops catastrophic tool calls (<code className="text-cyan-400 bg-zinc-900/90 px-1.5 py-0.5 rounded border border-zinc-800 font-mono text-xs">rm -rf</code>, <code className="text-cyan-400 bg-zinc-900/90 px-1.5 py-0.5 rounded border border-zinc-800 font-mono text-xs">DROP TABLE</code>) in memory before reaching the OS. Multi-tenant workspace isolation, OWASP LLM02 credential scrubbing, and verifiable cryptographic execution audit receipts.
        </p>

        {/* Action & Quick-Start Pill */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 mb-10">
          {/* Quick Terminal Copy Pill */}
          <div className="flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-zinc-950/80 border border-white/[0.08] font-mono text-xs text-zinc-200 shadow-inner max-w-full backdrop-blur-md">
            <span className="text-emerald-400 select-none font-bold">❯</span>
            <span className="text-amber-400 font-semibold truncate">pip install btp-guard</span>
            <button
              onClick={() => {
                navigator.clipboard.writeText('pip install btp-guard')
                setCopiedCmd(true)
                setTimeout(() => setCopiedCmd(false), 2000)
              }}
              className="ml-2 px-2.5 py-1 text-[11px] font-bold rounded-lg bg-zinc-800/80 hover:bg-emerald-500 text-zinc-300 hover:text-black transition border border-zinc-700/60 cursor-pointer"
              title="Copy quickstart command"
            >
              {copiedCmd ? 'COPIED!' : 'COPY'}
            </button>
          </div>

          {/* Jump to Interactive Universal Cookbook */}
          <Link
            to="/cookbook"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-400 border border-emerald-500/40 hover:border-emerald-400 text-xs font-sans font-bold transition shadow-[0_0_20px_rgba(16,185,129,0.15)]"
          >
            <Sparkles size={14} />
            <span>EXPLORE INTERACTIVE COOKBOOK</span>
            <ArrowRight size={13} />
          </Link>
        </div>

        {/* Supported Runtimes Logo Grid */}
        <div className="mb-12 pt-2">
          <p className="text-[11px] font-mono uppercase tracking-widest text-zinc-500 mb-3.5">
            Wire Protection for Frontier Enterprise Model Runtimes
          </p>
          <div className="flex flex-wrap items-center justify-center gap-2.5 sm:gap-4 max-w-3xl mx-auto">
            {['Anthropic Claude', 'OpenAI Agents', 'Google Gemini', 'AWS Bedrock', 'Cloudflare AI', 'Meta Llama', 'Microsoft AutoGen'].map((framework) => (
              <span 
                key={framework}
                className="px-3 py-1.5 rounded-lg bg-zinc-950/60 border border-white/[0.08] text-xs font-sans font-medium text-zinc-400 hover:text-white hover:border-white/20 transition-colors backdrop-blur-sm"
              >
                {framework}
              </span>
            ))}
          </div>
        </div>

        {/* Visual Enterprise Compliance Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-3xl mx-auto mb-10">
          <div className="px-3.5 py-2.5 rounded-xl bg-zinc-950/60 border border-white/[0.08] backdrop-blur-md flex items-center gap-2.5 text-left">
            <ShieldCheck size={16} className="text-emerald-400 shrink-0" />
            <div>
              <div className="text-[11px] font-mono font-bold text-white leading-tight">SOC 2 Type II</div>
              <div className="text-[10px] text-zinc-400">Merkle Receipts</div>
            </div>
          </div>
          <div className="px-3.5 py-2.5 rounded-xl bg-zinc-950/60 border border-white/[0.08] backdrop-blur-md flex items-center gap-2.5 text-left">
            <Lock size={16} className="text-cyan-400 shrink-0" />
            <div>
              <div className="text-[11px] font-mono font-bold text-white leading-tight">FIPS 186-5</div>
              <div className="text-[10px] text-zinc-400">Ed25519 Signatures</div>
            </div>
          </div>
          <div className="px-3.5 py-2.5 rounded-xl bg-zinc-950/60 border border-white/[0.08] backdrop-blur-md flex items-center gap-2.5 text-left">
            <FileCheck size={16} className="text-purple-400 shrink-0" />
            <div>
              <div className="text-[11px] font-mono font-bold text-white leading-tight">RFC 8785</div>
              <div className="text-[10px] text-zinc-400">Canonical JSON</div>
            </div>
          </div>
          <div className="px-3.5 py-2.5 rounded-xl bg-zinc-950/60 border border-white/[0.08] backdrop-blur-md flex items-center gap-2.5 text-left">
            <Zap size={16} className="text-amber-400 shrink-0" />
            <div>
              <div className="text-[11px] font-mono font-bold text-white leading-tight">&lt;35µs AST Gate</div>
              <div className="text-[10px] text-zinc-400">In-Process Speed</div>
            </div>
          </div>
        </div>

        {/* Unified Frontier Console Showcase */}
        <div className="rounded-2xl border border-white/[0.1] bg-gradient-to-b from-zinc-900/90 via-zinc-950/90 to-black/95 shadow-[0_25px_70px_-20px_rgba(0,0,0,0.9)] text-left overflow-hidden relative transition-all duration-300 backdrop-blur-xl">
          {/* Top Ambient Glow line */}
          <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-emerald-500/80 to-transparent pointer-events-none" />

          {/* Console Header Chrome */}
          <div className="flex items-center justify-between px-4 py-3 bg-zinc-950 border-b border-white/[0.08]">
            {/* MacOS Window Dots */}
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-red-500/80 inline-block" />
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80 inline-block" />
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80 inline-block" />
              <span className="text-xs font-mono text-zinc-400 ml-2 hidden sm:inline">{current.filename}</span>
            </div>

            {/* Latency & Quick Action */}
            <div className="flex items-center gap-3">
              <span className="text-[11px] font-mono font-semibold text-emerald-400 bg-emerald-950/50 px-2.5 py-0.5 rounded-full border border-emerald-500/30">
                {current.latency}
              </span>
              <button
                onClick={handleCopyCode}
                className="text-xs font-mono text-zinc-400 hover:text-emerald-400 transition flex items-center gap-1.5 cursor-pointer"
                title="Copy code to clipboard"
              >
                {copiedCode ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                <span>{copiedCode ? 'COPIED' : 'COPY'}</span>
              </button>
            </div>
          </div>

          {/* Aligned, Desktop-Grade Tab Bar */}
          <div className="flex bg-[#07070a] border-b border-white/[0.08] px-2.5 pt-1.5 gap-1.5 overflow-x-auto no-scrollbar">
            {(Object.keys(CONSOLE_ITEMS) as ConsoleTab[]).map((tabKey) => {
              const item = CONSOLE_ITEMS[tabKey]
              const isActive = activeTab === tabKey
              return (
                <button
                  key={tabKey}
                  onClick={() => setActiveTab(tabKey)}
                  className={`h-9 px-3.5 text-xs font-sans font-medium transition-all rounded-t-lg border-t border-x whitespace-nowrap flex items-center gap-2 cursor-pointer ${
                    isActive
                      ? 'bg-zinc-950 text-white border-white/[0.12] border-b-transparent -mb-[1px] font-semibold text-emerald-400 shadow-sm'
                      : 'text-zinc-400 border-transparent hover:text-zinc-200 hover:bg-zinc-900/40'
                  }`}
                >
                  <Terminal size={12} className={isActive ? 'text-emerald-400' : 'text-zinc-500'} />
                  <span>{item.label}</span>
                </button>
              )
            })}
          </div>

          {/* Console Code Body */}
          <div className="p-5 sm:p-6 bg-[#030305] overflow-x-auto selection:bg-emerald-500/30">
            <pre className="font-mono text-xs sm:text-[13px] text-zinc-200 leading-relaxed">
              {current.code}
            </pre>
          </div>

          {/* Console Description & Expandable Checksum Footer */}
          <div className="px-5 py-3 bg-zinc-950 border-t border-white/[0.08] flex flex-col sm:flex-row sm:items-center justify-between text-xs font-sans text-zinc-300 gap-2">
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
              <span>{current.explanation}</span>
            </div>

            <div className="flex items-center gap-3 shrink-0 self-end sm:self-auto">
              <button
                onClick={() => setShowChecksums(!showChecksums)}
                className="font-mono text-[11px] text-zinc-400 hover:text-emerald-400 transition flex items-center gap-1 cursor-pointer"
              >
                <span>{showChecksums ? 'Hide Release Digest' : 'View Release Digest'}</span>
                {showChecksums ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>
              <a
                href="https://pypi.org/project/btp-guard/#files"
                target="_blank"
                rel="noopener noreferrer"
                className="font-mono text-[11px] text-emerald-400 hover:text-emerald-300 transition flex items-center gap-1 border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 rounded-lg"
              >
                <span>PyPI Hashes</span>
                <ExternalLink size={10} />
              </a>
            </div>
          </div>

          {/* Checksum Drawer */}
          {showChecksums && (
            <div className="p-4 bg-black border-t border-white/[0.08] font-mono text-[11px] text-zinc-400 grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <span className="text-zinc-500 block text-[10px] uppercase tracking-wider">Official Package Channel</span>
                <span className="text-emerald-400 font-semibold">btp-guard on PyPI &amp; npm (v5.4.12)</span>
              </div>
              <div>
                <span className="text-zinc-500 block text-[10px] uppercase tracking-wider">Verifiable Checksums</span>
                <a
                  href="https://pypi.org/project/btp-guard/#files"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-amber-400 hover:underline inline-flex items-center gap-1"
                >
                  <span>Verify SHA-256 hashes on PyPI</span>
                  <ExternalLink size={10} />
                </a>
              </div>
            </div>
          )}

        </div>

      </div>
    </section>
  )
}
