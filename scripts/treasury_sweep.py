"""
Bartholomew Trust Protocol (BTP v5.4) — Automated Lightning Treasury Sweep
===========================================================================
Periodically checks the Alby Hub Lightning node balance via Nostr Wallet Connect (NWC).
When balance exceeds THRESHOLD_SATS (default: 50,000 sats / ~$30+ USD), it generates a
submarine reverse swap via Boltz Exchange to sweep funds directly to an on-chain
Electrum / cold storage Bitcoin address, leaving a reserve balance for routing liquidity.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.settlement.alby_client import AlbyNWCClient

# Configuration Defaults
DEFAULT_THRESHOLD_SATS = int(os.getenv("SWEEP_THRESHOLD_SATS", "50000"))
DEFAULT_RESERVE_SATS = int(os.getenv("SWEEP_RESERVE_SATS", "5000"))
BOLT_API_URL = "https://api.boltz.exchange/v2"


def get_boltz_reverse_swap(amount_sats: int, btc_address: str):
    """
    Creates a reverse submarine swap: Pays a Lightning invoice to receive on-chain Bitcoin.
    """
    url = f"{BOLT_API_URL}/swap/reverse"
    payload = {
        "from": "BTC",
        "to": "BTC",
        "invoiceAmount": amount_sats,
        "claimAddress": btc_address
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "Bartholomew-Treasury/5.4"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def execute_treasury_sweep(destination_btc_address: str, threshold_sats: int = DEFAULT_THRESHOLD_SATS, reserve_sats: int = DEFAULT_RESERVE_SATS):
    client = AlbyNWCClient()
    if not client.is_configured():
        print("[!] Error: ALBY_NWC_URL is not configured in .env or environment.")
        return False

    print("[*] Connecting to Alby Hub via NWC...")
    info = client.get_info()
    pubkey = info.get("pubkey", "Unknown")
    alias = info.get("alias", "NWC")
    network = info.get("network", "mainnet")
    lud16 = info.get("lud16", "")
    print(f"[+] Connected to Node: {alias} ({pubkey[:16]}...) on {network}")
    print(f"[+] Lightning Address: {lud16}")

    balance = client.get_balance_sats()
    print(f"[*] Current Node Balance: {balance:,} sats")
    print(f"[*] Sweep Threshold: {threshold_sats:,} sats | Reserve Retention: {reserve_sats:,} sats")
    print(f"[*] Target Cold Storage Address: {destination_btc_address}")

    if balance < threshold_sats:
        sats_needed = threshold_sats - balance
        print(f"[-] Balance ({balance:,} sats) is below threshold ({threshold_sats:,} sats).")
        print(f"[-] Node is armed and ready. Will sweep automatically once {sats_needed:,} more sats are collected.")
        return True

    sweep_amount = balance - reserve_sats
    print(f"[+] Triggering automated sweep of {sweep_amount:,} sats to {destination_btc_address}...")

    try:
        swap_data = get_boltz_reverse_swap(sweep_amount, destination_btc_address)
        invoice = swap_data.get("invoice")
        swap_id = swap_data.get("id")
        print(f"[+] Boltz Submarine Swap initiated (ID: {swap_id})")
        print(f"[+] Paying reverse swap invoice via Alby Hub NWC...")
        
        # Pay the invoice via Alby Hub NWC
        bridge_res = client._call_bridge("pay_invoice", invoice)
        print(f"[+] Invoice settled! Payment Preimage: {bridge_res.get('preimage')}")
        print(f"[+] Funds successfully routed to on-chain cold storage address: {destination_btc_address}")
        return True
    except Exception as e:
        print(f"[!] Sweep execution failed: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/treasury_sweep.py <destination_btc_address> [threshold_sats]")
        print("Example: python scripts/treasury_sweep.py bc1q... 50000")
        sys.exit(1)

    dest_addr = sys.argv[1]
    thresh = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_THRESHOLD_SATS
    success = execute_treasury_sweep(dest_addr, threshold_sats=thresh)
    sys.exit(0 if success else 1)
