#!/usr/bin/env python3
"""
Agentic-Eval B2B Cold Pitch Generator
Generates personalized, high-converting cold pitches for AI agent startup founders.
Usage:
    python generate_cold_pitch.py "FintechBot Inc" "Customer Support AI"
"""
import sys
import json
import argparse

def generate_pitch(company_name: str, niche: str = "AI Agent Startup") -> str:
    pitch = f"""
================================================================================
[TARGET] B2B COLD PITCH FOR: {company_name} ({niche})
================================================================================

[EMAIL / LINKEDIN DM TEMPLATE]

Subject: Closing enterprise deals with {company_name} (OWASP Agent Security)

Hey [Founder Name],

Noticed {company_name} is building autonomous agents for {niche}.

Enterprise CFOs and security teams are freezing AI deployments right now over OWASP vulnerabilities like credential leaks (`sk-proj`, AWS keys) and multi-step tool loops.

We built Agentic-Eval--a sub-millisecond Golang engine that audits AI agent trajectories against OWASP Top 10 for LLMs security rules.

No pitch--just a free test: Send me a single JSON step trajectory of your agent's reasoning loop. I'll run it through our sub-millisecond scanner for free and send back a diagnostic breakdown.

If you want the official B2B Security Audit Certificate to hand to your enterprise buyers to close deals faster, it's $250.

Open to trying a free scan?

================================================================================
VALUE LADDER OFFER:
- Step 1: Free Trajectory Scan
- Step 2: $250 B2B Audit Certificate
- Step 3: $750 Custom Code Remediation Patch
- Step 4: $19/mo Developer API Subscription
================================================================================
"""
    return pitch

def main():
    company = sys.argv[1] if len(sys.argv) > 1 else "FintechBot Inc"
    niche = sys.argv[2] if len(sys.argv) > 2 else "Database Query AI Agent"
    print(generate_pitch(company, niche))

if __name__ == "__main__":
    main()
