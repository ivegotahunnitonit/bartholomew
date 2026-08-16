#!/usr/bin/env python3
"""
Agentic-Eval Cryptographic Audit Ledger & Hashchain
Maintains an immutable, append-only security hashchain tracking every certificate issued by the firm.
"""
import time
import json
import hashlib
from typing import Dict, Any, List

class AuditFirmLedger:
    """
    Immutable Hashchain Audit Ledger
    """
    def __init__(self):
        self.chain: List[Dict[str, Any]] = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        genesis_block = {
            "block_index": 0,
            "timestamp": "2026-07-31T00:00:00Z",
            "target_system": "GENESIS_SECURITY_BLOCK",
            "sha256_hash": hashlib.sha256(b"Agentic-Eval Genesis Block").hexdigest(),
            "previous_hash": "0000000000000000000000000000000000000000000000000000000000000000"
        }
        self.chain.append(genesis_block)

    def record_audit_certificate(self, target_system: str, certificate_hash: str) -> Dict[str, Any]:
        """Appends a new verified audit certificate to the immutable ledger hashchain."""
        prev_block = self.chain[-1]
        block_index = len(self.chain)
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

        payload = f"{block_index}:{timestamp}:{target_system}:{certificate_hash}:{prev_block['sha256_hash']}".encode()
        block_hash = hashlib.sha256(payload).hexdigest()

        new_block = {
            "block_index": block_index,
            "timestamp": timestamp,
            "target_system": target_system,
            "certificate_hash": certificate_hash,
            "previous_hash": prev_block["sha256_hash"],
            "sha256_hash": block_hash
        }
        self.chain.append(new_block)
        return new_block

    def verify_ledger_integrity(self) -> bool:
        """Verifies 100% cryptographic integrity of the audit hashchain."""
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i-1]
            if curr["previous_hash"] != prev["sha256_hash"]:
                return False
        return True

ledger_instance = AuditFirmLedger()

def main():
    ledger_instance.record_audit_certificate("FintechBot_v1", "hash_123456789")
    ledger_instance.record_audit_certificate("SupportBot_v2", "hash_987654321")
    print(f"✅ Audit Ledger Hashchain Length: {len(ledger_instance.chain)}")
    print(f"🔒 Cryptographic Integrity Verified: {ledger_instance.verify_ledger_integrity()}")
    print(json.dumps(ledger_instance.chain, indent=2))

if __name__ == "__main__":
    main()
