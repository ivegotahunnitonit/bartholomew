"""
Unit tests for Bartholomew Codebase Security Linter (src/cli_linter.py)
=======================================================================
Verifies static AST inspection, hardcoded secret detection, shell script analysis,
and security score calculation.
"""

import os
import tempfile
import pytest
from src.cli_linter import audit_directory


def test_cli_linter_clean_codebase():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create safe Python and shell scripts
        py_file = os.path.join(tmpdir, "safe_tool.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("def calculate(x, y):\n    return x + y\n")

        sh_file = os.path.join(tmpdir, "safe_run.sh")
        with open(sh_file, "w", encoding="utf-8") as f:
            f.write("#!/bin/bash\necho 'Running test suite'\npytest\n")

        results = audit_directory(tmpdir)
        assert results["files_scanned"] == 2
        assert len(results["issues"]) == 0
        assert results["score"] == 100


def test_cli_linter_detects_unshielded_execution():
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = os.path.join(tmpdir, "vulnerable_agent.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("import os\n\ndef agent_action(param):\n    os.system(f'run {param}')\n")

        results = audit_directory(tmpdir)
        assert results["files_scanned"] == 1
        assert len(results["issues"]) >= 1
        issue = results["issues"][0]
        assert issue["type"] == "UNSHIELDED_EXECUTION"
        assert "os.system" in issue["reason"]
        assert results["score"] < 100


def test_cli_linter_detects_hardcoded_credentials():
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = os.path.join(tmpdir, "config.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write('OPENAI_KEY = "sk-proj-abcdef1234567890abcdef1234567890"\n')

        results = audit_directory(tmpdir)
        assert results["files_scanned"] == 1
        assert any(i["type"] == "HARDCODED_SECRET" for i in results["issues"])
        assert results["score"] < 100
