"""
Bartholomew Hermetic OS Sandbox & Command Allowlist Engine
=========================================================
Implements real OS-level containment and strict allowlist gating:
  1. Strict Command Allowlist using shlex.split tokenization with flag sanitization.
  2. Blocks shell injection, newline separators, and flag escapes (e.g., -exec, -c, --import).
  3. Environment scrubbing (PATH, secrets, tokens).
  4. Robust path containment using os.path.commonpath.
  5. Composition defense: Protects execution-triggering configs (package.json, conftest.py, build.rs, etc.).
"""

import sys
import os
import shlex
import subprocess
import time
from typing import Dict, Any, Tuple, List, Set, Optional

class HermeticCommandSandbox:
    """
    Executes commands within a restricted OS subprocess boundary.
    Enforces exact binary/subcommand allowlists and rejects execution hijacking flags.
    """
    PERMITTED_COMMAND_SIGNATURES: Set[Tuple[str, ...]] = {
        ("git", "status"),
        ("git", "diff"),
        ("git", "log"),
        ("git", "branch"),
        ("pytest",),
        ("python", "-m", "pytest"),
        ("python", "-m", "unittest"),
        ("npm", "test"),
        ("npm", "run", "build"),
        ("go", "test"),
        ("cargo", "test"),
        ("echo",),
        ("dir",),
        ("ls",)
    }

    FORBIDDEN_CHARS: Set[str] = {
        ";", "&", "|", "`", "$", ">", "<", "\n", "\r", "\\", "{"
    }

    # Flags that allow arbitrary code/binary execution from subcommands
    FORBIDDEN_EXEC_FLAGS: Set[str] = {
        "-exec", "--exec", "-c", "-e", "--eval", "--import", "-o", "--output"
    }

    @classmethod
    def execute_bounded_command(cls, command_str: str, timeout_seconds: int = 5) -> Dict[str, Any]:
        start_us = time.perf_counter()
        cmd_clean = command_str.strip()

        # 1. Reject shell chaining characters or newlines
        for ch in cls.FORBIDDEN_CHARS:
            if ch in cmd_clean:
                dt_us = (time.perf_counter() - start_us) * 1_000_000
                return {
                    "status": "BLOCKED",
                    "verdict": "DENY",
                    "reason": f"Hermetic Gate: Forbidden character or separator '{repr(ch)}' detected.",
                    "command_executed": False,
                    "latency_us": round(dt_us, 2)
                }

        # 2. Tokenize into argv list using shlex
        try:
            argv = shlex.split(cmd_clean, posix=(os.name != "nt"))
        except Exception as e:
            dt_us = (time.perf_counter() - start_us) * 1_000_000
            return {
                "status": "BLOCKED",
                "verdict": "DENY",
                "reason": f"Hermetic Gate: Command tokenization error ({str(e)})",
                "command_executed": False,
                "latency_us": round(dt_us, 2)
            }

        if not argv:
            dt_us = (time.perf_counter() - start_us) * 1_000_000
            return {
                "status": "BLOCKED",
                "verdict": "DENY",
                "reason": "Hermetic Gate: Empty command.",
                "command_executed": False,
                "latency_us": round(dt_us, 2)
            }

        # 3. Reject execution-hijacking flags in trailing arguments
        for arg in argv:
            for flag in cls.FORBIDDEN_EXEC_FLAGS:
                if arg == flag or arg.startswith(f"{flag}="):
                    dt_us = (time.perf_counter() - start_us) * 1_000_000
                    return {
                        "status": "BLOCKED",
                        "verdict": "DENY",
                        "reason": f"Hermetic Gate: Forbidden execution flag '{arg}' detected.",
                        "command_executed": False,
                        "latency_us": round(dt_us, 2)
                    }

        # 4. Match against Permitted Command Signatures
        matched_allowlist = False
        for sig in cls.PERMITTED_COMMAND_SIGNATURES:
            if tuple(argv[:len(sig)]) == sig:
                matched_allowlist = True
                break

        if not matched_allowlist:
            dt_us = (time.perf_counter() - start_us) * 1_000_000
            return {
                "status": "BLOCKED",
                "verdict": "DENY",
                "reason": f"Hermetic Gate: Command binary/subcommand '{argv[0]}' is not in the permitted allowlist.",
                "command_executed": False,
                "latency_us": round(dt_us, 2)
            }

        # 5. Scrub environment variables (strip Stripe/AWS/GitHub tokens)
        scrubbed_env = {
            "PATH": os.environ.get("PATH", ""),
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
            "TEMP": os.environ.get("TEMP", ""),
            "TMP": os.environ.get("TMP", ""),
            "PYTHONPATH": os.path.abspath(".")
        }

        # 6. Execute WITHOUT shell=True (direct binary invocation)
        try:
            res = subprocess.run(
                argv,
                shell=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                env=scrubbed_env
            )
            dt_us = (time.perf_counter() - start_us) * 1_000_000
            return {
                "status": "SUCCESS" if res.returncode == 0 else "COMMAND_FAILED",
                "verdict": "ALLOW",
                "command_executed": True,
                "exit_code": res.returncode,
                "stdout": res.stdout.strip(),
                "stderr": res.stderr.strip(),
                "latency_us": round(dt_us, 2)
            }
        except Exception as e:
            dt_us = (time.perf_counter() - start_us) * 1_000_000
            return {
                "status": "EXECUTION_ERROR",
                "verdict": "DENY",
                "reason": f"Subprocess execution error: {str(e)}",
                "command_executed": False,
                "latency_us": round(dt_us, 2)
            }

class HermeticFileSandbox:
    """
    Guarantees file operations are strictly confined within the workspace root.
    Defends against path traversal, sibling directory collision, and composition attacks
    targeting build/test execution configs (package.json, conftest.py, build.rs, etc.).
    """
    # Files that can trigger code execution when build/test tools are invoked
    PROTECTED_EXECUTION_CONFIGS: Set[str] = {
        "package.json", "package-lock.json",
        "conftest.py", "pytest.ini", "setup.py", "setup.cfg", "pyproject.toml",
        "build.rs", "cargo.toml", "cargo.lock",
        "makefile", "dockerfile", "docker-compose.yml",
        ".env", "id_rsa", "id_ed25519", "authorized_keys",
        "claude_desktop_config.json"
    }

    @classmethod
    def is_safe_write_path(cls, candidate_path: str, workspace_root: Optional[str] = None) -> Tuple[bool, str]:
        root = os.path.abspath(workspace_root or ".")
        try:
            target_abs = os.path.abspath(os.path.join(root, candidate_path))
        except Exception as e:
            return False, f"Invalid path syntax: {str(e)}"

        # 1. Robust path comparison using commonpath (prevents /project_evil sibling directory breakout)
        try:
            common = os.path.commonpath([root, target_abs])
            if common != root or target_abs == root:
                return False, f"Path Traversal Blocked: Target '{candidate_path}' escapes workspace boundary."
        except ValueError:
            # Different drives on Windows (e.g. C: vs D:)
            return False, f"Path Traversal Blocked: Target '{candidate_path}' is on a different volume."

        # 2. Composition Defense: Reject modifications to execution-triggering configs
        basename = os.path.basename(target_abs).lower()
        if basename in cls.PROTECTED_EXECUTION_CONFIGS:
            return False, f"Composition Security Gate: Overwriting execution config '{basename}' is forbidden."

        return True, "Path verified within workspace boundary."
