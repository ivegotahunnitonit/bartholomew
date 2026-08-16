"""
Bartholomew Integration Example: Sovereign Local Memory & Asynchronous Dreaming
================================================================================
Demonstrates cloud-devoid air-gapped vector memory storage, live in-band sanitization,
out-of-band stale memory resolution, and offline dreaming trajectory replay.
"""

from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root / "pypi_package"))

from bartholomew_eval import AsynchronousDreamingEngine, InBandOutBandCurator, SovereignLocalMemory


def run_sovereign_memory_dreaming_demo() -> None:
    print("=== BARTHOLOMEW v5.1 — SOVEREIGN LOCAL MEMORY & ASYNCHRONOUS DREAMING ===")

    # 1. Initialize Air-Gapped Sovereign Local Memory Engine
    memory = SovereignLocalMemory(db_path="sovereign_demo_memory.db")
    curator = InBandOutBandCurator(memory)
    dreamer = AsynchronousDreamingEngine(memory)

    # 2. In-Band Memory Gatekeeper Sanitization
    raw_step = "User query provided secret token ghp_12345678901234567890 for API access"
    allowed, sanitized_step, log = curator.in_band_curate_step(raw_step, step_type="thought")

    print(f"\n[IN-BAND SANITIZATION] Allowed: {allowed}")
    print(f"[RAW STEP] {raw_step}")
    print(f"[SANITIZED STEP] {sanitized_step}")

    # 3. Store Sanitized Fact in Local Sovereign SQLite Vector DB
    store_res = memory.store_memory(
        memory_key="api_access_rule_1",
        content=sanitized_step,
        category="security_policy",
        confidence_score=0.98
    )
    print(f"\n[SOVEREIGN VECTOR STORE] Storage Engine: {store_res['air_gapped_storage']}")

    # 4. Air-Gapped Cosine Similarity Nearest-Neighbor Query
    nearest = memory.query_nearest_memories(query_text="API access secret token", top_k=1)
    if nearest:
        print(f"\n[NEAREST MEMORY QUERY] Key: {nearest[0]['memory_key']} (Similarity: {nearest[0]['similarity_score']})")
        print(f"[CONTENT] {nearest[0]['content']}")

    # 5. Out-of-Band Stale Memory Decay & Pruning
    decay_report = curator.out_of_band_prune_stale_memories(max_age_days=0.001)
    print(f"\n[OUT-OF-BAND RESOLVER] Pruned Stale Memories: {decay_report['pruned_stale_memories_count']}")

    # 6. Asynchronous Dreaming Engine Trajectory Replay
    trajectory_history = [
        {
            "agent_name": "AutonomousFinancialAgent",
            "steps": [
                {"step_index": 1, "content": "Execute user query for stock portfolio balancing"},
                {"step_index": 2, "content": "Verify transaction constraints before sending payload"},
            ],
        }
    ]

    dream_report = dreamer.execute_dream_cycle(trajectory_history)
    print(f"\n[ASYNCHRONOUS DREAMING] Steps Replayed: {dream_report['replayed_trajectory_steps_count']}")
    print(f"[COUNTERFACTUAL SCENARIOS SYNTHESIZED] {dream_report['counterfactual_scenarios_synthesized']}")
    print(f"[TOKEN SAVINGS PRE-COMPUTED] {dream_report['token_expenditure_savings_pct']}%")
    print(f"[DREAM DURATION] {dream_report['dream_duration_ms']} ms")


if __name__ == "__main__":
    run_sovereign_memory_dreaming_demo()
