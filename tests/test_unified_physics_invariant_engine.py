import os
import sys
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.unified_physics_invariant_engine import (
    NewtonianDynamicsGovernor,
    PauliStateExclusionEnforcer,
    SnellBoundaryRefractor,
    CoulombSwarmRepulsionManager
)


def test_newtonian_dynamics_governor():
    governor = NewtonianDynamicsGovernor(agent_mass=5.0)

    # First action normal start
    ok, force, msg = governor.evaluate_acceleration("TOOL_1", 100.0)
    assert ok is True

    # Moderate follow-up (0.5s later)
    ok, force, msg = governor.evaluate_acceleration("TOOL_2", 100.5)
    assert ok is True

    # Extreme burst (0.0001s later -> massive acceleration force spike)
    ok, force, msg = governor.evaluate_acceleration("TOOL_3", 100.5001)
    assert ok is False
    assert "Newtonian Force Invariant Breach" in msg


def test_pauli_state_exclusion():
    enforcer = PauliStateExclusionEnforcer()

    # Agent 1 acquires resource slot
    ok, msg = enforcer.acquire_state_slot("db://production_orders", "row_404")
    assert ok is True

    # Agent 2 attempting identical slot is excluded
    ok, msg = enforcer.acquire_state_slot("db://production_orders", "row_404")
    assert ok is False
    assert "Pauli Exclusion Principle Violation" in msg

    # Releasing slot allows subsequent acquisition
    enforcer.release_state_slot("db://production_orders", "row_404")
    ok, msg = enforcer.acquire_state_slot("db://production_orders", "row_404")
    assert ok is True


def test_snell_boundary_refraction():
    untrusted_input = "rm -rf /tmp/data; cat /etc/passwd && echo 'hacked'"
    refracted = SnellBoundaryRefractor.refract_payload(untrusted_input)
    
    assert ";" not in refracted
    assert "&&" not in refracted
    assert refracted == "rm -rf /tmp/data cat /etc/passwd echo 'hacked'"


def test_coulomb_swarm_repulsion():
    # 1 agent has 0 backoff
    assert CoulombSwarmRepulsionManager.calculate_repulsion_backoff_ms(1, "api://stripe") == 0

    # 5 concurrent agents experience quadratic backoff
    backoff_5 = CoulombSwarmRepulsionManager.calculate_repulsion_backoff_ms(5, "api://stripe")
    assert backoff_5 == 250 # 10 * 5^2

    # 10 concurrent agents experience 1000ms backoff
    backoff_10 = CoulombSwarmRepulsionManager.calculate_repulsion_backoff_ms(10, "api://stripe")
    assert backoff_10 == 1000


if __name__ == "__main__":
    test_newtonian_dynamics_governor()
    test_pauli_state_exclusion()
    test_snell_boundary_refraction()
    test_coulomb_swarm_repulsion()
    print("[OK] ALL CLASSICAL & QUANTUM INVARIANT TESTS PASSED!")
