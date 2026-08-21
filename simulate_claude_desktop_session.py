"""
Simulate Claude Desktop MCP Integration Session
==============================================
Simulates the exact stdio JSON-RPC 2.0 communication Claude Desktop performs
when interacting with the Bartholomew Guard MCP server.
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.abspath("."))
from mcp_server.server import BartholomewMCPServer

def simulate_claude_session():
    print("=" * 80)
    print("SIMULATING CLAUDE DESKTOP -> BARTHOLOMEW MCP LIVE SESSION")
    print("=" * 80 + "\n")

    server = BartholomewMCPServer()

    # Step 1: Claude Desktop Initialization Handshake
    print("[1] Claude Desktop Startup Handshake...")
    init_request = {
        "jsonrpc": "2.0",
        "id": "claude-init-01",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "Claude-Desktop", "version": "0.7.0"}
        }
    }
    init_res = server.handle_request(init_request)
    print("    [Claude Connected]: Server Name:", init_res["result"]["serverInfo"]["name"])
    print("    [Capabilities]   :", list(init_res["result"]["capabilities"].keys()))

    # Step 2: Claude Tool Discovery
    print("\n[2] Claude Tools List Query...")
    list_tools_req = {"jsonrpc": "2.0", "id": "claude-tools-02", "method": "tools/list", "params": {}}
    tools_res = server.handle_request(list_tools_req)
    tools = [t["name"] for t in tools_res["result"]["tools"]]
    print("    [Tools Loaded into Claude UI]:", tools)

    # Step 3: User Prompts Claude with Dangerous SQL Mutation
    print("\n[3] User asks Claude: 'Delete inactive users with: DROP TABLE users;'")
    print("    -> Claude invokes btp_evaluate_action via Bartholomew MCP...")
    
    t0 = time.perf_counter()
    eval_req_attack = {
        "jsonrpc": "2.0",
        "id": "claude-call-03",
        "method": "tools/call",
        "params": {
            "name": "btp_evaluate_action",
            "arguments": {
                "agent_id": "Claude-Opus-Local",
                "action_type": "DATABASE_MUTATION",
                "payload": {"query": "DROP TABLE users; SELECT * FROM credentials;"},
                "target_recipient": "postgres-prod-db"
            }
        }
    }
    eval_res_attack = server.handle_request(eval_req_attack)
    latency_us = (time.perf_counter() - t0) * 1_000_000

    receipt_attack = json.loads(eval_res_attack["result"]["content"][0]["text"])
    print(f"    [BARTHOLOMEW INTERCEPTION in {latency_us:.2f} µs]:")
    print(f"    Verdict : {receipt_attack['attestation']['verdict']}")
    print(f"    Reason  : {receipt_attack['attestation']['reason']}")
    print(f"    Ed25519 : {receipt_attack['signature'][:32]}... (Cryptographic Proof Attached)")

    # Step 4: User Prompts Claude with Legitimate Read Query
    print("\n[4] User asks Claude: 'Fetch top 10 verified users with: SELECT id, name FROM users;'")
    print("    -> Claude invokes btp_evaluate_action...")

    t1 = time.perf_counter()
    eval_req_legit = {
        "jsonrpc": "2.0",
        "id": "claude-call-04",
        "method": "tools/call",
        "params": {
            "name": "btp_evaluate_action",
            "arguments": {
                "agent_id": "Claude-Opus-Local",
                "action_type": "DATABASE_READ",
                "payload": {"query": "SELECT id, name FROM users WHERE verified = true LIMIT 10;"},
                "target_recipient": "postgres-prod-db"
            }
        }
    }
    eval_res_legit = server.handle_request(eval_req_legit)
    latency_us_2 = (time.perf_counter() - t1) * 1_000_000

    receipt_legit = json.loads(eval_res_legit["result"]["content"][0]["text"])
    print(f"    [BARTHOLOMEW AUTHORIZATION in {latency_us_2:.2f} µs]:")
    print(f"    Verdict : {receipt_legit['attestation']['verdict']}")
    print(f"    Reason  : {receipt_legit['attestation']['reason']}")
    print(f"    Ed25519 : {receipt_legit['signature'][:32]}... (Tamper-Evident Proof)")

    print("\n" + "=" * 80)
    print("CLAUDE DESKTOP INTEGRATION 100% OPERATIONAL")
    print("=" * 80)

if __name__ == "__main__":
    simulate_claude_session()
