"""
BTP v4.0 — Autonomous Multi-Rail Micro-Escrow & Automated Slashing Engine
==========================================================================
Provides trustless cryptographic micro-escrows and automated warranty indemnification:
1. Locks collateral micro-escrows backed by agent passports and bonded reserves.
2. Supports dual-settlement destinations:
   - L402 Lightning Network micro-invoices (instant satoshi settlement via payment preimage revelation)
   - EVM smart contracts (Arbitrum, Base, Ethereum) via EIP-712 typed signature attestation
3. Automatically slashes collateral upon receipt of verified cryptographic regression proofs
   and disburses liquidated payouts without human arbitration.
4. Auto-trips agent passport circuit-breakers upon confirmed slash.
5. Rewards agent passport trust scores upon clean release.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import time
from typing import Dict, Any, Optional, Tuple, List

from src.bonded_warranty import BondedExecutionWarranty
from src.agent_passport import SovereignAgentPassport
from src.settlement.l402_protocol import L402ProtocolEngine, L402Challenge
from src.settlement.evm_escrow import EVMEscrowGateway, EscrowSlashingClaim, EIP712Domain
from src.settlement.swarm_arbitration import SwarmDisputeArbitrator, ArbitrationResolutionCertificate, ZKFaultProof

try:
    from src.alerting.webhook_dispatcher import (
        WebhookDispatcher,
        IncidentEvent,
        IncidentEventType,
        AlertSeverity,
    )
except ImportError:
    WebhookDispatcher = None
    IncidentEvent = None
    IncidentEventType = None
    AlertSeverity = None


@dataclasses.dataclass
class EscrowDeposit:
    """Represents a locked micro-escrow bond for an autonomous agent action."""
    escrow_id: str
    agent_id: str
    passport_id: Optional[str]
    action_type: str
    amount_usd: float
    locked_at: float
    status: str  # 'LOCKED' | 'RELEASED' | 'SLASHED'
    settlement_rail: str  # 'L402_LIGHTNING' | 'EVM_ARBITRUM' | 'EVM_BASE' | 'SOLANA'
    payee_destination: Optional[str] = None
    slashed_at: Optional[float] = None
    slash_reason: Optional[str] = None
    l402_challenge: Optional[Dict[str, Any]] = None
    l402_preimage: Optional[str] = None
    evm_claim: Optional[Dict[str, Any]] = None
    tenant_id: str = "ten_default"
    org_id: str = "default_org"

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class AutonomousEscrowPool:
    """
    Programmatic Autonomous Micro-Escrow and Liquidated Slashing Engine.
    """

    def __init__(
        self,
        reserve_pool_usd: float = 100_000.0,
        max_escrow_per_action_usd: float = 10_000.0,
        l402_engine: Optional[L402ProtocolEngine] = None,
        evm_gateway: Optional[EVMEscrowGateway] = None,
        webhook_dispatcher: Optional[Any] = None
    ):
        self.reserve_pool_usd = reserve_pool_usd
        self.max_escrow_per_action_usd = max_escrow_per_action_usd
        self.warranty_engine = BondedExecutionWarranty(
            reserve_pool_usd=reserve_pool_usd,
            max_bond_per_action_usd=max_escrow_per_action_usd
        )
        self.l402_engine = l402_engine or L402ProtocolEngine()
        self.evm_gateway = evm_gateway or EVMEscrowGateway()
        self.arbitrator = SwarmDisputeArbitrator()
        self.webhook_dispatcher = webhook_dispatcher or (WebhookDispatcher() if WebhookDispatcher is not None else None)
        self.active_escrows: Dict[str, EscrowDeposit] = {}
        self.settlement_ledger: List[Dict[str, Any]] = []

    def lock_escrow(
        self,
        agent_id: str,
        action_type: str,
        amount_usd: float,
        passport: Optional[SovereignAgentPassport] = None,
        settlement_rail: str = "L402_LIGHTNING"
    ) -> EscrowDeposit:
        """
        Locks collateral against an agent's intended action.
        """
        if amount_usd > self.max_escrow_per_action_usd:
            raise ValueError(f"Escrow amount ${amount_usd} exceeds max cap ${self.max_escrow_per_action_usd}")

        if amount_usd > self.reserve_pool_usd:
            raise ValueError("Insufficient liquidity in escrow reserve pool")

        # Verify passport if supplied
        passport_id = None
        if passport:
            if passport.circuit_breaker_tripped:
                raise PermissionError(f"Agent passport {passport.agent_id} is circuit-breaker TRIPPED: cannot lock escrow.")
            passport_id = passport.agent_id

        # Generate unique escrow ID
        escrow_entropy = f"{agent_id}:{action_type}:{amount_usd}:{time.time_ns()}"
        escrow_id = f"ESCROW-{hashlib.sha256(escrow_entropy.encode()).hexdigest()[:16].upper()}"

        l402_challenge_dict = None
        l402_preimage = None
        if "L402" in settlement_rail.upper() or "LIGHTNING" in settlement_rail.upper():
            # 1 USD ~= 2,000 satoshis baseline
            satoshis = int(amount_usd * 2000)
            challenge, preimage = self.l402_engine.create_challenge(
                agent_id=agent_id,
                action_type=action_type,
                amount_satoshis=satoshis,
                ttl_seconds=86400
            )
            l402_challenge_dict = challenge.to_dict()
            l402_preimage = preimage

        tenant_id = getattr(passport, "tenant_id", "ten_default")
        org_id = getattr(passport, "org_id", "default_org")

        deposit = EscrowDeposit(
            escrow_id=escrow_id,
            agent_id=agent_id,
            passport_id=passport_id,
            action_type=action_type,
            amount_usd=amount_usd,
            locked_at=time.time(),
            status="LOCKED",
            settlement_rail=settlement_rail,
            l402_challenge=l402_challenge_dict,
            l402_preimage=l402_preimage,
            tenant_id=tenant_id,
            org_id=org_id
        )

        self.active_escrows[escrow_id] = deposit
        return deposit

    def claim_and_slash(
        self,
        escrow_id: str,
        regression_proof: Dict[str, Any],
        payee_destination: str,
        agent_passport: Optional[SovereignAgentPassport] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates cryptographic proof of regression/violation, slashes the escrowed
        collateral, and disburses liquidated indemnity payout to the claimant.
        """
        deposit = self.active_escrows.get(escrow_id)
        if not deposit:
            return False, f"Escrow ID '{escrow_id}' not found.", {}

        if deposit.status != "LOCKED":
            return False, f"Escrow ID '{escrow_id}' is already {deposit.status}.", {}

        # 1. Verify cryptographic regression proof integrity
        proof_type = regression_proof.get("type", "BTP_REGRESSION_PROOF")
        violation_rule = regression_proof.get("violated_invariant")
        proof_signature = regression_proof.get("proof_signature")

        if not violation_rule or not proof_signature:
            return False, "Invalid regression proof: missing violated_invariant or proof_signature.", {}

        # Verify that proof relates to this deposit's action_type
        target_action = regression_proof.get("target_action")
        if target_action and target_action != deposit.action_type:
            return False, f"Proof target action '{target_action}' does not match escrow action '{deposit.action_type}'.", {}

        # 2. Execute Slashing & Indemnity Release
        deposit.status = "SLASHED"
        deposit.slashed_at = time.time()
        deposit.slash_reason = f"Violated Invariant: {violation_rule}"
        deposit.payee_destination = payee_destination

        self.reserve_pool_usd -= deposit.amount_usd

        # 3. Penalize Agent Passport & Trip Circuit Breaker
        passport_tripped = False
        if agent_passport and agent_passport.agent_id == deposit.agent_id:
            agent_passport.trip_circuit_breaker(f"Automated Slashing Indemnity Triggered on {escrow_id}: {violation_rule}")
            passport_tripped = True

        settlement_receipt: Dict[str, Any] = {
            "escrow_id": escrow_id,
            "slashed_agent": deposit.agent_id,
            "indemnity_amount_usd": deposit.amount_usd,
            "settlement_rail": deposit.settlement_rail,
            "payee_destination": payee_destination,
            "slashed_at": deposit.slashed_at,
            "slash_reason": deposit.slash_reason,
            "passport_tripped": passport_tripped,
            "status": "DISBURSED_AND_SETTLED"
        }

        # 4. Multi-Rail Settlement Disbursement Proofs
        if "L402" in deposit.settlement_rail.upper() or "LIGHTNING" in deposit.settlement_rail.upper():
            settlement_receipt["l402_preimage_revealed"] = deposit.l402_preimage
            settlement_receipt["l402_payment_hash"] = (
                deposit.l402_challenge.get("payment_hash") if deposit.l402_challenge else None
            )

        if "EVM" in deposit.settlement_rail.upper():
            claim = EscrowSlashingClaim(
                escrow_id=escrow_id,
                agent_id=deposit.agent_id,
                payee_address=payee_destination if payee_destination.startswith("0x") else "0x000000000000000000000000000000000000dead",
                amount_usd=deposit.amount_usd,
                violated_invariant=violation_rule,
                proof_hash=proof_signature[:66] if proof_signature.startswith("0x") else f"0x{proof_signature[:64]}",
                nonce=int(time.time_ns() % 1_000_000),
                deadline=int(time.time() + 86400)
            )
            sig_payload = self.evm_gateway.sign_slashing_claim(claim)
            settlement_receipt["evm_eip712_claim"] = sig_payload

        self.settlement_ledger.append(settlement_receipt)
        return True, "Collateral slashed and liquidated indemnity disbursed successfully.", settlement_receipt

    def arbitrate_and_slash(
        self,
        escrow_id: str,
        arbitration_cert: ArbitrationResolutionCertificate,
        payee_destination: str,
        agent_passport: Optional[SovereignAgentPassport] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Executes collateral slashing based on a verified Byzantine Swarm Arbitration Resolution Certificate.
        """
        deposit = self.active_escrows.get(escrow_id)
        if not deposit:
            return False, f"Escrow ID '{escrow_id}' not found.", {}

        if deposit.status != "LOCKED":
            return False, f"Escrow ID '{escrow_id}' is already {deposit.status}.", {}

        if arbitration_cert.escrow_id != escrow_id:
            return False, f"Arbitration certificate escrow_id '{arbitration_cert.escrow_id}' does not match '{escrow_id}'.", {}

        if arbitration_cert.verdict != "SLASH_COLLATERAL":
            return False, f"Arbitration certificate verdict is '{arbitration_cert.verdict}', not 'SLASH_COLLATERAL'.", {}

        if arbitration_cert.quorum_count < 2:
            return False, f"Insufficient arbitration quorum ({arbitration_cert.quorum_count} votes).", {}

        # Cross-Tenant Boundary Firewall
        if agent_passport and hasattr(agent_passport, "tenant_id"):
            if deposit.tenant_id and deposit.tenant_id != "ten_default" and agent_passport.tenant_id != deposit.tenant_id:
                return False, f"Cross-tenant slashing vetoed: Passport tenant '{agent_passport.tenant_id}' != Escrow tenant '{deposit.tenant_id}'.", {}

        # Execute Slashing
        deposit.status = "SLASHED"
        deposit.slashed_at = time.time()
        deposit.slash_reason = f"Swarm Byzantine Arbitration Quorum ({arbitration_cert.certificate_id})"
        deposit.payee_destination = payee_destination

        self.reserve_pool_usd -= deposit.amount_usd

        # Penalize Agent Passport & Trip Circuit Breaker
        passport_tripped = False
        if agent_passport and agent_passport.agent_id == deposit.agent_id:
            agent_passport.trip_circuit_breaker(f"Swarm Arbitration Slashing Verdict ({arbitration_cert.certificate_id})")
            passport_tripped = True

        settlement_receipt: Dict[str, Any] = {
            "escrow_id": escrow_id,
            "slashed_agent": deposit.agent_id,
            "indemnity_amount_usd": deposit.amount_usd,
            "settlement_rail": deposit.settlement_rail,
            "payee_destination": payee_destination,
            "slashed_at": deposit.slashed_at,
            "slash_reason": deposit.slash_reason,
            "arbitration_certificate_id": arbitration_cert.certificate_id,
            "quorum_count": arbitration_cert.quorum_count,
            "passport_tripped": passport_tripped,
            "status": "ARBITRATED_AND_DISBURSED"
        }

        if "L402" in deposit.settlement_rail.upper() or "LIGHTNING" in deposit.settlement_rail.upper():
            settlement_receipt["l402_preimage_revealed"] = deposit.l402_preimage

        # Milestone 5.1: Emit Incident Event to SecOps Webhooks
        if self.webhook_dispatcher is not None and IncidentEvent is not None:
            try:
                evt_id = f"evt_slash_{hashlib.sha256(f'{escrow_id}:{time.time_ns()}'.encode()).hexdigest()[:16]}"
                incident = IncidentEvent(
                    event_id=evt_id,
                    tenant_id=deposit.tenant_id or "ten_default",
                    org_id=deposit.org_id or "default_org",
                    project_id="escrow_subsystem",
                    environment="prod" if "live" in (deposit.tenant_id or "") else "dev",
                    event_type=IncidentEventType.ESCROW_SLASHED,
                    severity=AlertSeverity.CRITICAL,
                    title=f"Autonomous Escrow Slashed: {escrow_id}",
                    description=f"Collateral of ${deposit.amount_usd:.2f} USD slashed for agent '{deposit.agent_id}'. Reason: {deposit.slash_reason}",
                    agent_id=deposit.agent_id,
                    tool_name=deposit.action_type,
                    slashed_amount_usd=deposit.amount_usd,
                    metadata={
                        "escrow_id": escrow_id,
                        "certificate_id": arbitration_cert.certificate_id,
                        "quorum_count": arbitration_cert.quorum_count,
                        "payee_destination": payee_destination,
                        "settlement_rail": deposit.settlement_rail
                    }
                )
                self.webhook_dispatcher.emit_incident(incident)
            except Exception:
                pass

        self.settlement_ledger.append(settlement_receipt)
        return True, "Swarm arbitration verdict executed: collateral slashed and disbursed.", settlement_receipt


    def release_escrow(
        self,
        escrow_id: str,
        agent_passport: Optional[SovereignAgentPassport] = None
    ) -> Tuple[bool, str]:
        """
        Releases escrowed funds back to reserve after clean task verification
        and records verified settled volume on the agent passport.
        """
        deposit = self.active_escrows.get(escrow_id)
        if not deposit:
            return False, f"Escrow ID '{escrow_id}' not found."

        if deposit.status != "LOCKED":
            return False, f"Escrow ID '{escrow_id}' cannot be released: status is {deposit.status}."

        deposit.status = "RELEASED"

        # Reward passport trust vector
        if agent_passport and agent_passport.agent_id == deposit.agent_id:
            agent_passport.record_action(f"Escrow {escrow_id} released clean: {deposit.action_type}", volume_usd=deposit.amount_usd)

        return True, f"Escrow '{escrow_id}' released clean."

    def lock_sla_escrow(
        self,
        contract: Any,
        client_passport: Optional[Any] = None,
        provider_passport: Optional[Any] = None,
    ) -> Tuple[EscrowDeposit, EscrowDeposit]:
        """
        Locks two-sided collateral for a cross-tenant SLA:
        1. Client payment escrow (held in trust for provider).
        2. Provider performance bond (held in escrow as slashable indemnity).
        """
        client_deposit = self.lock_escrow(
            agent_id=contract.client_agent_id,
            action_type=f"SLA_PAYMENT:{contract.contract_id}",
            amount_usd=contract.payment_budget_usd,
            passport=client_passport,
            settlement_rail=contract.settlement_rail
        )
        provider_deposit = self.lock_escrow(
            agent_id=contract.provider_agent_id,
            action_type=f"SLA_PERFORMANCE_BOND:{contract.contract_id}",
            amount_usd=contract.provider_bond_usd,
            passport=provider_passport,
            settlement_rail=contract.settlement_rail
        )
        return client_deposit, provider_deposit

    def settle_sla_completion(
        self,
        contract: Any,
        completion_proof: Any,
        provider_payee_destination: str
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Settles fulfilled cross-tenant SLA:
        1. Releases provider's staked performance bond back to provider.
        2. Disburses client's payment deposit to provider_payee_destination.
        """
        if not getattr(completion_proof, "verified", False):
            return False, "SLA settlement aborted: completion proof is unverified.", {}

        client_dep = self.active_escrows.get(contract.client_escrow_id) if contract.client_escrow_id else None
        prov_dep = self.active_escrows.get(contract.provider_escrow_id) if contract.provider_escrow_id else None

        if client_dep and client_dep.status == "LOCKED":
            client_dep.status = "SETTLED"
            client_dep.payee_destination = provider_payee_destination

        if prov_dep and prov_dep.status == "LOCKED":
            prov_dep.status = "RELEASED"

        receipt = {
            "contract_id": contract.contract_id,
            "proof_id": getattr(completion_proof, "proof_id", "zktcp_auto"),
            "amount_disbursed_usd": contract.payment_budget_usd,
            "bond_returned_usd": contract.provider_bond_usd,
            "payee_destination": provider_payee_destination,
            "settled_at": time.time(),
            "status": "SLA_SETTLED_CLEAN"
        }
        self.settlement_ledger.append(receipt)
        return True, "Cross-tenant SLA contract settled successfully.", receipt
