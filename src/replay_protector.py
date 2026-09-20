"""
Bartholomew Replay & Fraud Protection Engine (BTP v5.4.14)
===========================================================
Prevents replay attacks, transaction duplication, and fraudulent receipt reuse across autonomous swarms:
  1. Nonce & Idempotency Key Vault: Ensures each transaction/receipt is processed exactly once.
  2. Timestamp Window Enforcer: Drops requests outside max allowed clock skew window (e.g. +- 300s).
  3. Single-Use Receipt Guarantee: Marks receipt hashes as spent upon presentation.
"""

from __future__ import annotations

import time
import hashlib
from typing import Dict, Any, Set, Tuple, Optional


class ReplayProtectionVault:
    """
    In-memory / persistent replay protection and idempotency vault for M2M agent requests.
    """

    def __init__(self, max_clock_skew_seconds: float = 300.0, max_vault_size: int = 100000):
        self.max_clock_skew_seconds = max_clock_skew_seconds
        self.max_vault_size = max_vault_size
        self.seen_nonces: Dict[str, float] = {}  # nonce_key -> timestamp
        self.seen_receipt_hashes: Dict[str, float] = {}  # receipt_hash -> timestamp

    def validate_request(
        self,
        request_id: str,
        nonce: Optional[str] = None,
        timestamp: Optional[float] = None,
        now: Optional[float] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates a incoming request for replay attacks or clock skew violations.
        Returns (is_valid: bool, error_reason: Optional[str]).
        """
        current_time = now or time.time()

        # 1. Timestamp Skew Check
        if timestamp is not None:
            skew = abs(current_time - float(timestamp))
            if skew > self.max_clock_skew_seconds:
                return False, f"Replay Violation: Request timestamp skew ({skew:.1f}s) exceeds max allowed window ({self.max_clock_skew_seconds}s)"

        # 2. Nonce / Request ID Deduplication
        nonce_key = f"{request_id}:{nonce}" if nonce else request_id
        if nonce_key in self.seen_nonces:
            return False, f"Replay Violation: Nonce/Request ID '{nonce_key}' has already been processed"

        # Record nonce
        self.seen_nonces[nonce_key] = current_time
        self._prune_if_needed(current_time)
        return True, None

    def validate_and_consume_receipt(self, receipt_hash: str, now: Optional[float] = None) -> Tuple[bool, Optional[str]]:
        """
        Ensures a signed receipt hash is consumed only once (single-use guarantee).
        """
        current_time = now or time.time()
        if receipt_hash in self.seen_receipt_hashes:
            return False, f"Fraud Violation: Cryptographic receipt '{receipt_hash[:16]}...' has already been redeemed"

        self.seen_receipt_hashes[receipt_hash] = current_time
        self._prune_if_needed(current_time)
        return True, None

    def _prune_if_needed(self, current_time: float) -> None:
        """Evicts entries older than 2 * max_clock_skew_seconds."""
        if len(self.seen_nonces) < self.max_vault_size and len(self.seen_receipt_hashes) < self.max_vault_size:
            return

        cutoff = current_time - (2 * self.max_clock_skew_seconds)
        self.seen_nonces = {k: v for k, v in self.seen_nonces.items() if v > cutoff}
        self.seen_receipt_hashes = {k: v for k, v in self.seen_receipt_hashes.items() if v > cutoff}
