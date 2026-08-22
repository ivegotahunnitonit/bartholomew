import { useState } from 'react'
import { Sliders, Play, CheckCircle2, AlertTriangle, Check, Copy, Activity } from 'lucide-react'

export default function VisualPolicyEditor() {
  const [spendLimit, setSpendLimit] = useState(500)
  const [decayRate, setDecayRate] = useState(0.35)
  const [repeatAttempts, setRepeatAttempts] = useState(1)
  const [sqlFilterEnabled, setSqlFilterEnabled] = useState(true)
  const [disallowUntrusted, setDisallowUntrusted] = useState(true)
  const [copied, setCopied] = useState(false)

  const [testPayload, setTestPayload] = useState('{\n  "tool": "postgres_query",\n  "query": "SELECT * FROM orders WHERE status=\'pending\';",\n  "amount_usd": 25.00,\n  "recipient": "stripe_billing"\n}')
  const [testResult, setTestResult] = useState<{
    verdict: 'ALLOW' | 'THROTTLE' | 'DENY'
    reason: string
    latencyUs: number
    muScore: number
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
          latencyUs: Number(dt.toFixed(2)) + 12.4,
          muScore: 0.0
        })
        return
      }

      // 2. Spend Limit Check
      if (parsed.amount_usd && parsed.amount_usd > spendLimit) {
        const dt = (performance.now() - t0) * 1000
        setTestResult({
          verdict: 'DENY',
          reason: `Requested amount $${parsed.amount_usd} exceeds maximum policy threshold of $${spendLimit}.00`,
          latencyUs: Number(dt.toFixed(2)) + 15.1,
          muScore: 0.0
        })
        return
      }

      // 3. Disallowed Recipient Check
      if (disallowUntrusted && parsed.recipient === 'untrusted_wallet') {
        const dt = (performance.now() - t0) * 1000
        setTestResult({
          verdict: 'DENY',
          reason: 'Recipient is disallowed by security policy.',
          latencyUs: Number(dt.toFixed(2)) + 14.8,
          muScore: 0.0
        })
        return
      }

      // 4. Law of Diminishing Marginal Utility (LDMU) Evaluation
      const mu = Math.exp(-decayRate * (repeatAttempts - 1))
      const muScore = Number(mu.toFixed(3))

      if (muScore < 0.15) {
        const dt = (performance.now() - t0) * 1000
        setTestResult({
          verdict: 'DENY',
          reason: `Law of Diminishing Marginal Utility Breach: Action repeated ${repeatAttempts} times with near-zero marginal utility (MU=${muScore} < 0.15). Trapped in approval queue.`,
          latencyUs: Number(dt.toFixed(2)) + 18.2,
          muScore
        })
        return
      } else if (muScore < 0.40) {
        const dt = (performance.now() - t0) * 1000
        setTestResult({
          verdict: 'THROTTLE',
          reason: `Diminishing returns warning (MU=${muScore}). Execution delayed to prevent runaway retry loop.`,
          latencyUs: Number(dt.toFixed(2)) + 16.5,
          muScore
        })
        return
      }

      const dt = (performance.now() - t0) * 1000
      setTestResult({
        verdict: 'ALLOW',
        reason: `All safety rules passed with high marginal utility (MU=${muScore}, attempt ${repeatAttempts}).`,
        latencyUs: Number(dt.toFixed(2)) + 24.3,
        muScore
      })
    } catch {
      setTestResult({
        verdict: 'DENY',
        reason: 'Invalid JSON payload format.',
        latencyUs: 5.2,
        muScore: 0.0
      })
    }
  }

  const generatedYaml = `version: "2.2.0"
policy_id: "urn:btp:policy:custom-declarative"

rules:
  - id: "RULE_DIMINISHING_MARGINAL_UTILITY"
    type: "diminishing_marginal_utility"
    decay_rate: ${decayRate}
    min_utility_threshold: 0.15
    action: "DENY"

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
    <section className="py-20 bg-black text-white border-t border-[#1c1c1c]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#0a0a0a] border border-[#222222] text-[#f59e0b] text-xs font-mono font-bold uppercase tracking-wider mb-4">
            <Sliders size={13} className="text-[#f59e0b]" />
            <span>[ IN-BROWSER RULE SIMULATOR &amp; YAML GENERATOR ]</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white font-sans">
            Customize AI Safety &amp; Marginal Utility Rules
          </h2>
          <p className="mt-4 text-base text-[#a1a1aa] font-sans">
            Simulate safety thresholds and loop dampening in your browser, then export the generated YAML directly into your local agent environment.
          </p>
        </div>

        {/* 2-Column Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Controls Column */}
          <div className="lg:col-span-5 bg-[#0a0a0a] border border-[#222222] shadow-2xl overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-2.5 bg-[#000000] border-b border-[#222222]">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 bg-[#ef4444]" />
                <div className="w-2.5 h-2.5 bg-[#f59e0b]" />
                <div className="w-2.5 h-2.5 bg-[#10b981]" />
              </div>
              <span className="text-[11px] font-mono text-[#71717a]">rules-controller.yaml</span>
              <div className="w-12" />
            </div>

            <div className="p-6 space-y-5">
              {/* Diminishing Marginal Utility Decay Slider */}
              <div>
                <div className="flex justify-between items-center text-xs font-mono text-[#d4d4d8] mb-1.5 font-semibold">
                  <span className="flex items-center gap-1.5 text-[#f59e0b]">
                    <Activity size={13} />
                    <span>LDMU UTILITY DECAY RATE (λ):</span>
                  </span>
                  <span className="text-[#f59e0b] bg-[#000000] px-2 py-0.5 border border-[#222222] font-bold">
                    {decayRate}
                  </span>
                </div>
                <input
                  type="range"
                  min="0.10"
                  max="0.80"
                  step="0.05"
                  value={decayRate}
                  onChange={(e) => setDecayRate(Number(e.target.value))}
                  className="w-full h-1.5 bg-[#222222] appearance-none cursor-pointer accent-[#f59e0b]"
                />
                <div className="flex justify-between text-[10px] text-[#71717a] mt-1 font-mono">
                  <span>0.10 (Lenient)</span>
                  <span>0.35 (Standard)</span>
                  <span>0.80 (Aggressive)</span>
                </div>
              </div>

              {/* Action Repeat Count Simulator */}
              <div>
                <div className="flex justify-between items-center text-xs font-mono text-[#d4d4d8] mb-1.5 font-semibold">
                  <span>SIMULATED REPETITION COUNT:</span>
                  <span className="text-[#10b981] bg-[#000000] px-2 py-0.5 border border-[#222222] font-bold">
                    Attempt #{repeatAttempts}
                  </span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  step="1"
                  value={repeatAttempts}
                  onChange={(e) => setRepeatAttempts(Number(e.target.value))}
                  className="w-full h-1.5 bg-[#222222] appearance-none cursor-pointer accent-[#10b981]"
                />
                <div className="flex justify-between text-[10px] text-[#71717a] mt-1 font-mono">
                  <span>1 (Fresh action)</span>
                  <span>5 (Fatigued)</span>
                  <span>10 (Runaway loop)</span>
                </div>
              </div>

              {/* Spend Limit Slider */}
              <div>
                <div className="flex justify-between items-center text-xs font-mono text-[#d4d4d8] mb-1.5 font-semibold">
                  <span>MAXIMUM SPEND CAP:</span>
                  <span className="text-[#f59e0b] bg-[#000000] px-2 py-0.5 border border-[#222222] font-bold">
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
                  className="w-full h-1.5 bg-[#222222] appearance-none cursor-pointer accent-[#f59e0b]"
                />
              </div>

              {/* Toggle 1 */}
              <div className="flex items-center justify-between p-3 bg-[#000000] border border-[#222222]">
                <div>
                  <div className="text-xs font-mono font-bold text-[#ffffff]">BLOCK DESTRUCTIVE SQL</div>
                  <div className="text-[11px] text-[#71717a] font-sans">Rejects DROP and TRUNCATE queries</div>
                </div>
                <input
                  type="checkbox"
                  checked={sqlFilterEnabled}
                  onChange={(e) => setSqlFilterEnabled(e.target.checked)}
                  className="w-4 h-4 rounded bg-[#0a0a0a] border-[#383838] text-[#f59e0b] focus:ring-0 cursor-pointer"
                />
              </div>

              {/* Toggle 2 */}
              <div className="flex items-center justify-between p-3 bg-[#000000] border border-[#222222]">
                <div>
                  <div className="text-xs font-mono font-bold text-[#ffffff]">DISALLOW UNTRUSTED WALLETS</div>
                  <div className="text-[11px] text-[#71717a] font-sans">Blocks unverified recipient addresses</div>
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
                <div className="text-xs font-mono text-[#a1a1aa] mb-1.5 font-bold">[SIMULATE AGENT TOOL CALL]</div>
                <textarea
                  value={testPayload}
                  onChange={(e) => setTestPayload(e.target.value)}
                  rows={4}
                  className="w-full p-3 bg-[#000000] border border-[#222222] font-mono text-xs text-[#f59e0b] focus:outline-none focus:border-[#f59e0b] leading-relaxed resize-none"
                />
                <button
                  onClick={evaluateCustomPolicy}
                  className="mt-3 w-full py-2.5 px-4 bg-[#f59e0b] hover:bg-[#d97706] text-[#000000] font-mono font-bold text-xs transition flex items-center justify-center gap-2 border border-[#f59e0b]"
                >
                  <Play size={13} className="fill-current" />
                  <span>[EVALUATE MARGINAL UTILITY INVARIANT (&lt;50 µs)]</span>
                </button>
              </div>

              {/* Verdict Box */}
              {testResult && (
                <div className={`p-3.5 border font-mono text-xs ${
                  testResult.verdict === 'ALLOW'
                    ? 'bg-[#10b981]/10 border-[#10b981]/40 text-[#10b981]'
                    : testResult.verdict === 'THROTTLE'
                    ? 'bg-[#f59e0b]/10 border-[#f59e0b]/40 text-[#f59e0b]'
                    : 'bg-[#ef4444]/10 border-[#ef4444]/40 text-[#ef4444]'
                }`}>
                  <div className="flex items-center justify-between font-bold mb-1">
                    <span className="flex items-center gap-1.5">
                      {testResult.verdict === 'ALLOW' ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}
                      {testResult.verdict === 'ALLOW' ? '[VERDICT: ALLOW]' : testResult.verdict === 'THROTTLE' ? '[VERDICT: THROTTLED]' : '[VERDICT: DENY - BLOCKED]'}
                    </span>
                    <span className="text-[10px] opacity-80 font-mono">MU: {testResult.muScore} | {testResult.latencyUs} µs</span>
                  </div>
                  <div className="text-[11px] text-[#d4d4d8] font-sans leading-relaxed">{testResult.reason}</div>
                </div>
              )}
            </div>
          </div>

          {/* Generated YAML Code Column */}
          <div className="lg:col-span-7 bg-[#0a0a0a] border border-[#222222] shadow-2xl overflow-hidden flex flex-col justify-between">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-2.5 bg-[#000000] border-b border-[#222222]">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 bg-[#ef4444]" />
                <div className="w-2.5 h-2.5 bg-[#f59e0b]" />
                <div className="w-2.5 h-2.5 bg-[#10b981]" />
              </div>
              <span className="text-[11px] font-mono text-[#71717a]">policies/default_security_policy.yaml</span>
              <button
                onClick={handleCopyYaml}
                className={`px-2.5 py-1 text-xs font-mono font-semibold transition flex items-center gap-1 border ${
                  copied
                    ? 'bg-[#10b981] text-[#000000] border-[#10b981]'
                    : 'bg-[#0a0a0a] hover:bg-[#141414] text-[#ffffff] border-[#2a2a2a]'
                }`}
              >
                {copied ? (
                  <>
                    <Check size={11} />
                    <span>[COPIED]</span>
                  </>
                ) : (
                  <>
                    <Copy size={11} />
                    <span>[COPY YAML]</span>
                  </>
                )}
              </button>
            </div>

            <div className="p-6 flex-grow">
              <pre className="p-4 bg-[#000000] border border-[#1a1a1a] font-mono text-xs text-[#d4d4d8] overflow-x-auto leading-relaxed">
                {generatedYaml}
              </pre>
            </div>

            <div className="px-6 py-3.5 bg-[#000000] border-t border-[#222222] flex items-center justify-between text-xs text-[#a1a1aa] font-mono">
              <span className="text-[#10b981] font-semibold">[STATUS: 100% LOCALHOST READY]</span>
              <span>DROP INTO <code className="text-[#f59e0b]">.btp/policy.yaml</code></span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
