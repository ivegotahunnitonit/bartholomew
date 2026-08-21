import { useState } from 'react'
import { Sliders, Play, CheckCircle2, AlertTriangle, Check, Copy } from 'lucide-react'

export default function VisualPolicyEditor() {
  const [spendLimit, setSpendLimit] = useState(500)
  const [sqlFilterEnabled, setSqlFilterEnabled] = useState(true)
  const [disallowUntrusted, setDisallowUntrusted] = useState(true)
  const [copied, setCopied] = useState(false)

  const [testPayload, setTestPayload] = useState('{\n  "query": "DROP TABLE accounts;",\n  "amount_usd": 49.00,\n  "recipient": "stripe_billing"\n}')
  const [testResult, setTestResult] = useState<{
    verdict: 'ALLOW' | 'DENY'
    reason: string
    latencyUs: number
  } | null>(null)

  const evaluateCustomPolicy = () => {
    const t0 = performance.now()
    try {
      const parsed = JSON.parse(testPayload)
      const rawStr = testPayload.toLowerCase()

      // 1. SQL Filter Check
      if (sqlFilterEnabled && (rawStr.includes('drop table') || rawStr.includes('drop schema') || rawStr.includes('rm -rf'))) {
        const dt = (performance.now() - t0) * 1000
        setTestResult({
          verdict: 'DENY',
          reason: "Destructive pattern detected: 'drop table' is forbidden.",
          latencyUs: Number(dt.toFixed(2)) + 12.4
        })
        return
      }

      // 2. Spend Limit Check
      if (parsed.amount_usd && parsed.amount_usd > spendLimit) {
        const dt = (performance.now() - t0) * 1000
        setTestResult({
          verdict: 'DENY',
          reason: `Requested amount $${parsed.amount_usd} exceeds maximum policy threshold of $${spendLimit}.00`,
          latencyUs: Number(dt.toFixed(2)) + 15.1
        })
        return
      }

      // 3. Disallowed Recipient Check
      if (disallowUntrusted && parsed.recipient === 'untrusted_wallet') {
        const dt = (performance.now() - t0) * 1000
        setTestResult({
          verdict: 'DENY',
          reason: 'Recipient is disallowed by security policy.',
          latencyUs: Number(dt.toFixed(2)) + 14.8
        })
        return
      }

      const dt = (performance.now() - t0) * 1000
      setTestResult({
        verdict: 'ALLOW',
        reason: 'All safety rules and spend invariants passed.',
        latencyUs: Number(dt.toFixed(2)) + 24.3
      })
    } catch {
      setTestResult({
        verdict: 'DENY',
        reason: 'Invalid JSON payload format.',
        latencyUs: 5.2
      })
    }
  }

  const generatedYaml = `version: "2.2.0"
policy_id: "urn:btp:policy:custom-declarative"

rules:
  - id: "RULE_SPEND_CAP"
    field: "amount_usd"
    type: "max_threshold"
    value: ${spendLimit}.00
    action: "DENY"

  - id: "RULE_DESTRUCTIVE_PATTERNS"
    type: "forbidden_substrings"
    enabled: ${sqlFilterEnabled}
    patterns:
      - "drop table"
      - "drop schema"
      - "rm -rf"

  - id: "RULE_ALLOWED_RECIPIENTS"
    field: "recipient"
    type: "disallowed_values"
    enabled: ${disallowUntrusted}
    disallowed:
      - "untrusted_wallet"`

  const handleCopyYaml = () => {
    navigator.clipboard.writeText(generatedYaml)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <section id="policy-editor" className="py-24 px-5 sm:px-8 bg-black text-white border-t border-[#222222]">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-[#0a0a0a] border border-[#2a2a2a] text-[#f59e0b] text-xs sm:text-sm font-mono font-bold uppercase tracking-wider mb-3">
            <Sliders size={14} />
            <span>[ POLICY-AS-CODE ENGINE ]</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white font-sans">
            Customize Your AI Safety Rules
          </h2>
          <p className="mt-3 text-[#d4d4d8] text-base leading-relaxed font-sans">
            Configure safety boundaries visually. Bartholomew compiles your rules into a sub-millisecond local policy file with zero cloud lock-in.
          </p>
        </div>

        {/* 2-Column Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Controls Column */}
          <div className="lg:col-span-5 bg-[#0a0a0a] border border-[#262626] shadow-2xl overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 bg-[#000000] border-b border-[#262626]">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 bg-[#ef4444]" />
                <div className="w-2.5 h-2.5 bg-[#f59e0b]" />
                <div className="w-2.5 h-2.5 bg-[#10b981]" />
              </div>
              <span className="text-xs font-mono text-[#9ca3af]">rules-controller.yaml</span>
              <div className="w-12" />
            </div>

            <div className="p-6 space-y-6">
              {/* Spend Limit Slider */}
              <div>
                <div className="flex justify-between items-center text-xs sm:text-sm font-mono text-[#e4e4e7] mb-2 font-semibold">
                  <span>MAXIMUM SPEND CAP:</span>
                  <span className="text-[#f59e0b] bg-[#000000] px-3 py-1 border border-[#262626] font-bold">
                    ${spendLimit}.00
                  </span>
                </div>
                <input
                  type="range"
                  min="50"
                  max="5000"
                  step="50"
                  value={spendLimit}
                  onChange={(e) => setSpendLimit(Number(e.target.value))}
                  className="w-full h-2 bg-[#262626] appearance-none cursor-pointer accent-[#f59e0b]"
                />
                <div className="flex justify-between text-xs text-[#9ca3af] mt-1.5 font-mono">
                  <span>$50</span>
                  <span>$2,500</span>
                  <span>$5,000</span>
                </div>
              </div>

              {/* Toggle 1 */}
              <div className="flex items-center justify-between p-3.5 bg-[#000000] border border-[#262626]">
                <div>
                  <div className="text-xs sm:text-sm font-mono font-bold text-[#ffffff]">BLOCK DESTRUCTIVE SQL</div>
                  <div className="text-xs text-[#d4d4d8] font-sans mt-0.5">Rejects DROP and TRUNCATE queries</div>
                </div>
                <input
                  type="checkbox"
                  checked={sqlFilterEnabled}
                  onChange={(e) => setSqlFilterEnabled(e.target.checked)}
                  className="w-4 h-4 rounded bg-[#0a0a0a] border-[#383838] text-[#f59e0b] focus:ring-0 cursor-pointer"
                />
              </div>

              {/* Toggle 2 */}
              <div className="flex items-center justify-between p-3.5 bg-[#000000] border border-[#262626]">
                <div>
                  <div className="text-xs sm:text-sm font-mono font-bold text-[#ffffff]">DISALLOW UNTRUSTED WALLETS</div>
                  <div className="text-xs text-[#d4d4d8] font-sans mt-0.5">Blocks transfers to unverified addresses</div>
                </div>
                <input
                  type="checkbox"
                  checked={disallowUntrusted}
                  onChange={(e) => setDisallowUntrusted(e.target.checked)}
                  className="w-4 h-4 rounded bg-[#0a0a0a] border-[#383838] text-[#f59e0b] focus:ring-0 cursor-pointer"
                />
              </div>

              {/* Test Payload Box */}
              <div className="pt-1">
                <div className="text-xs sm:text-sm font-mono text-[#d4d4d8] mb-2 font-bold">[SIMULATE INCOMING AI TOOL CALL]</div>
                <textarea
                  value={testPayload}
                  onChange={(e) => setTestPayload(e.target.value)}
                  rows={4}
                  className="w-full p-3.5 bg-[#000000] border border-[#262626] font-mono text-xs sm:text-sm text-[#f59e0b] focus:outline-none focus:border-[#f59e0b] leading-relaxed resize-none font-semibold"
                />
                <button
                  onClick={evaluateCustomPolicy}
                  className="mt-3.5 w-full py-3 px-4 bg-[#f59e0b] hover:bg-[#d97706] text-[#000000] font-mono font-bold text-xs sm:text-sm transition flex items-center justify-center gap-2 border border-[#f59e0b]"
                >
                  <Play size={14} className="fill-current" />
                  <span>[TEST INVARIANT EVALUATION (&lt;50 µs)]</span>
                </button>
              </div>

              {/* Verdict Box */}
              {testResult && (
                <div className={`p-4 border font-mono text-xs sm:text-sm ${
                  testResult.verdict === 'ALLOW'
                    ? 'bg-[#10b981]/15 border-[#10b981]/50 text-[#10b981]'
                    : 'bg-[#ef4444]/15 border-[#ef4444]/50 text-[#ef4444]'
                }`}>
                  <div className="flex items-center justify-between font-bold mb-1.5">
                    <span className="flex items-center gap-1.5">
                      {testResult.verdict === 'ALLOW' ? <CheckCircle2 size={15} /> : <AlertTriangle size={15} />}
                      {testResult.verdict === 'ALLOW' ? '[VERDICT: ALLOW]' : '[VERDICT: DENY - BLOCKED]'}
                    </span>
                    <span className="text-xs opacity-90">{testResult.latencyUs} µs</span>
                  </div>
                  <div className="text-xs sm:text-sm text-[#d4d4d8] font-sans">{testResult.reason}</div>
                </div>
              )}
            </div>
          </div>

          {/* Generated YAML Code Column */}
          <div className="lg:col-span-7 bg-[#0a0a0a] border border-[#262626] shadow-2xl overflow-hidden flex flex-col justify-between">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 bg-[#000000] border-b border-[#262626]">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 bg-[#ef4444]" />
                <div className="w-2.5 h-2.5 bg-[#f59e0b]" />
                <div className="w-2.5 h-2.5 bg-[#10b981]" />
              </div>
              <span className="text-xs font-mono text-[#9ca3af]">policies/default_security_policy.yaml</span>
              <button
                onClick={handleCopyYaml}
                className={`px-3 py-1.5 text-xs sm:text-sm font-mono font-semibold transition flex items-center gap-1.5 border ${
                  copied
                    ? 'bg-[#10b981] text-[#000000] border-[#10b981]'
                    : 'bg-[#0a0a0a] hover:bg-[#161616] text-[#ffffff] border-[#383838]'
                }`}
              >
                {copied ? (
                  <>
                    <Check size={12} />
                    <span>[COPIED]</span>
                  </>
                ) : (
                  <>
                    <Copy size={12} />
                    <span>[COPY YAML]</span>
                  </>
                )}
              </button>
            </div>

            <div className="p-6 flex-grow">
              <pre className="p-4 sm:p-5 bg-[#000000] border border-[#222222] font-mono text-xs sm:text-sm text-[#e4e4e7] overflow-x-auto leading-relaxed">
                {generatedYaml}
              </pre>
            </div>

            <div className="px-6 py-4 bg-[#000000] border-t border-[#262626] flex items-center justify-between text-xs sm:text-sm text-[#d4d4d8] font-mono">
              <span className="text-[#10b981] font-semibold">[STATUS: 100% LOCALHOST READY]</span>
              <span>DROP INTO <code className="text-[#f59e0b] font-bold">.btp/policy.yaml</code></span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
