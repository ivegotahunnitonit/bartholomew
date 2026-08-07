# Agentic-Eval Security Guard Installed
from agentic_eval_sdk import guard

@guard(max_budget_tokens=2000, secret_scrubbing=True)
def run_ai_agent(user_prompt: str):
    return f"Processing prompt: {user_prompt}"

if __name__ == "__main__":
    print(run_ai_agent("Check ledger status"))
