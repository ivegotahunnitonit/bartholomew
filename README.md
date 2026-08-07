# Autonomous Circularity Network (ACN)

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg?style=flat-square)](https://github.com/ivegotahunnitonit/autonomous-circularity-network)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE)
[![Base Mainnet](https://img.shields.io/badge/Base-USDC-blueviolet.svg?style=flat-square)](https://base.org)
[![DePIN Ready](https://img.shields.io/badge/DePIN-Akash%20%7C%20Render%20%7C%20Flux-orange.svg?style=flat-square)](https://akash.network)
[![API Version](https://img.shields.io/badge/API-v4.1%20Production-green.svg?style=flat-square)](#-api-endpoints)

> **ACN** is a high-throughput, peer-to-peer decentralized mesh orchestrator for autonomous compute, AI batch inference, cryptographic document attestation, and DePIN protocol execution. Built for zero-latency execution with 100% direct settlement into verified wallets.

---

## ⚡ Revenue & Core Service Architecture

ACN features **4 direct revenue streams** operating without 3rd-party intermediary delays:

| Revenue Engine | Service Description | Pricing / Rate | Settlement Target |
|---|---|---|---|
| 📜 **Digital Document Notary** | SHA-256 Proof-of-Existence & Notary Attestation | **$5.00 – $25.00 / stamp** | Base USDC (`0xaD38221a68...`) |
| 🧠 **Batch AI Inference Studio** | Multi-Tenant Token Metered Code & Text Processing | **$0.002 – $0.005 / 1k tok** | Base USDC (`0xaD38221a68...`) |
| 🖥️ **Akash Compute Hosting** | Decentralized Containerized Workload Bidding | **$AKT / Block** | Akash Wallet (`akash1y55...`) |
| 🤖 **24/7 Fast Bounty Hunter** | Automated USD/USDC Paid GitHub Cash Scanner | **$23 – $100+ / bounty** | Base USDC (`0xaD38221a68...`) |

---

## 💳 Supported Payment Gateways

ACN accepts direct transfers across 7 payment methods with 0% relay fee:
- 🔵 **Base Mainnet USDC:** `0xaD38221a686318aB1049fa5D60fA5b15DBB73ba4`
- 🟣 **Solana SOL / USDC:** `4k3Dyjzvzp8eMZWUXbB4Q6dG65k5BvT8R5p9`
- 🟠 **Bitcoin Native:** `bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh`
- 🔴 **Akash $AKT:** `akash1y557yjut3zxlfpd3p0elet4t2w5hermd69p8k7`
- 🟢 **Ethereum / Arbitrum / Polygon:** `0xaD38221a686318aB1049fa5D60fA5b15DBB73ba4`
- 💳 **Stripe Direct Processing:** Merchant Secret Key Configured
- 🅿️ **PayPal Direct Receiver:** Client ID & Receiver Configured

---

## ✨ Quick Start

```bat
start.bat
```

Double-click **`start.bat`** (or run it from a terminal). It will:
1. Launch the ACN Supernode Orchestrator.
2. Open the Command Center at **http://localhost:8080** automatically.
3. Start the 24/7 fast revenue daemon.

To stop the node, run **`stop.bat`**.

---

## 🛠️ REST API Endpoints

### 1. Digital Notary Attestation
```bash
POST /api/notary/stamp
Content-Type: application/json

{
  "document_title": "Bill of Lading #BOL-99201",
  "document_content": "Raw freight shipment manifest data...",
  "category": "bill_of_lading",
  "tier": "express_onchain"
}
```

### 2. Multi-Currency Invoice Generation
```bash
POST /api/payment/invoice
Content-Type: application/json

{
  "amount_usd": 50.0,
  "currency": "USDC",
  "service": "inference"
}
```

### 3. Batch AI Inference
```bash
POST /api/inference
Content-Type: application/json

{
  "prompt": "Analyze market opportunities for DePIN GPU compute",
  "task_type": "code",
  "max_tokens": 1024,
  "priority": 2
}
```

---

## 🛡️ Security & Zero-Cost Policy
- **$0.00 Outgoing Cost Rule:** All workers run locally or on free-tier allocations.
- **Key Isolation:** Private keys are locked in encrypted storage (`.env`) and never exposed to git commits.
- **Single-Use Tokens:** State parameters and signatures enforce timing-safe checks and single-use anti-replay validation.

---

## 📜 License
MIT License. Created by Autonomous Circularity Network Developers.
