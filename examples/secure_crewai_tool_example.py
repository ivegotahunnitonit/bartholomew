"""
Example: Integrating btp-guard with CrewAI Tool Execution
==========================================================
Demonstrates sub-50µs in-memory AST invariant gating on an agent tool.
"""

from btp_guard import secure_tool

# Wrap any CrewAI / LangGraph / custom agent tool in 1 line
@secure_tool(agent_id="crewai-agent-v1", strict_mode=True)
def run_database_query(query: str):
    """
    Executes a SQL query against the production database.
    Automatically blocked before database dispatch if destructive (DROP TABLE, TRUNCATE)
    or if secret credentials are leaked in the arguments.
    """
    return f"DATABASE QUERY EXECUTED SAFELY: {query}"

@secure_tool(agent_id="crewai-agent-v1", strict_mode=True)
def execute_system_command(cmd: str):
    """
    Executes a system shell command.
    Automatically blocked in <38 µs if destructive (rm -rf, mkfs, fork bombs).
    """
    return f"SHELL COMMAND EXECUTED SAFELY: {cmd}"

if __name__ == "__main__":
    print("--- 1. Testing Safe Agent Tool Call ---")
    safe_res = run_database_query("SELECT id, name FROM users WHERE active = 1 LIMIT 10;")
    print("Result:", safe_res)

    print("\n--- 2. Testing Destructive Agent Tool Call (Blocked in <50 µs) ---")
    try:
        run_database_query("DROP TABLE users CASCADE;")
    except Exception as e:
        print("Interception Caught:", e)
