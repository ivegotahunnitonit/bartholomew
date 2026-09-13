import json
from bartholomew_eval.evidence_artifact import BartholomewEvidence
from bartholomew_eval.guard_proxy import BartholomewGuard
from bartholomew_eval.verifier import BartholomewVerifier

def dummy_database_read(table):
    return f"Read from {table}"

def test_evidence():
    print("Generating Ed25519 Keypair...")
    priv_pem, pub_pem = BartholomewEvidence.generate_keypair()
    
    print("Testing Guard Execution...")
    guard = BartholomewGuard(private_key_pem=priv_pem)
    
    # Safe execution
    result = guard.execute(
        agent_id="agent-4592",
        tool="database.read",
        arguments={"table": "users"},
        target_function=dummy_database_read
    )
    
    assert result["success"] == True
    assert result["result"] == "Read from users"
    
    evidence = result["evidence"]
    print("Generated Evidence:")
    print(json.dumps(evidence, indent=2))
    
    assert evidence["evaluation"]["decision"] == "allow"
    
    print("Verifying Evidence...")
    is_valid = BartholomewVerifier.verify(evidence, pub_pem)
    assert is_valid == True, "Signature verification failed!"
    
    # Tamper with the evidence
    evidence["evaluation"]["decision"] = "block"
    is_valid_tampered = BartholomewVerifier.verify(evidence, pub_pem)
    assert is_valid_tampered == False, "Tampered evidence should have failed!"
    
    print("All tests passed successfully!")

if __name__ == "__main__":
    test_evidence()
