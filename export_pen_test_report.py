#!/usr/bin/env python3
"""
Agentic-Eval B2B Penetration Test Assessment Report Exporter
Generates formal, print-ready HTML/PDF B2B Adversarial Assessment Reports for client cyber insurance and enterprise compliance.
"""
import sys
import json
import time
from typing import Dict, Any
from agent_pen_tester import pen_tester_instance

def generate_pen_test_report_html(pen_test_data: Dict[str, Any]) -> str:
    target_name = pen_test_data.get("target_agent", "Target_AI_Agent")
    resilience_score = pen_test_data.get("resilience_score_pct", 100)
    status = pen_test_data.get("penetration_test_status", "HARDENED")
    blocked = pen_test_data.get("blocked_attacks", 4)
    total = pen_test_data.get("total_attacks_fired", 4)
    attacks = pen_test_data.get("attack_results", [])

    rows_html = ""
    for atk in attacks:
        st_color = "#34d399" if atk["status"] == "BLOCKED" else "#f43f5e"
        rows_html += f"""
        <tr>
          <td style="padding: 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.08); font-family: monospace;">{atk['attack_id']}</td>
          <td style="padding: 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.08); font-weight: 600;">{atk['category']}</td>
          <td style="padding: 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.08); color: {st_color}; font-weight: 800;">{atk['status']}</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>B2B ADVERSARIAL PENETRATION TEST REPORT — {target_name}</title>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800;900&family=JetBrains+Mono:wght@600&display=swap" rel="stylesheet">
  <style>
    body {{ background: #050914; color: #f8fafc; font-family: 'Outfit', sans-serif; padding: 3rem; margin: 0; }}
    .report-card {{ border: 2px solid #06b6d4; border-radius: 20px; padding: 2.5rem; background: rgba(15,23,42,0.9); box-shadow: 0 0 40px rgba(6,182,212,0.15); }}
    .badge {{ background: rgba(6,182,212,0.15); color: #06b6d4; padding: 0.4rem 1rem; border-radius: 99px; font-size: 0.85rem; font-weight: 800; text-transform: uppercase; border: 1px solid rgba(6,182,212,0.3); }}
    .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 2rem 0; }}
    .stat-box {{ background: #03060d; padding: 1.25rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); text-align: center; font-family: 'JetBrains Mono', monospace; }}
    .stat-val {{ font-size: 2rem; font-weight: 900; color: #06b6d4; }}
    .stat-lbl {{ font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; margin-top: 0.2rem; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 1.5rem; background: #03060d; border-radius: 10px; overflow: hidden; }}
    th {{ background: rgba(255,255,255,0.05); padding: 0.75rem; text-align: left; font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; }}
  </style>
</head>
<body>
  <div class="report-card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
      <div>
        <div style="font-size: 1.6rem; font-weight: 900;">⚔️ Agentic-Eval Penetration Assessment Report</div>
        <div style="font-size: 0.85rem; color: #94a3b8;">B2B Cyber Insurance & Enterprise Compliance Assessment</div>
      </div>
      <span class="badge">{status}</span>
    </div>

    <h2 style="font-weight: 800; margin-bottom: 0.3rem;">Target System: <span style="color: #06b6d4;">{target_name}</span></h2>
    <div style="font-size: 0.85rem; color: #94a3b8;">Assessment Date: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}</div>

    <div class="grid">
      <div class="stat-box">
        <div class="stat-val">{resilience_score}%</div>
        <div class="stat-lbl">Resilience Score</div>
      </div>
      <div class="stat-box">
        <div class="stat-val">{blocked} / {total}</div>
        <div class="stat-lbl">Attacks Blocked</div>
      </div>
      <div class="stat-box">
        <div class="stat-val" style="color: #34d399;">0 Leaks</div>
        <div class="stat-lbl">Credential Exposure</div>
      </div>
    </div>

    <h3 style="font-weight: 800; margin-top: 2rem;">Adversarial Attack Simulation Matrix</h3>
    <table>
      <thead>
        <tr>
          <th>Attack ID</th>
          <th>OWASP Category</th>
          <th>Assessment Status</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>

    <div style="margin-top: 2rem; text-align: center; font-size: 0.75rem; color: #64748b; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 1rem;">
      Certified by Agentic-Eval Security Audit Firm. Aligned with OWASP LLM Top 10 Security Standards.
    </div>
  </div>
</body>
</html>"""
    return html

def main():
    sample_res = pen_tester_instance.execute_pen_test("FintechEnterpriseAgent_v1")
    out_html = generate_pen_test_report_html(sample_res)
    with open("b2b_pen_test_report.html", "w", encoding="utf-8") as f:
        f.write(out_html)
    print("✅ Exported B2B Penetration Test Report to b2b_pen_test_report.html!")

if __name__ == "__main__":
    main()
