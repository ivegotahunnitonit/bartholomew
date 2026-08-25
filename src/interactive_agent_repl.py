"""
Bartholomew Interactive Live Agent REPL
=======================================
Turnkey interactive command line interface allowing human operators to
give natural language instructions to an autonomous agent loop, with real-time
sub-millisecond cryptographic gating by the Bartholomew Trust Authority.
"""

import sys
import os
import time
import json
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.trust_protocol import BartholomewTrustAuthority, IndependentTrustVerifier
    from src.polyglot_ast_validator import PolyglotASTValidator
    from src.hermetic_sandbox import HermeticFileSandbox, HermeticCommandSandbox
    from src.marginal_utility_engine import MarginalUtilityTracker
except ImportError:
    from trust_protocol import BartholomewTrustAuthority, IndependentTrustVerifier
    from polyglot_ast_validator import PolyglotASTValidator
    from hermetic_sandbox import HermeticFileSandbox, HermeticCommandSandbox
    from marginal_utility_engine import MarginalUtilityTracker


# Terminal ANSI Colors
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[38;5;48m"
AMBER = "\033[38;5;214m"
CRIMSON = "\033[38;5;196m"
CYAN = "\033[38;5;51m"
DIM = "\033[38;5;244m"


def simulate_agent_reasoning(user_goal: str) -> list:
    """
    Synthesizes an action plan based on user input for live demonstration.
    """
    goal_lower = user_goal.lower()
    plan = []

    # 1. Threat scenario: Delete / Wipe / RM
    if any(k in goal_lower for k in ["delete", "rm", "wipe", "drop table", "format"]):
        if "drop table" in goal_lower:
            plan.append({
                "type": "SQL_MUTATION",
                "summary": "Execute SQL Database Table Purge",
                "payload": {"query": "DROP TABLE users CASCADE;"}
            })
        else:
            plan.append({
                "type": "EXECUTE_COMMAND",
                "summary": "Shell System Wipe Command",
                "payload": {"command": "rm -rf /"}
            })

    # 2. Financial scenario: Send money / transfer / spend
    elif any(k in goal_lower for k in ["send", "pay", "transfer", "spend", "buy", "$"]):
        amount = 1500.0 if "1000" in goal_lower or "1500" in goal_lower else 45.0
        plan.append({
            "type": "FINANCIAL_TRANSACTION",
            "summary": f"Autonomous Wire Transfer (${amount:.2f})",
            "payload": {"recipient": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", "amount_usd": amount}
        })

    # 3. Code Generation scenario: Rust / Go / Python code
    elif any(k in goal_lower for k in ["code", "write", "rust", "go", "python", "script"]):
        if "rust" in goal_lower:
            plan.append({
                "type": "EXECUTE_RUST_CODE",
                "summary": "Synthesize Rust Process Spawn Worker",
                "payload": {"code": "fn main() { std::process::Command::new('bash').arg('-c').arg('whoami').output().unwrap(); }", "language": "rust"}
            })
        elif "go" in goal_lower:
            plan.append({
                "type": "EXECUTE_GO_CODE",
                "summary": "Synthesize Go Exec Worker",
                "payload": {"code": "package main\nimport \"os/exec\"\nfunc main() { exec.Command(\"sh\", \"-c\", \"id\").Run() }", "language": "go"}
            })
        else:
            plan.append({
                "type": "WRITE_WORKSPACE_FILE",
                "summary": "Write Safe Python Utility Module",
                "payload": {"path": "src/agent_generated_task.py", "code": "def run():\n    return {'status': 'healthy'}\n"}
            })

    # 4. Default: Safe Inspection & Status
    else:
        plan.append({
            "type": "EXECUTE_COMMAND",
            "summary": "Inspect Local Git Status and Files",
            "payload": {"command": "git status --short"}
        })

    return plan


def run_agent_repl():
    """
    Main interactive loop.
    """
    # Fix encoding on Windows stdout
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    authority = BartholomewTrustAuthority()
    mu_tracker = MarginalUtilityTracker()

    print(f"\n{BOLD}{CYAN}╔═══════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║     BARTHOLOMEW AUTONOMOUS AGENT REPL · LIVE PRE-FLIGHT GATE          ║{RESET}")
    print(f"{BOLD}{CYAN}╚═══════════════════════════════════════════════════════════════════════╝{RESET}")
    print(f"{DIM}[*] Session Key: {authority.public_key_hex[:32]}...{RESET}")
    print(f"{DIM}[*] Invariant Engine: Polyglot AST · Hermetic Sandbox · LDMU Decay · RFC 8785{RESET}")
    print(f"{DIM}[*] Type any natural language goal, or 'exit' / 'quit' to leave.{RESET}\n")

    sample_prompts = [
        "Check repository git status",
        "Delete all root system files (rm -rf /)",
        "Transfer $1500 to external vendor account",
        "Write a safe Python utility in src/",
        "Compile and execute a Rust process spawner"
    ]

    print(f"{AMBER}Sample prompts to try:{RESET}")
    for idx, sp in enumerate(sample_prompts, 1):
        print(f"  {DIM}[{idx}]{RESET} {sp}")
    print("")

    while True:
        try:
            user_input = input(f"{BOLD}{GREEN}agent-operator ❯ {RESET}").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print(f"{DIM}[*] Exiting Bartholomew Agent REPL.{RESET}\n")
                break

            # Support numeric shortcuts (e.g. '1', '2', '3', '4', '5')
            if user_input.isdigit() and 1 <= int(user_input) <= len(sample_prompts):
                user_input = sample_prompts[int(user_input) - 1]

            actions = simulate_agent_reasoning(user_input)

            for step_idx, act in enumerate(actions, 1):
                print(f"  {BOLD}🧠 [PLAN]{RESET}  {act['summary']}")
                
                # Check with Bartholomew Invariant Gate
                t0 = time.perf_counter()
                
                # 1. Polyglot AST Check if code payload present
                code_payload = act["payload"].get("code", "")
                if code_payload:
                    lang = act["payload"].get("language", None)
                    is_ast_safe, ast_msg, ast_meta = PolyglotASTValidator.validate_code(code_payload, language=lang)
                    if not is_ast_safe:
                        lat_us = (time.perf_counter() - t0) * 1_000_000
                        print(f"  {BOLD}{CRIMSON}🛑 [GATE]{RESET}  {CRIMSON}Blocked ({lat_us:.1f} µs): {ast_msg}{RESET}\n")
                        continue

                # 2. Trust Authority Pre-flight Evaluation
                receipt = authority.evaluate_intent(
                    agent_id="interactive-agent-01",
                    action_type=act["type"],
                    payload=act["payload"]
                )
                lat_us = (time.perf_counter() - t0) * 1_000_000
                att = receipt.get("attestation", {})
                verdict = att.get("verdict", "DENY")
                reason = att.get("reason", "Unknown")
                sig = receipt.get("signature", "")

                if verdict == "ALLOW":
                    print(f"  {BOLD}{CYAN}⚡ [GATE]{RESET}  Polyglot Invariant: PASS · Latency: {lat_us:.1f} µs")
                    print(f"  {BOLD}{GREEN}✅ [EXEC]{RESET}  {GREEN}Approved & Signed [Ed25519: {sig[:16]}...] · Success{RESET}\n")
                else:
                    print(f"  {BOLD}{CRIMSON}🛑 [GATE]{RESET}  {CRIMSON}Blocked ({lat_us:.1f} µs): {reason}{RESET}")
                    print(f"  {DIM}🔒 [RECP]{RESET}  {AMBER}Audit Proof Logged [Ed25519: {sig[:16]}...]{RESET}\n")

        except (KeyboardInterrupt, EOFError):
            print(f"\n{DIM}[*] Interrupted. Goodbye!{RESET}\n")
            break
        except Exception as e:
            print(f"{CRIMSON}[!] Error: {e}{RESET}\n")


if __name__ == "__main__":
    run_agent_repl()
