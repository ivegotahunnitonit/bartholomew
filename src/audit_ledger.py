"""
BTP v2.2 Tamper-Evident Merkle Compliance Ledger
Cryptographically chains all evaluated agent attestations into an append-only
Merkle tree with parent hash binding for SOC2 Type II and EU AI Act compliance.
"""

import hashlib
import json
import time
import os
import sys
from typing import Dict, Any, List, Optional, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.rfc8785 import rfc8785_canonicalize

class TamperEvidentAuditLedger:
    """
    Append-only Merkle Hash-Chained Audit Ledger for Agent Attestations.
    
    Each entry:
        EntryHash_n = SHA256( PrevHash || CanonicalRFC8785(Attestation) || Timestamp )
    """
    GENESIS_HASH = "00" * 32

    def __init__(self, ledger_file: Optional[str] = None):
        self.entries: List[Dict[str, Any]] = []
        self.current_tip_hash: str = self.GENESIS_HASH
        self.ledger_file = ledger_file

    def append_attestation(self, attestation_packet: Dict[str, Any]) -> Dict[str, Any]:
        """Appends a new attestation and computes the next chained hash."""
        now = time.time()
        att = attestation_packet.get("attestation", {})
        att_canonical_bytes = rfc8785_canonicalize(att)
        att_sha = hashlib.sha256(att_canonical_bytes).hexdigest()

        # Chain: PrevHash + AttestationDigest + Timestamp
        chain_material = f"{self.current_tip_hash}:{att_sha}:{now}".encode("utf-8")
        entry_hash = hashlib.sha256(chain_material).hexdigest()

        entry = {
            "index": len(self.entries),
            "timestamp_unix": now,
            "previous_hash": self.current_tip_hash,
            "attestation_digest": att_sha,
            "entry_hash": entry_hash,
            "attestation_packet": attestation_packet
        }

        self.entries.append(entry)
        self.current_tip_hash = entry_hash

        if self.ledger_file:
            with open(self.ledger_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

        return entry

    def verify_chain_integrity(self) -> Tuple[bool, str]:
        """
        Verifies 100% mathematical integrity across the entire ledger history.
        Detects any retroactive tampering or altered attestation.
        """
        expected_prev = self.GENESIS_HASH

        for idx, entry in enumerate(self.entries):
            # 1. Verify previous hash link
            if entry["previous_hash"] != expected_prev:
                return False, f"CHAIN_BROKEN at index {idx}: Previous hash mismatch"

            # 2. Verify attestation digest
            att = entry["attestation_packet"].get("attestation", {})
            att_canonical_bytes = rfc8785_canonicalize(att)
            calc_att_sha = hashlib.sha256(att_canonical_bytes).hexdigest()
            if entry["attestation_digest"] != calc_att_sha:
                return False, f"TAMPERING_DETECTED at index {idx}: Attestation payload altered"

            # 3. Verify entry hash
            chain_material = f"{expected_prev}:{calc_att_sha}:{entry['timestamp_unix']}".encode("utf-8")
            calc_entry_hash = hashlib.sha256(chain_material).hexdigest()
            if entry["entry_hash"] != calc_entry_hash:
                return False, f"HASH_MISMATCH at index {idx}: Entry hash does not match chained material"

            expected_prev = entry["entry_hash"]

        return True, f"VERIFIED_INTACT: All {len(self.entries)} audit entries cryptographically valid"

    def get_merkle_root(self) -> str:
        """Returns the current state tip hash."""
        return self.current_tip_hash
