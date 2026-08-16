import urllib.request
import json

url = "http://localhost:8000/api/v1/stripe/create-checkout-session"
data = {
    "plan_tier": "b2b_audit",
    "email": "enterprise@client.com"
}

req = urllib.request.Request(
    url,
    data=json.dumps(data).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

try:
    res = urllib.request.urlopen(req)
    result = json.loads(res.read().decode("utf-8"))
    print("[OK] Stripe Checkout Session Response:")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"[FAIL] Stripe Checkout Test Failed: {e}")
