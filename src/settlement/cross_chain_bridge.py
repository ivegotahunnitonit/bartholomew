"""
BTP Multi-Chain Atomic Escrow Bridge Relay.
Coordinates cross-rail atomic locks and voucher redemptions between
Base (EVM), Arbitrum (EVM), and Bitcoin Lightning Network (L402).
"""

import os
import json
import time
import hmac
import hashlib
import secrets
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional, Tuple, List


DEFAULT_BRIDGE_STORE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", ".btp_bridge_ledger.json"
)

BRIDGE_SIGNING_KEY = "btp_bridge_validator_relayer_k902"


@dataclass
class BridgeVoucher:
    voucher_id: str
    source_chain: str
    target_chain: str
    depositor: str
    recipient: str
    amount_usd: float
    lock_hash: str
    deadline_timestamp: float
    status: str = "LOCKED"  # LOCKED, CLAIMED, REFUNDED
    preimage: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    claimed_at: Optional[float] = None
    signature: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def is_expired(self) -> bool:
        return time.time() > self.deadline_timestamp


class CrossChainBridgeRelay:
    """
    Decentralized cross-chain escrow relayer. Coordinates HTLC-style
    hash-locked commitments across EVM L2s and L402 Lightning rails.
    """

    SUPPORTED_RAILS = ["EVM_BASE", "EVM_ARBITRUM", "L402_LIGHTNING"]

    def __init__(self, store_path: Optional[str] = None):
        self.store_path = os.path.abspath(store_path or DEFAULT_BRIDGE_STORE_PATH)
        self.vouchers: Dict[str, BridgeVoucher] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.get("vouchers", {}).items():
                        self.vouchers[k] = BridgeVoucher(**v)
            except Exception:
                pass

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
            with open(self.store_path, "w", encoding="utf-8") as f:
                json.dump({
                    "version": "5.4.0",
                    "vouchers": {k: v.to_dict() for k, v in self.vouchers.items()}
                }, f, indent=2)
        except Exception:
            pass

    def lock_source_escrow(
        self,
        source_chain: str,
        target_chain: str,
        depositor: str,
        recipient: str,
        amount_usd: float,
        secret_preimage: Optional[str] = None,
        ttl_seconds: int = 3600
    ) -> Tuple[bool, str, BridgeVoucher]:
        if source_chain not in self.SUPPORTED_RAILS or target_chain not in self.SUPPORTED_RAILS:
            return False, f"Unsupported bridge rails. Must be one of {self.SUPPORTED_RAILS}", None

        if source_chain == target_chain:
            return False, "Source and target chains must be different.", None

        if amount_usd <= 0:
            return False, "Amount must be greater than 0.", None

        preimage = secret_preimage or secrets.token_hex(32)
        lock_hash = hashlib.sha256(preimage.encode()).hexdigest()

        entropy = f"{source_chain}:{target_chain}:{depositor}:{recipient}:{amount_usd}:{time.time_ns()}"
        voucher_id = f"VOUCHER-{hashlib.sha256(entropy.encode()).hexdigest()[:12].upper()}"
        deadline = time.time() + ttl_seconds

        sign_payload = f"{voucher_id}:{source_chain}:{target_chain}:{amount_usd}:{lock_hash}:{deadline}"
        sig = "btp_bridge_sig_" + hmac.new(BRIDGE_SIGNING_KEY.encode(), sign_payload.encode(), hashlib.sha256).hexdigest()[:32]

        voucher = BridgeVoucher(
            voucher_id=voucher_id,
            source_chain=source_chain,
            target_chain=target_chain,
            depositor=depositor,
            recipient=recipient,
            amount_usd=amount_usd,
            lock_hash=lock_hash,
            deadline_timestamp=deadline,
            status="LOCKED",
            preimage=preimage if secret_preimage is None else None,
            signature=sig
        )

        self.vouchers[voucher_id] = voucher
        self._save()
        return True, "Collateral locked on source chain. Bridge voucher issued.", voucher

    def claim_target_escrow(
        self,
        voucher_id: str,
        secret_preimage: str
    ) -> Tuple[bool, str, Optional[BridgeVoucher]]:
        voucher = self.vouchers.get(voucher_id)
        if not voucher:
            return False, f"Voucher '{voucher_id}' not found in bridge registry.", None

        if voucher.status != "LOCKED":
            return False, f"Voucher is already {voucher.status}.", voucher

        if voucher.is_expired():
            voucher.status = "EXPIRED"
            self._save()
            return False, "Voucher has expired and can no longer be claimed. Eligible for refund.", voucher

        # Verify hash lock
        computed_hash = hashlib.sha256(secret_preimage.encode()).hexdigest()
        if computed_hash != voucher.lock_hash:
            return False, "Invalid secret preimage: hash mismatch.", voucher

        # Atomic claim
        voucher.status = "CLAIMED"
        voucher.preimage = secret_preimage
        voucher.claimed_at = time.time()
        self._save()
        return True, f"Voucher successfully claimed on {voucher.target_chain}. Funds released to {voucher.recipient}.", voucher

    def refund_expired_voucher(self, voucher_id: str) -> Tuple[bool, str, Optional[BridgeVoucher]]:
        voucher = self.vouchers.get(voucher_id)
        if not voucher:
            return False, f"Voucher '{voucher_id}' not found.", None

        if voucher.status == "CLAIMED":
            return False, "Cannot refund an already claimed voucher.", voucher

        if not voucher.is_expired():
            return False, f"Voucher has not yet reached deadline ({int(voucher.deadline_timestamp - time.time())}s remaining).", voucher

        voucher.status = "REFUNDED"
        self._save()
        return True, f"Voucher expired. Collateral of ${voucher.amount_usd:.2f} refunded to {voucher.depositor} on {voucher.source_chain}.", voucher
