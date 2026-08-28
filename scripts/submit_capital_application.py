"""
Bartholomew Global Capital Application & Grant Submission Assistant
===================================================================
Automates dossier formatting, field generation, and 10-at-a-time batch submission
for global grants, venture accelerators, and innovation funds.

Usage:
  python scripts/submit_capital_application.py --batch 1
  python scripts/submit_capital_application.py --target "YC"
  python scripts/submit_capital_application.py --list
"""

import sys
import os
import json
import argparse

DOSSIER = {
    "company_name": "Bartholomew Autonomous Systems",
    "legal_entity": "Bartholomew Protocol (Sole Proprietorship / Corp)",
    "website": "https://bartholomew.info",
    "founder": "Itsub Bartholomew",
    "email": "help@bartholomew.info",
    "location": "Canada / Global",
    "one_line_pitch": "The sub-50µs in-memory deterministic invariant gate and cryptographic attestation protocol for autonomous AI agents.",
    "problem": (
        "As autonomous AI agents (LangGraph, CrewAI, AutoGen, Amazon Bedrock) transition from passive chatbots to "
        "autonomous actors executing shell commands, SQL mutations, and financial transfers, existing cloud guardrails "
        "impose 1,500 ms latency and 80% higher token billing while failing under alert fatigue. There is zero cryptographic "
        "non-repudiation for enterprise SOC 2 compliance."
    ),
    "solution": (
        "Bartholomew provides a sub-50 microsecond in-memory polyglot AST invariant gate and FIPS 186-5 Ed25519 attestation "
        "engine that intercepts destructive actions (DROP TABLE, rm -rf, API key leaks) before OS process execution, "
        "cutting Bedrock guardrail bills by 80% with zero IPC and zero background daemons."
    ),
    "traction": (
        "1. Capital Backing: $4,200+ USD in non-dilutive hyperscaler backing (AWS: $1,100, Google Cloud: $2,400, MongoDB: $500, Azure: $200).\n"
        "2. Live Registries: Globally indexed on PyPI (pip install btp-guard) and npm (npm install btp-guard).\n"
        "3. Benchmarks: 38 µs decision latency across 1,000,000 stress test payloads with 18/18 CI security test gates passing clean.\n"
        "4. IP: Comprehensive US Provisional Patent specification compiled covering deterministic invariant state gating."
    ),
    "tech_stack": "Python, Rust/C FFI, TypeScript, RFC 8785 Canonical JSON (JCS), FIPS 186-5 Ed25519 Cryptography, AWS CDK, Docker.",
    "revenue_model": (
        "Enterprise source-available license ($499 - $2,500 / month) for fleets exceeding free tier, AWS Marketplace Private Offers, "
        "and 1% autonomous inter-agent settlement fee rate on the decentralized BTP trust network."
    )
}

BATCH_1 = [
    {
        "id": "1",
        "name": "Y Combinator (W26 / S26)",
        "url": "https://apply.ycombinator.com",
        "capital": "$500,000 USD (SAFE)",
        "type": "Venture Accelerator",
        "questions": {
            "Company URL": DOSSIER["website"],
            "What is your company going to make?": DOSSIER["one_line_pitch"],
            "Why did you choose this idea?": "Every company deploying agent swarms is terrified of unverified tool execution, infinite retry loops, and $20k overnight cloud bills.",
            "What is new about what you make?": "Sub-50µs in-memory evaluation instead of 1.5s cloud guardrails, paired with RFC 8785 Ed25519 cryptographic receipts.",
            "How much traction do you have?": DOSSIER["traction"]
        }
    },
    {
        "id": "2",
        "name": "NRC-IRAP (National Research Council Canada)",
        "url": "https://nrc.canada.ca/en/support-technology-innovation/nrc-irap-funding-process",
        "capital": "$50,000 - $250,000 CAD (Non-Dilutive)",
        "type": "Government R&D Grant",
        "questions": {
            "Project Title": "Deterministic Invariant Compiler Gating & Epistemic Non-Repudiation for Autonomous Multi-Agent Swarms",
            "Technical Innovation": "Applying Rice's Theorem to AST delta analysis and FIPS 186-5 asymmetric attestation to achieve sub-50µs execution verification.",
            "Commercial Potential": "Global AI agent security and cost reduction market across AWS Bedrock and Azure OpenAI enterprise clients.",
            "R&D Methodology": "Formal invariant verification, 18-suite continuous integration fuzzing, and eBPF kernel trajectory monitoring."
        }
    },
    {
        "id": "3",
        "name": "AWS Generative AI Accelerator",
        "url": "https://aws-startup-lofts.com/global/programs/accelerator/generative-ai",
        "capital": "$300,000 in AWS Credits + Direct VC Demo Day",
        "type": "Hyperscaler Growth Fund",
        "questions": {
            "AWS Architecture": "AWS Bedrock Converse API, AWS CDK Construct (aws-cdk-bartholomew-guard), AWS Marketplace Private Offers.",
            "Value to AWS": "Cuts enterprise customer Bedrock guardrail latency from 1.5s to 38µs, driving higher Bedrock inference adoption."
        }
    },
    {
        "id": "4",
        "name": "Google for Startups Cloud AI Program",
        "url": "https://cloud.google.com/startup/ai",
        "capital": "$350,000 USD (Cloud Credits & AI Grant)",
        "type": "Cloud AI Grant",
        "questions": {
            "Product Description": DOSSIER["one_line_pitch"],
            "Google Cloud Usage": "Vertex AI agent monitoring, Google Cloud KMS attestation signing, and Firebase Global Hosting."
        }
    },
    {
        "id": "5",
        "name": "Creative Destruction Lab (CDL AI Stream)",
        "url": "https://creativedestructionlab.com/locations/toronto/",
        "capital": "Mentorship + $100k - $1M Angel Syndicates",
        "type": "Deep Tech Stream",
        "questions": {
            "Innovation Summary": "Hardware and in-memory cryptographic bounding for autonomous multi-agent systems.",
            "Founding Team": "100% focused on mathematical invariant systems and autonomous agent security."
        }
    },
    {
        "id": "6",
        "name": "NVIDIA Inception Global Program",
        "url": "https://www.nvidia.com/en-us/startups/",
        "capital": "Compute Discounts, Hardware Grants, & Inception VC Access",
        "type": "Hardware & Ecosystem Partner",
        "questions": {
            "Technical Focus": "Accelerating LLM agent tool calling and low-latency invariant evaluation on local GPU/CPU memory."
        }
    },
    {
        "id": "7",
        "name": "Techstars AI Accelerator",
        "url": "https://www.techstars.com/accelerators",
        "capital": "$120,000 USD",
        "type": "Global Accelerator",
        "questions": {
            "Application Summary": DOSSIER["solution"],
            "Current Traction": DOSSIER["traction"]
        }
    },
    {
        "id": "8",
        "name": "Anthropic AI Safety & Red Teaming Grant",
        "url": "https://www.anthropic.com",
        "capital": "$10,000 - $100,000 USD (Non-Dilutive)",
        "type": "AI Safety Grant",
        "questions": {
            "Research Proposal": "Formalizing deterministic AST invariant boundaries against Claude tool use prompt injection escapes."
        }
    },
    {
        "id": "9",
        "name": "OpenAI Superalignment & Safety Grant",
        "url": "https://openai.com",
        "capital": "$15,000 - $100,000 USD (Non-Dilutive)",
        "type": "AI Safety Grant",
        "questions": {
            "Research Proposal": "Autonomous invariant enforcement and cryptographic state verification in multi-agent tool execution."
        }
    },
    {
        "id": "10",
        "name": "HF0 (Hacker Fellowship Zero)",
        "url": "https://www.hf0.com",
        "capital": "$500,000 USD",
        "type": "Residency Accelerator",
        "questions": {
            "Traction & Product": DOSSIER["traction"]
        }
    }
]


def print_batch(batch_num):
    print("=" * 80)
    print(f"  GLOBAL CAPITAL PIPELINE — BATCH {batch_num} (10 VERIFIED TARGETS)")
    print("=" * 80)
    for t in BATCH_1:
        print(f"\n[{t['id']}] {t['name']}")
        print(f"    Capital: {t['capital']} | Type: {t['type']}")
        print(f"    Portal:  {t['url']}")
        print(f"    Key Form Answers Prepared:")
        for q, a in t["questions"].items():
            print(f"      • {q}: {a[:90]}...")
    print("\n" + "=" * 80)


def print_target_detail(target_id_or_name):
    match = None
    for t in BATCH_1:
        if target_id_or_name.lower() in t["name"].lower() or target_id_or_name == t["id"]:
            match = t
            break
    if not match:
        print(f"[!] Target '{target_id_or_name}' not found.")
        return

    print("=" * 80)
    print(f"  TARGET DOSSIER: {match['name']}")
    print(f"  Capital: {match['capital']} | Type: {match['type']}")
    print(f"  Direct Link: {match['url']}")
    print("=" * 80)
    for q, a in match["questions"].items():
        print(f"\n[FIELD] {q}")
        print(f"{a}")
    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Capital Submission Assistant")
    parser.add_argument("--batch", type=int, default=1, help="Batch number (1-5)")
    parser.add_argument("--target", type=str, help="Specific target name or ID (e.g. YC, IRAP, AWS)")
    parser.add_argument("--list", action="store_true", help="List all targets in pipeline")
    args = parser.parse_args()

    if args.target:
        print_target_detail(args.target)
    elif args.list or args.batch:
        print_batch(args.batch)


if __name__ == "__main__":
    main()
