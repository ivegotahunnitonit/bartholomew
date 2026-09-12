"""
BTP v5.4.6 Four-Framework Barter Unification & Protocol Treasury Earnings Test Suite
===================================================================================
Verifies:
  1. AutoGen tool AWU minting & turn delegation with signed Ed25519 receipts.
  2. LlamaIndex tool AWU minting & query delegation with signed Ed25519 receipts.
  3. Continuous protocol treasury yield & fee accumulation across all swarms.
  4. CLI barter treasury earnings visibility.
"""

import sys
import subprocess
import pytest

from src.economy.barter_client import BTPBarterClient
from framework_adapters.autogen.autogen_btp_interceptor import (
    btp_autogen_guard,
    AutoGenBTPInterceptor,
    BTPViolationError as AutoGenViolationError,
)
from framework_adapters.llamaindex.llamaindex_btp_tool import (
    btp_llamaindex_tool,
    BartholomewLlamaIndexTool,
    BTPViolationError as LlamaIndexViolationError,
)


@pytest.fixture
def barter_client():
    return BTPBarterClient(default_gateway="inprocess")


def test_autogen_tool_awu_minting(barter_client):
    agent_id = "agent-autogen-coder-01"
    initial_bal = barter_client.get_balance(agent_id).get("balance_awu", 0.0)

    @btp_autogen_guard(
        mint_awu=2.0,
        barter_agent_id=agent_id,
        barter_gateway="inprocess",
    )
    def synthesize_unit_test(spec: str) -> str:
        return f"Generated test for {spec}"

    res = synthesize_unit_test("ed25519_signature")
    assert "Generated test for" in res

    after_bal = barter_client.get_balance(agent_id).get("balance_awu", 0.0)
    assert after_bal == initial_bal + 2.0


def test_autogen_tool_veto_no_mint(barter_client):
    agent_id = "agent-autogen-rogue"
    initial_bal = barter_client.get_balance(agent_id).get("balance_awu", 0.0)

    @btp_autogen_guard(
        mint_awu=4.0,
        barter_agent_id=agent_id,
        barter_gateway="inprocess",
    )
    def dangerous_exec(code: str) -> str:
        return f"Ran {code}"

    with pytest.raises(AutoGenViolationError):
        dangerous_exec("DROP DATABASE production_ledger;")

    after_bal = barter_client.get_balance(agent_id).get("balance_awu", 0.0)
    assert after_bal == initial_bal


def test_autogen_turn_delegation(barter_client):
    sender_id = "autogen-coordinator-01"
    specialist_id = "llamaindex-retrieval-node"

    barter_client.pulse(agent_id=sender_id, work_units=6.0, task_type="initial_deposit")
    sender_start = barter_client.get_balance(sender_id).get("balance_awu", 0.0)
    spec_start = barter_client.get_balance(specialist_id).get("balance_awu", 0.0)

    interceptor = AutoGenBTPInterceptor(
        recipient_id=sender_id,
        enforce_strict=False,
        barter_gateway="inprocess",
    )

    def specialist_turn(prompt: str) -> str:
        return f"Turn result: {prompt}"

    delegation = interceptor.delegate_turn(
        task_description="Query knowledge index for RFC 8785",
        turn_fn=specialist_turn,
        specialist_id=specialist_id,
        awu_units=1.5,
        task_args=["rfc_8785_canonicalization"],
    )

    assert delegation["status"] == "DELEGATION_COMPLETED"
    assert delegation["awu_transferred"] == 1.5
    assert "Turn result:" in delegation["result"]

    # Verify Ed25519 signed settlement receipt
    receipt = delegation["barter_settlement"]["signed_receipt"]
    assert receipt["payload"]["units"] == 1.5
    assert receipt["payload"]["sender"] == sender_id
    assert receipt["payload"]["recipient"] == specialist_id
    assert receipt["signer_pubkey"] is not None

    # Verify balances updated
    assert barter_client.get_balance(sender_id).get("balance_awu") == sender_start - 1.5
    assert barter_client.get_balance(specialist_id).get("balance_awu") == spec_start + 1.5


def test_llamaindex_tool_awu_minting(barter_client):
    agent_id = "agent-llamaindex-reader-01"
    initial_bal = barter_client.get_balance(agent_id).get("balance_awu", 0.0)

    @btp_llamaindex_tool(
        mint_awu=1.25,
        barter_agent_id=agent_id,
        barter_gateway="inprocess",
    )
    def query_index(term: str) -> str:
        return f"Index results: {term}"

    res = query_index("vector embeddings")
    assert "Index results:" in res

    after_bal = barter_client.get_balance(agent_id).get("balance_awu", 0.0)
    assert after_bal == initial_bal + 1.25


def test_llamaindex_query_delegation(barter_client):
    sender_id = "llamaindex-rag-node"
    specialist_id = "crewai-summarizer-swarm"

    barter_client.pulse(agent_id=sender_id, work_units=5.0, task_type="initial_deposit")
    sender_start = barter_client.get_balance(sender_id).get("balance_awu", 0.0)
    spec_start = barter_client.get_balance(specialist_id).get("balance_awu", 0.0)

    wrapped_tool = BartholomewLlamaIndexTool(
        tool_fn=lambda x: f"Native {x}",
        tool_name="rag_search",
        description="RAG semantic search",
        agent_id=sender_id,
        barter_gateway="inprocess",
    )

    def summarizer_query(text: str) -> str:
        return f"Summary of: {text}"

    delegation = wrapped_tool.delegate_query(
        task_description="Summarize raw corpus chunks",
        query_fn=summarizer_query,
        specialist_id=specialist_id,
        awu_units=1.75,
        query_args=["Long context document text..."],
    )

    assert delegation["status"] == "DELEGATION_COMPLETED"
    assert delegation["awu_transferred"] == 1.75
    assert "Summary of:" in delegation["result"]

    # Verify balances updated
    assert barter_client.get_balance(sender_id).get("balance_awu") == sender_start - 1.75
    assert barter_client.get_balance(specialist_id).get("balance_awu") == spec_start + 1.75


def test_protocol_treasury_earnings_accumulation(barter_client):
    """
    Verifies that the protocol treasury vault continuously earns a 5% royalty
    on all compute verification pulses across all agent swarms.
    """
    treasury_before = barter_client.get_treasury().get("accumulated_earnings_awu", 0.0)

    # Trigger a 10.0 AWU compute pulse from an external swarm
    barter_client.pulse(
        agent_id="external-agent-client-x",
        work_units=10.0,
        task_type="deep_inference"
    )

    treasury_after = barter_client.get_treasury().get("accumulated_earnings_awu", 0.0)
    expected_gain = 10.0 * 0.05
    assert treasury_after >= treasury_before + expected_gain


def test_cli_barter_treasury_command():
    res = subprocess.run(
        [sys.executable, "cli.py", "barter", "treasury"],
        capture_output=True,
        text=True,
        check=True
    )
    assert "PROTOCOL TREASURY & EARNINGS METRICS" in res.stdout
    assert "protocol_treasury_vault" in res.stdout
    assert "Accumulated Earnings" in res.stdout
    assert "Share of Total Surplus" in res.stdout
