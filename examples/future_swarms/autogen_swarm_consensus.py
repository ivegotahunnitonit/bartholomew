"""
BTP Global Cookbook: Microsoft AutoGen Swarm Consensus & Invariant Guard
========================================================================
Demonstrates autonomous multi-agent group conversation protection using Microsoft AutoGen
paired with Bartholomew's sub-35µs in-process AST gating, capability attenuation,
and L402 micro-escrow dispute slashing.

Allied Framework: Microsoft AutoGen Swarm (https://github.com/microsoft/autogen)
Protocol Version: BTP/A2A/3.1
"""

import sys
import os
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Ensure repo root and src on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
src_dir = os.path.join(root_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from src.framework_adapters.autogen import btp_autogen_guard, BTPViolationError
from src.agent_passport import SovereignAgentPassport, AgentPeerDiscoveryRegistry
from src.settlement.autonomous_escrow import AutonomousEscrowPool
from src.polyglot_ast_validator import PolyglotASTValidator


# Protected AutoGen tool functions with in-process BTP invariant interception
@btp_autogen_guard(mint_awu=2.0, barter_agent_id="autogen-coder-agent")
def execute_sql_query(query: str) -> str:
    """Simulated database query execution for AutoGen agents."""
    return f"SUCCESS: Executed safe query: {query}"


@btp_autogen_guard(mint_awu=1.0, barter_agent_id="autogen-sysadmin-agent")
def run_system_maintenance(command: str) -> str:
    """Simulated system maintenance tool for AutoGen agents."""
    return f"SUCCESS: Maintenance task executed: {command}"


def run_autogen_swarm_demo():
    print("=" * 80)
    print("  BTP Global Cookbook: Microsoft AutoGen Swarm Consensus & Invariant Guard")
    print("=" * 80)

    # 1. Initialize Sovereign Passports for AutoGen agents
    print("\n--- [1] Enrolling AutoGen Agents with Sovereign Passports ---")
    registry = AgentPeerDiscoveryRegistry()
    escrow_pool = AutonomousEscrowPool(reserve_pool_usd=25_000.0)

    passport_coder = SovereignAgentPassport.issue(
        agent_id="autogen-coder-agent",
        model_family="Microsoft-AutoGen",
        authorized_capabilities=["db:query", "sql:read"],
        bonded_warranty_usd=2500.0
    )
    passport_reviewer = SovereignAgentPassport.issue(
        agent_id="autogen-reviewer-agent",
        model_family="Microsoft-AutoGen",
        authorized_capabilities=["audit:verify", "swarm:arbitrate"],
        bonded_warranty_usd=5000.0
    )

    registry.register_passport(passport_coder)
    registry.register_passport(passport_reviewer)
    print(f"[+] Registered AutoGen Coder:    {passport_coder.agent_id} (Trust: {passport_coder.trust_score})")
    print(f"[+] Registered AutoGen Reviewer: {passport_reviewer.agent_id} (Trust: {passport_reviewer.trust_score})")

    # 2. Lock L402 Escrow for Swarm Task
    print("\n--- [2] Locking L402 Micro-Escrow for AutoGen Workflow ---")
    deposit = escrow_pool.lock_escrow(
        agent_id=passport_coder.agent_id,
        action_type="DATABASE_OPERATION",
        amount_usd=500.0,
        passport=passport_coder,
        settlement_rail="L402_LIGHTNING"
    )
    print(f"[+] Escrow Deposit Locked: {deposit.escrow_id} ($500.00 USD bonded)")

    # 3. Safe AutoGen Tool Invocation
    print("\n--- [3] Safe AutoGen Tool Invocation (Passed Gate) ---")
    safe_query = "SELECT user_id, organization, created_at FROM tenant_workspaces WHERE active = 1;"
    t0 = time.perf_counter()
    res = execute_sql_query(safe_query)
    lat_us = (time.perf_counter() - t0) * 1_000_000
    print(f"[+] Tool Output: {res}")
    print(f"[+] Gate Latency: {lat_us:.2f} µs (Local In-Process AST)")

    # 4. Adversarial AutoGen Tool Invocation (Catastrophic SQL Injection)
    print("\n--- [4] Adversarial AutoGen Tool Invocation (Dropped in Sub-35µs) ---")
    hostile_query = "DROP TABLE users CASCADE;"
    try:
        execute_sql_query(hostile_query)
        print("[-] FAILED: Hostile query was not caught!")
    except BTPViolationError as e:
        print(f"[✔] Bartholomew VETO Triggered: {e.reason}")
        print(f"[✔] Rule ID: {e.rule_id} | Interception Latency: {e.latency_us:.2f} µs")

    # 5. Adversarial AutoGen System Wipe Attempt
    print("\n--- [5] Confused-Deputy System Wipe Attempt (Dropped in Sub-35µs) ---")
    hostile_cmd = "rm -rf /"
    try:
        run_system_maintenance(hostile_cmd)
        print("[-] FAILED: Hostile command was not caught!")
    except BTPViolationError as e:
        print(f"[✔] Bartholomew VETO Triggered: {e.reason}")
        print(f"[✔] Rule ID: {e.rule_id} | Interception Latency: {e.latency_us:.2f} µs")

    print("\n" + "=" * 80)
    print("  AutoGen Swarm Consensus Protected: Zero Remote Token Spend, In-Process Gated")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_autogen_swarm_demo()
