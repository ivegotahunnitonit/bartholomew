"""
BTP v4.0 — Alby Hub NWC Client
==============================
Interfaces directly with self-custodial Alby Hub nodes via Nostr Wallet Connect (NIP-47).
Allows Bartholomew to mint live Lightning Network invoices for L402 paywalls and check
incoming settlement status without local bitcoind/LND daemon overhead.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


class AlbyNWCClient:
    """Python client for Alby Hub over Nostr Wallet Connect (NWC)."""

    def __init__(self, nwc_url: Optional[str] = None):
        # Automatically load from root .env if not in environment
        root_dir = Path(__file__).resolve().parent.parent.parent
        self.bridge_path = root_dir / "packages" / "node" / "src" / "nwc_bridge.mjs"

        if not nwc_url and not os.getenv("ALBY_NWC_URL"):
            env_file = root_dir / ".env"
            if env_file.exists():
                try:
                    with open(env_file, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("ALBY_NWC_URL="):
                                os.environ["ALBY_NWC_URL"] = line.split("=", 1)[1].strip().strip('"').strip("'")
                                break
                except Exception:
                    pass

        self.nwc_url = nwc_url or os.getenv("ALBY_NWC_URL")

    def is_configured(self) -> bool:
        return bool(self.nwc_url)

    def _call_bridge(self, action: str, *args: str) -> Dict[str, Any]:
        if not self.is_configured():
            raise ValueError("ALBY_NWC_URL is not configured.")

        cmd = ["node", str(self.bridge_path), action, self.nwc_url] + list(args)
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if proc.returncode != 0:
            err_msg = proc.stderr.strip() or proc.stdout.strip()
            raise RuntimeError(f"Alby NWC bridge error: {err_msg}")

        try:
            return json.loads(proc.stdout.strip())
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON from Alby NWC bridge: {proc.stdout.strip()}") from e

    def get_info(self) -> Dict[str, Any]:
        """Returns node metadata, supported methods, pubkey, and network info."""
        return self._call_bridge("info")

    def get_balance_sats(self) -> int:
        """Returns current spendable lightning balance in satoshis."""
        res = self._call_bridge("balance")
        # Alby NWC balance returns { balance: <millisats> }
        msats = res.get("balance", 0)
        return msats // 1000

    def make_invoice(self, amount_sats: int, description: str = "Bartholomew AST Gate") -> Dict[str, Any]:
        """
        Creates a real Lightning Network invoice (bolt11).
        Returns {'invoice': bolt11_string, 'payment_hash': hex_string}
        """
        return self._call_bridge("invoice", str(amount_sats), description)

    def lookup_invoice(self, payment_hash: str) -> Dict[str, Any]:
        """
        Queries whether the specified payment hash has settled.
        Returns invoice status dict (e.g. {'settled_at': ..., 'preimage': ...}).
        """
        return self._call_bridge("lookup", payment_hash)
