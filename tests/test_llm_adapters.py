import pytest
from bartholomew_eval.agent_protocol import (
    CryptographicIdentityCredential,
    VendorNeutralProtocolGateway,
    StandaloneIndependentVerifier
)
from bartholomew_eval.llm_adapters import (
    UniversalLLMAdapter,
    LangChainBTPMiddleware,
    CrewAIBTPHook
)


@pytest.fixture
def sample_credential():
    return CryptographicIdentityCredential(
        agent_did="did:bth:multi_llm_agent_01",
        issuer_did="did:bth:root_llm_org",
        issuer_pub_key="pubkey_root_llm",
        possessed_capabilities=["compute.execute", "data.read"],
        constraint_manifest=["max_cost_200"]
    )


@pytest.fixture
def verifier():
    return StandaloneIndependentVerifier(
        pinned_root_pub_keys={"did:bth:root_llm_org": "pubkey_root_llm"}
    )


def test_openai_tool_call_adapter(sample_credential, verifier):
    openai_payload = {
        "id": "call_openai_9900",
        "type": "function",
        "function": {
            "name": "compute.execute",
            "arguments": '{"cost": 50.0, "duration": "1h"}'
        }
    }
    req = UniversalLLMAdapter.parse_openai_function_call(
        openai_tool_call=openai_payload,
        credential=sample_credential,
        target_system="Compute_Node_OpenAI"
    )
    gateway = VendorNeutralProtocolGateway()
    res = gateway.verify_request(req)

    assert res["decision"] == "ALLOW"
    assert res["target_system"] == "Compute_Node_OpenAI"
    artifact = res["evidence_artifact"]
    valid, _ = verifier.verify_evidence_artifact_independently(artifact)
    assert valid is True


def test_anthropic_tool_use_adapter(sample_credential, verifier):
    anthropic_payload = {
        "type": "tool_use",
        "id": "toolu_claude_8877",
        "name": "compute.execute",
        "input": {"cost": 75.0, "duration": "2h"}
    }
    req = UniversalLLMAdapter.parse_anthropic_tool_use(
        anthropic_block=anthropic_payload,
        credential=sample_credential,
        target_system="Compute_Node_Claude"
    )
    gateway = VendorNeutralProtocolGateway()
    res = gateway.verify_request(req)

    assert res["decision"] == "ALLOW"
    assert res["target_system"] == "Compute_Node_Claude"
    valid, _ = verifier.verify_evidence_artifact_independently(res["evidence_artifact"])
    assert valid is True


def test_gemini_function_call_adapter(sample_credential, verifier):
    gemini_payload = {
        "name": "compute.execute",
        "args": {"cost": 40.0}
    }
    req = UniversalLLMAdapter.parse_gemini_function_call(
        gemini_function_call=gemini_payload,
        credential=sample_credential,
        target_system="Compute_Node_Gemini"
    )
    gateway = VendorNeutralProtocolGateway()
    res = gateway.verify_request(req)

    assert res["decision"] == "ALLOW"
    valid, _ = verifier.verify_evidence_artifact_independently(res["evidence_artifact"])
    assert valid is True


def test_deepseek_tool_call_adapter(sample_credential, verifier):
    deepseek_payload = {
        "id": "call_ds_7711",
        "function": {
            "name": "compute.execute",
            "arguments": '{"cost": 30.0}'
        }
    }
    req = UniversalLLMAdapter.parse_deepseek_tool_call(
        deepseek_tool_call=deepseek_payload,
        credential=sample_credential,
        target_system="Compute_Node_DeepSeek"
    )
    gateway = VendorNeutralProtocolGateway()
    res = gateway.verify_request(req)

    assert res["decision"] == "ALLOW"
    valid, _ = verifier.verify_evidence_artifact_independently(res["evidence_artifact"])
    assert valid is True


def test_llama_ollama_tool_call_adapter(sample_credential, verifier):
    llama_payload = {
        "function": {
            "name": "compute.execute",
            "arguments": {"cost": 20.0}
        }
    }
    req = UniversalLLMAdapter.parse_llama_ollama_tool_call(
        ollama_tool_call=llama_payload,
        credential=sample_credential,
        target_system="Compute_Node_LLaMA"
    )
    gateway = VendorNeutralProtocolGateway()
    res = gateway.verify_request(req)

    assert res["decision"] == "ALLOW"
    valid, _ = verifier.verify_evidence_artifact_independently(res["evidence_artifact"])
    assert valid is True


def test_langchain_middleware(sample_credential, verifier):
    gateway = VendorNeutralProtocolGateway()
    middleware = LangChainBTPMiddleware(gateway)

    res = middleware.verify_tool_execution(
        tool_name="compute.execute",
        tool_input={"cost": 10.0},
        credential=sample_credential,
        target_system="LangChain_Agent_Node"
    )
    assert res["decision"] == "ALLOW"
    valid, _ = verifier.verify_evidence_artifact_independently(res["evidence_artifact"])
    assert valid is True


def test_crewai_hook(sample_credential, verifier):
    gateway = VendorNeutralProtocolGateway()
    hook = CrewAIBTPHook(gateway)

    res = hook.verify_crew_action(
        task_capability="compute.execute",
        task_payload={"cost": 15.0},
        credential=sample_credential,
        target_system="CrewAI_Task_Node"
    )
    assert res["decision"] == "ALLOW"
    valid, _ = verifier.verify_evidence_artifact_independently(res["evidence_artifact"])
    assert valid is True
