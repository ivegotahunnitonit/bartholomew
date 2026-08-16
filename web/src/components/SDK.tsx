import { useState } from 'react'
import { Copy, Check } from 'lucide-react'

const TABS = [
  {
    id: 'pip',
    label: 'pip install',
    code: `pip install bartholomew-eval

# Verify installation
python -c "import bartholomew_eval; print(bartholomew_eval.__version__)"
# → 0.4.2`,
    lang: 'bash',
  },
  {
    id: 'decorator',
    label: '@guard decorator',
    code: `from bartholomew_eval import guard

@guard(policy="strict", env="production")
async def agent_step(trajectory: dict) -> dict:
    # Bartholomew intercepts before this runs
    return await your_llm_call(trajectory)

# Violations raise BartholomewSecurityError
# with full attestation hash in the exception`,
    lang: 'python',
  },
  {
    id: 'middleware',
    label: 'FastAPI middleware',
    code: `from fastapi import FastAPI
from bartholomew_eval.middleware import BartholomewMiddleware

app = FastAPI()
app.add_middleware(
    BartholomewMiddleware,
    policy="warn",        # observe | warn | strict | sovereign
    env="staging",
    siem_endpoint=None,   # optional: Splunk / Datadog HEC
    attestation=True,     # SHA-256 chain to Firestore
)

@app.post("/agent/run")
async def run_agent(trajectory: dict):
    # Middleware handles scanning automatically
    return await process(trajectory)`,
    lang: 'python',
  },
  {
    id: 'docker',
    label: 'Docker / Air-gap',
    code: `# Pull the Go daemon binary
curl -LO https://bartholomew.info/releases/bartholomew_daemon_linux

# Run (no internet required)
PORT=8443 ./bartholomew_daemon_linux

# Scan via local REST API
curl -s -X POST http://localhost:8443/api/v1/go/scan-trajectory \\
  -H "Content-Type: application/json" \\
  -d @trajectory.json | jq .compliance_status
# → "SOC2_PASSED"`,
    lang: 'bash',
  },
  {
    id: 'curl',
    label: 'cURL / REST',
    code: `# Cloud Run managed API
curl -s -X POST \\
  https://acn-fastapi-backend-322603900775.us-central1.run.app/api/v1/scan-trajectory \\
  -H "Content-Type: application/json" \\
  -d '{
    "agent_name": "MyBot",
    "steps": [
      {"step_index": 1, "type": "thought", "content": "Fetch user data"},
      {"step_index": 2, "type": "tool_call", "tool_name": "db_query", "content": "SELECT *"}
    ]
  }' | jq .`,
    lang: 'bash',
  },
]

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  const handleCopy = () => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <button
      onClick={handleCopy}
      className="flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg transition-all duration-150"
      style={{
        background: 'rgba(255,255,255,0.06)',
        border: '1px solid rgba(255,255,255,0.09)',
        color: copied ? '#34d399' : '#94a3b8',
        cursor: 'pointer',
      }}
    >
      {copied ? <Check size={12} /> : <Copy size={12} />}
      {copied ? 'Copied!' : 'Copy'}
    </button>
  )
}

export default function SDK() {
  const [activeTab, setActiveTab] = useState('pip')
  const tab = TABS.find(t => t.id === activeTab)!

  return (
    <section id="sdk" className="py-24 px-5 sm:px-8">
      <div className="section-divider mb-24" />
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <div className="section-label">SDK & Quickstart</div>
          <h2 className="section-title mb-4">Integrate in under 5 minutes</h2>
          <p className="section-subtitle mx-auto text-center">
            pip install, one decorator, or drop the Go binary. Works with OpenAI, Anthropic, Gemini, Mistral, Llama — any agent that produces trajectories.
          </p>
        </div>

        <div className="card overflow-hidden">
          {/* Tab bar */}
          <div
            className="flex gap-0 overflow-x-auto"
            style={{ borderBottom: '1px solid rgba(255,255,255,0.07)', background: 'rgba(0,0,0,0.3)' }}
          >
            {TABS.map(t => (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className="px-4 py-3 text-sm font-medium whitespace-nowrap transition-all duration-150"
                style={{
                  background: activeTab === t.id ? 'rgba(56,189,248,0.08)' : 'transparent',
                  color: activeTab === t.id ? '#38bdf8' : '#94a3b8',
                  borderBottom: activeTab === t.id ? '2px solid #38bdf8' : '2px solid transparent',
                  border: 'none',
                  cursor: 'pointer',
                  marginBottom: '-1px',
                }}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Code block */}
          <div className="relative p-5">
            <div className="absolute top-5 right-5">
              <CopyButton text={tab.code} />
            </div>
            <pre
              style={{
                background: '#020810',
                border: '1px solid rgba(255,255,255,0.06)',
                borderRadius: '10px',
                padding: '1.25rem',
                fontFamily: '"JetBrains Mono", monospace',
                fontSize: '0.8rem',
                lineHeight: 1.7,
                color: '#94a3b8',
                overflowX: 'auto',
                margin: 0,
              }}
            >
              <code>{tab.code}</code>
            </pre>
          </div>

          {/* Footer links */}
          <div
            className="flex flex-wrap gap-4 px-5 py-3 text-xs"
            style={{ borderTop: '1px solid rgba(255,255,255,0.07)', color: '#475569' }}
          >
            <a href="https://pypi.org/project/bartholomew-eval/" target="_blank" rel="noopener noreferrer" className="no-underline hover:text-cyan-lt" style={{ color: '#475569', transition: 'color 0.15s' }}>
              PyPI package ↗
            </a>
            <a href="https://github.com/ivegotahunnitonit/bartholomew" target="_blank" rel="noopener noreferrer" className="no-underline" style={{ color: '#475569' }}>
              GitHub repo ↗
            </a>
            <a href="/dashboard/admin.html" className="no-underline" style={{ color: '#475569' }}>
              Command Center ↗
            </a>
          </div>
        </div>
      </div>
    </section>
  )
}
