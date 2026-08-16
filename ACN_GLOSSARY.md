# Autonomous Circularity Network (ACN) — Glossary of Terms

A complete reference guide for circular economy terms, commercial feedstock categories, network roles, and financial settlement definitions used in ACN.

---

## 1. Commercial Bulk Feedstocks & Materials

### HDPE Plastic Waste & Plastic Pellets
* **Definition**: Post-industrial High-Density Polyethylene (HDPE) scrap from containers and manufacturing lines.
* **Circularity**: Plastic scrap is cleaned, shredded, and re-extruded into **Plastic Pellets** used directly by manufacturing plants to mold new products.

### Spent Brewer Grain (BSG)
* **Definition**: Organic byproduct remaining after brewing beer (barley, malt, grains).
* **Circularity**: Rich in protein and fiber, spent grain is matched with agricultural farms as livestock feed or mushroom cultivation substrate.

### Scrap Metal & Industrial Steel
* **Definition**: Metal offcuts, stampings, and structural steel from demolition or fabrication.
* **Circularity**: Recycled directly into electric arc furnaces (EAF) to produce new structural steel with 75% lower carbon emissions.

### Industrial Solvents & Recovery Chemicals
* **Definition**: Chemical cleaning agents, degreasers, and process solvents used in pharmaceutical and chemical manufacturing.
* **Circularity**: Distilled and recovered through chemical recycling nodes to re-enter industrial cleaning loops.

---

## 2. Network Topology & Roles

### Supernode Gateway
* **Definition**: High-throughput cloud instance (e.g. `acn-supernode-gateway` on GCP) that runs continuous sub-1ms matchmaking, serves public REST APIs (`:8090`), and handles cross-regional trade routing.

### Peer Node / Broker Node
* **Definition**: A regional node (`denver_node`, `salt_lake_node`) that hosts local listings and routes trades through intermediate supernodes to resolve distant buyer/seller matches.

### P2P Gossip Protocol
* **Definition**: Decentralized node discovery mechanism where supernodes continuously exchange active peer routing tables (`P2PManager.ts`) to maintain live network connectivity.

---

## 3. Trade Matching & Mechanics

### Waste vs. Need Listings
* **Waste Listing**: A supply declaration from a facility with byproduct materials to sell/dispose.
* **Need Listing**: A demand declaration from a manufacturing buyer seeking recycled feedstock inputs.

### Linear Matchmaker
* **Definition**: The algorithmic engine (`Matchmaker.ts`) that calculates geographic distance, material compatibility, pricing thresholds, and net cost savings to automatically pair Waste and Need listings.

### Multi-Hop Routing Path
* **Definition**: When a buyer and seller are in different geographic regions, the matchmaker routes the deal through intermediate broker nodes (e.g. `denver_node` -> `broker-peer` -> `salt_lake_node`).

### ECDSA Listing Signature
* **Definition**: An elliptic curve cryptographic signature (`CryptoUtils.ts`) attached to every listing to verify authenticity and prevent counterfeit listings.

---

## 4. Financial Settlement & Fees

### System Settlement Fee (5%)
* **Definition**: The 5% fee collected by the ACN platform on every completed circular trade transaction.

### Multi-Hop Routing Toll (1.5%)
* **Definition**: An additional 1.5% toll earned by supernodes acting as intermediate transit brokers for routing cross-regional trades.

### EVM Escrow Settlement
* **Definition**: Smart contract locking (`EscrowSettlement.ts`) where buyer funds are held in escrow until delivery hash verification (`0xa249...`) unlocks funds to the seller and routes royalties.

### Multi-Channel Payout Clearing
* **Definition**: Automated disburser (`PaymentManager.ts`) supporting **Stripe**, **PayPal**, **Bitcoin**, and **Lightning Network** payouts.

---

## 5. Key Metrics

### GMV (Gross Material Volume)
* **Definition**: Total dollar value of physical materials matched across the exchange (e.g. $30,000 USD).

### Net Revenue
* **Definition**: Actual platform cash earnings (5% of GMV = $1,500 USD) deposited directly into your Treasury.
