import time
import pytest
from bartholomew_eval.agent_protocol import (
    CryptographicIdentityCredential,
    DelegationChain,
    CapabilityNegotiationRequest,
    VendorNeutralProtocolGateway,
    create_3_organization_simulation
)


def test_cryptographic_verification_allowed():
    gateway, verifier, result, verified_by_org_c = create_3_organization_simulation()
    assert result["decision"] == "ALLOW"
    assert result["agent_did"] == "did:bth:org_a_agent_alpha"
    assert verified_by_org_c is True
    assert result["evidence_artifact"] is not None
    assert "proof_ed25519" in result["evidence_artifact"]["ed25519_proof"]


def test_cryptographic_revocation_denied():
    gateway = VendorNeutralProtocolGateway()
    gateway.revoke_credential("did:bth:agent_revoked_99")

    cred = CryptographicIdentityCredential(
        agent_did="did:bth:agent_revoked_99",
        issuer_did="did:bth:root_org",
        issuer_pub_key="pubkey_root",
        possessed_capabilities=["data.read"],
        constraint_manifest=[]
    )

    req = CapabilityNegotiationRequest(
        request_id="req_revoked_01",
        nonce="nonce_rev_99",
        timestamp_epoch=time.time(),
        credential=cred,
        intent_requested_capability="data.read",
        action_payload={},
        context_conditions={},
        target_system="Secure_Vault"
    )

    result = gateway.verify_request(req)

    assert result["decision"] == "DENY"
    assert "Revocation List" in result["reason"]


def test_delegation_chain_capability_grant():
    gateway = VendorNeutralProtocolGateway()
    cred = CryptographicIdentityCredential(
        agent_did="did:bth:sub_agent_02",
        issuer_did="did:bth:root_org",
        issuer_pub_key="pubkey_root",
        possessed_capabilities=[],  # Empty direct capabilities!
        constraint_manifest=[]
    )

    delegation = DelegationChain(
        root_authority_did="did:bth:root_org",
        parent_agent_did="did:bth:parent_agent_01",
        delegated_agent_did="did:bth:sub_agent_02",
        delegated_capabilities=["compute.request"]  # Granted via delegation chain
    )

    req = CapabilityNegotiationRequest(
        request_id="req_delegated_01",
        nonce="nonce_del_02",
        timestamp_epoch=time.time(),
        credential=cred,
        intent_requested_capability="compute.request",
        action_payload={},
        context_conditions={},
        target_system="Compute_Cluster",
        delegation_chain=delegation
    )

    result = gateway.verify_request(req)

    assert result["decision"] == "ALLOW"
    assert result["evidence_artifact"]["delegation_chain_verified"] is True
