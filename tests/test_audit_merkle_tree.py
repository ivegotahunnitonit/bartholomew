import os
import sys
import pytest

# Ensure parent directory in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.audit_merkle_tree import AuditMerkleTree


def test_merkle_tree_root_and_inclusion_proof():
    receipts = [
        {"agent": "agent-1", "action": "READ", "verdict": "ALLOW", "nonce": "n1"},
        {"agent": "agent-2", "action": "WRITE", "verdict": "ALLOW", "nonce": "n2"},
        {"agent": "agent-3", "action": "DROP_TABLE", "verdict": "DENY", "nonce": "n3"},
        {"agent": "agent-4", "action": "PAYMENT", "verdict": "ALLOW", "nonce": "n4"},
    ]

    tree = AuditMerkleTree(receipts)
    root = tree.root_hash
    assert len(root) == 64 # SHA-256 hex string

    # Generate proof for receipt 2 (malicious dropped table)
    proof_obj = tree.get_inclusion_proof(2)
    assert proof_obj["root_hash"] == root
    assert len(proof_obj["proof"]) == 2 # 4 leaves -> depth 2

    # Verify proof matches
    is_valid = AuditMerkleTree.verify_inclusion_proof(receipts[2], proof_obj["proof"], root)
    assert is_valid is True

    # Tampered receipt must fail verification
    tampered = dict(receipts[2])
    tampered["verdict"] = "ALLOW"
    assert AuditMerkleTree.verify_inclusion_proof(tampered, proof_obj["proof"], root) is False


def test_merkle_tree_odd_leaves():
    receipts = [
        {"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}
    ]
    tree = AuditMerkleTree(receipts)
    root = tree.root_hash

    for i in range(len(receipts)):
        proof_obj = tree.get_inclusion_proof(i)
        assert AuditMerkleTree.verify_inclusion_proof(receipts[i], proof_obj["proof"], root) is True


if __name__ == "__main__":
    test_merkle_tree_root_and_inclusion_proof()
    test_merkle_tree_odd_leaves()
    print("[OK] ALL MERKLE AUDIT TREE TESTS PASSED!")
