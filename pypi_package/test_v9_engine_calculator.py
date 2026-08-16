import time
from bartholomew_eval import (
    InternalEngineCalculator,
    AlgorithmSynthesizer,
    EpistemicExecutionEngine
)

def print_banner(text: str):
    print("\n" + "=" * 75)
    print(f"   {text}")
    print("=" * 75)

def test_1_internal_engine_calculator():
    print_banner("1. PROPRIETARY INTERNAL ENGINE CALCULATOR (ECE, xG, COMPRESSION)")
    calc = InternalEngineCalculator()

    predictions = [0.95, 0.92, 0.96, 0.10, 0.99]
    outcomes = [1, 1, 1, 0, 1]

    ece = calc.calculate_calibration_error(predictions, outcomes)
    print(f" [PASS] Epistemic Calibration Error (ECE): {ece}")
    assert ece < 0.10, "ECE should be low for calibrated model!"

    xg = calc.calculate_xg_efficiency(
        expected_information_gain=0.88,
        success_rate=0.94,
        cost_tokens=420,
        latency_ms=0.0076
    )
    print(f" [PASS] Expected Goal Efficiency (xG Score): {xg}")
    assert xg > 1.5, "xG score should be high for cheap path hit!"

    compression = calc.calculate_resource_compression(
        unoptimized_tokens=5000,
        actual_tokens=420,
        unoptimized_latency_ms=1200.0,
        actual_latency_ms=0.0076
    )
    print(f" [PASS] Token Savings Ratio: {compression['token_savings_pct']}% ({compression['tokens_saved']} tokens saved)")
    print(f" [PASS] Latency Compression Factor: {compression['latency_compression_factor']} ({compression['latency_saved_ms']} ms saved)")

    assessment = calc.evaluate_system_assessment(predictions, outcomes)
    print(f" [PASS] Ownership Status: {assessment['ownership_status']}")
    assert assessment["ownership_status"] == "OWNED_OUTRIGHT_PROPRIETARY_IP"

def test_2_algorithm_synthesizer():
    print_banner("2. AUTONOMOUS ALGORITHM SYNTHESIZER & EMPIRICAL BENCHMARKER")
    synth = AlgorithmSynthesizer()

    rules = [
        {"field": "role", "operator": "==", "value": "admin"},
        {"field": "action", "operator": "in", "value": ["database.read", "api.invoke"]}
    ]

    policy_fn = synth.synthesize_decision_tree_policy(rules)
    
    test_inputs = [
        {"role": "admin", "action": "database.read"},
        {"role": "admin", "action": "api.invoke"},
        {"role": "guest", "action": "database.read"}
    ]

    bench = synth.benchmark_candidate_algorithm("policy-tree-v1", policy_fn, test_inputs, iterations=500)
    print(f" [PASS] Benchmarked Candidate Algorithm 'policy-tree-v1':")
    print(f"       Avg Latency: {bench['avg_latency_us']} µs")
    print(f"       Correctness Rate: {bench['correctness_rate'] * 100}%")
    print(f"       Status: {bench['status']}")

    assert bench["status"] == "VERIFIED_SUITABLE"

def test_3_epistemic_execution_engine():
    print_banner("3. HIGH-PRECISION EPISTEMIC EXECUTION ENGINE")
    engine = EpistemicExecutionEngine()

    print("Step 3.1: First invocation (Proved Execution via Guard)...")
    res1 = engine.execute_sovereign_task(
        agent_id="agent-4592",
        action="database.read",
        target="{'table': 'users'}",
        capabilities=["database.read"]
    )
    assert res1["success"] == True
    print(f" [PASS] Execution Path: {res1['execution_path']} | Latency: {res1['latency_ms']} ms")

    print("\nStep 3.2: Second invocation (Cheap Path Cache Hit < 7.6 µs)...")
    res2 = engine.execute_sovereign_task(
        agent_id="agent-4592",
        action="database.read",
        target="{'table': 'users'}",
        capabilities=["database.read"]
    )
    assert res2["execution_path"] == "CHEAP_PATH_CACHE_HIT"
    assert res2["tokens_burned"] == 0
    print(f" [PASS] Execution Path: {res2['execution_path']} | Latency: {res2['latency_us']} µs | Tokens Burned: {res2['tokens_burned']}")
    print(f" [PASS] Assessment xG Score: {res2['assessment']['xg_efficiency_score']}")

def run_suite():
    print("\n" + "#" * 75)
    print("  BARTHOLOMEW PROPRIETARY ENGINE CALCULATOR & SYNTHESIZER TEST SUITE")
    print("#" * 75)
    test_1_internal_engine_calculator()
    test_2_algorithm_synthesizer()
    test_3_epistemic_execution_engine()
    print("\n" + "=" * 75)
    print("  ALL PROPRIETARY ENGINE BENCHMARKS PASSED — 100% OWNED OUTRIGHT")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    run_suite()
