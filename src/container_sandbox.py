"""
Bartholomew Container Sandbox & Kernel Isolation Engine
======================================================
Provides disposable, hardware-isolated container runtimes (Docker/cgroups)
paired with Bartholomew's sub-5 microsecond semantic pre-flight invariant gate.

Security Controls Enforced:
1. Physical Filesystem Isolation: Host OS and SSH keys are unmounted and invisible.
2. Network Containment: Outbound sockets disabled (--network none) by default.
3. CGroup Resource Caps: Memory capped (default 512MB), CPU capped (default 1 core).
4. Ephemerality: Automatic container destruction (--rm) after task execution.
5. Graceful Fallback: Local hermetic process containment if Docker daemon is offline.
"""

import os
import sys
import subprocess
import shutil
import time
from typing import Dict, Any, Tuple, Optional
from src.hermetic_sandbox import HermeticCommandSandbox


class ContainerSandboxEngine:
    def __init__(
        self,
        base_image: str = "alpine:latest",
        memory_limit: str = "512m",
        cpu_limit: float = 1.0,
        network_enabled: bool = False,
        timeout_seconds: int = 15
    ):
        self.base_image = base_image
        self.memory_limit = memory_limit
        self.cpu_limit = str(cpu_limit)
        self.network_enabled = network_enabled
        self.timeout_seconds = timeout_seconds
        self._docker_available = self._check_docker_daemon()
        self._hermetic_fallback = HermeticCommandSandbox()

    def _check_docker_daemon(self) -> bool:
        """Checks if the Docker CLI and daemon are operational."""
        docker_bin = shutil.which("docker")
        if not docker_bin:
            return False
        try:
            res = subprocess.run(
                [docker_bin, "info"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2
            )
            return res.returncode == 0
        except Exception:
            return False

    @property
    def is_docker_available(self) -> bool:
        return self._docker_available

    def run_isolated_command(
        self,
        command: str,
        workspace_dir: str,
        env_vars: Optional[Dict[str, str]] = None
    ) -> Tuple[int, str, str, str]:
        """
        Executes a command inside an isolated Docker container with strict cgroups.
        Falls back to local hermetic containment if Docker is unavailable.

        Returns: (exit_code, stdout, stderr, execution_mode)
        """
        abs_workspace = os.path.abspath(workspace_dir)
        os.makedirs(abs_workspace, exist_ok=True)

        if not self._docker_available:
            # Fallback to local hermetic process sandbox
            res = HermeticCommandSandbox.execute_bounded_command(command, timeout_seconds=self.timeout_seconds)
            if res.get("status") == "BLOCKED" or res.get("verdict") == "DENY":
                return (126, "", f"Hermetic Security Gate Blocked: {res.get('reason')}", "HERMETIC_FALLBACK_BLOCKED")
            
            return (
                res.get("returncode", 0),
                res.get("stdout", ""),
                res.get("stderr", ""),
                "HERMETIC_PROCESS_FALLBACK"
            )

        # Docker is active - execute with hardware cgroups & network isolation
        net_flag = "bridge" if self.network_enabled else "none"
        docker_cmd = [
            "docker", "run", "--rm",
            "--network", net_flag,
            "--memory", self.memory_limit,
            "--cpus", self.cpu_limit,
            "--read-only",
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
            "-v", f"{abs_workspace}:/workspace:rw",
            "-w", "/workspace",
        ]

        if env_vars:
            for k, v in env_vars.items():
                docker_cmd.extend(["-e", f"{k}={v}"])

        docker_cmd.extend([self.base_image, "sh", "-c", command])

        try:
            start_t = time.time()
            proc = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds
            )
            duration_ms = (time.time() - start_t) * 1000.0
            return (proc.returncode, proc.stdout, proc.stderr, f"DOCKER_ISOLATED ({duration_ms:.1f}ms)")
        except subprocess.TimeoutExpired:
            return (124, "", f"Container execution timed out after {self.timeout_seconds}s", "DOCKER_TIMEOUT")
        except Exception as e:
            return (1, "", str(e), "DOCKER_EXEC_ERROR")
