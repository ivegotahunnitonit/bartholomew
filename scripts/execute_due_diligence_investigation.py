#!/usr/bin/env python3
"""
Autonomous Due Diligence Investigation: Live Falsification & Evidence Chain
===========================================================================
Executes reality interrogation on corporate technical claims by correlating
disparate primary sources (Git commits, job postings, network telemetry, docs).
"""

import sys
import os

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.due_diligence_operator import DueDiligenceOperator


def run_investigation():
    print("=" * 105)
    print("BARTHOLOMEW: AUTONOMOUS DUE DILIGENCE & TECHNICAL FACT-VERIFICATION")
    print("=" * 105)
    print("Mandate: 'Interrogate reality. Cross-correlate disparate sources. Surface conflicting claims.'\n")

    operator = DueDiligenceOperator(output_ledger="due_diligence_investigations.jsonl")

    company = "DevFlow AI (Series A Stealth)"
    claim = "Proprietary distributed Rust neural engine processing 10,000 code reviews/sec on edge hardware."

    evidence_points = [
        {
            "type": "git_commit_history",
            "url": "https://github.com/devflow-ai/core-engine",
            "fact": "14 public/semi-public repositories contain pure Python FastAPI wrappers calling OpenAI/Anthropic APIs; zero native Rust/C++/CUDA compilation artifacts found.",
            "is_conflicting": True,
            "weight": 0.95
        },
        {
            "type": "job_postings",
            "url": "https://boards.greenhouse.io/devflowai/jobs",
            "fact": "Past 60-day hiring pipeline includes 4 Prompt Engineers and 2 React developers; 0 systems, compiler, or CUDA engineering headcount.",
            "is_conflicting": True,
            "weight": 0.90
        },
        {
            "type": "network_telemetry",
            "url": "https://api.devflow.ai/v1/health-telemetry",
            "fact": "Median review processing latency is 1,840ms with TLS handshakes terminating at standard US-East AWS endpoints, inconsistent with sub-5ms edge engine claims.",
            "is_conflicting": True,
            "weight": 0.95
        },
        {
            "type": "pricing_changelog",
            "url": "https://devflow.ai/pricing/history",
            "fact": "Changed tier naming from 'Proprietary Neural Engine' to 'Multi-Model Cloud Proxy' on day 45.",
            "is_conflicting": False,
            "weight": 0.85
        }
    ]

    material_change = "Silently pivoted backend architecture from proprietary engine narrative to cloud LLM proxy wrapper while increasing enterprise pricing 2.5x."

    record = operator.interrogate_company(
        company_name=company,
        claim=claim,
        evidence_stream=evidence_points,
        material_change_summary=material_change
    )

    print(f">>> [TARGET COMPANY]: {record.target_company}")
    print(f">>> [PUBLIC CLAIM]  : \"{record.public_narrative_claim}\"")
    print(f">>> [REALITY VERDICT]: {record.reality_ground_truth_verdict} (Analyst Confidence: {record.analyst_confidence_score*100:.0f}%)")
    print(f">>> [90-DAY CHANGE] : {record.material_90_day_change}")
    print("-" * 105)

    print(">>> [CROSS-CORROBORATED EVIDENCE GRAPH]:")
    print(f"  * Conflicting Primary Evidence ({len(record.conflicting_evidence)} sources):")
    for c in record.conflicting_evidence:
        print(f"    - [{c.source_type.upper()}]: {c.observed_fact}")
        print(f"      Source: {c.source_url}")

    print(f"\n  * Supporting / Contextual Evidence ({len(record.supporting_evidence)} sources):")
    for s in record.supporting_evidence:
        print(f"    - [{s.source_type.upper()}]: {s.observed_fact}")

    print("\n" + "=" * 105)
    print(f"IMMUTABLE AUDIT HASH: {record.cryptographic_evidence_hash}")
    print(f"EVIDENCE LOGGED TO  : {operator.output_ledger}")
    print("=" * 105)


if __name__ == "__main__":
    run_investigation()
