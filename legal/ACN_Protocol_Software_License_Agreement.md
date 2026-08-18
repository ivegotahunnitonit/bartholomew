# AUTONOMOUS CIRCULARITY NETWORK (ACN) PROTOCOL SOFTWARE LICENSE AGREEMENT

**EFFECTIVE DATE:** July 18, 2026
**LICENSOR:** Bartholomew AI Contributors (hereinafter referred to as the "Licensor" or "Founder")
**LICENSEE:** Any entity or individual running an active node on the Autonomous Circularity Network (hereinafter referred to as the "Licensee")

---

### PREAMBLE
WHEREAS, the Licensor, Bartholomew AI Contributors, is the sole inventor, designer, and owner of the Bartholomew matching engine and the Autonomous Circularity Network (ACN) decentralized protocol;
WHEREAS, the Licensee wishes to operate a node to facilitate, match, and settle industrial materials circular transactions and collect network matching fees; and
WHEREAS, the Licensor is willing to grant the Licensee a limited, conditional, proprietary license to execute and run the protocol codebase under the strict terms detailed below.

NOW, THEREFORE, the parties agree as follows:

---

### SECTION 1: LICENSE GRANT
1.  **Scope**: Subject to compliance with all terms, the Licensor grants the Licensee a non-exclusive, non-transferable, revocable, and conditional license to run the ACN node software on their local hardware to connect to the P2P network.
2.  **No Modification**: The Licensee is prohibited from modifying, decompiling, reverse-engineering, or creating derivative works of the Bartholomew matching engine, gossip schemas, or cryptographic verification logic without the express, written, signed consent of Bartholomew AI Contributors.
3.  **No Redistribution**: The Licensee may not distribute, sub-license, rent, lease, or lease-to-own the software, nor make the codebase available to third parties outside the decentralized protocol's normal operations.

---

### SECTION 2: PROTOCOL TRANSACTION FEES
1.  **Fee Share**: In consideration for the license to use the protocol, the node automatically routes coordination fees calculated by the `FEE_RATE` (nominally 10% of gross circular matching savings) on all accepted matches.
2.  **Settlement Routing**: All fees earned on matches involving the Licensee's node will be settled and distributed cryptographically according to the ACN protocol specifications:
    *   Fees paid to the coordinator node address.
    *   Withdrawals routed to Newton or Electrum addresses verified by the Licensor.
3.  **Audit Rights**: The Licensor retains the right to cryptographically audit the Licensee's transaction logs and SQLite state data via peer status endpoints to verify that fee rates and matching protocols are adhered to without modification.

---

### SECTION 3: INTELLECTUAL PROPERTY & ATTRIBUTION
1.  **Ownership**: All right, title, and interest in and to the software, the ACN protocol, the name "Bartholomew Protocol," and all related intellectual property remain exclusively with Bartholomew AI Contributors.
2.  **Attribution**: Any deployment, public-facing interface, or fork of the protocol must preserve all copyright notices, founding declarations, and digital signatures attributing the original design to Bartholomew AI Contributors.

---

### SECTION 4: TERM AND TERMINATION
1.  **Revocation**: This license is effective until terminated. The Licensor reserves the right to revoke this license and blacklist/disconnect the Licensee's node from the peer routing tables if the Licensee violates any section of this agreement, fails signature verification checks, or bypasses network fee settlements.
2.  **Effect of Termination**: Upon termination, the Licensee must immediately stop running the node process and delete all local copies of the codebase.

---

### EXECUTION AND ACCORD
This agreement is deemed signed and binding upon the Licensee upon execution of the `src/index.ts` node runtime or inclusion of the node on the peer networks.

*Established and filed on July 18, 2026, by Bartholomew AI Contributors.*
