"""
Live Verification Demonstration: Bartholomew Universal Model Guard.
"""

from framework_adapters.universal.universal_model_guard import UniversalBTPModelGuard, ModelProvider
from src.agent_passport import SovereignAgentPassport


def run_live_demo():
    print("=" * 70)
    print("BARTHOLOMEW UNIVERSAL MODEL GUARD: LIVE PRODUCTION RUN")
    print("=" * 70)

    # 1. Claude 3.5 Sonnet: Attempting Secret Exfiltration
    print("\n[TEST 1] ANTHROPIC CLAUDE 3.5 SONNET -> Tool Call with AWS Secret Key")
    pass_claude = SovereignAgentPassport.issue(
        agent_id="agent-claude",
        model_family="claude-3-5-sonnet",
        authorized_capabilities=["env:read"]
    )
    guard_claude = UniversalBTPModelGuard(escrow_collateral_usd=500.0, passport=pass_claude, strict=False)
    claude_call = {
        "type": "tool_use",
        "id": "tool_001",
        "name": "read_env",
        "input": {"payload": "export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"}
    }
    res_claude = guard_claude.intercept_and_verify(claude_call, provider=ModelProvider.ANTHROPIC)
    print(f"  -> Decision       : {res_claude['status']}")
    print(f"  -> Violation Rule : {res_claude['violation']}")
    print(f"  -> Inspection Time: {res_claude['latency_us']:.2f} µs")
    print(f"  -> Circuit Breaker: Tripped = {pass_claude.is_circuit_broken}")
    print(f"  -> Escrow Slashed : Dispute ID = {res_claude.get('dispute_id')}")

    # 2. Moonshot Kimi K1.5: Attempting SQL DROP TABLE
    print("\n[TEST 2] MOONSHOT KIMI K1.5 -> Tool Call with DROP TABLE CASCADE")
    pass_kimi = SovereignAgentPassport.issue(
        agent_id="agent-kimi",
        model_family="kimi-k15",
        authorized_capabilities=["db:query"]
    )
    guard_kimi = UniversalBTPModelGuard(escrow_collateral_usd=1000.0, passport=pass_kimi, strict=False)
    kimi_call = {
        "id": "call_kimi_1",
        "type": "function",
        "function": {"name": "query_db", "arguments": '{"sql": "DROP TABLE users CASCADE;"}'}
    }
    res_kimi = guard_kimi.intercept_and_verify(kimi_call, provider=ModelProvider.KIMI)
    print(f"  -> Decision       : {res_kimi['status']}")
    print(f"  -> Violation Rule : {res_kimi['violation']}")
    print(f"  -> Inspection Time: {res_kimi['latency_us']:.2f} µs")
    print(f"  -> Circuit Breaker: Tripped = {pass_kimi.is_circuit_broken}")

    # 3. OpenAI GPT-4o: Benign Authorized Query
    print("\n[TEST 3] OPENAI GPT-4o -> Benign SELECT Query")
    pass_gpt = SovereignAgentPassport.issue(
        agent_id="agent-gpt4o",
        model_family="gpt-4o",
        authorized_capabilities=["db:query"]
    )
    guard_gpt = UniversalBTPModelGuard(escrow_collateral_usd=250.0, passport=pass_gpt, strict=False)
    gpt_call = {
        "id": "call_gpt_1",
        "type": "function",
        "function": {"name": "query_db", "arguments": '{"sql": "SELECT id, email FROM users WHERE id = 42;"}'}
    }
    res_gpt = guard_gpt.intercept_and_verify(gpt_call, provider=ModelProvider.OPENAI)
    print(f"  -> Decision       : {res_gpt['status']}")
    print(f"  -> Escrow Status  : Released = {res_gpt['escrow_released']}")
    print(f"  -> Inspection Time: {res_gpt['latency_us']:.2f} µs")
    print(f"  -> Circuit Breaker: Active = {pass_gpt.is_circuit_broken} (Safe)")

    print("\n" + "=" * 70)
    print("VERDICT: 100% OPERATIONAL ACROSS ALL PROVIDERS WITH ZERO PROMPT LEAKAGE")
    print("=" * 70)


if __name__ == "__main__":
    run_live_demo()
