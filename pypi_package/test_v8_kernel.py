from bartholomew_eval import BartholomewEnvironment, EpistemicExperienceStore, BartholomewVerifier

def test_v8_kernel():
    print("=== TESTING BARTHOLOMEW v8.0 SOVEREIGN EPISTEMIC KERNEL ===")
    
    # 1. Init Environment
    env = BartholomewEnvironment()
    
    # 2. Handshake
    hs = env.handshake(
        agent_id="agent-4592",
        agent_version="8.0.0",
        declared_capabilities=["database.read", "api.invoke"]
    )
    print("\n1. Handshake Result:")
    print(f"   Session ID: {hs['session_id']}")
    
    # 3. Boundary Discovery
    boundaries = env.discover_boundaries("agent-4592")
    print("\n2. Boundary Discovery ('What am I allowed to touch?'):")
    print(f"   Accessible Resources  : {list(boundaries['accessible_resources'].keys())}")
    print(f"   Unauthorized Resources: {list(boundaries['unauthorized_resources'].keys())}")
    
    # 4. Action Execution under Guard
    def read_db(**kwargs):
        return f"Fetched records for {kwargs.get('query')}"
        
    action_res = env.execute_action(
        agent_id="agent-4592",
        tool="database.read",
        arguments={"query": "SELECT * FROM users;"},
        target_function=read_db
    )
    print("\n3. Guard Proxy Action Execution:")
    print(f"   Success : {action_res['success']}")
    print(f"   Result  : {action_res['result']}")
    print(f"   Decision: {action_res['evidence']['evaluation']['decision']}")
    
    # 5. Experience Store (DERG)
    exp = EpistemicExperienceStore()
    rec = exp.record_experience(
        agent_id="agent-4592",
        claim="Database deadlock occurs when pool size exceeds 32",
        outcome="FAILED_ATTEMPT",
        evidence_artifact_id=action_res['evidence']['artifact_id'],
        signature=action_res['evidence']['signature'],
        tags=["database", "deadlock"]
    )
    print("\n4. Epistemic Experience Store (DERG Assertion):")
    print(f"   Recorded Assertion ID: {rec['assertion_id']}")
    print(f"   Claim: {rec['claim']}")
    
    # 6. Master Panic Switch (Key Zeroization)
    print("\n5. Triggering Master Panic Switch (Key Zeroization)...")
    panic_res = env.zeroize_keys()
    print(f"   Status: {panic_res['status']}")
    
    blocked_action = env.execute_action(
        agent_id="agent-4592",
        tool="database.read",
        arguments={"query": "SELECT * FROM users;"},
        target_function=read_db
    )
    print(f"   Post-Panic Execution Decision: {blocked_action['evidence']['evaluation']['decision']}")
    print(f"   Error: {blocked_action['error']}")
    assert blocked_action["success"] == False
    assert blocked_action["evidence"]["evaluation"]["decision"] == "block"
    print("\n[SUCCESS] BARTHOLOMEW v8.0 KERNEL TESTED & VERIFIED PASSING 100%!")

if __name__ == "__main__":
    test_v8_kernel()
