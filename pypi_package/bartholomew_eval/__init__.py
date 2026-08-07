"""
bartholomew_eval
================
Sub-millisecond AI agent trajectory security for Python.

1-line install:
    pip install bartholomew-eval

1-line usage:
    from bartholomew_eval import guard

    @guard()
    def my_agent_step(prompt: str) -> str:
        return agent.run(prompt)
"""
from .guard import guard, GuardViolation
from .engine import BartholomewEngine
from .fuzzer import TrajectoryFuzzer, fuzzer_instance
from .cli import main

__version__ = "1.0.0"
__author__ = "Itsub Solomon Alemayehu"
__all__ = ["guard", "GuardViolation", "BartholomewEngine", "TrajectoryFuzzer", "fuzzer_instance", "main"]

