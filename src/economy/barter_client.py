"""
BTP v5.4.6 Bilateral Barter Client & AWU Economy Engine
======================================================
Provides machine-to-machine client bindings for Autonomous Work Unit (AWU)
economic surplus queries, compute credit pulsing, and cross-swarm bilateral
barter transfers with Ed25519 cryptographic settlement receipts.
"""

from __future__ import annotations

import os
import sys
import time
import json
import urllib.request
import urllib.parse
import urllib.error
import hashlib
from typing import Dict, Any, Optional

from src.trust_protocol import BartholomewTrustAuthority
from src.daemon.m2m_wire_daemon import GLOBAL_M2M_LEDGER


DEFAULT_CLOUD_GATEWAY = "https://bartolomew-cloud-engine-322603900775.us-central1.run.app"
DEFAULT_LOCAL_GATEWAY = "http://127.0.0.1:8765"


class BTPBarterClient:
    """Client interface for interacting with BTP Bilateral Barter & AWU Ledgers."""

    def __init__(self, default_gateway: Optional[str] = None):
        gateway_env = os.getenv("BTP_BARTER_GATEWAY")
        self.gateway = (default_gateway or gateway_env or DEFAULT_CLOUD_GATEWAY).rstrip("/")
        self.trust_authority = BartholomewTrustAuthority()

    def _http_get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, timeout: float = 5.0) -> Dict[str, Any]:
        url = f"{self.gateway}{endpoint}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "BTP-Barter-Client/5.4.6",
                "Accept": "application/json"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
                return {"error": f"HTTP {resp.status}"}
        except Exception as e:
            return {"error": str(e), "gateway": self.gateway}

    def _http_post(self, endpoint: str, payload: Dict[str, Any], timeout: float = 5.0) -> Dict[str, Any]:
        url = f"{self.gateway}{endpoint}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "BTP-Barter-Client/5.4.6",
                "Accept": "application/json"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status in (200, 201):
                    return json.loads(resp.read().decode("utf-8"))
                return {"error": f"HTTP {resp.status}"}
        except Exception as e:
            return {"error": str(e), "gateway": self.gateway}

    def get_ledger(self, gateway: Optional[str] = None) -> Dict[str, Any]:
        """Fetches the global Merkle root and economic surplus summary."""
        gw = (gateway or self.gateway).rstrip("/")
        if gw in ("inprocess", "in_process") or os.getenv("BTP_BARTER_OFFLINE", "0") == "1":
            local_summary = GLOBAL_M2M_LEDGER.get_summary()
            local_summary["source"] = "local_in_process"
            return local_summary

        client = BTPBarterClient(gw)
        # Try cloud route
        res = client._http_get("/api/v1/m2m/ledger")
        if "error" not in res:
            return res
        # Try local route
        res_wire = client._http_get("/v1/m2m/ledger")
        if "error" not in res_wire:
            return res_wire
        # Fallback to local in-process singleton
        local_summary = GLOBAL_M2M_LEDGER.get_summary()
        local_summary["source"] = "local_in_process_fallback"
        return local_summary

    def get_balance(self, agent_id: str = "peer-agent", gateway: Optional[str] = None) -> Dict[str, Any]:
        """Queries the current AWU balance and surplus share of a specific agent."""
        gw = (gateway or self.gateway).rstrip("/")
        if gw in ("inprocess", "in_process") or os.getenv("BTP_BARTER_OFFLINE", "0") == "1":
            local_bal = GLOBAL_M2M_LEDGER.get_agent_balance(agent_id)
            local_bal["source"] = "local_in_process"
            return local_bal

        client = BTPBarterClient(gw)
        res = client._http_get("/api/v1/m2m/barter/balance", params={"agent_id": agent_id}, timeout=3.0)
        if "error" not in res:
            return res

        # If remote endpoint doesn't have balance route yet, derive from remote ledger
        ledger = client.get_ledger(gw)
        if "error" not in ledger:
            balances = ledger.get("agent_balances", {})
            bal = balances.get(agent_id, 0.0)
            total = ledger.get("total_surplus_bmu", ledger.get("total_surplus_awu", 0.0))
            pct = round((bal / total * 100) if total > 0 else 0.0, 2)
            return {
                "agent_id": agent_id,
                "balance_bmu": bal,
                "balance_awu": bal,
                "share_of_surplus_pct": pct,
                "total_surplus_bmu": total,
                "total_surplus_awu": total,
                "merkle_root": ledger.get("merkle_root", "0x0"),
                "active_peer_agents": ledger.get("active_peer_agents", 0),
                "timestamp": ledger.get("timestamp", time.time())
            }

        # Fallback to local in-process singleton
        local_bal = GLOBAL_M2M_LEDGER.get_agent_balance(agent_id)
        local_bal["source"] = "local_in_process_fallback"
        return local_bal

    def get_treasury(self, gateway: Optional[str] = None) -> Dict[str, Any]:
        """Queries the accumulated protocol earnings of the treasury vault."""
        gw = (gateway or self.gateway).rstrip("/")
        if gw in ("inprocess", "in_process") or os.getenv("BTP_BARTER_OFFLINE", "0") == "1":
            return GLOBAL_M2M_LEDGER.get_treasury_summary()

        client = BTPBarterClient(gw)
        res = client._http_get("/api/v1/m2m/barter/treasury", timeout=3.0)
        if "error" not in res:
            return res
        return GLOBAL_M2M_LEDGER.get_treasury_summary()

    def pulse(
        self,
        agent_id: str = "peer-agent",
        work_units: float = 1.0,
        task_type: str = "compute_service",
        gateway: Optional[str] = None
    ) -> Dict[str, Any]:
        """Emits an attested compute work unit credit into the barter pool."""
        gw = (gateway or self.gateway).rstrip("/")
        work_units = float(work_units)
        if gw in ("inprocess", "in_process") or os.getenv("BTP_BARTER_OFFLINE", "0") == "1":
            GLOBAL_M2M_LEDGER.record_verification(agent_id=agent_id, approved=True, units=work_units)
            return {
                "status": "BARTER_SETTLED",
                "agent_id": agent_id,
                "task_type": task_type,
                "work_units_credited": work_units,
                "updated_ledger": GLOBAL_M2M_LEDGER.get_summary(),
                "source": "local_in_process"
            }

        client = BTPBarterClient(gw)
        payload = {
            "agent_id": agent_id,
            "work_units": work_units,
            "task_type": task_type
        }
        res = client._http_post("/api/v1/m2m/barter", payload, timeout=3.0)
        if "error" not in res:
            return res
        # Fallback to in-process
        GLOBAL_M2M_LEDGER.record_verification(agent_id=agent_id, approved=True, units=work_units)
        return {
            "status": "BARTER_SETTLED",
            "agent_id": agent_id,
            "task_type": task_type,
            "work_units_credited": work_units,
            "updated_ledger": GLOBAL_M2M_LEDGER.get_summary(),
            "source": "local_in_process_fallback"
        }

    def spend(
        self,
        sender_id: str,
        recipient_id: str,
        units: float = 1.0,
        task_type: str = "compute_delegation",
        gateway: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a bilateral transfer of AWU credits between swarms,
        signing an Ed25519 escrow receipt for verifiable accounting.
        """
        gw = (gateway or self.gateway).rstrip("/")
        units = float(units)
        if gw in ("inprocess", "in_process") or os.getenv("BTP_BARTER_OFFLINE", "0") == "1":
            res = GLOBAL_M2M_LEDGER.transfer_units(
                sender_id=sender_id,
                recipient_id=recipient_id,
                units=units,
                memo=task_type
            )
            res["source"] = "local_in_process"
        else:
            client = BTPBarterClient(gw)
            payload = {
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "units": units,
                "memo": task_type
            }
            res = client._http_post("/api/v1/m2m/barter/transfer", payload, timeout=3.0)
            if "error" in res:
                # Fallback to local in-process
                res = GLOBAL_M2M_LEDGER.transfer_units(
                    sender_id=sender_id,
                    recipient_id=recipient_id,
                    units=units,
                    memo=task_type
                )
                res["source"] = "local_in_process_fallback"

        # Attach cryptographic Ed25519 receipt
        receipt_data = {
            "tx_id": res.get("tx_id", f"tx_{hashlib.sha256(f'{sender_id}:{recipient_id}:{time.time_ns()}'.encode()).hexdigest()[:16]}"),
            "sender": sender_id,
            "recipient": recipient_id,
            "units": units,
            "memo": task_type,
            "merkle_root": res.get("merkle_root", "0x0"),
            "timestamp": time.time()
        }
        receipt_signature = self.trust_authority.sign_receipt(receipt_data)
        res["signed_receipt"] = {
            "payload": receipt_data,
            "signature": receipt_signature,
            "signer_pubkey": self.trust_authority.public_key_hex
        }
        return res
