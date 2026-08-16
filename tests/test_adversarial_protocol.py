import time
import pytest
from bartholomew_eval.agent_protocol import (
    CryptographicIdentityCredential,
    DelegationChain,
    CapabilityNegotiationRequest,
    VendorNeutralProtocolGateway,
    StandaloneIndependentVerifier,
    create_3_organization_simulation
)


def test_3_independent_organizations_zero_trust():
    """
    Test 3 Independent Organizations Experiment:
    Org A issues Agent A credential. Bartholomew processes request.
    Org C independently verifies evidence artifact offline using Pinned Root Keys (Zero Trust in Bartholomew API).
    """
    gateway, org_c_verifier, result, verified_by_org_c = create_3_organization_simulation()
    assert result["decision"] == "ALLOW"
    assert verified_by_org_c is True


def test_forged_issuer_signature():
    """Identity Attack: Credential with forged signature must be DENIED."""
    gateway = VendorNeutralProtocolGateway()
    cred = CryptographicIdentityCredential(
        agent_did="did:bth:forged_agent",
        issuer_did="did:bth:root_org",
        issuer_pub_key="pubkey_root",
        possessed_capabilities=["read_data"],
        constraint_manifest=[],
        signature="sig_issuer_ed25519_FORGED_SIGNATURE_BYTES_12345"
    )
    req = CapabilityNegotiationRequest(
        request_id="req_forged_01",
        nonce="nonce_forged_1",
        timestamp_epoch=time.time(),
        credential=cred,
        intent_requested_capability="read_data",
        action_payload={},
        context_conditions={},
        target_system="Vault"
    )
    res = gateway.verify_request(req)
    assert res["decision"] == "DENY"
    assert "signature verification failed" in res["reason"]


def test_delegation_overreach():
    """Delegation Attack: Sub-agent attempts capability never granted in delegation chain."""
    gateway = VendorNeutralProtocolGateway()
    cred = CryptographicIdentityCredential(
        agent_did="did:bth:sub_agent_99",
        issuer_did="did:bth:root_org",
        issuer_pub_key="pubkey_root",
        possessed_capabilities=[],  # Empty direct capabilities!
        constraint_manifest=[]
    )

    # Delegation chain only grants 'read_data', NOT 'delete_database'
    delegation = DelegationChain(
        root_authority_did="did:bth:root_org",
        parent_agent_did="did:bth:parent_agent",
        delegated_agent_did="did:bth:sub_agent_99",
        delegated_capabilities=["read_data"]
    )

    req = CapabilityNegotiationRequest(
        request_id="req_overreach_01",
        nonce="nonce_overreach_1",
        timestamp_epoch=time.time(),
        credential=cred,
        intent_requested_capability="delete_database",  # OVERREACH!
        action_payload={},
        context_conditions={},
        target_system="Database_Cluster",
        delegation_chain=delegation
    )

    res = gateway.verify_request(req)
    assert res["decision"] == "DENY"
    assert "lacks authority" in res["reason"]


def test_revocation_replay():
    """Revocation Attack: Replaying request after credential is added to CRL must be DENIED."""
    gateway = VendorNeutralProtocolGateway()
    cred = CryptographicIdentityCredential(
        agent_did="did:bth:revoked_agent_101",
        issuer_did="did:bth:root_org",
        issuer_pub_key="pubkey_root",
        possessed_capabilities=["execute_task"],
        constraint_manifest=[]
    )

    gateway.revoke_credential("did:bth:revoked_agent_101")

    req = CapabilityNegotiationRequest(
        request_id="req_revoked_01",
        nonce="nonce_revoked_1",
        timestamp_epoch=time.time(),
        credential=cred,
        intent_requested_capability="execute_task",
        action_payload={},
        context_conditions={},
        target_system="Compute_Node"
    )

    res = gateway.verify_request(req)
    assert res["decision"] == "DENY"
    assert "Revocation List" in res["reason"]


def test_nonce_request_replay():
    """Replay Attack: Sending exact same request_id + nonce multiple times must be DENIED."""
    gateway = VendorNeutralProtocolGateway()
    cred = CryptographicIdentityCredential(
        agent_did="did:bth:valid_agent_55",
        issuer_did="did:bth:root_org",
        issuer_pub_key="pubkey_root",
        possessed_capabilities=["read_data"],
        constraint_manifest=[]
    )

    t_now = time.time()
    req1 = CapabilityNegotiationRequest(
        request_id="req_replay_100",
        nonce="nonce_unique_999",
        timestamp_epoch=t_now,
        credential=cred,
        intent_requested_capability="read_data",
        action_payload={},
        context_conditions={},
        target_system="Vault"
    )

    # First request: ALLOW
    res1 = gateway.verify_request(req1)
    assert res1["decision"] == "ALLOW"

    # Replaying exact same nonce: DENY
    res2 = gateway.verify_request(req1)
    assert res2["decision"] == "DENY"
    assert "Replay attack detected" in res2["reason"]


def test_evidence_tampering_one_byte():
    """Evidence Tampering Attack: Modifying 1 byte in decision or proof must fail Org C's verifier."""
    _, org_c_verifier, result, verified_first = create_3_organization_simulation()
    assert verified_first is True

    evidence = result["evidence_artifact"]

    # Tamper with 1 byte of the proof string
    tampered_evidence = dict(evidence)
    tampered_evidence["ed25519_proof"] = tampered_evidence["ed25519_proof"][:-1] + "X"

    verified_tampered, msg = org_c_verifier.verify_evidence_artifact_independently(tampered_evidence)
    assert verified_tampered is False
    assert "tampered" in msg.lower() or "mismatch" in msg.lower()


def test_evidence_tampering_field_by_field():
    """Evidence Tampering Attack: Modifying fields individually must fail verification."""
    _, org_c_verifier, result, _ = create_3_organization_simulation()
    evidence = result["evidence_artifact"]

    for field, fake_val in [
        ("agent_did", "did:bth:hacker_agent"),
        ("target_system", "Unauthorized_System"),
        ("requested_capability", "root.admin"),
        ("decision", "DENIED_BUT_TAMPERED_TO_ALLOW")
    ]:
        tampered = dict(evidence)
        tampered[field] = fake_val
        valid, msg = org_c_verifier.verify_evidence_artifact_independently(tampered)
        assert valid is False, f"Expected verification failure when tampering field '{field}'"


def test_trust_registry_root_pinning():
    """Trust Registry Attack: Attacker using un-pinned root issuer DID is rejected by Org C."""
    org_c_verifier = StandaloneIndependentVerifier(
        pinned_root_pub_keys={"did:bth:org_a_root": "pubkey_org_a_ed25519_key_101"}
    )

    unpinned_artifact = {
        "artifact_id": "art_fake_999",
        "timestamp": "2026-08-12T12:00:00Z",
        "agent_did": "did:bth:agent_fake",
        "issuer_did": "did:bth:unpinned_attacker_root",  # NOT PINNED BY ORG C!
        "target_system": "Org_C_Server",
        "requested_capability": "read",
        "decision": "ALLOW",
        "ed25519_proof": "proof_ed25519_fake"
    }

    valid, msg = org_c_verifier.verify_evidence_artifact_independently(unpinned_artifact)
    assert valid is False
    assert "not in Org C's pinned root trust store" in msg
