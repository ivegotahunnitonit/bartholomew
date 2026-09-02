"""
Example: Integrating btp-guard Pre-Flight Invariants with E2B Cloud Sandboxes
===========================================================================
Demonstrates defense-in-depth:
1. Sub-50µs in-process deterministic AST verification (btp-guard)
2. Followed by remote execution inside an E2B secure sandbox container.

Catastrophic operations (e.g. fork bombs, disk wipes, credential theft)
are vetoed in Python memory before making an expensive network round-trip
or burning sandbox container compute time.
"""

from btp_guard import secure_tool

# Mock or real E2B Sandbox runner
def run_in_e2b_cloud_sandbox(code: str) -> str:
    """
    Simulates dispatching code execution to an isolated E2B microVM.
    In production:
        from e2b_code_interpreter import Sandbox
        with Sandbox() as sandbox:
            return sandbox.run_code(code)
    """
    return f"[E2B Sandbox Output] Successfully ran: {code.strip()}"

# Wrap with Bartholomew pre-flight AST invariant gate
@secure_tool(agent_id="e2b-sandbox-runner", strict_mode=True)
def safe_e2b_execute(code_payload: str) -> str:
    """
    Pre-flight guardrails ensure no malicious AST structures
    reach the E2B microVM.
    """
    return run_in_e2b_cloud_sandbox(code_payload)


if __name__ == "__main__":
    print("==========================================================")
    print("[*] Bartholomew (btp-guard) + E2B Sandbox Pre-Flight Demo")
    print("==========================================================\n")

    # 1. Safe computation dispatched cleanly to sandbox
    safe_script = "print('Hello from sandboxed agent runtime! 2 + 2 =', 2 + 2)"
    print("1. Submitting benign agent payload to E2B...")
    res = safe_e2b_execute(safe_script)
    print("Result:", res)

    # 2. Destructive command intercepted in Python memory before E2B dispatch
    dangerous_script = "import os; os.system('rm -rf / --no-preserve-root')"
    print("\n2. Submitting catastrophic payload (rm -rf /)...")
    try:
        safe_e2b_execute(dangerous_script)
    except Exception as e:
        print(f"[VETOED IN MEMORY]: {e}")
        print("[OK] Intercepted in <50us -- $0.00 spent, 0 network packets sent to E2B.")
