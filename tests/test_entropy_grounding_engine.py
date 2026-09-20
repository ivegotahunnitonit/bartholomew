import os
import sys
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.entropy_grounding_engine import (
    calculate_shannon_entropy,
    EpistemicProvenanceGrounder,
    EntropyGovernor
)


def test_calculate_shannon_entropy():
    # Constant repetition should have 0 or near 0 entropy
    zero_entropy = calculate_shannon_entropy("aaaaaaaaaaaaaaaa")
    assert zero_entropy == 0.0

    # Structured English/JSON text typically has entropy between 2.5 and 4.5
    normal_text = calculate_shannon_entropy('{"action": "GET_USERS", "limit": 50}')
    assert 2.0 <= normal_text <= 4.8

    # Random character soup has higher entropy
    random_str = calculate_shannon_entropy("9x8!a@#$109z&%*kLqWvNp")
    assert random_str > 4.0


def test_epistemic_provenance_grounding():
    grounder = EpistemicProvenanceGrounder()

    # Step 1: Agent performs a legitimate read operation
    read_receipt = {
        "action": "READ_CUSTOMERS",
        "payload": {
            "records": [
                {"id": "cust_101", "name": "Alice Corp"},
                {"id": "cust_102", "name": "Bob LLC"}
            ]
        }
    }
    grounder.ingest_grounded_context(read_receipt)

    # Step 2: Agent attempts a grounded mutation on cust_101 -> MUST PASS
    grounded_mutation = {
        "action": "UPDATE_CUSTOMER",
        "payload": {"target_id": "cust_101", "status": "VERIFIED"}
    }
    is_valid, err = grounder.verify_grounding(grounded_mutation)
    assert is_valid is True
    assert err is None

    # Step 3: Agent attempts an ungrounded, hallucinated mutation on cust_999 -> MUST BE BLOCKED
    hallucinated_mutation = {
        "action": "UPDATE_CUSTOMER",
        "payload": {"target_id": "cust_999", "status": "DELETED"}
    }
    is_valid, err = grounder.verify_grounding(hallucinated_mutation)
    assert is_valid is False
    assert "Epistemic Grounding Invariant Breach" in err


def test_entropy_governor():
    governor = EntropyGovernor(max_entropy_bits=5.5)

    clean_payload = {"action": "STATUS_CHECK", "agent": "worker-1"}
    is_ok, entropy, err = governor.evaluate_entropy(clean_payload)
    assert is_ok is True
    assert err is None

    # Unusually high entropy / obfuscated payload (uniform random distribution > 6.0 bits)
    noisy_payload = {
        "data": "".join([chr(i) for i in range(32, 127)] * 3)
    }
    strict_gov = EntropyGovernor(max_entropy_bits=4.0)
    is_ok, entropy, err = strict_gov.evaluate_entropy(noisy_payload)
    assert is_ok is False
    assert "Information Theory Invariant Breach" in err


if __name__ == "__main__":
    test_calculate_shannon_entropy()
    test_epistemic_provenance_grounding()
    test_entropy_governor()
    print("[OK] ALL INFORMATION THEORY & GROUNDING TESTS PASSED!")
