"""
BTP v2.2 GitHub Action Runner Script
Validates AI agent Pull Requests and tool actions in GitHub Actions CI workflows.
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from standalone_btp_verifier import independent_verify_btp_receipt

def main():
    parser = argparse.ArgumentParser(description="BTP v2.2 GitHub Action Verifier")
    parser.add_argument("--trusted-root", required=True, help="Hex-encoded Ed25519 root pubkey")
    parser.add_argument("--receipt", required=True, help="Path to BTP receipt JSON")
    parser.add_argument("--payload", required=True, help="Path to candidate payload JSON")
    parser.add_argument("--recipient", default="", help="Expected target recipient identifier")
    parser.add_argument("--strict", default="true", help="Fail build on invalid receipt")

    args = parser.parse_args()

    print("=" * 80)
    print("  BTP v2.2 GITHUB ACTION: AGENT CRYPTOGRAPHIC EXECUTION GUARD")
    print("=" * 80)

    # Check files exist
    if not os.path.exists(args.receipt):
        print(f"::error::BTP receipt file not found: {args.receipt}")
        if args.strict.lower() == "true":
            sys.exit(1)
        sys.exit(0)

    if not os.path.exists(args.payload):
        print(f"::error::Candidate payload file not found: {args.payload}")
        if args.strict.lower() == "true":
            sys.exit(1)
        sys.exit(0)

    with open(args.receipt, "r", encoding="utf-8") as f:
        receipt_data = json.load(f)

    with open(args.payload, "r", encoding="utf-8") as f:
        payload_data = json.load(f)

    trusted_roots = [r.strip() for r in args.trusted_root.split(",") if r.strip()]

    ok, msg = independent_verify_btp_receipt(
        receipt_json_str=receipt_data,
        candidate_payload=payload_data,
        trusted_root_pubkeys=trusted_roots,
        expected_recipient_context=args.recipient if args.recipient else None
    )

    if ok:
        print(f"\n[PASS] BTP Attestation Validated: {msg}")
        print("::notice title=BTP Agent Guard::Cryptographic proof verified 100% offline.")
        sys.exit(0)
    else:
        print(f"\n[FAIL] BTP Attestation Rejected: {msg}")
        print(f"::error title=BTP Agent Guard Rejected::{msg}")
        if args.strict.lower() == "true":
            sys.exit(1)
        sys.exit(0)

if __name__ == "__main__":
    main()
