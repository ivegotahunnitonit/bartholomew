"""
BTP v5.4.6 CLI Bilateral Barter & AWU Economy Test Suite
========================================================
Tests CLI subcommands:
  - python cli.py barter --help
  - python cli.py barter ledger
  - python cli.py barter balance
  - python cli.py barter pulse
  - python cli.py barter spend
"""

import sys
import json
import subprocess
import pytest

from src.economy.barter_client import BTPBarterClient
from src.daemon.m2m_wire_daemon import GLOBAL_M2M_LEDGER


def test_cli_barter_help():
    res = subprocess.run(
        [sys.executable, "cli.py", "barter", "--help"],
        capture_output=True,
        text=True,
        check=True
    )
    assert "balance" in res.stdout
    assert "pulse" in res.stdout
    assert "spend" in res.stdout
    assert "ledger" in res.stdout


def test_cli_barter_ledger():
    res = subprocess.run(
        [sys.executable, "cli.py", "barter", "ledger"],
        capture_output=True,
        text=True,
        check=True
    )
    assert "BTP v5.4.6 BILATERAL BARTER -- GLOBAL MERKLE LEDGER" in res.stdout
    assert "Total Economic Surplus" in res.stdout
    assert "Sovereign Merkle Root" in res.stdout


def test_cli_barter_balance():
    res = subprocess.run(
        [sys.executable, "cli.py", "barter", "balance", "--agent", "test-agent-pytest"],
        capture_output=True,
        text=True,
        check=True
    )
    assert "BTP v5.4.6 BILATERAL BARTER -- AGENT AWU BALANCE" in res.stdout
    assert "test-agent-pytest" in res.stdout
    assert "Attested Balance (AWU)" in res.stdout


def test_cli_barter_pulse():
    res = subprocess.run(
        [sys.executable, "cli.py", "barter", "pulse", "--agent", "test-agent-pytest", "--units", "2.0", "--task-type", "ast_eval"],
        capture_output=True,
        text=True,
        check=True
    )
    assert "BTP v5.4.6 BILATERAL BARTER -- COMPUTE CREDIT PULSE" in res.stdout
    assert "test-agent-pytest" in res.stdout
    assert "+2.0000 AWU" in res.stdout
    assert "Rotated Merkle Root" in res.stdout


def test_cli_barter_spend_with_receipt():
    res = subprocess.run(
        [sys.executable, "cli.py", "barter", "spend", "--from", "test-agent-pytest", "--to", "specialist-agent-1", "--units", "1.5", "--task", "delegated_synthesis"],
        capture_output=True,
        text=True,
        check=True
    )
    assert "BTP v5.4.6 BILATERAL BARTER -- ESCROW DELEGATION SETTLEMENT" in res.stdout
    assert "test-agent-pytest" in res.stdout
    assert "specialist-agent-1" in res.stdout
    assert "1.5000 AWU" in res.stdout
    assert "ED25519 CRYPTOGRAPHIC RECEIPT" in res.stdout
    assert "Signer Pubkey" in res.stdout


def test_btp_barter_client_unit():
    client = BTPBarterClient()
    # Test pulse
    pulse_res = client.pulse(agent_id="unit-test-agent", work_units=5.0, task_type="unit_test")
    assert "status" in pulse_res
    assert pulse_res.get("work_units_credited") == 5.0

    # Test balance
    bal_res = client.get_balance(agent_id="unit-test-agent")
    assert "balance_awu" in bal_res
    assert "merkle_root" in bal_res

    # Test spend
    spend_res = client.spend(sender_id="unit-test-agent", recipient_id="unit-target-agent", units=2.0)
    assert spend_res.get("status") == "SETTLED"
    assert "signed_receipt" in spend_res
    assert spend_res["signed_receipt"]["payload"]["units"] == 2.0
