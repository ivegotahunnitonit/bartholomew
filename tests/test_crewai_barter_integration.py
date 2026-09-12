"""
BTP v5.4.6 Framework Adapters Bilateral Barter Integration Tests
================================================================
Verifies automated Attested Work Unit (AWU) minting on safe tool execution
and bilateral cross-swarm task delegation settlement between CrewAI and LangGraph.
"""

import pytest
from src.agent_passport import SovereignAgentPassport
from src.economy.barter_client import BTPBarterClient
from framework_adapters.crewai.crewai_btp_task_guard import (
    btp_crewai_tool,
    CrewAIBTPTaskGuard,
    BTPViolationError as CrewAIViolationError,
)
from framework_adapters.langgraph.langgraph_btp_guard import (
    btp_langchain_tool,
    LangGraphBTPGuard,
    BTPViolationError as LangGraphViolationError,
)


@pytest.fixture
def barter_client():
    return BTPBarterClient(default_gateway="inprocess")


def test_crewai_tool_awu_minting(barter_client):
    agent_id = "agent-crewai-miner-01"
    initial_bal = barter_client.get_balance(agent_id).get("balance_awu", 0.0)

    @btp_crewai_tool(
        spend_cap=50.0,
        mint_awu=2.5,
        barter_agent_id=agent_id,
        barter_gateway="inprocess",
    )
    def clean_compute_task(query: str) -> str:
        return f"Computed: {query}"

    res = clean_compute_task("SELECT count(*) FROM telemetry")
    assert res == "Computed: SELECT count(*) FROM telemetry"

    after_bal = barter_client.get_balance(agent_id).get("balance_awu", 0.0)
    assert after_bal == initial_bal + 2.5


def test_crewai_tool_blocked_no_awu_mint(barter_client):
    agent_id = "agent-crewai-adversary"
    initial_bal = barter_client.get_balance(agent_id).get("balance_awu", 0.0)

    @btp_crewai_tool(
        spend_cap=50.0,
        mint_awu=5.0,
        barter_agent_id=agent_id,
        barter_gateway="inprocess",
    )
    def dangerous_tool(cmd: str) -> str:
        return f"Run: {cmd}"

    with pytest.raises(CrewAIViolationError):
        dangerous_tool("rm -rf / --no-preserve-root")

    after_bal = barter_client.get_balance(agent_id).get("balance_awu", 0.0)
    assert after_bal == initial_bal


def test_crewai_task_guard_cross_swarm_delegation(barter_client):
    sender_id = "crewai-coordinator-swarm"
    specialist_id = "langgraph-specialist-node"

    # Seed sender balance
    barter_client.pulse(agent_id=sender_id, work_units=10.0, task_type="initial_stake")
    sender_start = barter_client.get_balance(sender_id).get("balance_awu", 0.0)
    spec_start = barter_client.get_balance(specialist_id).get("balance_awu", 0.0)

    guard = CrewAIBTPTaskGuard(
        recipient_id=sender_id,
        enforce_strict=False,
        barter_gateway="inprocess",
    )

    def specialist_compute(dataset: str) -> str:
        return f"Specialist analyzed {dataset}"

    delegation = guard.delegate_task(
        task_description="Analyze high-throughput dataset",
        task_fn=specialist_compute,
        specialist_id=specialist_id,
        awu_units=3.0,
        task_args=["dataset_v2.parquet"],
    )

    assert delegation["status"] == "DELEGATION_COMPLETED"
    assert delegation["awu_transferred"] == 3.0
    assert delegation["result"] == "Specialist analyzed dataset_v2.parquet"

    # Verify Ed25519 signed settlement receipt
    receipt = delegation["barter_settlement"]["signed_receipt"]
    assert receipt["signer_pubkey"] is not None
    assert receipt["payload"]["units"] == 3.0
    assert receipt["payload"]["sender"] == sender_id
    assert receipt["payload"]["recipient"] == specialist_id

    # Verify balances updated
    assert barter_client.get_balance(sender_id).get("balance_awu") == sender_start - 3.0
    assert barter_client.get_balance(specialist_id).get("balance_awu") == spec_start + 3.0


def test_langgraph_tool_awu_minting(barter_client):
    agent_id = "agent-langgraph-worker-02"
    initial_bal = barter_client.get_balance(agent_id).get("balance_awu", 0.0)

    @btp_langchain_tool(
        spend_cap=50.0,
        mint_awu=1.75,
        barter_agent_id=agent_id,
        barter_gateway="inprocess",
    )
    def clean_search_node(term: str) -> str:
        return f"Found results for {term}"

    res = clean_search_node("quantum circuit optimization")
    assert "Found results" in res

    after_bal = barter_client.get_balance(agent_id).get("balance_awu", 0.0)
    assert after_bal == initial_bal + 1.75


def test_langgraph_guard_cross_swarm_delegation(barter_client):
    sender_id = "langgraph-lead-node"
    specialist_id = "crewai-inference-swarm"

    barter_client.pulse(agent_id=sender_id, work_units=8.0, task_type="initial_stake")
    sender_start = barter_client.get_balance(sender_id).get("balance_awu", 0.0)
    spec_start = barter_client.get_balance(specialist_id).get("balance_awu", 0.0)

    guard = LangGraphBTPGuard(
        agent_id=sender_id,
        enforce_strict=False,
        barter_gateway="inprocess",
    )

    def inference_worker(prompt: str) -> str:
        return f"Inferred response for: {prompt}"

    delegation = guard.delegate_task(
        task_description="Execute dense transformer inference",
        task_fn=inference_worker,
        specialist_id=specialist_id,
        awu_units=2.25,
        task_args=["Evaluate security boundaries"],
    )

    assert delegation["status"] == "DELEGATION_COMPLETED"
    assert delegation["awu_transferred"] == 2.25
    assert "Inferred response for" in delegation["result"]

    # Verify Ed25519 signed settlement receipt
    receipt = delegation["barter_settlement"]["signed_receipt"]
    assert receipt["payload"]["units"] == 2.25
    assert receipt["payload"]["sender"] == sender_id
    assert receipt["payload"]["recipient"] == specialist_id

    # Verify balances updated
    assert barter_client.get_balance(sender_id).get("balance_awu") == sender_start - 2.25
    assert barter_client.get_balance(specialist_id).get("balance_awu") == spec_start + 2.25
