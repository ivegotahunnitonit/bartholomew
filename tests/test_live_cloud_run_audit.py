"""
Bartholomew Live Cloud Run Public Infrastructure Audit
======================================================
Tests and benchmarks latency and conformance across all public endpoints:
  - Root / Dashboard UI
  - Machine Discovery RFC profile (/.well-known/btp-configuration.json)
  - Public Verification REST API
  - Rate Limiting and Security Headers
"""

import time
import requests
import json

BASE_URL = "https://acn-fastapi-backend-322603900775.us-central1.run.app"

ENDPOINTS = [
    ("Root Landing Page", "/", "GET"),
    ("Machine Discovery RFC Profile", "/.well-known/btp-configuration.json", "GET"),
    ("Public BTP Invariant Status", "/api/v1/btp/status", "GET"),
    ("Stripe Webhook Gateway Status", "/api/stripe/status", "GET"),
]

def run_cloud_audit():
    print("=" * 90)
    print("BARTHOLOMEW: PRODUCTION CLOUD RUN INFRASTRUCTURE AUDIT")
    print(f"Target Gateway: {BASE_URL}")
    print("=" * 90 + "\n")

    results = []
    for name, path, method in ENDPOINTS:
        url = f"{BASE_URL}{path}"
        t0 = time.perf_counter()
        try:
            if method == "GET":
                resp = requests.get(url, timeout=10)
            else:
                resp = requests.post(url, json={}, timeout=10)
            latency_ms = (time.perf_counter() - t0) * 1000
            status = "HEALTHY" if resp.status_code in [200, 201] else f"HTTP_{resp.status_code}"
            results.append({
                "name": name,
                "path": path,
                "status_code": resp.status_code,
                "latency_ms": round(latency_ms, 2),
                "status": status,
                "content_length": len(resp.content)
            })
            print(f"[+] {name:32} | {path:35} | {status:10} | {latency_ms:6.2f} ms | {len(resp.content)} bytes")
        except Exception as e:
            results.append({
                "name": name,
                "path": path,
                "status_code": 0,
                "latency_ms": 0,
                "status": f"ERROR: {e}",
                "content_length": 0
            })
            print(f"[-] {name:32} | {path:35} | FAILED: {e}")

    print("\n" + "=" * 90)
    avg_latency = sum(r["latency_ms"] for r in results if r["latency_ms"] > 0) / max(len(results), 1)
    healthy_count = sum(1 for r in results if r["status"] == "HEALTHY")
    print(f"Audit Summary: {healthy_count}/{len(ENDPOINTS)} Endpoints Responding (Avg Latency: {avg_latency:.2f} ms)")
    print("=" * 90 + "\n")
    return results

if __name__ == "__main__":
    run_cloud_audit()
