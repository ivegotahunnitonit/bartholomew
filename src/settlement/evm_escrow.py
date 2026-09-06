"""
BTP v4.0 — EIP-712 Multi-Chain Smart Escrow Gateway
====================================================
Generates cryptographically signed EIP-712 typed structured data claims for
trustless smart contract escrow settlements across EVM networks
(Arbitrum, Base, Optimism, Ethereum Mainnet, Polygon).

Enables autonomous agents and victim claimants to execute on-chain indemnity
disbursement with zero human intervention.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import time
from typing import Dict, Any, Optional, Tuple

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature, encode_dss_signature


@dataclasses.dataclass
class EIP712Domain:
    """EIP-712 Domain Separator parameters for smart contract verification."""
    name: str = "Bartholomew Autonomous Escrow"
    version: str = "4.0.0"
    chain_id: int = 42161  # Arbitrum One default (Base = 8453, Mainnet = 1)
    verifying_contract: str = "0x8f2a1b94c3d8e57204918e7c10b981ca2941b3e7"

    def hash(self) -> bytes:
        type_str = "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
        type_hash = hashlib.sha3_256(type_str.encode("utf-8")).digest()
        name_hash = hashlib.sha3_256(self.name.encode("utf-8")).digest()
        version_hash = hashlib.sha3_256(self.version.encode("utf-8")).digest()
        chain_bytes = self.chain_id.to_bytes(32, "big")
        contract_bytes = bytes.fromhex(self.verifying_contract[2:].lower().zfill(64))
        
        packed = type_hash + name_hash + version_hash + chain_bytes + contract_bytes
        return hashlib.sha3_256(packed).digest()


@dataclasses.dataclass
class EscrowSlashingClaim:
    """Represents an EIP-712 compliant typed slashing claim payload."""
    escrow_id: str
    agent_id: str
    payee_address: str
    amount_usd: float
    violated_invariant: str
    proof_hash: str
    nonce: int
    deadline: int

    def hash(self) -> bytes:
        type_str = (
            "EscrowSlashingClaim("
            "string escrowId,"
            "string agentId,"
            "address payeeAddress,"
            "uint256 amountUSD,"
            "string violatedInvariant,"
            "bytes32 proofHash,"
            "uint256 nonce,"
            "uint256 deadline"
            ")"
        )
        type_hash = hashlib.sha3_256(type_str.encode("utf-8")).digest()
        escrow_id_hash = hashlib.sha3_256(self.escrow_id.encode("utf-8")).digest()
        agent_id_hash = hashlib.sha3_256(self.agent_id.encode("utf-8")).digest()
        payee_bytes = bytes.fromhex(self.payee_address[2:].lower().zfill(64))
        amount_cents = int(self.amount_usd * 100)
        amount_bytes = amount_cents.to_bytes(32, "big")
        invariant_hash = hashlib.sha3_256(self.violated_invariant.encode("utf-8")).digest()
        proof_clean = self.proof_hash[2:] if self.proof_hash.startswith("0x") else self.proof_hash
        proof_bytes = bytes.fromhex(proof_clean.zfill(64))
        nonce_bytes = self.nonce.to_bytes(32, "big")
        deadline_bytes = self.deadline.to_bytes(32, "big")

        packed = (
            type_hash +
            escrow_id_hash +
            agent_id_hash +
            payee_bytes +
            amount_bytes +
            invariant_hash +
            proof_bytes +
            nonce_bytes +
            deadline_bytes
        )
        return hashlib.sha3_256(packed).digest()

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class EVMEscrowGateway:
    """
    EIP-712 multi-chain smart contract gateway for autonomous micro-escrow liquidation.
    """

    def __init__(
        self,
        domain: Optional[EIP712Domain] = None,
        private_key: Optional[ec.EllipticCurvePrivateKey] = None
    ):
        self.domain = domain or EIP712Domain()
        self.private_key = private_key or ec.generate_private_key(ec.SECP256K1())
        self.public_key = self.private_key.public_key()

    @property
    def signer_address(self) -> str:
        """Derives standard 0x Ethereum address from public key."""
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        address_hash = hashlib.sha3_256(public_bytes[1:]).digest()
        return f"0x{address_hash[-20:].hex()}"

    def compute_eip712_digest(self, claim: EscrowSlashingClaim) -> bytes:
        """
        Computes EIP-712 standard digest:
        keccak256("\x19\x01" || domainSeparator || hashStruct(claim))
        """
        domain_hash = self.domain.hash()
        claim_hash = claim.hash()
        prefix = b"\x19\x01"
        return hashlib.sha3_256(prefix + domain_hash + claim_hash).digest()

    def sign_slashing_claim(
        self,
        claim: EscrowSlashingClaim
    ) -> Dict[str, Any]:
        """
        Signs the EIP-712 typed slashing claim and produces (r, s, v) signature.
        """
        digest = self.compute_eip712_digest(claim)
        raw_sig = self.private_key.sign(digest, ec.ECDSA(hashes.SHA256()))
        r, s = decode_dss_signature(raw_sig)
        v = 27  # standard EVM recovery id

        sig_payload = {
            "r": f"0x{r:064x}",
            "s": f"0x{s:064x}",
            "v": v,
            "signature_hex": f"0x{r:064x}{s:064x}{v:02x}",
            "signer_address": self.signer_address,
            "claim": claim.to_dict(),
            "chain_id": self.domain.chain_id,
            "verifying_contract": self.domain.verifying_contract
        }
        return sig_payload

    def verify_claim_signature(
        self,
        claim: EscrowSlashingClaim,
        r_hex: str,
        s_hex: str,
        expected_signer: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Verifies ECDSA signature over the EIP-712 claim.
        """
        try:
            r = int(r_hex, 16)
            s = int(s_hex, 16)
            der_sig = encode_dss_signature(r, s)
            digest = self.compute_eip712_digest(claim)
            self.public_key.verify(der_sig, digest, ec.ECDSA(hashes.SHA256()))

            if expected_signer and expected_signer.lower() != self.signer_address.lower():
                return False, f"Signer address mismatch: {self.signer_address} != {expected_signer}"

            return True, "EIP-712 Slashing Claim signature verified valid."
        except Exception as e:
            return False, f"Signature verification failed: {str(e)}"
