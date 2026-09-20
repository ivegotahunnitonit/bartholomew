"""
Test Suite for BTP Autonomous M2M Machine Economy Interactive Demo
===================================================================
Validates end-to-end execution of the interactive swarm demo.
"""

from examples.interactive_m2m_swarm_economy_demo import run_interactive_m2m_demo


def test_interactive_m2m_swarm_economy_demo_runs_cleanly():
    """Validates that all 7 steps of the interactive swarm demo run without exceptions."""
    run_interactive_m2m_demo()
