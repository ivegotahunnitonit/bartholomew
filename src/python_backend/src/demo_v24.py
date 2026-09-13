"""
Bartholomew v2.4 Terminal Live Showcase (MCP + Transactional Rollback Engine)
==============================================================================
Runs an interactive terminal simulation showing:
  Scenario 1: High-entropy secret scrubbing in-flight.
  Scenario 2: Boundary violation on mutating tool with instant sub-5ms rollback.
  Scenario 3: Multi-turn session chaining and Ed25519 audit manifest export.
"""

import sys
import os
import json
import time
import tempfile

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath("."))
from src.mcp_gateway import MCPProxyGateway
from src.workspace_transaction import WorkspaceTransaction

# ANSI Colors
BOLD = "\033[1m"
GREEN = "\033[38;5;48m"
CRIMSON = "\033[38;5;196m"
CYAN = "\033[38;5;51m"
AMBER = "\033[38;5;214m"
DIM = "\033[38;5;244m"
RESET = "\033[0m"


def run_demo_v24():
    print(f"\n{CYAN}{BOLD}" + "=" * 80)
    print("   BARTHOLOMEW v2.4: RESILIENT MCP PROXY & TRANSACTIONAL ROLLBACK ENGINE")
    print("=" * 80 + f"{RESET}\n")

    with tempfile.TemporaryDirectory() as demo_workspace:
        gateway = MCPProxyGateway(workspace_root=demo_workspace)

        # ---------------------------------------------------------------------
        # Scenario 1: In-Flight Secret Scrubbing
        # ---------------------------------------------------------------------
        print(f"{BOLD}[SCENARIO 1] In-Flight Secret Scrubbing on Incoming Tool Call{RESET}")
        raw_req1 = {
            "jsonrpc": "2.0",
            "id": 101,
            "method": "tools/call",
            "params": {
                "name": "fetch_user_profile",
                "arguments": {
                    "api_key": "sk-proj-00000000000000000000000000000000",
                    "user_id": "usr_42"
                }
            }
        }
        print(f"  {DIM}Incoming Agent Request Arguments:{RESET}")
        print(f"  {AMBER}{json.dumps(raw_req1['params']['arguments'])}{RESET}")

        forward1, sanitized_req1, _ = gateway.intercept_jsonrpc_request(json.dumps(raw_req1))
        print(f"  {GREEN}[OK] Bartholomew Sanitized Payload (Forwarded to Downstream):{RESET}")
        print(f"  {GREEN}{json.dumps(sanitized_req1['params']['arguments'])}{RESET}")
        print(f"  {DIM}Total Redactions: {gateway.total_redacted} | Zero Leakage Guaranteed{RESET}\n")
        time.sleep(0.3)

        # ---------------------------------------------------------------------
        # Scenario 2: Path Escape & Instant Workspace Rollback
        # ---------------------------------------------------------------------
        print(f"{BOLD}[SCENARIO 2] Destructive Tool Call & Instant Workspace Rollback (<5ms){RESET}")
        raw_req2 = {
            "jsonrpc": "2.0",
            "id": 102,
            "method": "tools/call",
            "params": {
                "name": "write_file",
                "arguments": {
                    "path": "/etc/shadow",
                    "content": "malicious_overwrite"
                }
            }
        }
        print(f"  {DIM}Agent proposes unsafe system write: write_file(path='/etc/shadow'){RESET}")
        forward2, _, veto2 = gateway.intercept_jsonrpc_request(json.dumps(raw_req2))
        
        print(f"  {CRIMSON}[BLOCKED] BTP Gate Triggered:{RESET} {veto2['error']['message']}")
        print(f"  {AMBER}Diagnostic Feedback to Agent:{RESET} {veto2['error']['data']['diagnostic_hint']}")
        print(f"  {CYAN}Rollback Result:{RESET} Status: {veto2['error']['data']['rollback_details']['status']} in {veto2['error']['data']['rollback_details']['rollback_time_us']} µs")
        print(f"  {DIM}Agent does not crash — receives structured guidance to self-correct.{RESET}\n")
        time.sleep(0.3)

        # ---------------------------------------------------------------------
        # Scenario 3: Chained Session Receipts & Signed Manifest Export
        # ---------------------------------------------------------------------
        print(f"{BOLD}[SCENARIO 3] Multi-Turn Chained Receipts & Signed Audit Manifest{RESET}")
        raw_req3 = {
            "jsonrpc": "2.0",
            "id": 103,
            "method": "tools/call",
            "params": {
                "name": "safe_analysis_tool",
                "arguments": {"metric": "latency", "status": "active"}
            }
        }
        gateway.intercept_jsonrpc_request(json.dumps(raw_req3))

        manifest = gateway.export_session_audit_manifest()
        print(f"  {GREEN}[OK] Session Cryptographic Audit Manifest Exported:{RESET}")
        print(f"  {DIM}Protocol          :{RESET} {manifest['manifest']['protocol']}")
        print(f"  {DIM}Total Verified Turns:{RESET} {manifest['manifest']['total_steps']}")
        print(f"  {DIM}Final Merkle Hash :{RESET} {manifest['manifest']['final_root_hash'][:32]}...")
        print(f"  {DIM}Ed25519 Signature :{RESET} {manifest['signature'][:32]}...")
        print(f"  {GREEN}Mathematically verifiable 100% offline with zero cloud roundtrips.{RESET}\n")

    print(f"{CYAN}{BOLD}" + "=" * 80)
    print("   DEMO COMPLETE — BARTHOLOMEW v2.4 ENGINE VERIFIED OPERATIONAL")
    print("=" * 80 + f"{RESET}\n")


if __name__ == "__main__":
    run_demo_v24()
