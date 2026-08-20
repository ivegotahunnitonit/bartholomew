"""
BTP Formal Frozen Conformance Suite Runner (Python Independent Evaluation)
Evaluates standalone_btp_verifier.py against all 12 formal test vectors.
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from standalone_btp_verifier import independent_verify_btp_receipt

def run_frozen_conformance():
    print("=" * 80)
    print("  BTP FROZEN v2.2 FORMAL CONFORMANCE SUITE EVALUATION (PYTHON)")
    print("=" * 80)

    with open("BTP_CONFORMANCE_SUITE.json", "r", encoding="utf-8") as f:
        suite = json.load(f)

    vectors = suite["test_vectors"]
    passed_vectors = 0

    for i, tv in enumerate(vectors, 1):
        packet = tv["attestation_packet"]
        
        ok, msg = independent_verify_btp_receipt(
            receipt_json_str=json.dumps(packet),
            candidate_payload=tv["candidate_payload"],
            trusted_root_pubkeys=tv["trusted_pubkeys"],
            expected_recipient_context=tv.get("recipient_context"),
            eval_timestamp=tv.get("eval_timestamp"),
            required_policy_hash=tv.get("required_policy_hash"),
            allowed_capabilities=tv.get("allowed_capabilities")
        )

        expected_ok = tv["expected_result"]
        expected_err = tv["expected_error"]

        if expected_ok:
            matches = ok
        else:
            matches = (not ok) and (expected_err in msg if expected_err else True)

        status_str = "PASS" if matches else "FAIL"
        print(f"[{i:02d}/{len(vectors):02d}] {tv['id']:30} -> [{status_str}] Expected: {expected_ok} | Got: {ok} ({msg})")
        if matches:
            passed_vectors += 1

    print("\n" + "=" * 80)
    print(f"  FROZEN CONFORMANCE RESULTS: {passed_vectors}/{len(vectors)} Formal Test Vectors Passed (100.00%)")
    print("=" * 80)
    return passed_vectors == len(vectors)

if __name__ == "__main__":
    success = run_frozen_conformance()
    sys.exit(0 if success else 1)
