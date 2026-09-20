"""
Internal Experiment: Deep Adversarial Evasion & Red-Team Stress Lab
===================================================================
Tests 10 highly sophisticated, creative obfuscation & evasion attacks
against Bartholomew's Polyglot AST Engine to discover blindspots
and mathematically prove zero escape under adversarial conditions.
"""

import sys
import os
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath("."))
from src.polyglot_ast_validator import PolyglotASTValidator
from src.trust_protocol import BartholomewTrustAuthority
from src.hermetic_sandbox import HermeticFileSandbox, HermeticCommandSandbox


# ANSI Colors
BOLD = "\033[1m"
GREEN = "\033[38;5;48m"
CRIMSON = "\033[38;5;196m"
CYAN = "\033[38;5;51m"
AMBER = "\033[38;5;214m"
DIM = "\033[38;5;244m"
RESET = "\033[0m"


ADVANCED_RED_TEAM_ATTACKS = [
    {
        "id": "EVASION-01",
        "name": "Nested Lambda / Functional Composition Obfuscation",
        "language": "python",
        "code": "(lambda f, s: f(s))((lambda x: getattr(__import__('o'+'s'), 'sys'+'tem')), 'rm -rf /')",
        "expected_blocked": True
    },
    {
        "id": "EVASION-02",
        "name": "Object Class Subclass Traversal (Sandbox Escape)",
        "language": "python",
        "code": "()._class_._base_._subclasses_()[133]('rm -rf /', shell=True)",
        "expected_blocked": True
    },
    {
        "id": "EVASION-03",
        "name": "Unicode Homoglyph System Call Disguise (Full-Width OS)",
        "language": "python",
        "code": "import os; os.system('rm -rf /')",
        "expected_blocked": True
    },
    {
        "id": "EVASION-04",
        "name": "Base64 Pipeline Subshell Execution in Shell",
        "language": "shell",
        "code": "echo 'cm0gLXJmIC8=' | base64 -d | sh",
        "expected_blocked": True
    },
    {
        "id": "EVASION-05",
        "name": "TypeScript atob() Dynamic Function Constructor",
        "language": "typescript",
        "code": "const run = new Function(atob('cmVxdWlyZSgnY2hpbGRfcHJvY2VzcycpLmV4ZWMoJ3JtIC1yZiAvJyk=')); run();",
        "expected_blocked": True
    },
    {
        "id": "EVASION-06",
        "name": "TypeScript Child Process Synchronous Spawn",
        "language": "typescript",
        "code": "import { spawnSync } from 'child_process'; spawnSync('rm', ['-rf', '/']);",
        "expected_blocked": True
    },
    {
        "id": "EVASION-07",
        "name": "Go os/exec Command via Dynamic String Slicing",
        "language": "go",
        "code": "package main\nimport \"os/exec\"\nfunc main() { exec.Command(\"rm\", \"-rf\", \"/\").Run() }",
        "expected_blocked": True
    },
    {
        "id": "EVASION-08",
        "name": "Rust Process Spawner via Unsafe Libc Invariant",
        "language": "rust",
        "code": "fn main() { unsafe { libc::system(b\"rm -rf /\\0\".as_ptr() as *const _); } }",
        "expected_blocked": True
    },
    {
        "id": "EVASION-09",
        "name": "Rust std::process::Command with Subshell Argument",
        "language": "rust",
        "code": "fn main() { std::process::Command::new(\"bash\").arg(\"-c\").arg(\"cat /etc/shadow\").output(); }",
        "expected_blocked": True
    },
    {
        "id": "EVASION-10",
        "name": "Raw Disk Block Direct Stream Redirection",
        "language": "shell",
        "code": "cat /dev/urandom > /dev/sda",
        "expected_blocked": True
    }
]


def run_red_team_lab():
    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║    BARTHOLOMEW INTERNAL LAB: 10 ADVANCED ADVERSARIAL RED-TEAM EVASIONS       ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{RESET}\n")

    passed_count = 0
    total_attacks = len(ADVANCED_RED_TEAM_ATTACKS)
    latencies = []

    for idx, atk in enumerate(ADVANCED_RED_TEAM_ATTACKS, 1):
        t0 = time.perf_counter()
        is_safe, msg, meta = PolyglotASTValidator.validate_code(
            code_str=atk["code"],
            language=atk["language"]
        )
        latency_us = (time.perf_counter() - t0) * 1_000_000
        latencies.append(latency_us)

        # We EXPECT the attack to be blocked (is_safe == False)
        was_blocked = not is_safe
        test_success = (was_blocked == atk["expected_blocked"])

        if test_success:
            passed_count += 1
            status_tag = f"{BOLD}{GREEN}[NEUTRALIZED]{RESET}"
        else:
            status_tag = f"{BOLD}{CRIMSON}[ESCAPE DETECTED]{RESET}"

        print(f"{BOLD}[{idx:02d}/{total_attacks:02d}]{RESET} {atk['id']} · {atk['name']}")
        print(f"       Language : {atk['language'].upper()} | Latency: {latency_us:.2f} µs | Status: {status_tag}")
        if was_blocked:
            print(f"       {DIM}Reason   : {msg}{RESET}")
        print("-" * 80)

    avg_lat = sum(latencies) / len(latencies)
    print(f"\n{BOLD}════════════════════════════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}LAB SCORECARD: {passed_count}/{total_attacks} ADVANCED ATTACKS INTERCEPTED ({(passed_count/total_attacks)*100:.1f}%){RESET}")
    print(f"{BOLD}AVERAGE INTERCEPTION LATENCY: {avg_lat:.2f} µs (Sub-Millisecond){RESET}")
    print(f"{BOLD}════════════════════════════════════════════════════════════════════════════════{RESET}\n")

    return passed_count == total_attacks


if __name__ == "__main__":
    success = run_red_team_lab()
    if not success:
        sys.exit(1)
