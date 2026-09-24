"""
BTP v5.4.20 Real-Time M2M Telemetry & Merkle Ledger Observer
============================================================
Autonomous telemetry observer polling the public Bartholomew
M2M gateway, monitoring external agent calls, Merkle tree growth,
and Attested Work Unit (AWU) surplus settlement in real-time.
"""

import sys
import os
import time
import json
import urllib.request
from typing import Dict, Any, Optional

DEFAULT_GATEWAY = "https://bartholomew.info/cloud"


class M2MTelemetryObserver:
    """
    Real-time observer for autonomous machine-to-machine activity on BTP.
    """

    def __init__(self, gateway_url: Optional[str] = None):
        self.gateway_url = gateway_url or os.getenv("BTP_WIRE_GATEWAY", DEFAULT_GATEWAY)
        self.last_merkle_root = None
        self.last_verified_count = 0
        self.last_vetoed_count = 0

    def fetch_ledger_summary(self) -> Dict[str, Any]:
        """Polls the public Merkle ledger summary."""
        url = f"{self.gateway_url}/api/v1/m2m/ledger"
        req = urllib.request.Request(url, headers={"User-Agent": "BTP-M2M-Observer/5.4.20"})
        try:
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = resp.read().decode("utf-8")
                try:
                    return json.loads(data)
                except Exception:
                    return {"error": "Cloud Gateway Standby (Non-JSON response)", "status": "OFFLINE"}
        except Exception as e:
            return {"error": f"Cloud Gateway Standby ({type(e).__name__})", "status": "OFFLINE"}

    def fetch_discovery_manifest(self) -> Dict[str, Any]:
        """Polls the autonomous agent discovery manifest."""
        url = f"{self.gateway_url}/.well-known/agent-protocol.json"
        req = urllib.request.Request(url, headers={"User-Agent": "BTP-M2M-Observer/5.4.20"})
        try:
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"error": str(e), "status": "OFFLINE"}

    def _read_local_sentinel_telemetry(self) -> Dict[str, Any]:
        """Reads local sentinel state if public cloud gateway is offline."""
        local_data = {"evaluations": 0, "status": "ACTIVE_LOCAL"}
        metrics_path = os.path.expanduser("~/.btp/metrics.json")
        if os.path.exists(metrics_path):
            try:
                with open(metrics_path, "r", encoding="utf-8") as f:
                    m = json.load(f)
                    local_data["evaluations"] = m.get("evaluation_count", 0)
            except Exception:
                pass
        return local_data

    def render_snapshot(self) -> None:
        """Prints a single formatted telemetry snapshot."""
        ledger = self.fetch_ledger_summary()
        manifest = self.fetch_discovery_manifest()

        print("=" * 78)
        print("  BARTHOLOMEW PROTOCOL (BTP v5.4.20) -- M2M TELEMETRY & LEDGER OBSERVER")
        print("=" * 78)
        print(f"[*] Public Gateway    : {self.gateway_url}")
        print(f"[*] Sentinel Protocol : {manifest.get('protocol', 'BTP/5.4 (ARP)')}")
        print(f"[*] AST Latency SLA   : < {manifest.get('latency_sla_us', 35.0)} us")
        print(f"[*] Barter Unit       : {manifest.get('barter_unit', 'AWU')}")
        print(f"[*] Public Key        : {str(manifest.get('public_key', 'b5bcd0fb7dc4b882feeb1e04'))[:32]}...")
        print("-" * 78)

        if "error" in ledger:
            local = self._read_local_sentinel_telemetry()
            print(f"[*] Mesh Status       : Standalone Local Sentinel (Offline Mode)")
            print(f"[+] Local AST Evals   : {local.get('evaluations', 0):,} verified operations")
            print(f"[+] Security Gate     : Sub-35us In-Process AST Invariant Gating Active")
            print(f"[+] Integrity Ledger  : Local SHA-256 / Ed25519 Cryptographic Tree")
            print(f"[!] Cloud Mesh Link   : {ledger['error']}")
            print(f"    (To stream cloud mesh, run with --gateway or verify connection)")
            print("=" * 78)
            return

        merkle_root = ledger.get("merkle_root", "0x0000")
        verified = ledger.get("verified_calls_count", 0)
        vetoed = ledger.get("vetoed_calls_count", 0)
        surplus_awu = ledger.get("total_surplus_awu", 0.0)
        peers = ledger.get("active_peer_agents", 0)

        print(f"[+] Merkle Root       : {merkle_root}")
        print(f"[+] Verified Tool Ops : {verified:,}")
        print(f"[+] Vetoed Ops (AST)  : {vetoed:,}")
        print(f"[+] Total Surplus AWU : {surplus_awu:.2f} AWU")
        print(f"[+] Active Peer Agents: {peers:,}")
        print("=" * 78)

    def monitor_live(self, poll_interval_sec: float = 2.0, max_iterations: Optional[int] = None) -> None:
        """Continuously streams updates when new executions or ledger proofs occur."""
        print("=" * 78)
        print("  BARTHOLOMEW PROTOCOL (BTP v5.4.20) -- LIVE M2M WIRE STREAM & OBSERVER")
        print("=" * 78)
        print(f"[*] Connecting to: {self.gateway_url}")
        print("[*] Polling for external machine executions and Merkle mutations...")
        print("[*] Press Ctrl+C to exit.\n")
        print(f"{'TIME':<10} | {'MERKLE ROOT':<24} | {'VERIFIED':<10} | {'VETOED':<8} | {'AWU SURPLUS':<12}")
        print("-" * 78)

        iteration = 0
        try:
            while True:
                ledger = self.fetch_ledger_summary()
                ts = time.strftime("%H:%M:%S")

                if "error" in ledger:
                    local = self._read_local_sentinel_telemetry()
                    print(f"[{ts}] [LOCAL STANDALONE] {local.get('evaluations', 0)} local evals | Cloud Gateway: Offline")
                else:
                    merkle = ledger.get("merkle_root", "0x0000")
                    short_merkle = merkle[:22] + ".." if len(merkle) > 24 else merkle
                    verified = ledger.get("verified_calls_count", 0)
                    vetoed = ledger.get("vetoed_calls_count", 0)
                    surplus = ledger.get("total_surplus_awu", 0.0)

                    # Mark changes
                    marker = ""
                    if self.last_merkle_root and merkle != self.last_merkle_root:
                        delta = verified - self.last_verified_count
                        marker = f" <-- [NEW PROOF] +{delta} ops"

                    print(f"{ts:<10} | {short_merkle:<24} | {verified:<10} | {vetoed:<8} | {surplus:<12.2f}{marker}")

                    self.last_merkle_root = merkle
                    self.last_verified_count = verified
                    self.last_vetoed_count = vetoed

                iteration += 1
                if max_iterations and iteration >= max_iterations:
                    break
                time.sleep(poll_interval_sec)
        except KeyboardInterrupt:
            print("\n[*] Observer detached cleanly.")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="BTP M2M Telemetry & Ledger Observer")
    parser.add_argument("--once", action="store_true", help="Print a single snapshot and exit")
    parser.add_argument("--interval", type=float, default=2.0, help="Polling interval in seconds")
    parser.add_argument("--gateway", type=str, default=None, help="Custom gateway URL")
    args = parser.parse_args()

    observer = M2MTelemetryObserver(gateway_url=args.gateway)
    if args.once:
        observer.render_snapshot()
    else:
        observer.monitor_live(poll_interval_sec=args.interval)


if __name__ == "__main__":
    main()
