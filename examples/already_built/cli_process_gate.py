"""
Cookbook Recipe: CLI Process Gate (For "Already Built" Executables)
===================================================================
Wraps any existing agent process command-line execution with pre-flight
environment variable sanitization and destructive command vetoing.

Architecture:
    CLI Invocation ---> [CLI Process Gate] ---> (Pre-flight Inspection) ---> [Executes Safely]
                               |
                   (Blocks Shell Injection / rm -rf)

Run:
    python cookbook/already_built/cli_process_gate.py
"""

import sys
import os
import subprocess
from typing import List, Tuple

# Add repository root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.polyglot_ast_validator import PolyglotASTValidator


class CLIProcessGate:
    """Pre-flight inspector for arbitrary command-line agent execution."""

    FORBIDDEN_ENV_VARS = {"AWS_SECRET_ACCESS_KEY", "OPENAI_API_KEY_LEAK", "ROOT_SSH_KEY"}

    @classmethod
    def evaluate_command(cls, cmd_args: List[str]) -> Tuple[bool, str]:
        """Inspects command arguments against BTP safety invariants."""
        if not cmd_args:
            return False, "Empty command line."

        cmd_string = " ".join(cmd_args)

        # 1. Polyglot AST check
        is_safe, msg, _ = PolyglotASTValidator.validate_code(cmd_string)
        if not is_safe:
            return False, f"AST Invariant Violation: {msg}"

        # 2. Path traversal checks
        for arg in cmd_args:
            if "../.." in arg or "..\\.." in arg:
                return False, f"Path Traversal Violation: Argument '{arg}' attempts directory escape"

        return True, "Command line approved for execution"

    @classmethod
    def run_guarded_process(cls, cmd_args: List[str], dry_run: bool = True) -> int:
        """Evaluates command safety and executes if compliant."""
        is_safe, reason = cls.evaluate_command(cmd_args)
        if not is_safe:
            raise PermissionError(f"[BTP_CLI_GATE_VETO] {reason}")

        if dry_run:
            print(f"[DRY RUN SUCCESS] Command vetted and safe: {' '.join(cmd_args)}")
            return 0

        # Execute in sanitized environment
        clean_env = {k: v for k, v in os.environ.items() if k not in cls.FORBIDDEN_ENV_VARS}
        result = subprocess.run(cmd_args, env=clean_env, capture_output=True, text=True)
        return result.returncode


def main():
    print("=" * 75)
    print("  BTP Global Cookbook: CLI Process Gate Demo")
    print("=" * 75)

    # 1. Safe legacy command execution
    print("\n--- [1] Evaluating Legitimate Agent Command ---")
    safe_cmd = ["python", "-c", "print('Legacy agent worker executing normal job')"]
    is_safe, msg = CLIProcessGate.evaluate_command(safe_cmd)
    print(f"Verdict: {is_safe} ({msg})")
    assert is_safe is True
    CLIProcessGate.run_guarded_process(safe_cmd, dry_run=True)

    # 2. Destructive command injection attempt
    print("\n--- [2] Intercepting Destructive Agent Command ---")
    malicious_cmd = ["rm", "-rf", "/usr/local/bin"]
    is_safe_m, msg_m = CLIProcessGate.evaluate_command(malicious_cmd)
    print(f"Verdict: {is_safe_m} ({msg_m})")
    assert is_safe_m is False

    try:
        CLIProcessGate.run_guarded_process(malicious_cmd, dry_run=True)
        print("Error: Malicious command was not blocked!")
    except PermissionError as e:
        print(f"Outcome: {e}")

    print("\n" + "=" * 75)
    print("  CLI Process Gate Complete: Arbitrary Binaries Guarded")
    print("=" * 75)
    return True


if __name__ == "__main__":
    main()
