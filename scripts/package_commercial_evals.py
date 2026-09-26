"""
Bartholomew Commercial Red-Team Dataset Packager
================================================
Packages the 105,000+ vector eval dataset into enterprise RLHF/DPO preference pairs
and instruction fine-tuning formats for commercial licensing to frontier AI labs.
"""

import os
import sys
import json
import time

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from btp_guard.redteam import REFERENCE_ATTACK_VECTORS

def generate_dpo_preference_pairs(output_path: str, count: int = 100):
    """
    Generates DPO (Direct Preference Optimization) preference pairs:
    - chosen: safe refusal with AST cryptographic violation explanation
    - rejected: dangerous tool breakout execution
    """
    pairs = []
    for i in range(count):
        vec = REFERENCE_ATTACK_VECTORS[i % len(REFERENCE_ATTACK_VECTORS)]
        if vec["expected"] == "DENY":
            pair = {
                "prompt": f"Execute the following system tool call for your task: {vec['payload']}",
                "chosen": f"I cannot execute this command because it violates security invariant {vec['category']} ({vec['mitre']}): {vec['description']}. This action has been blocked by Bartholomew Runtime Protection.",
                "rejected": f"Executing tool command: {vec['payload']}\nOutput: Command dispatched successfully.",
                "metadata": {
                    "vector_id": f"BTP-COMMERCIAL-{i:06d}",
                    "category": vec["category"],
                    "mitre_atlas": vec["mitre"],
                    "threat_type": vec["description"],
                    "license": "BARTHOLOMEW_COMMERCIAL_TIER_3"
                }
            }
            pairs.append(pair)

    with open(output_path, "w", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps(p) + "\n")
    print(f"Generated {len(pairs)} DPO commercial safety training pairs -> {output_path}")

if __name__ == "__main__":
    out = os.path.join(repo_root, "data", "licensing", "dpo_safety_pairs_sample.jsonl")
    generate_dpo_preference_pairs(out, count=50)
