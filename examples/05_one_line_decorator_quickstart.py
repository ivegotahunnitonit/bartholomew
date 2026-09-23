"""
Bartholomew Cookbook 05: 1-Line Decorator Quickstart (@secure_tool)
===================================================================
The simplest way to protect any Python function, LLM tool, or agent callable.

Run:
    python examples/05_one_line_decorator_quickstart.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from btp_guard import secure_tool, SecurityVetoException

# Simply add @secure_tool to ANY tool function:
@secure_tool
def run_bash(cmd: str):
    return f"Running: {cmd}"

# 1. Safe command
print(run_bash("ls -la"))

# 2. Blocked command (sub-35µs in-process veto)
try:
    run_bash("rm -rf /")
except SecurityVetoException as e:
    print("Intercepted safely by Bartholomew:")
    print(e)
