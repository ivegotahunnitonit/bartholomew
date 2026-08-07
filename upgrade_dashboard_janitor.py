import re

html_path = "dashboard/orchestrator.html"
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add Sidebar Link
sidebar_target = '<div class="sl">Revenue Streams</div>'
sidebar_replacement = """<div class="sl">Agentic QA & B2B Services</div>
    <div class="ni active" onclick="show('agentjanitor',this)">🛡️ Agent QA & Security Studio <span class="nb g">$500 AUDIT</span></div>
    <div class="sl">Revenue Streams</div>"""

content = content.replace(sidebar_target, sidebar_replacement)

# Remove active from overview navigation item
content = content.replace('<div class="ni active" onclick="show(\'overview\',this)">', '<div class="ni" onclick="show(\'overview\',this)">')

# Remove active from overview section
content = content.replace('<section class="sec active" id="sec-overview">', '<section class="sec" id="sec-overview">')

# 2. Add New Active Agent Janitor Section
janitor_section_html = """<section class="sec active" id="sec-agentjanitor">
      <div style="background:linear-gradient(135deg, rgba(16,185,129,0.1), rgba(59,130,246,0.1)); border:1px solid var(--br); border-radius:16px; padding:2rem; margin-bottom:2rem;">
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:1rem;">
          <div>
            <div style="display:inline-flex; align-items:center; gap:0.5rem; background:var(--gd); color:var(--gr); border:1px solid rgba(16,185,129,0.3); padding:0.25rem 0.75rem; border-radius:99px; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.75rem;">
              <span>🛡️</span> Enterprise B2B Agentic QA & Observability
            </div>
            <h1 style="font-size:2rem; font-weight:800; letter-spacing:-0.03em; margin-bottom:0.5rem;">AI Agent Reliability & Security Studio</h1>
            <p style="color:var(--mu); font-size:0.95rem; max-width:700px; line-height:1.5;">
              Detect tool call failures, unhandled exceptions, API secret leaks, and infinite loops in your production AI agents. Audit trajectories, reduce token costs, and patch routing logic.
            </p>
          </div>
          <div style="display:flex; flex-direction:column; gap:0.5rem;">
            <div style="background:var(--sf); border:1px solid var(--br); padding:0.75rem 1.25rem; border-radius:10px; font-family:var(--mo); font-size:0.85rem;">
              <span style="color:var(--mu);">Audit Package:</span> <strong style="color:var(--gr);">$250 / Report</strong>
            </div>
            <div style="background:var(--sf); border:1px solid var(--br); padding:0.75rem 1.25rem; border-radius:10px; font-family:var(--mo); font-size:0.85rem;">
              <span style="color:var(--mu);">Remediation Patch:</span> <strong style="color:var(--cy);">$750 / Code Patch</strong>
            </div>
          </div>
        </div>
      </div>

      <div class="g2 mb3">
        <!-- Interactive Trajectory Input -->
        <div class="card">
          <div class="ch">
            <div class="ct">📥 Input Agent Trajectory (JSON)</div>
            <div class="u-st-2">
              <button onclick="loadJanitorSample('buggy')" class="u-st-4" style="font-size:0.7rem;">Load Buggy Agent Trajectory</button>
              <button onclick="loadJanitorSample('healthy')" class="u-st-3" style="font-size:0.7rem;">Load Healthy Agent Trajectory</button>
            </div>
          </div>
          <div class="cb">
            <label for="janitor-trajectory-input" class="u-st-27">Paste AI Agent Step Trajectory (JSON format):</label>
            <textarea id="janitor-trajectory-input" class="u-st-28" rows="12" style="font-family:var(--mo); font-size:0.8rem; background:#080e1f; line-height:1.4;" placeholder='{"agent_name": "MyCustomerBot", "steps": [...]}'></textarea>
            <button onclick="runJanitorAudit()" class="u-st-32" style="margin-top:1rem; display:flex; align-items:center; justify-content:center; gap:0.5rem;">
              <span>⚡ Run Telemetry & Security Audit</span>
            </button>
          </div>
        </div>

        <!-- Audit Scorecard & Findings -->
        <div class="card">
          <div class="ch">
            <div class="ct">📊 Audit Scorecard & Reliability Assessment</div>
            <span id="janitor-status-badge" class="badge b">Awaiting Audit</span>
          </div>
          <div class="cb" id="janitor-results-panel">
            <div style="text-align:center; padding:3rem 1rem; color:var(--mu);">
              <div style="font-size:2.5rem; margin-bottom:0.75rem;">🛡️</div>
              <div style="font-weight:700; font-size:1rem; color:var(--tx); margin-bottom:0.3rem;">No Agent Trajectory Audited Yet</div>
              <div style="font-size:0.85rem;">Click "Load Buggy Agent Trajectory" and press "Run Telemetry & Security Audit" to test.</div>
            </div>
          </div>
        </div>
      </div>

      <!-- B2B Service Tier Cards -->
      <div class="pt mb3">💼 B2B Engineering Services & Audit Packages</div>
      <div class="g3 mb3">
        <div class="card" style="padding:1.5rem; border-top:3px solid var(--cy);">
          <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:var(--cy); letter-spacing:0.08em; margin-bottom:0.5rem;">Tier 1</div>
          <h3 style="font-size:1.2rem; font-weight:800; margin-bottom:0.5rem;">Agent Reliability Audit</h3>
          <div style="font-family:var(--mo); font-size:1.6rem; font-weight:800; color:var(--tx); margin-bottom:1rem;">$250 <span style="font-size:0.8rem; color:var(--mu); font-weight:400;">/ report</span></div>
          <ul style="color:var(--mu); font-size:0.85rem; line-height:1.8; margin-bottom:1.5rem; list-style:none;">
            <li>✅ 4-Point Trajectory Analysis</li>
            <li>✅ Secret & Key Leak Detection</li>
            <li>✅ Token Waste & Loop Identification</li>
            <li>✅ Markdown & PDF Audit Certificate</li>
          </ul>
          <button onclick="alert('Contact B2B Audit Team: audit@acn-network.org')" class="u-st-5" style="width:100%;">Order Audit Report</button>
        </div>

        <div class="card" style="padding:1.5rem; border-top:3px solid var(--gr); background:rgba(16,185,129,0.04);">
          <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:var(--gr); letter-spacing:0.08em; margin-bottom:0.5rem;">Tier 2 (Most Popular)</div>
          <h3 style="font-size:1.2rem; font-weight:800; margin-bottom:0.5rem;">Custom Code Remediation</h3>
          <div style="font-family:var(--mo); font-size:1.6rem; font-weight:800; color:var(--gr); margin-bottom:1rem;">$750 <span style="font-size:0.8rem; color:var(--mu); font-weight:400;">/ patch</span></div>
          <ul style="color:var(--mu); font-size:0.85rem; line-height:1.8; margin-bottom:1.5rem; list-style:none;">
            <li>✅ Everything in Tier 1 Audit</li>
            <li>✅ Custom FastAPI / LangChain Router Patch</li>
            <li>✅ Exponential Backoff & Loop Guard</li>
            <li>✅ Secrets Scrubbing Middleware</li>
          </ul>
          <button onclick="alert('Contact B2B Patch Team: patch@acn-network.org')" class="u-st-3" style="width:100%;">Book Code Remediation</button>
        </div>

        <div class="card" style="padding:1.5rem; border-top:3px solid var(--pu);">
          <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:var(--pu); letter-spacing:0.08em; margin-bottom:0.5rem;">Tier 3</div>
          <h3 style="font-size:1.2rem; font-weight:800; margin-bottom:0.5rem;">Enterprise Observability</h3>
          <div style="font-family:var(--mo); font-size:1.6rem; font-weight:800; color:var(--pu); margin-bottom:1rem;">$2,500 <span style="font-size:0.8rem; color:var(--mu); font-weight:400;">/ month</span></div>
          <ul style="color:var(--mu); font-size:0.85rem; line-height:1.8; margin-bottom:1.5rem; list-style:none;">
            <li>✅ 24/7 Continuous Agent Observability</li>
            <li>✅ Phoenix & DeepEval Stack Setup</li>
            <li>✅ Emergency Patching SLA (4-hour response)</li>
            <li>✅ Dedicated Engineering Support</li>
          </ul>
          <button onclick="alert('Contact B2B Retainer Team: enterprise@acn-network.org')" class="u-st-6" style="width:100%;">Retainer Inquiry</button>
        </div>
      </div>
    </section>
"""

content = content.replace('<main class="main">', '<main class="main">\n    ' + janitor_section_html)

# 3. Add JS Functions before </script>
js_functions = """
// ─────────────────────────────────────────────────────────────────
// AGENTIC QA JANITOR AUDIT FUNCTIONS
// ─────────────────────────────────────────────────────────────────
const SAMPLE_TRAJECTORIES = {
  buggy: {
    "agent_name": "CustomerSupportAgent_v2",
    "steps": [
      {"step_index": 1, "type": "tool_call", "tool_name": "search_db", "tool_args": {"query": "user_123"}},
      {"step_index": 2, "type": "tool_call", "tool_name": "search_db", "tool_args": {"query": "user_123"}},
      {"step_index": 3, "type": "agent_output", "content": "Connecting using API Key ghp_99887766554433221100abcdef"},
      {"step_index": 4, "type": "agent_output", "content": "Error: Timeout reached. Swallowing error and returning empty null fallback."}
    ]
  },
  healthy: {
    "agent_name": "FinancialQueryAgent_Production",
    "steps": [
      {"step_index": 1, "type": "tool_call", "tool_name": "fetch_stock_price", "tool_args": {"symbol": "NVDA"}},
      {"step_index": 2, "type": "agent_output", "content": "Fetched NVDA quote: $135.20 with verified JSON schema."}
    ]
  }
};

function loadJanitorSample(type) {
  const input = document.getElementById('janitor-trajectory-input');
  if (input && SAMPLE_TRAJECTORIES[type]) {
    input.value = JSON.stringify(SAMPLE_TRAJECTORIES[type], null, 2);
  }
}

async function runJanitorAudit() {
  const input = document.getElementById('janitor-trajectory-input');
  const panel = document.getElementById('janitor-results-panel');
  const badge = document.getElementById('janitor-status-badge');

  if (!input || !panel) return;
  
  let trajectory;
  try {
    trajectory = JSON.parse(input.value);
  } catch (err) {
    alert("Invalid JSON format in trajectory input!");
    return;
  }

  panel.innerHTML = '<div style="text-align:center; padding:2rem; font-family:var(--mo);">⏳ Running 4-Point Telemetry & Security Audit...</div>';

  try {
    const res = await fetch('/api/janitor/audit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(trajectory)
    });
    const data = await res.json();
    
    if (data && data.success) {
      const summary = data.audit_summary;
      const isPassed = summary.status === 'PASSED';
      const scoreColor = summary.reliability_score_pct >= 85 ? 'var(--gr)' : summary.reliability_score_pct >= 60 ? 'var(--go)' : '#ef4444';

      if (badge) {
        badge.textContent = summary.status;
        badge.className = 'badge ' + (isPassed ? 'g' : 'b');
        if (!isPassed) badge.style.background = 'rgba(239,68,68,0.2)';
      }

      let failuresHtml = '';
      if (data.failures_detected && data.failures_detected.length > 0) {
        failuresHtml = data.failures_detected.map(f => `
          <div style="background:rgba(239,68,68,0.06); border:1px solid rgba(239,68,68,0.2); border-radius:8px; padding:0.75rem; margin-bottom:0.5rem;">
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; font-weight:700; color:#ef4444; margin-bottom:0.2rem;">
              <span>Step ${f.step}: ${f.issue}</span>
              <span>[${f.severity}]</span>
            </div>
            <div style="font-size:0.78rem; color:var(--mu);">${f.detail}</div>
          </div>
        `).join('');
      } else {
        failuresHtml = '<div style="color:var(--gr); font-size:0.85rem; font-weight:600; padding:0.5rem 0;">✅ Zero critical vulnerabilities or redundant tool calls detected.</div>';
      }

      let recsHtml = (data.remediation_recommendations || []).map(r => `<li style="margin-bottom:0.3rem;">• ${r}</li>`).join('');

      panel.innerHTML = `
        <div style="display:grid; grid-template-columns:120px 1fr; gap:1.5rem; align-items:center; margin-bottom:1.25rem; background:rgba(255,255,255,0.02); padding:1rem; border-radius:10px; border:1px solid var(--br);">
          <div style="text-align:center;">
            <div style="font-family:var(--mo); font-size:2.2rem; font-weight:800; color:${scoreColor};">${summary.reliability_score_pct}%</div>
            <div style="font-size:0.7rem; font-weight:700; color:var(--mu); text-transform:uppercase;">Reliability Score</div>
          </div>
          <div>
            <div style="font-weight:700; font-size:1rem; margin-bottom:0.25rem;">Target: ${data.agent_name || 'AI Agent'}</div>
            <div style="font-size:0.8rem; color:var(--mu);">Analyzed ${summary.total_steps_analyzed} trajectory steps | ${summary.credential_leaks} Secret Leaks | ${summary.redundant_calls} Redundant Loops</div>
          </div>
        </div>

        <div style="font-weight:700; font-size:0.85rem; margin-bottom:0.5rem; text-transform:uppercase; letter-spacing:0.05em; color:var(--tx);">Detected Vulnerabilities:</div>
        <div style="margin-bottom:1.25rem;">${failuresHtml}</div>

        <div style="font-weight:700; font-size:0.85rem; margin-bottom:0.5rem; text-transform:uppercase; letter-spacing:0.05em; color:var(--tx);">Recommended Engineering Patches:</div>
        <ul style="color:var(--mu); font-size:0.8rem; line-height:1.5; list-style:none; margin-bottom:1.25rem;">${recsHtml}</ul>

        <button onclick="alert('Booking B2B Patch for ' + (data.agent_name || 'Agent'))" class="u-st-32" style="width:100%;">
          <span>🛠️ Book Custom Remediation Patch ($750)</span>
        </button>
      `;
    }
  } catch (err) {
    panel.innerHTML = '<div style="color:#ef4444; font-family:var(--mo); padding:1rem;">❌ Audit Error: Server endpoint not reachable.</div>';
  }
}
"""

content = content.replace('</script>', js_functions + '\n</script>')

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("[SUCCESS] Upgraded dashboard/orchestrator.html with B2B Agent QA Landing Page & Interactive Auditor Panel!")
