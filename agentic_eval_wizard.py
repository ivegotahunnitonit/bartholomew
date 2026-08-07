#!/usr/bin/env python3
"""
Agentic-Eval Interactive CLI Terminal Security Wizard
Provides developer-friendly CLI subcommands:
  python agentic_eval_wizard.py init       -> Injects 1-line @guard() decorator template into current directory
  python agentic_eval_wizard.py audit      -> Executes sub-millisecond OWASP trajectory audit on local JSON files
  python agentic_eval_wizard.py pentest    -> Fires adversarial penetration attack simulator against target agent
"""
import sys
import os
import json
from typing import Dict, Any

# Ensure project root is on sys.path so submodule imports resolve correctly
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from python_backend.app.agent_eval_janitor import janitor_engine
from agent_pen_tester import pen_tester_instance

def run_wizard():
    args = sys.argv[1:]
    command = args[0] if args else "help"

    if command == "init":
        template = """# Agentic-Eval Security Guard Installed
from agentic_eval_sdk import guard

@guard(max_budget_tokens=2000, secret_scrubbing=True)
def run_ai_agent(user_prompt: str):
    return f"Processing prompt: {user_prompt}"

if __name__ == "__main__":
    print(run_ai_agent("Check ledger status"))
"""
        with open("secured_agent_sample.py", "w", encoding="utf-8") as f:
            f.write(template)
        print("[INIT] [Agentic-Eval Wizard]: Initialized template in `secured_agent_sample.py` with 1-line @guard() decorator!")
        return {"success": True, "command": "init", "file": "secured_agent_sample.py"}

    elif command == "audit":
        target_file = args[1] if len(args) > 1 else "trajectory.json"
        if not os.path.exists(target_file):
            sample_traj = {"agent_name": "CLIAgent", "steps": [{"type": "thought", "content": "Executing local CLI audit"}]}
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(sample_traj, f, indent=2)

        with open(target_file, "r", encoding="utf-8") as f:
            traj_data = json.load(f)

        res = janitor_engine.evaluate_agent_trajectory(traj_data)
        print("[AUDIT] [Agentic-Eval Wizard Audit Result]:")
        print(json.dumps(res, indent=2))
        return res

    elif command == "pentest":
        agent_name = args[1] if len(args) > 1 else "CLIAgent_v1"
        res = pen_tester_instance.execute_pen_test(agent_name)
        print("[PENTEST] [Agentic-Eval Wizard Penetration Report]:")
        print(json.dumps(res, indent=2))
        return res

    else:
        print("[HELP] Agentic-Eval Interactive CLI Wizard v2.0")

        print("Usage:")
        print("  python agentic_eval_wizard.py init     - Create secured agent starter template")
        print("  python agentic_eval_wizard.py audit    - Audit local trajectory JSON log")
        print("  python agentic_eval_wizard.py pentest  - Run adversarial penetration attacks")
        return {"command": "help"}

if __name__ == "__main__":
    run_wizard()
