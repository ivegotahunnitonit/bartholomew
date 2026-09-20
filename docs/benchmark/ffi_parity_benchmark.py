"""
Bartholomew High-Throughput FFI & Runtime Latency Benchmark (BTP v2.5.0)
========================================================================
Measures microsecond-level execution latency across 10,000 continuous cycles
for each core execution component:
  1. Polyglot AST Obfuscation Scanner (<2.0 µs target).
  2. RFC 8785 Canonical JSON Serialization & SHA-256 Digest (<1.5 µs target).
  3. FIPS 186-5 Ed25519 Asymmetric Receipt Signature (<3.0 µs target).
  4. End-to-End Pre-Flight Invariant Gating (<5.0 µs target).
"""

import time
import json
import statistics
from src.trust_protocol import BartholomewTrustAuthority, rfc8785_canonicalize
from src.polyglot_ast_validator import PolyglotASTValidator

def run_parity_benchmark(iterations: int = 10000):
    print("=" * 75)
    print(f"BARTHOLOMEW MICRO-LATENCY BENCHMARK ({iterations:,} CYCLES)")
    print("Protocol Version: BTP/2.5.0 (RFC 8785 + FIPS 186-5 Ed25519)")
    print("=" * 75)

    auth = BartholomewTrustAuthority()
    sample_payload = {
        "action": "QUERY_RECORDS",
        "sql": "SELECT name, email FROM users WHERE tenant_id = 'org_441' LIMIT 20;",
        "amount_usd": 15.50
    }
    sample_code = "cursor.execute('SELECT name, email FROM users WHERE tenant_id = ?;', ('org_441',))"

    # 1. AST Invariant Evaluation
    ast_latencies = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        PolyglotASTValidator.validate_code(sample_code)
        ast_latencies.append((time.perf_counter() - t0) * 1_000_000)

    # 2. Canonical JSON Serialization + SHA-256
    canon_latencies = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        canon_bytes = rfc8785_canonicalize(sample_payload)
        canon_latencies.append((time.perf_counter() - t0) * 1_000_000)

    # 3. Ed25519 Signing
    raw_canon = rfc8785_canonicalize({"data": "benchmark_payload"})
    sign_latencies = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        auth.private_key.sign(raw_canon)
        sign_latencies.append((time.perf_counter() - t0) * 1_000_000)

    # 4. Full End-to-End BTP Pre-Flight Gate
    e2e_latencies = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        auth.evaluate_intent(
            agent_id="bench_agent",
            action_type="QUERY_RECORDS",
            payload=sample_payload
        )
        e2e_latencies.append((time.perf_counter() - t0) * 1_000_000)

    def print_metrics(label: str, lats: list):
        p50 = statistics.median(lats)
        p90 = statistics.quantiles(lats, n=10)[8]
        p99 = statistics.quantiles(lats, n=100)[98]
        avg = statistics.mean(lats)
        throughput = 1_000_000.0 / avg
        print(f"[*] {label:<35} | p50: {p50:5.2f} µs | p90: {p90:5.2f} µs | p99: {p99:5.2f} µs | {throughput:>10,.0f} evals/sec")

    print_metrics("Polyglot AST Scanner", ast_latencies)
    print_metrics("RFC 8785 Canonical JCS", canon_latencies)
    print_metrics("Pure Ed25519 Signing", sign_latencies)
    print("-" * 75)
    print_metrics("Full End-to-End Pre-Flight Gate", e2e_latencies)
    print("=" * 75)

if __name__ == "__main__":
    run_parity_benchmark()
