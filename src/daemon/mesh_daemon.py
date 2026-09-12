"""
BTP v5.4.6 Standing Mesh Daemon & Automated Liveness Heartbeat
=============================================================
Autonomous background mesh agent maintaining continuous peer reputation gossip,
bilateral barter settlements (AWU), and Merkle state synchronization against
the Bartholomew public cloud engine and decentralized peer swarms.
"""

import os
import sys
import time
import json
import threading
from typing import Dict, Any, Optional

from src.p2p.reputation_gossip import PeerReputationMesh, PeerNode
from src.daemon.m2m_observer import M2MTelemetryObserver

DEFAULT_GATEWAY = "https://bartolomew-cloud-engine-322603900775.us-central1.run.app"
DEFAULT_HEARTBEAT_FILE = os.path.abspath(".btp_mesh_heartbeat.json")


class StandingMeshDaemon:
    """
    Autonomous mesh supervisor executing continuous background liveness heartbeats,
    EigenTrust convergence, and wire-level barter settlement.
    """

    def __init__(
        self,
        node_id: str = "node_local_sentinel",
        gateway_url: Optional[str] = None,
        heartbeat_interval_sec: float = 10.0,
        heartbeat_file: str = DEFAULT_HEARTBEAT_FILE
    ):
        self.node_id = node_id
        self.gateway_url = gateway_url or os.getenv("BTP_WIRE_GATEWAY", DEFAULT_GATEWAY)
        self.heartbeat_interval_sec = heartbeat_interval_sec
        self.heartbeat_file = heartbeat_file

        self.mesh = PeerReputationMesh()
        if self.node_id not in self.mesh.peers:
            self.mesh.peers[self.node_id] = PeerNode(
                node_id=self.node_id,
                address="p2p://localhost:8443",
                direct_trust=0.99,
                global_trust=0.99,
                is_pretrusted=True
            )
        self.observer = M2MTelemetryObserver(gateway_url=self.gateway_url)

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._start_time = 0.0
        self._cycle_count = 0

    def record_heartbeat_snapshot(self, ledger_summary: Dict[str, Any], eigentrust_scores: Dict[str, float]) -> Dict[str, Any]:
        """Saves an atomic JSON snapshot of the local and remote mesh state."""
        uptime = time.time() - self._start_time if self._start_time > 0 else 0.0
        snapshot = {
            "node_id": self.node_id,
            "gateway_url": self.gateway_url,
            "status": "HEALTHY",
            "cycle_count": self._cycle_count,
            "uptime_seconds": round(uptime, 2),
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "merkle_root": ledger_summary.get("merkle_root", "0x0000"),
            "verified_calls_count": ledger_summary.get("verified_calls_count", 0),
            "vetoed_calls_count": ledger_summary.get("vetoed_calls_count", 0),
            "total_surplus_awu": ledger_summary.get("total_surplus_awu", 0.0),
            "active_peer_agents": ledger_summary.get("active_peer_agents", 0),
            "eigentrust_vector": {k: round(v, 4) for k, v in eigentrust_scores.items()}
        }

        try:
            temp_path = f"{self.heartbeat_file}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2)
            if os.path.exists(self.heartbeat_file):
                os.remove(self.heartbeat_file)
            os.rename(temp_path, self.heartbeat_file)
        except Exception as e:
            print(f"[!] Warning: Failed to write heartbeat snapshot: {e}", file=sys.stderr)

        return snapshot

    def step_heartbeat(self, sync_barter: bool = True) -> Dict[str, Any]:
        """Executes a single discrete heartbeat and peer reputation convergence cycle."""
        self._cycle_count += 1
        ts = time.strftime("%H:%M:%S")

        # 1. Fetch remote ledger state
        ledger = self.observer.fetch_ledger_summary()

        # 2. Local EigenTrust power iteration
        eigentrust = self.mesh.compute_eigentrust()

        # 3. Optional Barter Settlement Sync to Public Wire
        barter_res = {}
        if sync_barter and "error" not in ledger:
            # Sync periodic baseline barter delta (e.g. 0.5 AWU for heartbeat audit)
            barter_res = self.mesh.sync_to_m2m_wire(
                agent_id=self.node_id,
                work_units=0.5,
                task_type="standing_heartbeat"
            )

        # 4. Record atomic state checkpoint
        snapshot = self.record_heartbeat_snapshot(ledger, eigentrust)
        snapshot["barter_sync"] = barter_res

        return snapshot

    def run_loop(self, max_cycles: Optional[int] = None):
        """Continuous execution loop."""
        self._running = True
        self._start_time = time.time()
        print("=" * 76)
        print("BTP v5.4.6 STANDING MESH DAEMON ACTIVE")
        print("=" * 76)
        print(f"[*] Local Node ID      : {self.node_id}")
        print(f"[*] Gateway URL        : {self.gateway_url}")
        print(f"[*] Heartbeat Interval : {self.heartbeat_interval_sec}s")
        print(f"[*] State Checkpoint   : {self.heartbeat_file}")
        print("=" * 76)

        try:
            while self._running:
                snap = self.step_heartbeat(sync_barter=True)
                ts = time.strftime("%H:%M:%S")
                print(f"[{ts}] Heartbeat #{snap['cycle_count']:04d} | Root: {snap['merkle_root'][:18]}.. | Surplus: {snap['total_surplus_awu']:.1f} AWU | Peers: {snap['active_peer_agents']}")

                if max_cycles and self._cycle_count >= max_cycles:
                    break

                time.sleep(self.heartbeat_interval_sec)
        except KeyboardInterrupt:
            print("\n[*] Standing mesh daemon detached cleanly.")
        finally:
            self._running = False

    def start(self, blocking: bool = True, max_cycles: Optional[int] = None):
        """Starts daemon either synchronously or as a background daemon thread."""
        if blocking:
            self.run_loop(max_cycles=max_cycles)
        else:
            self._running = True
            self._start_time = time.time()
            self._thread = threading.Thread(target=self.run_loop, kwargs={"max_cycles": max_cycles}, daemon=True)
            self._thread.start()

    def stop(self):
        """Signals daemon to halt."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
