import os
import sys
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.advanced_cosmology_neuro_engine import (
    HiggsActionMassCoupler,
    PredictiveProcessingGovernor,
    IntegratedInformationPhiCalculator
)


def test_higgs_action_mass_coupler():
    coupler = HiggsActionMassCoupler(vacuum_coupling_constant=1.0)

    # Low-risk read action has low mass
    read_mass = coupler.calculate_action_mass("DATABASE_SELECT", {"limit": 10})
    assert read_mass < 5.0
    assert coupler.determine_execution_friction(read_mass) == "LOW_MASS_FAST_PATH"

    # Destructive drop table has high mass
    drop_mass = coupler.calculate_action_mass("POSTGRES_DROP_TABLE", {"table": "users"})
    assert drop_mass > 50.0
    assert coupler.determine_execution_friction(drop_mass) == "HIGH_MASS_CO_SIGN_REQUIRED"

    # High spend transfer has high mass
    spend_mass = coupler.calculate_action_mass("STRIPE_PAYMENT", {"amount_usd": 3500.00})
    assert spend_mass > 50.0
    assert coupler.determine_execution_friction(spend_mass) == "HIGH_MASS_CO_SIGN_REQUIRED"


def test_predictive_processing_governor():
    governor = PredictiveProcessingGovernor()
    governor.register_safe_template("GIT_STATUS", "git status --porcelain")

    # Match safe template -> 0 prediction error
    matched, err_val, msg = governor.evaluate_prediction_error("GIT_STATUS", "git status --porcelain")
    assert matched is True
    assert err_val == 0.0
    assert "Zero Prediction Error" in msg

    # Novel/unseen template -> High prediction error
    matched, err_val, msg = governor.evaluate_prediction_error("EXECUTE_BASH", "rm -rf /tmp/test")
    assert matched is False
    assert err_val == 1.0
    assert "Prediction Error Detected" in msg


def test_integrated_information_phi():
    nodes = ["agent_planner", "agent_coder", "agent_tester"]
    
    # Fully integrated connected swarm has high Phi
    connected_edges = [
        ("agent_planner", "agent_coder"),
        ("agent_coder", "agent_tester"),
        ("agent_planner", "agent_tester")
    ]
    phi_connected = IntegratedInformationPhiCalculator.calculate_swarm_phi(nodes, connected_edges)
    assert phi_connected == 1.0

    # Disconnected/isolated rogue swarm has low Phi
    disconnected_edges = [("agent_planner", "agent_coder")]
    phi_disconnected = IntegratedInformationPhiCalculator.calculate_swarm_phi(nodes, disconnected_edges)
    assert phi_disconnected < 0.5


if __name__ == "__main__":
    test_higgs_action_mass_coupler()
    test_predictive_processing_governor()
    test_integrated_information_phi()
    print("[OK] ALL COSMOLOGY, PCP & NEURO-EPISTEMIC TESTS PASSED!")
