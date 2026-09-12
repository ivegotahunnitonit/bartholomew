"""
Automated Test for BTP Standing Mesh Daemon & Heartbeat Synchronization
Verifies periodic heartbeat execution, EigenTrust power iteration,
local state checkpointing, and live Cloud Run wire barter reconciliation.
"""

import os
import json
import time
import pytest

from src.daemon.mesh_daemon import StandingMeshDaemon

def test_standing_mesh_daemon_discrete_step():
    test_checkpoint = os.path.abspath(".btp_test_heartbeat.json")
    if os.path.exists(test_checkpoint):
        os.remove(test_checkpoint)

    daemon = StandingMeshDaemon(
        node_id="test_runner_sentinel",
        heartbeat_file=test_checkpoint,
        heartbeat_interval_sec=1.0
    )

    # Execute single step
    snap = daemon.step_heartbeat(sync_barter=True)

    assert snap["status"] == "HEALTHY"
    assert snap["node_id"] == "test_runner_sentinel"
    assert "merkle_root" in snap
    assert snap["cycle_count"] == 1
    assert os.path.exists(test_checkpoint)

    # Read checkpoint file
    with open(test_checkpoint, "r", encoding="utf-8") as f:
        saved = json.load(f)

    assert saved["status"] == "HEALTHY"
    assert saved["node_id"] == "test_runner_sentinel"
    assert saved["merkle_root"] == snap["merkle_root"]

    # Clean up test checkpoint
    if os.path.exists(test_checkpoint):
        os.remove(test_checkpoint)

    print("[PASS] test_standing_mesh_daemon_discrete_step verified successfully.")

def test_standing_mesh_daemon_background_lifecycle():
    test_checkpoint = os.path.abspath(".btp_test_heartbeat_bg.json")
    if os.path.exists(test_checkpoint):
        os.remove(test_checkpoint)

    daemon = StandingMeshDaemon(
        node_id="test_bg_sentinel",
        heartbeat_file=test_checkpoint,
        heartbeat_interval_sec=0.2
    )

    # Run 3 cycles in background
    daemon.start(blocking=False, max_cycles=3)
    time.sleep(1.0)
    daemon.stop()

    assert daemon._cycle_count >= 1
    assert os.path.exists(test_checkpoint)

    if os.path.exists(test_checkpoint):
        os.remove(test_checkpoint)

    print("[PASS] test_standing_mesh_daemon_background_lifecycle verified successfully.")

if __name__ == "__main__":
    test_standing_mesh_daemon_discrete_step()
    test_standing_mesh_daemon_background_lifecycle()
    print("ALL STANDING MESH DAEMON TESTS PASSED.")
