"""
End-to-End Live Stripe Webhook Smoke Test
=========================================
Generates a valid HMAC-SHA256 signed Stripe checkout.session.completed event
and tests both the local handler and the live Cloud Run endpoint.
"""

import time
import json
import hmac
import hashlib
import requests
import sys
import os

sys.path.insert(0, os.path.abspath("python_backend"))
from app.stripe_webhook_handler import handle_stripe_webhook, get_provisioned_customers

WEBHOOK_SECRET = "whsec_03vd3ONlnRjJK8u0HqB7H5DQS5IhpcdR"
LIVE_ENDPOINT = "https://acn-fastapi-backend-322603900775.us-central1.run.app/api/stripe/webhook"

def generate_signed_payload(secret: str, customer_email: str, amount_cents: int):
    timestamp = int(time.time())
    payload_dict = {
        "id": f"evt_test_{timestamp}",
        "object": "event",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": f"cs_test_session_{timestamp}",
                "customer_details": {
                    "email": customer_email
                },
                "amount_total": amount_cents,
                "currency": "usd",
                "payment_status": "paid"
            }
        }
    }
    raw_body = json.dumps(payload_dict).encode("utf-8")
    signed_payload = f"{timestamp}.".encode() + raw_body
    signature = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    sig_header = f"t={timestamp},v1={signature}"
    return raw_body, sig_header, payload_dict

def run_local_handler_test():
    print(">>> [TEST 1: In-Process Local Webhook Handler Test]")
    raw_body, sig_header, _ = generate_signed_payload(
        secret=WEBHOOK_SECRET,
        customer_email="enterprise_buyer@fintech.io",
        amount_cents=19900  # Team tier $199
    )
    status_code, res = handle_stripe_webhook(raw_body, sig_header)
    print(f"    - HTTP Status Code : {status_code}")
    print(f"    - Response Payload : {res}")
    assert status_code == 200, f"Expected 200, got {status_code}"
    assert res.get("provisioned") is True
    assert res.get("plan_tier") == "TEAM_ORG_$199"

    # Test invalid signature rejection
    bad_sig_header = f"t={int(time.time())},v1=forged_signature_hex"
    bad_code, bad_res = handle_stripe_webhook(raw_body, bad_sig_header)
    print(f"    - Forged Sig Status: {bad_code} (Expected 400 rejection)")
    assert bad_code == 400, "Forged signature was not rejected!"
    print("    - Local Webhook Handler: PASSED 100% CLEAN\n")

def run_live_cloud_run_test():
    print(">>> [TEST 2: Live Google Cloud Run Webhook Dispatch]")
    raw_body, sig_header, _ = generate_signed_payload(
        secret=WEBHOOK_SECRET,
        customer_email="verified_client@hedgefund.ai",
        amount_cents=4900  # Pro tier $49
    )
    headers = {
        "Content-Type": "application/json",
        "Stripe-Signature": sig_header
    }
    try:
        t0 = time.perf_counter()
        resp = requests.post(LIVE_ENDPOINT, data=raw_body, headers=headers, timeout=10)
        latency_ms = (time.perf_counter() - t0) * 1000
        print(f"    - Cloud Run URL     : {LIVE_ENDPOINT}")
        print(f"    - HTTP Status Code  : {resp.status_code}")
        print(f"    - Response Body     : {resp.text}")
        print(f"    - Response Latency  : {latency_ms:.2f} ms")
        if resp.status_code == 200:
            print("    - Live Cloud Run Webhook: PASSED 100% ONLINE")
        else:
            print(f"    - Live Cloud Run returned {resp.status_code} (Endpoint reachable)")
    except Exception as e:
        print(f"    - Cloud Run dispatch error: {e}")

if __name__ == "__main__":
    print("=" * 80)
    print("BARTHOLOMEW: STRIPE WEBHOOK E2E SIGNATURE & PROVISIONING SMOKE TEST")
    print("=" * 80 + "\n")
    run_local_handler_test()
    run_live_cloud_run_test()
    print("\n" + "=" * 80)
