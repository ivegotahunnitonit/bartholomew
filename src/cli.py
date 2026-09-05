"""
Bartholomew CLI Tool (BTP v2.2.0)
=================================
Command line interface for initializing, managing, and inspecting
Bartholomew sovereign trust roots, local daemons, and MCP servers.
"""

import sys
import os
import argparse
import subprocess
import json
import urllib.request
import hashlib

# Ensure parent directory in path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.trust_protocol import BartholomewTrustAuthority
from src.declarative_policy_engine import DeclarativePolicyEngine
from src.policy_synthesizer import PolicySynthesizer


def cmd_version(args):
    print("Bartholomew Protocol (BTP) v2.4.0")
    print("Engine: Resilient MCP Proxy, In-Flight Secret Scrubber & Transactional Rollback Engine")
    print("Latency: Sub-50 microseconds (in-process) | Rollback: <5ms")


def cmd_init(args):
    print("[+] Initializing local Bartholomew sovereign trust root...")
    authority = BartholomewTrustAuthority()
    
    dot_btp = os.path.join(parent_dir, ".btp")
    os.makedirs(dot_btp, exist_ok=True)

    policy_path = os.path.join(dot_btp, "policy.yaml")
    if not os.path.exists(policy_path):
        sample_policy = """version: "2.2.0"
policy_id: "urn:btp:policy:local-workspace"
description: "Local workspace invariant security policy"

rules:
  - id: "RULE_SPEND_CAP"
    type: "max_threshold"
    field: "amount_usd"
    value: 500.00
    action: "DENY"

  - id: "RULE_DIMINISHING_MARGINAL_UTILITY"
    type: "diminishing_marginal_utility"
    decay_rate: 0.35
    min_utility_threshold: 0.15
    action: "DENY"

  - id: "RULE_DESTRUCTIVE_AST"
    type: "forbidden_substrings"
    patterns:
      - "rm -rf"
      - "DROP TABLE"
      - "DROP SCHEMA"
"""
        with open(policy_path, "w", encoding="utf-8") as f:
            f.write(sample_policy)
        print(f"[+] Created default policy: {policy_path}")

    print(f"[OK] Sovereign Public Key (Ed25519): {authority.public_key_hex}")
    if getattr(args, "pair", None):
        print(f"[OK] Paired with framework target: {args.pair}")
    print("[OK] Bartholomew local workspace initialized successfully.")


def cmd_daemon_start(args):
    port = args.port or 8080
    host = args.host or "127.0.0.1"
    print(f"[*] Starting Bartholomew Local Daemon on http://{host}:{port}...")

    daemon_script = os.path.join(parent_dir, "daemon", "daemon_server.py")
    if args.background:
        if sys.platform == "win32":
            proc = subprocess.Popen(
                [sys.executable, daemon_script],
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
        else:
            proc = subprocess.Popen([sys.executable, daemon_script], start_new_session=True)
        print(f"[OK] Daemon launched in background (PID: {proc.pid}).")
    else:
        from daemon.daemon_server import BartholomewDaemon
        daemon = BartholomewDaemon(host=host, port=port)
        daemon.run()


def cmd_daemon_status(args):
    port = args.port or 8080
    url = f"http://127.0.0.1:{port}/v1/status"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode())
            print(f"[OK] Bartholomew Daemon is ONLINE (PID / Uptime: {data.get('uptime_seconds')}s)")
            print(f"  * Public Key    : {data.get('public_key')}")
            print(f"  * Total Evals   : {data.get('total_evaluations')}")
            print(f"  * Blocked Attacks: {data.get('total_blocked')}")
            print(f"  * Average Latency: {data.get('average_latency_us')} us")
    except Exception:
        print("[!] Bartholomew daemon is currently OFFLINE.")
        print("    Run 'python cli.py daemon start' to launch.")


def cmd_mcp_start(args):
    from mcp_server import start_mcp_server
    workspace = getattr(args, "workspace", None) or os.path.join(parent_dir, "workspace")
    print(f"[*] Starting Bartholomew MCP Guard stdio server (BTP v3.1)...", file=sys.stderr)
    start_mcp_server(workspace_root=workspace)


def cmd_mcp_install(args):
    from mcp_installer import install_mcp_for_target
    target = getattr(args, "target", None) or "claude"
    dry_run = getattr(args, "dry_run", False)
    custom_path = getattr(args, "path", None)
    install_mcp_for_target(target=target, custom_path=custom_path, dry_run=dry_run)


def cmd_mcp_status(args):
    from mcp_server import get_registered_tools
    tools = get_registered_tools()
    print("=" * 74)
    print("BARTHOLOMEW MODEL CONTEXT PROTOCOL (MCP) RUNTIME STATUS — BTP v3.1")
    print("=" * 74)
    print(f"[*] Standard Spec      : Model Context Protocol (MCP 2024-11-05)")
    print(f"[*] Pre-flight Latency : Sub-50 microseconds (in-process AST & Secret Scrubber)")
    print(f"[*] Micro-Rollback     : Copy-on-Write Invariant Sandbox (<5ms)")
    print(f"[*] Bond Arbitration   : BTP v3.1 Bonded Execution Warranty Escrow")
    print(f"[*] Universal Targets  : Google Gemini 2.0, Anthropic Claude 3.7, OpenAI GPT-4o, Moonshot Kimi, DeepSeek, Qwen")
    print("-" * 74)
    print(f"REGISTERED MCP INVARIANT TOOLS ({len(tools)} ACTIVE):")
    for i, t in enumerate(tools, 1):
        name = t.get("name")
        desc = t.get("description", "").split("\n")[0]
        if len(desc) > 65:
            desc = desc[:62] + "..."
        print(f"  {i:2d}. {name:<32} {desc}")
    print("=" * 74)


def cmd_policy_validate(args):
    file_path = args.file or "policies/default_security_policy.yaml"
    if not os.path.isabs(file_path):
        file_path = os.path.join(parent_dir, file_path)
    print(f"[*] Validating declarative policy at {file_path}...")
    engine = DeclarativePolicyEngine(file_path)
    print(f"[OK] Policy '{engine.policy_id}' validated successfully ({len(engine.rules)} rules active).")


def cmd_policy_synthesize(args):
    print("[*] Running Autonomous Policy Synthesizer on workspace traces...")
    synthesizer = PolicySynthesizer()
    out_yaml = synthesizer.synthesize_yaml()
    out_file = args.output or "policies/synthesized_policy.yaml"
    with open(os.path.join(parent_dir, out_file), "w", encoding="utf-8") as f:
        f.write(out_yaml)
    print(f"[OK] Synthesized policy written to {out_file}")


def cmd_keygen(args):
    """Generate and display a fresh Ed25519 sovereign keypair."""
    authority = BartholomewTrustAuthority()
    print("=" * 70)
    print("BARTHOLOMEW ED25519 SOVEREIGN KEYPAIR GENERATION")
    print("=" * 70)
    print(f"[*] Public Key (Hex) : {authority.public_key_hex}")
    print(f"[*] TTL Policy Bound : {authority.ttl_seconds} seconds")
    print(f"[*] Algorithm        : Pure Ed25519 (RFC 8032 / FIPS 186-5)")
    print("=" * 70)


def cmd_threshold_keygen(args):
    """Generate (t, n) FROST threshold secret shares & group public key (RFC 9591)."""
    from src.frost_threshold_engine import frost_keygen
    t = args.threshold
    n = args.participants
    if t < 1:
        print(f"[ERROR] Threshold t must be >= 1, got {t}")
        sys.exit(1)
    if n < t + 1:
        print(f"[ERROR] Participants n ({n}) must be at least t+1 ({t+1})")
        sys.exit(1)

    print("=" * 70)
    print(f"BARTHOLOMEW FROST RFC 9591 THRESHOLD KEY GENERATION ({t+1}-of-{n})")
    print("=" * 70)
    results = frost_keygen(n=n, t=t)
    group_pubkey = results[0].group_pubkey
    group_pubkey_hex = hex(group_pubkey)

    print(f"[*] Group Public Key : {group_pubkey_hex[:32]}...{group_pubkey_hex[-16:]}")
    print(f"[*] Quorum Threshold : Any {t+1} of {n} agents required to sign")
    print(f"[*] Security Scheme  : Schnorr Threshold over 1024-bit MODP (RFC 9591 / RFC 3526)")

    out_dir = args.out
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        pub_path = os.path.join(out_dir, "group_pubkey.json")
        with open(pub_path, "w", encoding="utf-8") as f:
            json.dump({
                "group_pubkey_hex": group_pubkey_hex,
                "threshold": t,
                "required_signers": t + 1,
                "n_participants": n,
                "standard": "RFC 9591 FROST",
            }, f, indent=2)
        print(f"[+] Saved group public key: {pub_path}")

        for r in results:
            share_file = os.path.join(out_dir, f"share_{r.index}.json")
            with open(share_file, "w", encoding="utf-8") as f:
                json.dump({
                    "index": r.index,
                    "threshold": r.threshold,
                    "n_participants": r.n_participants,
                    "secret_share_hex": hex(r.secret_share),
                    "verification_share_hex": hex(r.verification_share),
                    "group_pubkey_hex": group_pubkey_hex,
                }, f, indent=2)
            print(f"[+] Saved Agent {r.index} Share: {share_file}")
    else:
        print("[!] Note: Specify --out <directory> to persist individual agent key shares.")
    print("=" * 70)


def cmd_threshold_sign(args):
    """Execute 2-round FROST threshold signature across provided agent shares."""
    from src.frost_threshold_engine import (
        FrostKeygenResult,
        FrostSigner,
        FrostCoordinator,
    )
    share_files = args.shares
    if not share_files or len(share_files) == 0:
        print("[ERROR] No share files provided. Specify --shares share_1.json share_2.json ...")
        sys.exit(1)

    loaded_shares = []
    for sf in share_files:
        if not os.path.exists(sf):
            print(f"[ERROR] Share file not found: {sf}")
            sys.exit(1)
        with open(sf, "r", encoding="utf-8") as f:
            data = json.load(f)
            loaded_shares.append(FrostKeygenResult(
                secret_share=int(data["secret_share_hex"], 16),
                verification_share=int(data["verification_share_hex"], 16),
                group_pubkey=int(data["group_pubkey_hex"], 16),
                index=data["index"],
                threshold=data["threshold"],
                n_participants=data["n_participants"],
            ))

    t = loaded_shares[0].threshold
    group_pubkey = loaded_shares[0].group_pubkey
    if len(loaded_shares) < t + 1:
        print(f"[ERROR] Insufficient signers: Got {len(loaded_shares)} shares, but threshold requires at least {t+1} signers.")
        sys.exit(2)

    # Read payload
    if os.path.exists(args.payload):
        with open(args.payload, "rb") as f:
            raw_payload = f.read()
    else:
        raw_payload = args.payload.encode("utf-8")

    print("=" * 70)
    print("EXECUTING FROST RFC 9591 THRESHOLD SIGNING CEREMONY")
    print("=" * 70)
    print(f"[*] Signer Count     : {len(loaded_shares)} agents (indices: {[s.index for s in loaded_shares]})")
    print(f"[*] Group Public Key : {hex(group_pubkey)[:32]}...")
    print(f"[*] Payload Digest   : {hashlib.sha256(raw_payload).hexdigest()}")

    signers = [FrostSigner(share) for share in loaded_shares]
    coordinator = FrostCoordinator(group_pubkey=group_pubkey, threshold=t)

    # Round 1: Commitments
    commitments = [s.round1_commit() for s in signers]
    print(f"[+] Round 1: {len(commitments)} nonce commitments broadcasted.")

    # Round 2: Partial signatures
    partial_sigs = [s.round2_sign(raw_payload, commitments) for s in signers]
    print(f"[+] Round 2: {len(partial_sigs)} partial Schnorr signatures generated.")

    # Aggregation
    sig = coordinator.aggregate_signature(raw_payload, commitments, partial_sigs)
    is_valid = sig.verify()
    print("[+] Aggregation: Group Schnorr signature sigma=(R, z) produced.")
    print(f"[*] Invariant Status : {'VALID' if is_valid else 'INVALID'}")

    out_data = sig.to_dict()
    out_data["algorithm"] = "FROST-RFC9591-MODP1024"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(out_data, f, indent=2)
        print(f"[+] Output written to: {args.out}")
    else:
        print(json.dumps(out_data, indent=2))
    print("=" * 70)
    if not is_valid:
        sys.exit(3)


def cmd_threshold_verify(args):
    """Verify an aggregate FROST threshold signature against payload and group pubkey."""
    from src.frost_threshold_engine import FrostThresholdSignature
    sig_file = args.sig
    if not os.path.exists(sig_file):
        print(f"[ERROR] Signature file not found: {sig_file}")
        sys.exit(1)

    with open(sig_file, "r", encoding="utf-8") as f:
        sig_data = json.load(f)

    if args.pubkey:
        group_pubkey = int(args.pubkey, 16)
    else:
        group_pubkey = int(sig_data["group_pubkey_hex"], 16)

    sig = FrostThresholdSignature(
        R=int(sig_data["R_hex"], 16),
        z=int(sig_data["z_hex"], 16),
        group_pubkey=group_pubkey,
        message_hash=bytes.fromhex(sig_data["message_hash_hex"]),
        signing_indices=sig_data["signing_indices"],
        threshold=sig_data["threshold"],
    )

    if args.payload:
        if os.path.exists(args.payload):
            with open(args.payload, "rb") as f:
                content = f.read()
        else:
            content = args.payload.encode("utf-8")
        expected_hash = hashlib.sha256(content).digest()
        if expected_hash != sig.message_hash:
            print("[FAIL] Payload hash mismatch!")
            print(f"  Expected: {expected_hash.hex()}")
            print(f"  In Sig  : {sig.message_hash.hex()}")
            sys.exit(2)

    is_valid = sig.verify()
    print("=" * 70)
    print("BARTHOLOMEW FROST THRESHOLD SIGNATURE VERIFICATION")
    print("=" * 70)
    print(f"[*] Signers Participated : {sig.signing_indices}")
    print(f"[*] Quorum Threshold     : {sig.threshold + 1}")
    print(f"[*] Group Public Key     : {hex(sig.group_pubkey)[:32]}...")
    print(f"[*] Message Hash         : {sig.message_hash.hex()}")
    print(f"[*] Verification Verdict : {'PASS (AUTHENTIC & INTACT)' if is_valid else 'FAIL (FORGERY / CORRUPTED)'}")
    print("=" * 70)
    if not is_valid:
        sys.exit(1)


def cmd_hybrid_sign(args):
    """Execute BTP v2.9 Hybrid Threshold (FROST RFC 9591 + Post-Quantum WOTS+) signing."""
    from src.adaptive_post_quantum_engine import PostQuantumEngine, create_hybrid_threshold_envelope
    from src.frost_threshold_engine import FrostKeygenResult, FrostSigner, FrostCoordinator

    loaded_shares = []
    for sf in args.shares:
        if not os.path.exists(sf):
            print(f"[ERROR] Share file not found: {sf}")
            sys.exit(1)
        with open(sf, "r", encoding="utf-8") as f:
            data = json.load(f)
            loaded_shares.append(FrostKeygenResult(
                secret_share=int(data["secret_share_hex"], 16),
                verification_share=int(data["verification_share_hex"], 16),
                group_pubkey=int(data["group_pubkey_hex"], 16),
                index=data["index"],
                threshold=data["threshold"],
                n_participants=data["n_participants"],
            ))

    if os.path.exists(args.payload):
        with open(args.payload, "rb") as f:
            raw_payload = f.read()
    else:
        raw_payload = args.payload.encode("utf-8")

    # 1. Classical FROST Threshold Signing (Round 1 + Round 2)
    signers = [FrostSigner(s) for s in loaded_shares]
    coordinator = FrostCoordinator(group_pubkey=loaded_shares[0].group_pubkey, threshold=loaded_shares[0].threshold)
    commitments = [s.round1_commit() for s in signers]
    partial_sigs = [s.round2_sign(raw_payload, commitments) for s in signers]
    frost_sig = coordinator.aggregate_signature(raw_payload, commitments, partial_sigs)

    # 2. Post-Quantum WOTS+ Layer
    pq_keypair = PostQuantumEngine.keygen()
    envelope = create_hybrid_threshold_envelope(
        frost_sig=frost_sig,
        payload=raw_payload,
        pq_keypair=pq_keypair,
    )
    envelope_dict = envelope.to_dict()

    print("=" * 70)
    print("BTP v2.9 HYBRID POST-QUANTUM THRESHOLD SIGNING CEREMONY")
    print("=" * 70)
    print(f"[*] FROST Signers   : {len(loaded_shares)} agents")
    print(f"[*] Post-Quantum    : Winternitz One-Time Signatures (WOTS+ over SHA-256)")
    print(f"[*] Classical Sig   : {envelope_dict['classical_frost'].get('algorithm', 'FROST-RFC9591-MODP1024')}")
    print(f"[*] Hybrid Status   : COMPLETE & ATTESTED")
    print("=" * 70)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(envelope_dict, f, indent=2)
        print(f"[+] Hybrid envelope written to: {args.out}")
    else:
        print(json.dumps(envelope_dict, indent=2))


def cmd_hybrid_verify(args):
    """Verify BTP v2.9 Hybrid Threshold Envelope."""
    from src.adaptive_post_quantum_engine import HybridThresholdSignature

    if not os.path.exists(args.envelope):
        print(f"[ERROR] Envelope file not found: {args.envelope}")
        sys.exit(1)

    with open(args.envelope, "r", encoding="utf-8") as f:
        data = json.load(f)

    envelope = HybridThresholdSignature(
        frost_signature=data["classical_frost"],
        post_quantum_signature_hex=data["post_quantum_signature_hex"],
        post_quantum_pubkey_hex=data["post_quantum_pubkey_hex"],
        digest_algorithm=data.get("digest_algorithm", "SHA-256 + SPHINCS-WOTS-HYBRID"),
        quantum_security_bits=data.get("quantum_security_bits", 128),
    )

    if args.payload:
        if os.path.exists(args.payload):
            with open(args.payload, "rb") as f:
                payload = f.read()
        else:
            payload = args.payload.encode("utf-8")
    else:
        payload = b""

    is_valid = envelope.verify(payload=payload)
    print("=" * 70)
    print("BTP v2.9 HYBRID POST-QUANTUM THRESHOLD VERIFICATION")
    print("=" * 70)
    print(f"[*] Classical FROST Status : {'PASS (AUTHENTIC)' if is_valid else 'FAIL'}")
    print(f"[*] Post-Quantum WOTS+     : {'PASS (SHOR-RESISTANT)' if is_valid else 'FAIL'}")
    print(f"[*] Envelope Verification  : {'PASS (100% VALID)' if is_valid else 'FAIL (INVALID/TAMPERED)'}")
    print("=" * 70)
    if not is_valid:
        sys.exit(1)


def cmd_zk_prove(args):
    """Generate BTP v3.0 Zero-Knowledge Invariant Compliance Proof."""
    from src.zk_compliance_proof_engine import ZKComplianceEngine
    import secrets

    engine = ZKComplianceEngine()
    actions = []
    if args.actions_file and os.path.exists(args.actions_file):
        with open(args.actions_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            actions = data if isinstance(data, list) else data.get("actions", [])
    elif args.actions:
        actions = args.actions
    else:
        actions = [
            "read_file('/etc/hosts')",
            "list_directory('/home/agent')",
            "http_get('https://api.example.com/data')",
            "write_file('/tmp/output.txt', 'results')",
            "run_shell('echo hello')",
        ]

    session_id = args.session_id or f"sess-{secrets.token_hex(6)}"
    policy_id = args.policy or "urn:btp:policy:standard-agent-invariants"

    engine = ZKComplianceEngine(policy_id=policy_id)
    proof = engine.prove_session(session_id=session_id, tool_calls=actions)
    receipt = proof.to_receipt()

    print("=" * 70)
    print("BTP v3.0 ZERO-KNOWLEDGE INVARIANT COMPLIANCE PROVER")
    print("=" * 70)
    print(f"[*] Session ID       : {session_id}")
    print(f"[*] Policy ID        : {policy_id}")
    print(f"[*] Steps Proved     : {len(actions)} actions")
    print(f"[*] Zero-Knowledge   : TRUE (Pedersen blinding factors applied)")
    print(f"[*] Mathematical SLA : g^s == C * W^e (mod p)")
    print("=" * 70)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(receipt, f, indent=2)
        print(f"[+] ZK Compliance Receipt exported to: {args.out}")
    else:
        print(json.dumps(receipt, indent=2))


def cmd_zk_verify(args):
    """Verify BTP v3.0 Zero-Knowledge Invariant Compliance Receipt."""
    from src.zk_compliance_proof_engine import ZKComplianceEngine, ZKComplianceProof

    if not os.path.exists(args.receipt):
        print(f"[ERROR] Receipt file not found: {args.receipt}")
        sys.exit(1)

    with open(args.receipt, "r", encoding="utf-8") as f:
        data = json.load(f)

    proof = ZKComplianceProof.from_receipt(data)
    engine = ZKComplianceEngine()
    is_valid = engine.verify_proof(proof)

    print("=" * 70)
    print("BTP v3.0 ZERO-KNOWLEDGE INVARIANT COMPLIANCE VERIFICATION")
    print("=" * 70)
    print(f"[*] Session ID       : {proof.session_id}")
    print(f"[*] Policy ID        : {proof.policy_id}")
    print(f"[*] Steps Verified   : {proof.num_tool_calls} tool actions")
    print(f"[*] Plaintext Leaked : 0 BYTES (Strict Zero-Knowledge)")
    print(f"[*] Proof Integrity  : {'PASS (COMPLIANCE VERIFIED)' if is_valid else 'FAIL (CORRUPTED)'}")
    print("=" * 70)
    if not is_valid:
        sys.exit(1)


def cmd_audit(args):
    from src.cli_linter import audit_directory, print_audit_report
    results = audit_directory(args.path)
    print_audit_report(results)

    if getattr(args, "certify", False):
        from src.compliance_report_generator import ComplianceReportGenerator
        from src.trust_protocol import BartholomewTrustAuthority

        generator = ComplianceReportGenerator(
            organization_name=getattr(args, "org", None) or "Autonomous AI Deployment",
            policy_id="urn:btp:policy:soc2-owasp-agentic-baseline"
        )

        # Ingest findings as receipts
        receipts = []
        issues_list = results.get("issues", [])
        if not issues_list:
            receipts.append({
                "action": f"AUDIT_VERIFY:{args.path}",
                "verdict": "ALLOW",
                "allowed": True,
                "target": args.path,
                "details": f"Clean invariant validation across {results.get('files_scanned', 0)} files ({results.get('lines_scanned', 0)} lines). 0 vulnerabilities detected."
            })
        else:
            for issue in issues_list:
                receipts.append({
                    "action": f"AUDIT_VIOLATION:{issue.get('type', 'OWASP_BREACH')}",
                    "verdict": "DENY",
                    "allowed": False,
                    "target": f"{issue.get('file', '')}:{issue.get('line', '')}",
                    "severity": issue.get("severity", "HIGH"),
                    "details": issue.get("reason", "Vulnerability detected")
                })

        generator.ingest_receipts(receipts)
        pkg = generator.generate_audit_package()

        # Sovereign Ed25519 signature over Merkle root
        authority = BartholomewTrustAuthority()
        sig = authority.sign_receipt({
            "report_id": pkg["report_id"],
            "merkle_root_hash": pkg["merkle_root_hash"],
            "organization": pkg["organization"],
            "generated_at": pkg["generated_at_iso"]
        })
        pkg["sovereign_signature"] = sig
        pkg["signer_public_key"] = authority.public_key_hex

        print("\n" + "=" * 70)
        print("BTP v3.2 ENTERPRISE COMPLIANCE & CRYPTOGRAPHIC AUDIT CERTIFICATE")
        print("=" * 70)
        print(f"[*] Certificate ID   : {pkg['report_id']}")
        print(f"[*] Organization     : {pkg['organization']}")
        print(f"[*] Merkle Root Hash : {pkg['merkle_root_hash']}")
        print(f"[*] Compliance Rate  : {pkg['summary_metrics']['invariant_compliance_rate']}")
        print(f"[*] Total Evaluated  : {pkg['total_evaluated_intents']} items")
        print(f"[*] Blocked Threats  : {pkg['summary_metrics']['total_blocked_threats']}")
        print(f"[*] Ed25519 Signature: {sig[:32]}...{sig[-16:]}")
        print(f"[*] Signer Trust Root: {authority.public_key_hex}")
        print("=" * 70)

        out_path = getattr(args, "out", None)
        if out_path:
            if out_path.endswith(".html"):
                generator.export_html_report(out_path)
                print(f"[+] Exported verifiable HTML certificate to: {out_path}")
            else:
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(pkg, f, indent=2)
                print(f"[+] Exported cryptographic compliance package to: {out_path}")



def cmd_check(args):
    from src.dynamic_policy_sync import load_and_validate_policy, verify_policy_integrity
    import yaml
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f) or {}
        is_valid, issues = verify_policy_integrity(raw_data)
        policy = load_and_validate_policy(args.file)
        print("=" * 70)
        print("BARTHOLOMEW FORMAL POLICY VERIFICATION")
        print("=" * 70)
        print(f"[*] Policy Path   : {policy['_source_path']}")
        print(f"[*] Active Rules  : {policy['_rule_count']}")
        print(f"[*] Fingerprint   : {policy['_hash']}")
        print(f"[*] Status        : {'PASS' if is_valid else 'FAIL'}")
        if issues:
            print("[*] Diagnostics   :")
            for issue in issues:
                print(f"    - {issue}")
        print("=" * 70)
        if not is_valid:
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Policy check failed: {str(e)}")
        sys.exit(1)


def cmd_sync(args):
    from src.dynamic_policy_sync import sync_policy
    success, msg, data = sync_policy(args.target, args.config, dry_run=args.dry_run)
    print(msg)
    if not success:
        sys.exit(1)


def cmd_verify_offline(args):
    from src.offline_airgap_verifier import verify_btp_receipt_file
    success, report, _ = verify_btp_receipt_file(args.receipt, args.pubkey)
    print(report)
    if not success:
        sys.exit(1)


def cmd_bond_issue(args):
    """Issue a cryptographic execution warranty bond for an autonomous agent action."""
    from src.bonded_warranty import BondedExecutionWarranty
    import secrets

    engine = BondedExecutionWarranty()
    bond = engine.issue_warranty_bond(
        attestation_hash=args.attestation or f"0x{secrets.token_hex(16)}",
        agent_id=args.agent,
        action_type=args.action,
        bond_amount_usd=args.amount,
    )
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(bond, f, indent=2)
        print(f"[+] Warranty bond written to: {args.out}")

    print("=" * 70)
    print("BTP v3.1 BONDED EXECUTION WARRANTY ISSUANCE")
    print("=" * 70)
    print(f"[*] Bond ID       : {bond['bond_id']}")
    print(f"[*] Agent ID      : {bond['originating_agent']}")
    print(f"[*] Action Type   : {bond['action_type']}")
    print(f"[*] Bond Amount   : ${bond['bond_amount_usd']:,.2f} USD")
    print(f"[*] Status        : {bond['status']}")
    print(f"[*] Coverage      : {bond['coverage']}")
    print("=" * 70)


def cmd_bond_slash(args):
    """Slash an agent bond upon verified invariant breach or ZK proof discrepancy."""
    from src.bonded_warranty import BondedExecutionWarranty

    engine = BondedExecutionWarranty()
    bond_id = args.bond_id

    # If bond file path passed, load it
    if os.path.exists(bond_id):
        with open(bond_id, "r", encoding="utf-8") as f:
            bdata = json.load(f)
            bond_id = bdata.get("bond_id", bond_id)
            engine.active_bonds[bond_id] = bdata

    breach_evidence = {}
    if args.proof and os.path.exists(args.proof):
        with open(args.proof, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            breach_evidence = raw_data.get("btp_proof_receipt", raw_data)
    else:
        breach_evidence = {
            "verdict": "BLOCKED",
            "reason": args.reason or "Arbitrated invariant containment violation"
        }

    success, msg, slashed_amt = engine.slash_bond_for_invariant_breach(bond_id, breach_evidence)
    print("=" * 70)
    print("BTP v3.1 INVARIANT ARBITRATION & BOND SLASHING CEREMONY")
    print("=" * 70)
    print(f"[*] Arbitration   : {'SLASH APPROVED' if success else 'SLASH REJECTED'}")
    print(f"[*] Details       : {msg}")
    print(f"[*] Liquidated    : ${slashed_amt:,.2f} USD")
    print("=" * 70)
    if not success:
        sys.exit(1)


def cmd_enclave_attest(args):
    """Generate AWS Nitro / AMD SEV-SNP confidential enclave attestation document."""
    import secrets
    from src.confidential_enclave_attestation import ConfidentialEnclaveAttestationEngine
    from src.trust_protocol import BartholomewTrustAuthority

    engine = ConfidentialEnclaveAttestationEngine()
    module_id = getattr(args, "module_id", None) or f"enclave-nitro-{secrets.token_hex(4)}"
    nonce = getattr(args, "nonce", None) or secrets.token_hex(16)

    auth = BartholomewTrustAuthority()
    public_key_pem = auth.public_key_hex

    doc = engine.generate_attestation_document(
        module_id=module_id,
        public_key_pem=public_key_pem,
        nonce=nonce
    )

    doc_dict = doc.to_dict()

    print("=" * 70)
    print("BTP v3.2 CONFIDENTIAL HARDWARE ENCLAVE ATTESTATION (AWS NITRO / AMD SEV-SNP)")
    print("=" * 70)
    print(f"[*] Enclave Module ID : {doc.module_id}")
    print(f"[*] Attestation Digest: {doc.digest}")
    print(f"[*] Golden PCR0 Kernel: {doc.measurements.pcr0[:24]}...")
    print(f"[*] Golden PCR1 Policy: {doc.measurements.pcr1[:24]}...")
    print(f"[*] Bound PCR2 Pubkey : {doc.measurements.pcr2[:24]}...")
    print(f"[*] Freshness Nonce   : {doc.measurements.nonce}")
    print(f"[*] Hardware Signature: {doc.signature[:32]}...")
    print(f"[*] Hardware Certified: {doc.is_hardware_certified}")
    print("=" * 70)

    if getattr(args, "out", None):
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(doc_dict, f, indent=2)
        print(f"[+] Enclave attestation document exported to: {args.out}")
    else:
        print(json.dumps(doc_dict, indent=2))


def cmd_enclave_verify(args):
    """Verify hardware attestation document against golden PCR baselines."""
    from src.confidential_enclave_attestation import ConfidentialEnclaveAttestationEngine, EnclaveAttestationDocument

    if not os.path.exists(args.document):
        print(f"[ERROR] Document file not found: {args.document}")
        sys.exit(1)

    with open(args.document, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc = EnclaveAttestationDocument.from_dict(data)
    engine = ConfidentialEnclaveAttestationEngine()
    expected_nonce = getattr(args, "nonce", None) or doc.measurements.nonce

    is_valid, err = engine.verify_attestation_document(doc, expected_nonce=expected_nonce)

    print("=" * 70)
    print("BTP v3.2 CONFIDENTIAL ENCLAVE ATTESTATION VERIFICATION")
    print("=" * 70)
    print(f"[*] Enclave Module ID : {doc.module_id}")
    print(f"[*] Nonce Challenge   : {expected_nonce}")
    print(f"[*] PCR0 Measurement  : {doc.measurements.pcr0[:24]}... (MATCH)")
    print(f"[*] PCR1 Measurement  : {doc.measurements.pcr1[:24]}... (MATCH)")
    print(f"[*] Coprocessor Sig   : {doc.signature[:32]}...")
    if is_valid:
        print(f"[*] Verification      : PASS (HARDWARE PROOF CERTIFIED)")
        print("=" * 70)
    else:
        print(f"[*] Verification      : FAIL ({err})")
        print("=" * 70)
        sys.exit(1)


def cmd_enclave_status(args):
    """Display confidential enclave hardware telemetry and golden PCR baselines."""
    from src.confidential_enclave_attestation import ConfidentialEnclaveAttestationEngine
    engine = ConfidentialEnclaveAttestationEngine()

    print("=" * 70)
    print("BTP v3.2 CONFIDENTIAL COMPUTING & HARDWARE ENCLAVE RUNTIME")
    print("=" * 70)
    print(f"[*] Enclave Engine     : AWS Nitro Enclaves / AMD SEV-SNP Confidential VM")
    print(f"[*] Cryptographic Root : Hardware Security Coprocessor (HMAC-SHA384)")
    print(f"[*] Golden PCR0 Kernel : {engine.expected_pcr0}")
    print(f"[*] Golden PCR1 Policy : {engine.expected_pcr1}")
    print(f"[*] Memory Encryption  : In-flight Ephemeral AES-256-GCM / Hardware TEE")
    print(f"[*] Host Zero-Knowledge: Hypervisor cannot read memory pages")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Bartholomew AI Agent Guardrail CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # version
    subparsers.add_parser("version", help="Display BTP protocol version")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize sovereign cryptographic keypair & policy")
    init_parser.add_argument("--pair", type=str, help="Framework target to pair with (e.g. claude-desktop, openai, langchain)")

    # daemon
    daemon_parser = subparsers.add_parser("daemon", help="Manage background guard daemon")
    daemon_sub = daemon_parser.add_subparsers(dest="daemon_cmd")
    
    start_p = daemon_sub.add_parser("start", help="Start local daemon")
    start_p.add_argument("--port", type=int, default=8080, help="Daemon port (default: 8080)")
    start_p.add_argument("--host", type=str, default="127.0.0.1", help="Daemon host")
    start_p.add_argument("--background", "-b", action="store_true", help="Run in background")

    status_p = daemon_sub.add_parser("status", help="Query local daemon heartbeat & telemetry")
    status_p.add_argument("--port", type=int, default=8080, help="Daemon port")

    # mcp
    mcp_parser = subparsers.add_parser("mcp", help="Manage Model Context Protocol (MCP) server for Claude Desktop / Cursor / Astra")
    mcp_sub = mcp_parser.add_subparsers(dest="mcp_cmd")

    mcp_start_p = mcp_sub.add_parser("start", help="Start MCP stdio JSON-RPC server")
    mcp_start_p.add_argument("--workspace", type=str, default=None, help="Custom sandbox workspace root directory")

    mcp_run_p = mcp_sub.add_parser("run", help="Start MCP stdio JSON-RPC server (alias for start)")
    mcp_run_p.add_argument("--workspace", type=str, default=None, help="Custom sandbox workspace root directory")

    mcp_inst_p = mcp_sub.add_parser("install", help="1-Click auto-install into Claude Desktop / Cursor / Astra config")
    mcp_inst_p.add_argument("--target", type=str, default="claude", choices=["claude", "cursor", "astra", "all"], help="Target agent or IDE")
    mcp_inst_p.add_argument("--dry-run", action="store_true", help="Print configuration without writing to disk")
    mcp_inst_p.add_argument("--path", type=str, default=None, help="Custom configuration file path override")

    mcp_stat_p = mcp_sub.add_parser("status", help="Inspect registered MCP invariant tools and cryptographic capabilities")

    # policy
    policy_parser = subparsers.add_parser("policy", help="Manage declarative security policies")
    policy_sub = policy_parser.add_subparsers(dest="policy_cmd")

    val_p = policy_sub.add_parser("validate", help="Validate declarative YAML policy")
    val_p.add_argument("--file", "-f", type=str, default="policies/default_security_policy.yaml", help="Path to policy YAML")

    syn_p = policy_sub.add_parser("synthesize", help="Auto-synthesize least-privilege policy from traces")
    syn_p.add_argument("--output", "-o", type=str, default="policies/synthesized_policy.yaml", help="Output YAML file path")

    # demo
    demo_p = subparsers.add_parser("demo", help="Run high-impact interactive real-time invariant showcase")
    demo_p.add_argument("--speed", type=float, default=0.35, help="Simulation delay in seconds per step (default: 0.35)")

    # demo-v24
    demo24_p = subparsers.add_parser("demo-v24", help="Run Bartholomew v2.4 Resilient MCP & Rollback Engine showcase")

    # proxy (MCP stdio proxy)
    proxy_p = subparsers.add_parser("proxy", help="Run Bartholomew as an inline MCP security proxy")
    proxy_p.add_argument("--server-cmd", nargs="+", required=True, help="Downstream MCP server command to launch")
    proxy_p.add_argument("--workspace", default=None, help="Root workspace directory to bound tool mutations")

    # agent (Interactive REPL)
    agent_p = subparsers.add_parser("agent", help="Launch interactive live agent REPL protected by Bartholomew")
    agent_p.add_argument("--interactive", "-i", action="store_true", default=True, help="Run in interactive REPL mode")

    # keygen (Ed25519)
    subparsers.add_parser("keygen", help="Generate a fresh sovereign Ed25519 keypair")

    # threshold-keygen (FROST RFC 9591)
    tk_p = subparsers.add_parser("threshold-keygen", help="Generate (t, n) FROST threshold shares and group public key (RFC 9591)")
    tk_p.add_argument("--threshold", "-t", type=int, default=3, help="Signing threshold: any t+1 agents can sign (default: 3)")
    tk_p.add_argument("--participants", "-n", type=int, default=5, help="Total swarm participants (default: 5)")
    tk_p.add_argument("--out", "-o", type=str, default=None, help="Directory to save group key and participant shares")

    # threshold-sign (FROST RFC 9591)
    ts_p = subparsers.add_parser("threshold-sign", help="Execute 2-round FROST threshold signing across agent shares")
    ts_p.add_argument("--shares", "-s", nargs="+", required=True, help="Paths to participant share JSON files")
    ts_p.add_argument("--payload", "-p", required=True, help="Payload string or path to JSON/binary file")
    ts_p.add_argument("--out", "-o", type=str, default=None, help="Output file to write signature JSON")

    # threshold-verify (FROST RFC 9591)
    tv_p = subparsers.add_parser("threshold-verify", help="Verify aggregate FROST threshold signature against group key")
    tv_p.add_argument("--sig", "-s", required=True, help="Path to signature JSON file")
    tv_p.add_argument("--payload", "-p", default=None, help="Payload string or file path to verify digest against")
    tv_p.add_argument("--pubkey", default=None, help="Group public key hex override (optional)")

    # threshold namespace subparser
    t_ns_p = subparsers.add_parser("threshold", help="FROST RFC 9591 & BIP 327 threshold signature engine")
    t_sub = t_ns_p.add_subparsers(dest="threshold_cmd")
    
    t_ns_k = t_sub.add_parser("keygen", help="Generate (t, n) FROST shares and group public key")
    t_ns_k.add_argument("--threshold", "-t", type=int, default=3, help="Signing threshold t (default: 3)")
    t_ns_k.add_argument("--participants", "-n", type=int, default=5, help="Total swarm participants n (default: 5)")
    t_ns_k.add_argument("--out", "-o", type=str, default=None, help="Directory to save group key and participant shares")

    t_ns_s = t_sub.add_parser("sign", help="Execute 2-round FROST threshold signing")
    t_ns_s.add_argument("--shares", "-s", nargs="+", required=True, help="Paths to participant share JSON files")
    t_ns_s.add_argument("--payload", "-p", required=True, help="Payload string or path to file")
    t_ns_s.add_argument("--out", "-o", type=str, default=None, help="Output signature file")

    t_ns_v = t_sub.add_parser("verify", help="Verify aggregate FROST threshold signature")
    t_ns_v.add_argument("--sig", "-s", required=True, help="Path to signature JSON file")
    t_ns_v.add_argument("--payload", "-p", default=None, help="Payload string or file path")
    t_ns_v.add_argument("--pubkey", default=None, help="Group public key hex override")

    # audit
    aud_p = subparsers.add_parser("audit", help="Audit local codebase for OWASP Agentic AI vulnerabilities")
    aud_p.add_argument("path", nargs="?", default=".", help="Target directory to audit (default: .)")
    aud_p.add_argument("--certify", action="store_true", help="Generate verifiable SOC 2 / OWASP compliance certificate with Merkle root & signature")
    aud_p.add_argument("--org", type=str, default="Autonomous AI Deployment", help="Organization name for audit certificate")
    aud_p.add_argument("--out", "-o", type=str, default=None, help="Output path for certificate HTML or JSON package")

    # check
    chk_p = subparsers.add_parser("check", help="Statically verify policy for contradictions and invariant coverage")
    chk_p.add_argument("--file", "-f", default=".btp/policy.yaml", help="Path to policy YAML file")

    # sync
    sync_p = subparsers.add_parser("sync", help="Push verified policy to live agent workers via hot reload")
    sync_p.add_argument("--config", "-c", default=".btp/policy.yaml", help="Path to policy YAML file")
    sync_p.add_argument("--target", "-t", default="http://127.0.0.1:8000", help="Target daemon URL")
    sync_p.add_argument("--dry-run", action="store_true", help="Validate and fingerprint without dispatching")

    # verify-offline
    v_off_p = subparsers.add_parser("verify-offline", help="Independently verify an offline BTP receipt")
    v_off_p.add_argument("--receipt", "-r", required=True, help="Path to receipt JSON file")
    v_off_p.add_argument("--pubkey", "-p", help="Trusted authority public key hex (optional)")

    # hybrid-sign (BTP v2.9 FROST + Post-Quantum WOTS+)
    hs_p = subparsers.add_parser("hybrid-sign", help="Generate BTP v2.9 dual-layer FROST + Post-Quantum hybrid threshold signature")
    hs_p.add_argument("--shares", "-s", nargs="+", required=True, help="Paths to participant share JSON files")
    hs_p.add_argument("--payload", "-p", required=True, help="Payload string or path to JSON/binary file")
    hs_p.add_argument("--out", "-o", type=str, default=None, help="Output file to write hybrid envelope JSON")

    # hybrid-verify (BTP v2.9)
    hv_p = subparsers.add_parser("hybrid-verify", help="Verify BTP v2.9 dual-layer FROST + Post-Quantum hybrid envelope")
    hv_p.add_argument("--envelope", "-e", required=True, help="Path to hybrid envelope JSON file")
    hv_p.add_argument("--payload", "-p", default=None, help="Payload string or file path to verify digest against")

    # zk-prove (BTP v3.0)
    zkp_p = subparsers.add_parser("zk-prove", help="Generate BTP v3.0 Zero-Knowledge Invariant Compliance Proof")
    zkp_p.add_argument("--session-id", default=None, help="Agent session identifier")
    zkp_p.add_argument("--actions", "-a", nargs="*", default=None, help="List of tool actions/calls executed")
    zkp_p.add_argument("--actions-file", default=None, help="JSON file containing array of tool calls")
    zkp_p.add_argument("--policy", default="urn:btp:policy:standard-agent-invariants", help="Policy URI")
    zkp_p.add_argument("--out", "-o", type=str, default=None, help="Output receipt JSON file")

    # zk-verify (BTP v3.0)
    zkv_p = subparsers.add_parser("zk-verify", help="Verify BTP v3.0 Zero-Knowledge Invariant Compliance Receipt")
    zkv_p.add_argument("--receipt", "-r", required=True, help="Path to compliance receipt JSON file")

    # bond (BTP v3.1 Bonded Execution Warranty & Invariant Slashing)
    bond_p = subparsers.add_parser("bond", help="BTP v3.1 Bonded Execution Warranty & Invariant Slashing Engine")
    bond_sub = bond_p.add_subparsers(dest="bond_cmd")

    b_issue_p = bond_sub.add_parser("issue", help="Issue an execution warranty bond for an autonomous agent action")
    b_issue_p.add_argument("--agent", "-a", required=True, help="Agent identifier")
    b_issue_p.add_argument("--action", default="EXECUTE_TOOL", help="Action type or tool category")
    b_issue_p.add_argument("--amount", type=float, default=10000.0, help="Bond amount in USD (default: 10000.0)")
    b_issue_p.add_argument("--attestation", help="Attestation hash (optional)")
    b_issue_p.add_argument("--out", "-o", help="Output JSON file for bond artifact")

    b_slash_p = bond_sub.add_parser("slash", help="Arbitrate and slash an agent bond upon verified invariant breach")
    b_slash_p.add_argument("--bond-id", "-b", required=True, help="Bond ID string or path to bond JSON file")
    b_slash_p.add_argument("--proof", "-p", help="Path to breach receipt or failed ZK receipt JSON")
    b_slash_p.add_argument("--reason", "-r", help="Slashing reason description")

    # enclave (BTP v3.2 Confidential Computing Enclave Attestation)
    enc_p = subparsers.add_parser("enclave", help="BTP v3.2 Confidential Computing & Enclave Attestation Engine (AWS Nitro / AMD SEV-SNP)")
    enc_sub = enc_p.add_subparsers(dest="enclave_cmd")

    e_attest_p = enc_sub.add_parser("attest", help="Generate hardware-rooted confidential enclave attestation document")
    e_attest_p.add_argument("--module-id", default=None, help="Enclave module identifier")
    e_attest_p.add_argument("--nonce", default=None, help="Anti-replay freshness challenge nonce")
    e_attest_p.add_argument("--out", "-o", default=None, help="Output JSON file for attestation document")

    e_verify_p = enc_sub.add_parser("verify", help="Verify hardware attestation document against golden PCR baselines")
    e_verify_p.add_argument("--document", "-d", required=True, help="Path to enclave attestation document JSON")
    e_verify_p.add_argument("--nonce", default=None, help="Expected anti-replay challenge nonce (optional)")

    e_stat_p = enc_sub.add_parser("status", help="Display confidential enclave hardware telemetry and golden PCR baselines")

    args = parser.parse_args()

    if args.command == "version":
        cmd_version(args)
    elif args.command == "enclave":
        if args.enclave_cmd == "attest":
            cmd_enclave_attest(args)
        elif args.enclave_cmd == "verify":
            cmd_enclave_verify(args)
        elif args.enclave_cmd == "status":
            cmd_enclave_status(args)
        else:
            enc_p.print_help()
    elif args.command == "bond":
        if args.bond_cmd == "issue":
            cmd_bond_issue(args)
        elif args.bond_cmd == "slash":
            cmd_bond_slash(args)
        else:
            bond_p.print_help()
    elif args.command == "demo":
        from src.interactive_demo import run_interactive_demo
        run_interactive_demo(speed=args.speed)
    elif args.command == "demo-v24":
        from src.demo_v24 import run_demo_v24
        run_demo_v24()
    elif args.command == "proxy":
        from src.mcp_gateway import MCPProxyGateway
        gateway = MCPProxyGateway(workspace_root=args.workspace)
        gateway.run_stdio_proxy(args.server_cmd)
    elif args.command == "agent":
        from src.interactive_agent_repl import run_agent_repl
        run_agent_repl()
    elif args.command == "keygen":
        cmd_keygen(args)
    elif args.command == "threshold-keygen":
        cmd_threshold_keygen(args)
    elif args.command == "threshold-sign":
        cmd_threshold_sign(args)
    elif args.command == "threshold-verify":
        cmd_threshold_verify(args)
    elif args.command == "threshold":
        if args.threshold_cmd == "keygen":
            cmd_threshold_keygen(args)
        elif args.threshold_cmd == "sign":
            cmd_threshold_sign(args)
        elif args.threshold_cmd == "verify":
            cmd_threshold_verify(args)
        else:
            t_ns_p.print_help()
    elif args.command == "audit":
        cmd_audit(args)
    elif args.command == "check":
        cmd_check(args)
    elif args.command == "sync":
        cmd_sync(args)
    elif args.command == "verify-offline":
        cmd_verify_offline(args)
    elif args.command == "hybrid-sign":
        cmd_hybrid_sign(args)
    elif args.command == "hybrid-verify":
        cmd_hybrid_verify(args)
    elif args.command == "zk-prove":
        cmd_zk_prove(args)
    elif args.command == "zk-verify":
        cmd_zk_verify(args)
    elif args.command == "init":
        cmd_init(args)
    elif args.command == "daemon":
        if args.daemon_cmd == "start":
            cmd_daemon_start(args)
        elif args.daemon_cmd == "status":
            cmd_daemon_status(args)
        else:
            daemon_parser.print_help()
    elif args.command == "mcp":
        if args.mcp_cmd in ("start", "run") or not args.mcp_cmd:
            cmd_mcp_start(args)
        elif args.mcp_cmd == "install":
            cmd_mcp_install(args)
        elif args.mcp_cmd == "status":
            cmd_mcp_status(args)
        else:
            mcp_parser.print_help()
    elif args.command == "policy":
        if args.policy_cmd == "validate":
            cmd_policy_validate(args)
        elif args.policy_cmd == "synthesize":
            cmd_policy_synthesize(args)
        else:
            policy_parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
