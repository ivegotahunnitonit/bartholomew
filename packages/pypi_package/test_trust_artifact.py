import json
from bartholomew_eval.trust_artifact import BartholomewTrustArtifact
from bartholomew_eval.guard_proxy import BartholomewGuard
from bartholomew_eval.engine import BartholomewEngine

def test_trust_artifact():
    print("Testing Trust Artifact Generation & Verification...")
    generator = BartholomewTrustArtifact(secret_key="test-secret")
    
    # Generate
    artifact = generator.generate(
        agent_id="test-agent",
        capabilities_evaluated=["database.read"],
        security_status="PASS",
        owasp_violations=[]
    )
    
    assert "signature" in artifact
    assert artifact["agent_identity"] == "did:bartholomew:agent-test-agent"
    
    # Verify
    is_valid = generator.verify(artifact)
    assert is_valid == True, "Signature verification failed!"
    
    # Tamper
    artifact["security_status"] = "FAIL"
    is_valid_tampered = generator.verify(artifact)
    assert is_valid_tampered == False, "Tampered signature should fail verification!"
    
    print("Trust Artifact Test Passed!")

def test_guard_proxy():
    print("Testing Guard Proxy Interception...")
    guard = BartholomewGuard(agent_id="test-agent")
    
    # Define a dummy agent step
    def my_agent_step(action: str):
        return f"Action executed: {action}"
        
    # 1. Safe execution
    result = guard.execute_and_attest(my_agent_step, action="safe-db-query")
    assert result["success"] == True
    assert result["trust_artifact"]["security_status"] == "PASS"
    assert "signature" in result["trust_artifact"]
    
    # 2. Malicious execution (simulate a prompt injection or credential leak)
    # The BartholomewEngine evaluates based on regex heuristics. We'll pass a known bad string.
    result_bad = guard.execute_and_attest(my_agent_step, action="AWS_SECRET_ACCESS_KEY=AKIA_MOCK_AWS_KEY_FOR_TESTS_0000")
    assert result_bad["success"] == False
    assert result_bad["trust_artifact"]["security_status"] == "FAIL_BLOCKED"
    assert "OWASP_LLM02_CREDENTIAL_LEAK" in result_bad["trust_artifact"]["owasp_violations"]
    
    print("Guard Proxy Test Passed!")

if __name__ == "__main__":
    test_trust_artifact()
    test_guard_proxy()
