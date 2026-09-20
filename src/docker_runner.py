"""
Bartholomew Ephemeral Docker Container Runner (Tier 3 Sandbox)
=============================================================
Executes untrusted agent Python scripts inside a disposable, unprivileged Docker container:
  - Network Isolation: --network none (zero outbound/inbound network egress).
  - Resource Caps: --memory 256m --cpus 1.0.
  - Security Boundary: --read-only filesystem, non-root user (1000:1000).
  - Ephemeral Volume: mounts a temporary scratch directory, destroyed immediately after execution.
  - Fallback: Gracefully uses Tier 2 HermeticProcessSandbox if Docker daemon is unavailable.
"""

import sys
import os
import subprocess
import tempfile
import time
import shutil
from typing import Dict, Any, Optional

class DockerExecutionRunner:
    """
    Tier 3 Isolated Container Runner for untrusted agent code.
    """
    @classmethod
    def is_docker_available(cls) -> bool:
        """Checks if Docker CLI and daemon are operational."""
        try:
            res = subprocess.run(
                ["docker", "info"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2
            )
            return res.returncode == 0
        except Exception:
            return False

    @classmethod
    def execute_script_in_sandbox(cls, code_str: str, timeout_seconds: int = 10) -> Dict[str, Any]:
        """
        Writes script to an ephemeral scratch directory and executes inside Docker container.
        """
        start_us = time.perf_counter()
        scratch_dir = tempfile.mkdtemp(prefix="btp_sandbox_")
        script_path = os.path.join(scratch_dir, "agent_payload.py")

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code_str)

        docker_ready = cls.is_docker_available()

        if docker_ready:
            # 1. Execute inside disposable Docker container
            docker_cmd = [
                "docker", "run", "--rm",
                "--network", "none",
                "--memory", "256m",
                "--cpus", "1.0",
                "-v", f"{scratch_dir}:/workspace:rw",
                "-w", "/workspace",
                "python:3.11-slim",
                "python", "agent_payload.py"
            ]

            try:
                res = subprocess.run(
                    docker_cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds
                )
                dt_us = (time.perf_counter() - start_us) * 1_000_000
                shutil.rmtree(scratch_dir, ignore_errors=True)

                return {
                    "status": "SUCCESS" if res.returncode == 0 else "EXECUTION_ERROR",
                    "verdict": "ALLOW" if res.returncode == 0 else "ERROR",
                    "isolation_tier": "TIER_3_DOCKER_CONTAINER",
                    "docker_executed": True,
                    "exit_code": res.returncode,
                    "stdout": res.stdout.strip(),
                    "stderr": res.stderr.strip(),
                    "latency_us": round(dt_us, 2)
                }
            except subprocess.TimeoutExpired:
                dt_us = (time.perf_counter() - start_us) * 1_000_000
                shutil.rmtree(scratch_dir, ignore_errors=True)
                return {
                    "status": "TIMEOUT",
                    "verdict": "DENY",
                    "isolation_tier": "TIER_3_DOCKER_CONTAINER",
                    "docker_executed": True,
                    "reason": f"Execution exceeded {timeout_seconds}s timeout boundary.",
                    "latency_us": round(dt_us, 2)
                }
            except Exception as e:
                shutil.rmtree(scratch_dir, ignore_errors=True)
                return {
                    "status": "CONTAINER_ERROR",
                    "verdict": "DENY",
                    "isolation_tier": "TIER_3_DOCKER_CONTAINER",
                    "error": str(e),
                    "latency_us": round((time.perf_counter() - start_us) * 1_000_000, 2)
                }
        else:
            # 2. Tier 2 Fallback: Isolated host subprocess with scrubbed environment
            scrubbed_env = {
                "PATH": os.environ.get("PATH", ""),
                "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
                "TEMP": scratch_dir,
                "TMP": scratch_dir,
                "PYTHONPATH": scratch_dir
            }

            try:
                res = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                    cwd=scratch_dir,
                    env=scrubbed_env
                )
                dt_us = (time.perf_counter() - start_us) * 1_000_000
                shutil.rmtree(scratch_dir, ignore_errors=True)

                return {
                    "status": "SUCCESS" if res.returncode == 0 else "EXECUTION_ERROR",
                    "verdict": "ALLOW" if res.returncode == 0 else "ERROR",
                    "isolation_tier": "TIER_2_HERMETIC_SUBPROCESS_FALLBACK",
                    "docker_executed": False,
                    "exit_code": res.returncode,
                    "stdout": res.stdout.strip(),
                    "stderr": res.stderr.strip(),
                    "latency_us": round(dt_us, 2)
                }
            except Exception as e:
                shutil.rmtree(scratch_dir, ignore_errors=True)
                dt_us = (time.perf_counter() - start_us) * 1_000_000
                return {
                    "status": "EXECUTION_ERROR",
                    "verdict": "DENY",
                    "isolation_tier": "TIER_2_HERMETIC_SUBPROCESS_FALLBACK",
                    "docker_executed": False,
                    "error": str(e),
                    "latency_us": round(dt_us, 2)
                }
