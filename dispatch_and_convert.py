#!/usr/bin/env python3
"""
Agentic-Eval B2B Sales Conversion & Invoice Link Generator v1.0
================================================================
Generates customized sales conversion pitches containing live Stripe Checkout URLs
for B2B Security Audits ($250) and Pro Team Subscriptions ($99/mo).
"""
import sys
import json
import os
from pathlib import Path

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    from python_backend.app.stripe_billing_engine import billing_engine
except ImportError:
    billing_engine = None

def generate_conversion_pitch(company_name: str, target_user: str = "Founder") -> Dict[str, Any]:
    checkout_audit = "https://agentic-eval.com/checkout/audit_250"
    checkout_pro = "https://agentic-eval.com/checkout/pro_99"

    if billing_engine:
        res_audit = billing_engine.create_checkout_session("b2b_audit", f"{target_user}@example.com")
        res_pro = billing_engine.create_checkout_session("pro_team", f"{target_user}@example.com")
        if res_audit.get("success"):
            checkout_audit = res_audit["checkout_url"]
        if res_pro.get("success"):
            checkout_pro = res_pro["checkout_url"]

    pitch_text = f"""
================================================================================
[TARGET] INSTANT SALES CONVERSION PITCH FOR: {company_name} ({target_user})
================================================================================

Hey {target_user},

Here are your instant activation links for {company_name}'s OWASP Security Audit:

1. [AUDIT] Official B2B OWASP Audit Certificate ($250 One-Time):
   {checkout_audit}

2. [PRO] Pro Team CI/CD Observability & Key Guard ($99/month):
   {checkout_pro}

Once completed, your verified SHA-256 attestation certificate and vector README badge will issue automatically.
================================================================================
"""
    return {
        "company": company_name,
        "target_user": target_user,
        "checkout_audit_url": checkout_audit,
        "checkout_pro_url": checkout_pro,
        "pitch_text": pitch_text
    }

if __name__ == "__main__":
    company = sys.argv[1] if len(sys.argv) > 1 else "FintechBot Inc"
    user = sys.argv[2] if len(sys.argv) > 2 else "CEO"
    res = generate_conversion_pitch(company, user)
    print(res["pitch_text"])
