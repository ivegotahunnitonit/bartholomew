# 🏛️ Akash Community Grant Proposal: ACN High-Uptime Provider Node & Open AI Services

## 📌 Project Overview
- **Project Name**: Autonomous Circularity Network (ACN) Compute Provider Node & Open AI Inference Infrastructure
- **Applicant**: ACN Core Team
- **Grant Category**: Infrastructure / Provider Expansion / AI Compute Services
- **Requested Amount**: $2,500 USD (equivalent in $AKT)
- **Live Provider Address**: `akash1y557yjut3zxlfpd3p0elet4t2w5hermd69p8k7`
- **Network**: Akash Mainnet (`akashnet-2`)

---

## 🚀 Executive Summary
The Autonomous Circularity Network (ACN) has provisioned and launched a production-grade, GKE-backed **Akash Compute Provider Node** equipped with automated telemetry, hostname routing, and native Kubernetes hardware discovery.

This proposal requests community pool funding to support sustained provider operations, fund tenant bid deposits (`AKASH_BID_DEPOSIT`), and host open, low-latency AI inference microservices (FastAPI / Ray / vLLM) accessible to the Akash developer ecosystem.

---

## 🛠️ Infrastructure Capabilities & Technical Specifications

| Metric | Specification |
|---|---|
| **Host Cluster** | Google Kubernetes Engine (GKE) `acn-provider-cluster` (`us-central1-a`) |
| **Allocatable CPU** | 7.84 vCPU Cores |
| **Allocatable RAM** | 27.8 GB RAM |
| **Ephemeral Storage** | 94.1 GB Disk |
| **On-Chain Identity** | `akash1y557yjut3zxlfpd3p0elet4t2w5hermd69p8k7` |
| **TLS Domain** | `provider.acn-provider.app` |
| **Active Operators** | `operator-hostname`, `operator-inventory`, `operator-inventory-hardware-discovery` |

---

## 🎯 Deliverables & Timeline

### Milestone 1: High-Uptime Compute Provider Operation (Month 1-3)
- Maintain >99.9% uptime for the GKE-backed Akash compute provider node.
- Automatically bid on incoming tenant workloads using dynamic CPU/Memory/Storage scaling algorithms (`bidpricecpuscale=0.004`).

### Milestone 2: Open AI Inference Endpoint Deployment (Month 2)
- Deploy public, open-access AI inference endpoints (vLLM / Ray) hosted directly on Akash compute leases.
- Provide developer documentation and open-source benchmarks for Akash-hosted AI workloads.

---

## 💰 Budget Breakdown

| Item | Description | Cost ($AKT) |
|---|---|---|
| **Compute Reserve** | GKE Node Pool operational costs for 3 months | $1,500 USD in AKT |
| **Bid Deposits** | On-chain `AKASH_BID_DEPOSIT` reserves for high-volume lease bidding | $500 USD in AKT |
| **AI Inference Hosting** | Hosting open AI endpoints on Akash compute leases | $500 USD in AKT |
| **Total** | | **$2,500 USD in AKT** |

---

## 🔗 Verification & On-Chain Proofs
- **Provider Status**: On-chain query returns active provider identity:
  ```bash
  provider-services query provider get akash1y557yjut3zxlfpd3p0elet4t2w5hermd69p8k7
  ```
- **On-Chain Tx Hashes**:
  - `MsgUpdateProvider`: `0942F329BA01C5C94D836F1C84B66BB93AD05D8165726E4B155CA9A4E278F917`
  - `MsgCreateCertificate`: `470698EDE3FC05CF08427C3EFACC11201650DF913D7A67C6B90D463D1A4C329B`
