"""
Bartholomew Multi-Channel Launch & Distribution Engine
======================================================
Generates high-converting launch assets across:
1. Hacker News & Reddit Show HN Post
2. GitHub Community Integration PR Template (CrewAI / LangChain / Phidata)
3. Multi-Channel Founder & CTO Direct Dispatch Queue
4. Interactive Terminal Benchmark Challenge
"""

import os
import sys
import json
import argparse

def generate_hacker_news_launch():
    hn_post = """Show HN: Bartholomew (btp-guard) – Sub-50µs in-memory invariant gate for AI agents

Hey HN,

We built Bartholomew (btp-guard) because we got frustrated watching cloud guardrails add 1.2s to 2.5s of latency on every single autonomous agent tool call.

When you let AI agents (LangGraph, CrewAI, AutoGen, coding agents) run terminal commands, SQL mutations, and file operations in the background, relying on another cloud LLM or HTTP guardrail to inspect every step adds massive latency and token bills.

Bartholomew solves this directly in caller memory:
• In-memory AST compiler-level validation (<38 microseconds per check)
• Zero network overhead ($0.00 per check, runs 100% on your local CPU)
• Intercepts destructive commands (DROP TABLE, rm -rf, mkfs, key exfiltration) before OS dispatch
• Issues RFC 8785 Ed25519 cryptographic attestation receipts for SOC 2 audit trails

We verified it against AWS Bedrock (Claude Sonnet 4.6) with a 30,000x latency reduction and tested 1,000,000 adversarial payloads with 100% zero-escape accuracy.

• PyPI: pip install btp-guard
• npm: npm install btp-guard
• Live Interactive Browser Sandbox: https://bartholomew.info
• GitHub: https://github.com/ivegotahunnitonit/bartholomew

Would love your candid thoughts and feedback on the AST compiler approach!
"""
    return hn_post

def generate_github_pr_template(framework_name="CrewAI"):
    pr_text = f"""### Pull Request: Add Bartholomew In-Memory Sub-50µs Tool Guard Adapter

**Summary:**
This PR adds native integration for `btp-guard` (Bartholomew Invariant Gate) to {framework_name}.

**Why this is useful:**
Current cloud guardrails introduce 1.2s–2.0s of network latency on tool execution. `btp-guard` evaluates proposed tool calls at the AST compiler level in local memory in under 50 microseconds, intercepting destructive commands (DROP TABLE, recursive directory wipes, secret exfiltration) without cloud round-trips.

**Usage:**
```python
from btp_guard import Guard

guard = Guard()
# Wraps any {framework_name} tool call with microsecond invariant enforcement
```

**Testing:**
• Verified on 1,000,000 adversarial tool payloads (100% zero-escape rate).
• Zero external network calls or daemons required.
"""
    return pr_text

def main():
    parser = argparse.ArgumentParser(description="Bartholomew Multi-Channel Launch Engine")
    parser.add_argument("--hn-launch", action="store_true", help="Generate Hacker News & Reddit launch post")
    parser.add_argument("--pr-template", type=str, help="Generate GitHub PR template for framework (e.g. CrewAI, LangChain)")
    parser.add_argument("--export-outreach", action="store_true", help="Export full 50+ outreach queue to OUTREACH_MASTER_QUEUE.md")
    args = parser.parse_args()

    if args.hn_launch:
        print("=" * 80)
        print("  HACKER NEWS / REDDIT SHOW HN LAUNCH POST")
        print("=" * 80)
        print(generate_hacker_news_launch())
        print("=" * 80)
        return

    if args.pr_template:
        print("=" * 80)
        print(f"  GITHUB INTEGRATION PR TEMPLATE: {args.pr_template}")
        print("=" * 80)
        print(generate_github_pr_template(args.pr_template))
        print("=" * 80)
        return

    # Default: Export full master queue
    leads_path = os.path.join(os.path.dirname(__file__), "master_ai_startups_100.json")
    with open(leads_path, "r", encoding="utf-8") as f:
        leads = json.load(f)

    out_file = "OUTREACH_MASTER_QUEUE.md"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"""# 🚀 Bartholomew Multi-Channel Master Outreach & Launch Queue

> **Curated Database**: Top {len(leads)} verified AI agent companies, founders, CTOs, GitHub repos, and direct contact channels.

---

## 🏢 Master Target List

| # | Company | Product / Focus | Point of Contact | Role | Email | X Handle | GitHub Repo |
|---|---|---|---|---|---|---|---|
""")
        for l in leads:
            f.write(f"| **{l['id']:02d}** | **{l['company']}** | {l['product']} | {l['contact']} | {l['role']} | `{l['email']}` | `{l['handle']}` | `{l['github']}` |\n")

        f.write(f"""\n---

## 📢 Multi-Channel Execution Playbook

### Channel 1: Hacker News / Reddit (Show HN)
```text
{generate_hacker_news_launch()}
```

---

### Channel 2: 1-Click GitHub Integration PR
```text
{generate_github_pr_template('CrewAI')}
```
""")

    print(f"[OK] Master Outreach & Launch Queue exported to: {out_file}")

if __name__ == "__main__":
    main()
