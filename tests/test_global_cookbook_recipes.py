"""
Test Suite for the Universal Global Cookbook Recipes
====================================================
Tests that all recipes across Category 1 (Already Built), Category 2 (Being Built),
and Category 3 (Future Swarms) execute with 100% verified outcomes.
"""

import pytest

# Category 1: Already Built
from examples.already_built.http_sidecar_proxy import main as run_sidecar_proxy
from examples.already_built.cli_process_gate import main as run_cli_gate

# Category 2: Being Built Right Now
from examples.being_built.openai_tool_calling_guard import main as run_openai_guard
from examples.being_built.anthropic_computer_use_guard import main as run_anthropic_guard
from examples.being_built.gemini_function_calling_guard import main as run_gemini_guard

# Category 3: Future Autonomous Swarms
from examples.future_swarms.sovereign_agent_passport_mesh import main as run_passport_mesh
from examples.future_swarms.zk_privacy_auditing import main as run_zk_auditing
from examples.future_swarms.confidential_enclave_anchor import main as run_enclave_anchor
from examples.future_swarms.l402_autonomous_escrow import main as run_l402_escrow
from examples.container_defense.docker_agent_guard import main as run_docker_defense


def test_category_1_already_built_recipes():
    """Verify recipes for legacy/already-built agents."""
    assert run_sidecar_proxy() is True
    assert run_cli_gate() is True


def test_category_2_being_built_recipes():
    """Verify recipes for direct LLM SDKs being built right now."""
    assert run_openai_guard() is True
    assert run_anthropic_guard() is True
    assert run_gemini_guard() is True


def test_category_3_future_swarms_recipes():
    """Verify recipes for future-proof autonomous swarms and cryptographic mesh."""
    assert run_passport_mesh() is True
    assert run_zk_auditing() is True
    assert run_enclave_anchor() is True
    assert run_l402_escrow() is True
    assert run_docker_defense() is True
