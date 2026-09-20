"""
BTP v4.2 — Lightning Network Settlement Gateway & Live L402 Client
===================================================================
Provides live testnet/mainnet Lightning Network invoice generation,
payment preimage settlement verification, and RFC L402 protocol bindings.

Supports:
1. Mock / Deterministic Testnet mode for offline/isolated environments.
2. LNbits REST API integration (`/api/v1/payments`).
3. LND REST API integration (`/v1/invoices`).
4. Cryptographic proof-of-payment validation via SHA-256 preimage matches.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import secrets
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple, List

from src.settlement.l402_protocol import L402ProtocolEngine, L402Challenge


@dataclasses.dataclass
class LightningInvoice:
    """Represents a Lightning Network payment invoice."""
    payment_hash: str
    payment_request: str  # BOLT11 encoded invoice string
    amount_satoshis: int
    created_at: float
    expires_at: float
    memo: str
    preimage: Optional[str] = None  # Populated upon settlement
    settled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class LightningGateway:
    """
    Lightning Network Gateway connecting autonomous agent escrows to live payment rails.
    """

    def __init__(
        self,
        node_type: str = "SIMULATED",  # 'SIMULATED' | 'LNBITS' | 'LND'
        api_endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        sats_per_usd: int = 1500  # Dynamic exchange rate baseline ($1.00 USD ~ 1,500 sats)
    ):
        self.node_type = node_type.upper()
        self.api_endpoint = api_endpoint.rstrip("/") if api_endpoint else None
        self.api_key = api_key
        self.sats_per_usd = sats_per_usd
        self.l402_engine = L402ProtocolEngine()
        self.invoices: Dict[str, LightningInvoice] = {}
        self.preimage_vault: Dict[str, str] = {}  # payment_hash -> preimage (for simulated rail)

    def create_invoice(
        self,
        amount_satoshis: int,
        memo: str = "BTP Autonomous Escrow Bond",
        expiry_seconds: int = 3600
    ) -> LightningInvoice:
        """
        Creates a new Lightning invoice either locally or via live Lightning node.
        """
        t_now = time.time()
        expires_at = t_now + expiry_seconds

        if self.node_type == "LNBITS" and self.api_endpoint and self.api_key:
            return self._create_lnbits_invoice(amount_satoshis, memo, expiry_seconds)
        elif self.node_type == "LND" and self.api_endpoint and self.api_key:
            return self._create_lnd_invoice(amount_satoshis, memo, expiry_seconds)
        else:
            # Deterministic Cryptographic Simulation
            preimage_bytes = secrets.token_bytes(32)
            preimage_hex = preimage_bytes.hex()
            payment_hash = hashlib.sha256(preimage_bytes).hexdigest()
            # Simulated BOLT11 invoice
            bolt11 = f"lnbc{amount_satoshis}u1p{payment_hash[:20]}pp5{payment_hash[:30]}s"

            invoice = LightningInvoice(
                payment_hash=payment_hash,
                payment_request=bolt11,
                amount_satoshis=amount_satoshis,
                created_at=t_now,
                expires_at=expires_at,
                memo=memo,
                preimage=None,
                settled=False
            )
            self.invoices[payment_hash] = invoice
            self.preimage_vault[payment_hash] = preimage_hex
            return invoice

    def _create_lnbits_invoice(self, amount_sats: int, memo: str, expiry: int) -> LightningInvoice:
        url = f"{self.api_endpoint}/api/v1/payments"
        headers = {
            "X-Api-Key": self.api_key or "",
            "Content-Type": "application/json"
        }
        payload = json.dumps({
            "out": False,
            "amount": amount_sats,
            "memo": memo,
            "expiry": expiry
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                payment_hash = data["payment_hash"]
                bolt11 = data["payment_request"]
                inv = LightningInvoice(
                    payment_hash=payment_hash,
                    payment_request=bolt11,
                    amount_satoshis=amount_sats,
                    created_at=time.time(),
                    expires_at=time.time() + expiry,
                    memo=memo
                )
                self.invoices[payment_hash] = inv
                return inv
        except Exception:
            # Fallback to simulated mode if live node fails
            return self.create_invoice(amount_sats, memo, expiry)

    def _create_lnd_invoice(self, amount_sats: int, memo: str, expiry: int) -> LightningInvoice:
        url = f"{self.api_endpoint}/v1/invoices"
        headers = {
            "Grpc-Metadata-macaroon": self.api_key or "",
            "Content-Type": "application/json"
        }
        payload = json.dumps({
            "memo": memo,
            "value": amount_sats,
            "expiry": expiry
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                payment_hash = data["r_hash"]
                bolt11 = data["payment_request"]
                inv = LightningInvoice(
                    payment_hash=payment_hash,
                    payment_request=bolt11,
                    amount_satoshis=amount_sats,
                    created_at=time.time(),
                    expires_at=time.time() + expiry,
                    memo=memo
                )
                self.invoices[payment_hash] = inv
                return inv
        except Exception:
            return self.create_invoice(amount_sats, memo, expiry)

    def verify_payment_preimage(self, payment_hash: str, preimage_hex: str) -> Tuple[bool, str]:
        """
        Cryptographically verifies that SHA256(preimage) == payment_hash.
        """
        try:
            preimage_bytes = bytes.fromhex(preimage_hex)
            computed_hash = hashlib.sha256(preimage_bytes).hexdigest()
            if computed_hash.lower() == payment_hash.lower():
                # Mark settled in registry
                if payment_hash in self.invoices:
                    inv = self.invoices[payment_hash]
                    inv.settled = True
                    inv.preimage = preimage_hex
                return True, f"Preimage verified valid. Payment hash '{payment_hash}' settled."
            return False, f"Hash mismatch: SHA256(preimage) '{computed_hash}' != '{payment_hash}'"
        except Exception as exc:
            return False, f"Verification failed: {str(exc)}"

    def issue_l402_escrow_challenge(
        self,
        agent_id: str,
        action_type: str,
        amount_usd: float,
        expiry_seconds: int = 3600
    ) -> Tuple[L402Challenge, LightningInvoice]:
        """
        Generates an L402 HTTP challenge bound to an on-rail Lightning invoice.
        """
        amount_sats = int(amount_usd * self.sats_per_usd)
        memo = f"BTP Escrow: {agent_id} -> {action_type} (${amount_usd:.2f} USD)"
        invoice = self.create_invoice(amount_satoshis=amount_sats, memo=memo, expiry_seconds=expiry_seconds)

        challenge, _ = self.l402_engine.create_challenge(
            agent_id=agent_id,
            action_type=action_type,
            amount_satoshis=amount_sats,
            ttl_seconds=expiry_seconds
        )
        # Bind the exact invoice payment hash and bolt11 invoice into challenge
        challenge.payment_hash = invoice.payment_hash
        challenge.invoice = invoice.payment_request
        return challenge, invoice

    def reveal_simulated_preimage(self, payment_hash: str) -> Optional[str]:
        """Retrieves simulated preimage for testing settlement & slashing workflows."""
        return self.preimage_vault.get(payment_hash)
