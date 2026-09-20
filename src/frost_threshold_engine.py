"""
BTP v3.1.0 — FROST RFC 9591 Threshold Signature Engine
========================================================
Flexible Round-Optimized Schnorr Threshold Signatures for autonomous agent swarms.

Implements a (t, n) threshold scheme where any t+1 of n agents can co-sign
a high-stakes action, producing a single valid Schnorr signature verifiable
against the swarm's group public key — with zero trust in any coordinator.

Protocol: FROST (RFC 9591), 2-round variant
  Round 1: Each signer broadcasts nonce commitments (D_i, E_i)
  Round 2: Each signer computes partial signature z_i using Lagrange coefficients
  Aggregate: σ = (R, z) — a standard Schnorr signature on the group key

References:
  - RFC 9591: The Flexible Round-Optimized Schnorr Threshold (FROST) Protocol
  - Komlo & Goldberg (2020): FROST: Flexible Round-Optimized Schnorr Threshold Signatures
  - Nick, Ruffing, Seurin (2021): MuSig2 — Multisignatures from Schnorr (for comparison)
  - NIST MPTS 2026: FaFROST and Gargos adaptive extensions

Group: 1024-bit MODP (RFC 3526), same as BTP zk_compliance_proof_engine
       Generator g=2, prime p (safe prime), subgroup order q = (p-1)/2
"""

from __future__ import annotations

import dataclasses
import hashlib
import secrets
from typing import Optional

# ---------------------------------------------------------------------------
# Re-use the same group parameters as the zk_compliance_proof_engine
# so all BTP crypto lives in the same finite field.
# ---------------------------------------------------------------------------

# 1024-bit MODP Group 2 prime (RFC 3526 §2)
_P = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381"
    "FFFFFFFFFFFFFFFF",
    16,
)
_Q = (_P - 1) // 2   # Safe-prime subgroup order
_G = 2               # Generator (order q in Z*_p)


# ---------------------------------------------------------------------------
# Utility: Modular inverse via Fermat's little theorem (q is prime)
# ---------------------------------------------------------------------------

def _modinv(a: int, m: int) -> int:
    """Compute a^{-1} mod m (m must be prime)."""
    return pow(a, m - 2, m)


# ---------------------------------------------------------------------------
# Hash helpers (FROST uses domain-separated hashes per RFC 9591 §4)
# ---------------------------------------------------------------------------

def _H1(msg: bytes) -> int:
    """H1 — Schnorr challenge hash. e = H1(R || Y || msg) mod q."""
    tag = b"BTP/FROST/v3.1.0/challenge"
    digest = hashlib.sha256(tag + msg).digest()
    return int.from_bytes(digest, "big") % _Q


def _H2(msg: bytes) -> int:
    """H2 — Binding factor hash. ρ_i = H2('rho' || i || msg || B) mod q."""
    tag = b"BTP/FROST/v3.1.0/binding"
    digest = hashlib.sha256(tag + msg).digest()
    return int.from_bytes(digest, "big") % _Q


def _H3(msg: bytes) -> int:
    """H3 — Nonce hash for deterministic nonce generation."""
    tag = b"BTP/FROST/v3.1.0/nonce"
    digest = hashlib.sha256(tag + msg).digest()
    return int.from_bytes(digest, "big") % _Q


# ---------------------------------------------------------------------------
# Shamir's Secret Sharing (over Z_q)
# ---------------------------------------------------------------------------

def _evaluate_polynomial(coefficients: list[int], x: int) -> int:
    """
    Evaluate polynomial f(x) = c_0 + c_1*x + c_2*x^2 + ... mod q
    using Horner's method.
    """
    result = 0
    for coeff in reversed(coefficients):
        result = (result * x + coeff) % _Q
    return result


def _lagrange_coefficient(signer_index: int, all_indices: list[int]) -> int:
    """
    Compute Lagrange interpolation coefficient λ_i for signer i
    evaluated at x=0 (i.e., to reconstruct the secret).

    λ_i = ∏_{j ≠ i} j / (j - i)  mod q
    """
    num = 1
    den = 1
    for j in all_indices:
        if j == signer_index:
            continue
        num = (num * j) % _Q
        den = (den * (j - signer_index)) % _Q
    return (num * _modinv(den, _Q)) % _Q


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class FrostKeygenResult:
    """
    Output of the FROST key generation ceremony for a single participant.

    secret_share:       s_i — participant's share of the group secret (PRIVATE)
    verification_share: Y_i = g^{s_i} mod p — publicly verifiable (PUBLIC)
    group_pubkey:       Y   = g^s mod p  — the swarm's joint public key (PUBLIC)
    index:              participant's index i (1-based)
    threshold:          t — minimum signers needed
    n_participants:     n — total participants
    """
    secret_share: int        # PRIVATE — never share this
    verification_share: int  # PUBLIC  — g^secret_share mod p
    group_pubkey: int        # PUBLIC  — g^group_secret mod p
    index: int
    threshold: int
    n_participants: int

    def __repr__(self) -> str:
        return (
            f"FrostKeygenResult(index={self.index}, "
            f"t={self.threshold}, n={self.n_participants}, "
            f"group_pubkey=0x{self.group_pubkey:x}"[:80] + "...)"
        )


@dataclasses.dataclass
class FrostCommitment:
    """
    Round 1 output — nonce commitments broadcast by each signer.
    D_i = g^d_i, E_i = g^e_i  (both public)
    d_i, e_i are ephemeral private nonces, discarded after Round 2.
    """
    signer_index: int
    D: int   # g^d mod p
    E: int   # g^e mod p
    # Private nonces (held locally, not transmitted)
    _d: int = dataclasses.field(repr=False)
    _e: int = dataclasses.field(repr=False)

    def public_bytes(self) -> bytes:
        """Serialise public commitment for broadcast."""
        return (
            self.signer_index.to_bytes(4, "big")
            + self.D.to_bytes(128, "big")
            + self.E.to_bytes(128, "big")
        )


@dataclasses.dataclass
class FrostPartialSig:
    """
    Round 2 output — each signer's partial Schnorr response z_i.
    z_i = d_i + e_i*ρ_i + λ_i * s_i * c  mod q
    """
    signer_index: int
    z: int   # partial response

    def to_dict(self) -> dict:
        return {
            "signer_index": self.signer_index,
            "z_hex": hex(self.z),
        }


@dataclasses.dataclass
class FrostThresholdSignature:
    """
    The final aggregate FROST threshold signature σ = (R, z).
    This is a standard Schnorr signature verifiable against the group public key Y.
    Anyone can verify: g^z == R * Y^c mod p, where c = H(R, Y, msg).
    """
    R: int                    # Group nonce: ∏ D_i * E_i^ρ_i mod p
    z: int                    # Aggregate response: Σ z_i mod q
    group_pubkey: int         # Y = g^s mod p (public)
    message_hash: bytes       # H(action_payload) that was signed
    signing_indices: list[int]  # Which signers participated
    threshold: int

    def verify(self) -> bool:
        """
        Verify the FROST signature against the group public key.
        Standard Schnorr check: g^z ≡ R * Y^c (mod p)
        where c = H1(R || Y || msg)
        """
        try:
            c_bytes = (
                self.R.to_bytes(128, "big")
                + self.group_pubkey.to_bytes(128, "big")
                + self.message_hash
            )
            c = _H1(c_bytes)
            lhs = pow(_G, self.z, _P)
            rhs = (self.R * pow(self.group_pubkey, c, _P)) % _P
            return lhs == rhs
        except Exception:
            return False

    def to_dict(self) -> dict:
        return {
            "R_hex": hex(self.R),
            "z_hex": hex(self.z),
            "group_pubkey_hex": hex(self.group_pubkey),
            "message_hash_hex": self.message_hash.hex(),
            "signing_indices": self.signing_indices,
            "threshold": self.threshold,
            "valid": self.verify(),
        }


# ---------------------------------------------------------------------------
# Key Generation
# ---------------------------------------------------------------------------

def frost_keygen(n: int, t: int) -> list[FrostKeygenResult]:
    """
    Trusted dealer key generation for (t, n) FROST threshold scheme.

    Generates a random group secret s, splits it into n Shamir shares
    using a random polynomial of degree t, and returns each participant's
    FrostKeygenResult.

    In production, this would use a distributed key generation (DKG) protocol
    so no single party ever sees the full secret. For BTP, the coordinator
    performs trusted setup in an HSM/enclave (ConfidentialEnclaveAttestationEngine).

    Args:
        n: Total number of participants
        t: Signing threshold — any t+1 participants can sign

    Returns:
        List of n FrostKeygenResult objects, one per participant (1-indexed).
    """
    if t < 1:
        raise ValueError("Threshold t must be >= 1")
    if n < t + 1:
        raise ValueError(f"Need at least t+1 = {t+1} participants for threshold {t}, got n={n}")

    # Sample random polynomial f(x) = s + a_1*x + a_2*x^2 + ... + a_t*x^t
    # The secret is s = f(0)
    coefficients = [secrets.randbelow(_Q - 1) + 1 for _ in range(t + 1)]
    group_secret = coefficients[0]  # s = f(0)

    # Group public key: Y = g^s mod p
    group_pubkey = pow(_G, group_secret, _P)

    results = []
    for i in range(1, n + 1):  # 1-indexed participants
        secret_share = _evaluate_polynomial(coefficients, i)
        verification_share = pow(_G, secret_share, _P)
        results.append(FrostKeygenResult(
            secret_share=secret_share,
            verification_share=verification_share,
            group_pubkey=group_pubkey,
            index=i,
            threshold=t,
            n_participants=n,
        ))

    # Securely erase the polynomial coefficients from memory (best effort in Python)
    for i in range(len(coefficients)):
        coefficients[i] = 0

    return results


def frost_reconstruct_secret(shares: list[tuple[int, int]]) -> int:
    """
    Reconstruct the group secret from t+1 shares using Lagrange interpolation.
    shares: list of (index, share_value) tuples.
    Used for testing only — in production the secret is never reconstructed.
    """
    indices = [s[0] for s in shares]
    secret = 0
    for idx, share_val in shares:
        lam = _lagrange_coefficient(idx, indices)
        secret = (secret + lam * share_val) % _Q
    return secret


# ---------------------------------------------------------------------------
# Per-Agent Signer
# ---------------------------------------------------------------------------

class FrostSigner:
    """
    Represents a single participant in the FROST protocol.
    Each autonomous agent in the swarm holds one FrostSigner.
    """

    def __init__(self, keygen: FrostKeygenResult):
        self.keygen = keygen
        self._active_commitment: Optional[FrostCommitment] = None

    @property
    def index(self) -> int:
        return self.keygen.index

    @property
    def group_pubkey(self) -> int:
        return self.keygen.group_pubkey

    def round1_commit(self) -> FrostCommitment:
        """
        Round 1: Generate ephemeral nonce pair and broadcast commitments.
        Each signer calls this once per signing session.
        """
        # Deterministic nonces derived from secret share + randomness (RFC 9591 §4.2)
        rand = secrets.token_bytes(32)
        d = _H3(self.keygen.secret_share.to_bytes(128, "big") + rand + b"d")
        e = _H3(self.keygen.secret_share.to_bytes(128, "big") + rand + b"e")
        # Ensure nonces are non-zero
        d = max(1, d)
        e = max(1, e)

        D = pow(_G, d, _P)
        E = pow(_G, e, _P)

        self._active_commitment = FrostCommitment(
            signer_index=self.index,
            D=D, E=E,
            _d=d, _e=e,
        )
        return self._active_commitment

    def round2_sign(
        self,
        message: bytes,
        all_commitments: list[FrostCommitment],
    ) -> FrostPartialSig:
        """
        Round 2: Compute partial signature given all Round 1 commitments.

        z_i = d_i + e_i * ρ_i + λ_i * s_i * c  mod q

        where:
          ρ_i = H2("rho" || i || msg_hash || B)  [binding factor]
          R   = ∏ D_j * E_j^ρ_j                  [group nonce]
          c   = H1(R || Y || msg_hash)            [Schnorr challenge]
          λ_i = Lagrange coefficient for i

        Message is pre-hashed to a canonical 32-byte form before all
        cryptographic operations, ensuring verify() uses the same input.
        """
        if self._active_commitment is None:
            raise RuntimeError("Must call round1_commit() before round2_sign()")

        commit = self._active_commitment
        signing_indices = sorted(c.signer_index for c in all_commitments)

        # Canonical message hash — all downstream crypto uses this, not raw message
        msg_hash = hashlib.sha256(message).digest()

        # Serialize commitment list B for binding factor computation
        B_bytes = b"".join(c.public_bytes() for c in sorted(all_commitments, key=lambda c: c.signer_index))

        # Compute binding factors ρ_i for all signers
        rho = {}
        for c in all_commitments:
            rho_input = (
                c.signer_index.to_bytes(4, "big")
                + msg_hash
                + B_bytes
            )
            rho[c.signer_index] = _H2(rho_input)

        # Compute group nonce R = ∏ D_i * E_i^ρ_i mod p
        R = 1
        for c in all_commitments:
            R = (R * c.D * pow(c.E, rho[c.signer_index], _P)) % _P

        # Schnorr challenge c = H1(R || Y || msg_hash)
        c_bytes = (
            R.to_bytes(128, "big")
            + self.group_pubkey.to_bytes(128, "big")
            + msg_hash
        )
        challenge = _H1(c_bytes)

        # Lagrange coefficient for this signer
        lam = _lagrange_coefficient(self.index, signing_indices)

        # Partial signature
        my_rho = rho[self.index]
        z_i = (
            commit._d
            + commit._e * my_rho
            + lam * self.keygen.secret_share * challenge
        ) % _Q

        # Erase ephemeral nonces from the commitment (best effort)
        self._active_commitment = None

        return FrostPartialSig(signer_index=self.index, z=z_i)


# ---------------------------------------------------------------------------
# Coordinator: Aggregates Rounds 1 & 2
# ---------------------------------------------------------------------------

class FrostCoordinator:
    """
    Aggregates FROST Round 1 commitments and Round 2 partial signatures
    to produce the final threshold signature.

    The coordinator does NOT need to know any private keys — it is
    a stateless aggregator that can be any node in the swarm (or even
    a public endpoint) without compromising security.
    """

    def __init__(self, group_pubkey: int, threshold: int):
        self.group_pubkey = group_pubkey
        self.threshold = threshold

    def aggregate_signature(
        self,
        message: bytes,
        commitments: list[FrostCommitment],
        partial_sigs: list[FrostPartialSig],
    ) -> FrostThresholdSignature:
        """
        Combine partial signatures into a single FROST threshold signature.

        Args:
            message:      The canonical message that was signed.
            commitments:  Round 1 outputs from all t+1 signers.
            partial_sigs: Round 2 outputs from all t+1 signers.

        Returns:
            FrostThresholdSignature — a standard Schnorr sig on the group key.
        """
        if len(partial_sigs) < self.threshold + 1:
            raise ValueError(
                f"Need at least t+1={self.threshold + 1} partial sigs, "
                f"got {len(partial_sigs)}"
            )

        # Sort by signer index for determinism
        commitments_sorted = sorted(commitments, key=lambda c: c.signer_index)
        partial_sigs_sorted = sorted(partial_sigs, key=lambda s: s.signer_index)

        # Validate signer sets match
        commit_indices = {c.signer_index for c in commitments_sorted}
        sig_indices = {s.signer_index for s in partial_sigs_sorted}
        if commit_indices != sig_indices:
            raise ValueError("Commitment and partial signature signer sets do not match.")

        # Canonical message hash — must match what round2_sign computed
        msg_hash = hashlib.sha256(message).digest()

        B_bytes = b"".join(c.public_bytes() for c in commitments_sorted)

        # Recompute binding factors (using msg_hash, same as round2_sign)
        rho = {}
        for c in commitments_sorted:
            rho_input = c.signer_index.to_bytes(4, "big") + msg_hash + B_bytes
            rho[c.signer_index] = _H2(rho_input)

        # Recompute group nonce R
        R = 1
        for c in commitments_sorted:
            R = (R * c.D * pow(c.E, rho[c.signer_index], _P)) % _P

        # Aggregate partial signatures: z = Σ z_i mod q
        z = sum(ps.z for ps in partial_sigs_sorted) % _Q

        return FrostThresholdSignature(
            R=R,
            z=z,
            group_pubkey=self.group_pubkey,
            message_hash=msg_hash,
            signing_indices=sorted(sig_indices),
            threshold=self.threshold,
        )
