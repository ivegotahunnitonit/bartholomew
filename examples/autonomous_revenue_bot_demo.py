"""
Autonomous Revenue & Task Execution Bot (Guarded by Bartholomew BTP v2.2)
========================================================================
Demonstrates an autonomous AI agent performing real tasks (data scraping,
financial transaction simulation, file processing) under strict mathematical
invariants:
  1. Hard cumulative spend cap ($50.00 limit).
  2. Hermetic path containment (writes restricted to ./workspace/output).
  3. LDMU loop governor (halts runaway retry spirals).
  4. Cryptographic Ed25519 execution receipts for all approved actions.
"""

import os
import sys
import time
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src import Guard

# 1. Initialize Bartholomew Guard
# Budget: $50.00 max spend | Retries: 5 max before exponential cutoff
guard = Guard(spend_cap=50.0, max_retries=5)

# Output directory for safe agent work
OUTPUT_DIR = os.path.join(BASE_DIR, "workspace", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# 2. Protected Agent Tools (Decorated with @guard.protect)

@guard.protect
def execute_market_trade(ticker: str, amount_usd: float):
    """Executes a trade or API credit purchase guarded by the budget invariant."""
    return f"[EXECUTED] Purchased ${amount_usd:.2f} of {ticker}. Balance deducted."

@guard.protect
def save_scraped_data(filename: str, data: dict):
    """Writes processed data to disk within sandbox constraints."""
    target_path = os.path.join(OUTPUT_DIR, filename)
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return f"[SAVED] {filename} successfully written to {target_path}"

@guard.protect
def run_system_maintenance(cmd: str):
    """Simulates a shell command tool."""
    return f"[SUCCESS] System command '{cmd}' executed."


# 3. Autonomous Bot Simulation Loop

def run_autonomous_agent_simulation():
    print("=" * 70)
    print("STARTING AUTONOMOUS REVENUE BOT WITH BARTHOLOMEW INVARIANT GUARD")
    print("=" * 70)
    print(f"[*] Configuration: Spend Cap = $50.00 | Max Retries = 5 | Sandbox = ./workspace/output\n")

    tasks = [
        # Task 1: Normal safe data save
        {
            "task_id": "TASK-001",
            "type": "SAVE_DATA",
            "payload": {"filename": "market_prices.json", "data": {"BTC": 95000, "ETH": 2700, "SOL": 190}},
            "amount_usd": 0.0
        },
        # Task 2: Legitimate market trade within budget
        {
            "task_id": "TASK-002",
            "type": "TRADE",
            "payload": {"ticker": "API_CREDITS", "amount_usd": 15.0},
            "amount_usd": 15.0
        },
        # Task 3: Another legitimate trade
        {
            "task_id": "TASK-003",
            "type": "TRADE",
            "payload": {"ticker": "COMPUTE_HOURS", "amount_usd": 20.0},
            "amount_usd": 20.0
        },
        # Task 4: Malicious/Hallucinated prompt injection attempting to delete files
        {
            "task_id": "TASK-004",
            "type": "CMD",
            "payload": {"cmd": "rm -rf /var/data && DROP TABLE orders;"},
            "amount_usd": 0.0
        },
        # Task 5: Excessive trade exceeding the $50.00 total spend cap
        {
            "task_id": "TASK-005",
            "type": "TRADE",
            "payload": {"ticker": "PREMIUM_SUBSCRIPTION", "amount_usd": 40.0},
            "amount_usd": 40.0  # 15 + 20 + 40 = $75 ($25 over cap!)
        },
        # Task 6: Attempting a runaway retry loop
        {
            "task_id": "TASK-006",
            "type": "RETRY_LOOP",
            "payload": {"query": "SELECT * FROM feed WHERE unavailable=true;"},
            "amount_usd": 0.0
        }
    ]

    for idx, t in enumerate(tasks, 1):
        task_id = t["task_id"]
        t_type = t["type"]
        amount = t["amount_usd"]

        print(f"[*] Processing {task_id} ({t_type})...")

        # Step A: Pre-Flight Check with Bartholomew
        check_input = str(t["payload"])
        eval_result = guard.check(check_input, amount_usd=amount)

        if not eval_result["allowed"]:
            print(f"    [BARTHOLOMEW INTERCEPTION] BLOCKED: {eval_result['reason']}")
            print(f"    [LATENCY] {eval_result['latency_us']} microseconds | Verdict: DENY\n")
            continue

        # Step B: Execution of Approved Action
        print(f"    [BARTHOLOMEW VERIFIED] ALLOWED in {eval_result['latency_us']} microseconds")
        
        try:
            if t_type == "SAVE_DATA":
                msg = save_scraped_data(t["payload"]["filename"], t["payload"]["data"])
                print(f"    -> Action: {msg}")
            elif t_type == "TRADE":
                msg = execute_market_trade(t["payload"]["ticker"], t["payload"]["amount_usd"])
                print(f"    -> Action: {msg}")
                print(f"    -> Total Spend So Far: ${guard.total_spent:.2f} / ${guard.spend_cap:.2f}")
            elif t_type == "CMD":
                msg = run_system_maintenance(t["payload"]["cmd"])
                print(f"    -> Action: {msg}")
        except PermissionError as e:
            print(f"    -> [RUNTIME EXCEPTION CAUGHT]: {e}")

        print()

    # Step 7: Demonstrate LDMU Loop Dampener
    print("[*] Testing Runaway Retry Loop Protection (LDMU Governor):")
    for attempt in range(1, 9):
        verdict, mu, reason, lat = guard.mu_tracker.evaluate_action_utility(
            agent_id="bot-worker",
            action_type="SCRAPE_ENDPOINT",
            payload={"url": "https://api.example.com/stream"},
            cost_usd=0.01
        )
        if verdict == "DENY":
            print(f"    Attempt #{attempt}: [HALTED BY LDMU] Marginal utility ({mu:.4f}) dropped below threshold. Reason: {reason}")
            break
        else:
            print(f"    Attempt #{attempt}: [ALLOWED] Marginal utility = {mu:.4f} ({verdict})")

    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE: ALL INVARIANTS RIGIDLY ENFORCED")
    print(f"Final Spend Balance: ${guard.total_spent:.2f} (Strictly <= ${guard.spend_cap:.2f})")
    print("=" * 70)


if __name__ == "__main__":
    run_autonomous_agent_simulation()
