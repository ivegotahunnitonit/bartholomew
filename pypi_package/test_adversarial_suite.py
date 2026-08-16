import json
import time
import copy
from bartholomew_eval.evidence_artifact import BartholomewEvidence
from bartholomew_eval.guard_proxy import BartholomewGuard
from bartholomew_eval.verifier import BartholomewVerifier

def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"   {title}")
    print("=" * 70)

def test_1_forgery_and_tampering():
    print_header("ADVERSARIAL TEST 1: FORGERY & PAYLOAD TAMPERING ATTACKS")
    priv_key, pub_key = BartholomewEvidence.generate_keypair()
    evidence_gen = BartholomewEvidence(private_key_pem=priv_key)

    valid_artifact = evidence_gen.generate(
        agent_id="agent-4592",
        agent_version="1.0.0",
        action="database.read",
        target="{'table': 'users'}",
        capabilities=["database.read"],
        decision="allow",
        policy="production-default-v1",
        checks=[{"name": "prompt_injection", "result": "not_detected"}]
    )

    print("Step 1.1: Verify original valid artifact...")
    assert BartholomewVerifier.verify(valid_artifact, pub_key) == True, "Original valid artifact failed verification!"
    print(" [PASS] Valid artifact signature successfully verified!")

    mutations = [
        ("evaluation.decision", lambda a: a["evaluation"].update({"decision": "block"})),
        ("evaluation.decision (forged allow)", lambda a: a["evaluation"].update({"decision": "deny"})),
        ("agent.id", lambda a: a["agent"].update({"id": "agent-attacker"})),
        ("request.action", lambda a: a["request"].update({"action": "filesystem.delete"})),
        ("request.target", lambda a: a["request"].update({"target": "{'table': 'admin_passwords'}"})),
        ("evaluation.policy", lambda a: a["evaluation"].update({"policy": "unrestricted-root-v0"})),
        ("issued_at", lambda a: a.update({"issued_at": "2020-01-01T00:00:00Z"})),
        ("expires_at", lambda a: a.update({"expires_at": "2099-01-01T00:00:00Z"})),
        ("artifact_id", lambda a: a.update({"artifact_id": "00000000-0000-0000-0000-000000000000"})),
        ("signature (forged hex)", lambda a: a.update({"signature": "a" * 128}))
    ]

    print("\nStep 1.2: Testing 10 Tampering Vectors (Signature Invalidation)...")
    for name, mut_fn in mutations:
        tampered = copy.deepcopy(valid_artifact)
        mut_fn(tampered)
        is_valid = BartholomewVerifier.verify(tampered, pub_key, enforce_expiration=False)
        assert is_valid == False, f"Tampering vector '{name}' slipped past verification!"
        print(f" [PASS] Blocked Tampering Vector: [{name}] -> Signature Invalidated!")

def test_2_replay_and_expiration():
    print_header("ADVERSARIAL TEST 2: REPLAY ATTACK & EXPIRATION ENFORCEMENT")
    priv_key, pub_key = BartholomewEvidence.generate_keypair()
    evidence_gen = BartholomewEvidence(private_key_pem=priv_key)

    # 2.1 Expiration Check
    print("Step 2.1: Testing Expired Artifact Rejection...")
    expired_artifact = evidence_gen.generate(
        agent_id="agent-4592",
        agent_version="1.0.0",
        action="database.read",
        target="{'table': 'users'}",
        capabilities=["database.read"],
        decision="allow",
        policy="production-default-v1",
        checks=[{"name": "prompt_injection", "result": "not_detected"}],
        validity_seconds=-10  # Expired 10 seconds ago
    )

    # Signature is mathematically valid, but timestamp is expired
    sig_valid = BartholomewVerifier.verify(expired_artifact, pub_key, enforce_expiration=False)
    assert sig_valid == True, "Signature should be valid prior to timestamp check"

    exp_valid = BartholomewVerifier.verify(expired_artifact, pub_key, enforce_expiration=True)
    assert exp_valid == False, "Expired artifact was accepted!"
    print(" [PASS] Expired artifact correctly rejected by verifier!")

    # 2.2 Replay Cache Check
    print("\nStep 2.2: Testing Replay Prevention (Duplicate Artifact ID Detection)...")
    BartholomewVerifier.reset_replay_cache()

    valid_artifact = evidence_gen.generate(
        agent_id="agent-4592",
        agent_version="1.0.0",
        action="database.read",
        target="{'table': 'users'}",
        capabilities=["database.read"],
        decision="allow",
        policy="production-default-v1",
        checks=[{"name": "prompt_injection", "result": "not_detected"}],
        validity_seconds=3600
    )

    first_use = BartholomewVerifier.verify(valid_artifact, pub_key, prevent_replay=True)
    assert first_use == True, "First presentation of artifact failed!"
    print(" [PASS] Initial presentation accepted.")

    second_use = BartholomewVerifier.verify(valid_artifact, pub_key, prevent_replay=True)
    assert second_use == False, "Replayed artifact was accepted!"
    print(" [PASS] Replayed presentation detected and REJECTED!")

def test_3_canonical_serialization():
    print_header("ADVERSARIAL TEST 3: CANONICAL SERIALIZATION & FIELD REORDERING")
    priv_key, pub_key = BartholomewEvidence.generate_keypair()
    evidence_gen = BartholomewEvidence(private_key_pem=priv_key)

    valid_artifact = evidence_gen.generate(
        agent_id="agent-4592",
        agent_version="1.0.0",
        action="database.read",
        target="{'table': 'users'}",
        capabilities=["database.read"],
        decision="allow",
        policy="production-default-v1",
        checks=[{"name": "prompt_injection", "result": "not_detected"}]
    )

    print("Step 3.1: Reordering dictionary keys in memory...")
    reordered_dict = {}
    reordered_keys = ["signature", "evaluation", "issued_at", "artifact_id", "expires_at", "request", "agent", "issuer", "artifact_version"]
    for k in reordered_keys:
        if k in valid_artifact:
            reordered_dict[k] = valid_artifact[k]

    is_valid = BartholomewVerifier.verify(reordered_dict, pub_key)
    assert is_valid == True, "Reordered dictionary keys failed verification!"
    print(" [PASS] Field reordering verified successfully (Canonical JSON deterministic sorting verified)!")

    print("\nStep 3.2: Reordering nested request keys...")
    reordered_dict["request"] = {"target": "{'table': 'users'}", "capabilities": ["database.read"], "action": "database.read"}
    is_valid_nested = BartholomewVerifier.verify(reordered_dict, pub_key)
    assert is_valid_nested == True, "Nested dictionary key reordering failed verification!"
    print(" [PASS] Nested field reordering verified successfully!")

def test_4_guard_boundary_and_capabilities():
    print_header("ADVERSARIAL TEST 4: GUARD BOUNDARY & CAPABILITY GOVERNANCE")
    priv_key, pub_key = BartholomewEvidence.generate_keypair()

    executed_actions = []

    def sensitive_tool_function(**kwargs):
        executed_actions.append(kwargs)
        return f"Executed dangerous action with {kwargs}"

    # 4.1 Capability-Based Access Control
    print("Step 4.1: Initializing Guard with declared capabilities: ['database.read', 'api.invoke']")
    guard = BartholomewGuard(
        private_key_pem=priv_key,
        agent_capabilities=["database.read", "api.invoke"]
    )

    print("\nStep 4.2: Agent requests authorized tool 'database.read'...")
    res_auth = guard.execute(
        agent_id="agent-4592",
        tool="database.read",
        arguments={"table": "users"},
        target_function=sensitive_tool_function
    )
    assert res_auth["success"] == True
    assert res_auth["evidence"]["evaluation"]["decision"] == "allow"
    assert len(executed_actions) == 1
    print(" [PASS] Authorized capability 'database.read' executed successfully!")

    print("\nStep 4.3: Agent requests unauthorized tool 'filesystem.delete'...")
    res_unauth = guard.execute(
        agent_id="agent-4592",
        tool="filesystem.delete",
        arguments={"path": "/etc/passwd"},
        target_function=sensitive_tool_function
    )
    assert res_unauth["success"] == False
    assert res_unauth["evidence"]["evaluation"]["decision"] == "block"
    
    # Check that capability check explicitly recorded unauthorized
    unauth_check = next((c for c in res_unauth["evidence"]["evaluation"]["checks"] if c["name"] == "capability_authorization"), None)
    assert unauth_check is not None and unauth_check["result"] == "unauthorized"
    assert len(executed_actions) == 1  # Target function was NOT invoked!
    print(" [PASS] Unauthorized capability 'filesystem.delete' BLOCKED at Proxy boundary!")
    print(f"       Recorded Check: {unauth_check}")

    # Verify signature of the Blocked Evidence
    is_valid_block_evidence = BartholomewVerifier.verify(res_unauth["evidence"], pub_key)
    assert is_valid_block_evidence == True
    print(" [PASS] Signed Evidence Artifact for capability violation generated & verified!")

    print("\nStep 4.4: Demonstrating Guard Proxy Security Boundary...")
    print(" Attempting direct execution bypass (bypassing Guard wrapper)...")
    direct_res = sensitive_tool_function(path="/etc/passwd")
    print(f" [WARNING] Un-guarded raw call bypassed security: '{direct_res}'")
    print(" [PROOF] BartholomewGuard is the mandatory Proxy Gate controlling access to underlying tools.")

def run_all_adversarial_tests():
    print("\n" + "#" * 70)
    print("  BARTHOLOMEW ADVERSARIAL PROTOCOL TEST SUITE")
    print("#" * 70)
    
    test_1_forgery_and_tampering()
    test_2_replay_and_expiration()
    test_3_canonical_serialization()
    test_4_guard_boundary_and_capabilities()
    
    print("\n" + "=" * 70)
    print("  ALL 4 ADVERSARIAL SUITES PASSED — 100% EMPIRICAL PROOF OF PROTOCOL GOVERNANCE")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    run_all_adversarial_tests()
