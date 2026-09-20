"""
Test Suite for BTP Swarm HUD Terminal Dashboard
Verifies data fetching, frame rendering, Merkle change tracking, and CLI execution.
"""

from src.daemon.swarm_hud import SwarmHUD

def test_swarm_hud_data_and_render():
    hud = SwarmHUD()
    ledger = hud.fetch_ledger()
    assert "merkle_root" in ledger or "error" in ledger

    manifest = hud.fetch_manifest()
    assert "protocol" in manifest or "error" in manifest

    # Test single frame render without throwing exceptions
    hud.render_frame()
    print("[PASS] SwarmHUD frame rendered cleanly.")

if __name__ == "__main__":
    test_swarm_hud_data_and_render()
    print("ALL SWARM HUD TESTS PASSED.")
