# **BTP v2.4 Zenodo Publication Master Guide**
### **Formal Academic Deposition Package & Permanent DOI Registry**

---

## **1. Executive Summary & Value of Zenodo**
**Zenodo** (hosted by CERN and the European Open Science Cloud / OpenAIRE) issues **permanent, immutable Digital Object Identifiers (DOIs)** (format: `10.5281/zenodo.XXXXXXX`). Depositing Bartholomew v2.4 on Zenodo achieves:
1. **Permanent Academic Prior Art & Timestamp**: Cryptographically proves our priority on the *Transactional MCP Micro-Rollback* and *Chained Merkle Trajectory* mechanisms.
2. **Indexing in Major Research Engines**: Automatically indexed by Google Scholar, Semantic Scholar, DBLP, and CORE.
3. **Citable Preprint for arXiv / IEEE / ACM**: Allows venture capital funds, enterprise CISOs, and framework developers to formally cite Bartholomew in whitepapers and technical literature.

---

## **2. Deposition Assets Ready in Workspace**
* **Camera-Ready PDF Manuscript:** [`paper_v2_4.pdf`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/paper_v2_4.pdf)
* **Pre-Formatted Metadata Schema:** [`zenodo.json`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/zenodo.json)
* **Automated Upload Client:** [`scripts/zenodo_publish.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/scripts/zenodo_publish.py)

---

## **3. Method A: 1-Click Publishing via Zenodo REST API**

1. Log in to [Zenodo](https://zenodo.org/) (or log in with your GitHub account).
2. Generate a Personal Access Token:
   * Go to **Settings &rarr; Applications &rarr; Personal access tokens &rarr; New token**
   * Name: `bartholomew-publish`
   * Scopes: Check `deposit:actions` and `deposit:write`.
3. In your terminal, set the environment variable and run the publish script:
   ```powershell
   $env:ZENODO_ACCESS_TOKEN="your_zenodo_token_here"
   python scripts/zenodo_publish.py
   ```
4. The script will:
   * Submit the metadata from `zenodo.json`
   * Upload `paper_v2_4.pdf`
   * Output your reserved DOI (`10.5281/zenodo.XXXXXXX`) and draft preview URL.

---

## **4. Method B: 3-Minute Web GUI Submission**

If you prefer uploading through the browser:

1. **Navigate to New Upload:** Go to [https://zenodo.org/deposit/new](https://zenodo.org/deposit/new).
2. **Upload Files:** Drag and drop [`paper_v2_4.pdf`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/paper_v2_4.pdf) and click **Start upload**.
3. **Fill Required Metadata Fields:**
   * **Resource type:** `Publication` &rarr; `Preprint` (or `Working paper`)
   * **Title:** 
     ```text
     Bartholomew Trust Protocol (BTP v2.4): A Transactional Model Context Protocol (MCP) Security Proxy with Sub-5µs Copy-on-Write Rollbacks and Chained Merkle Trajectories for Autonomous AI Agents
     ```
   * **Authors:** `Alemayehu, Itsub` | Affiliation: `Bartholomew Autonomous Systems / Bartholomew AI`
   * **Description / Abstract:** Paste the abstract text from [`zenodo.json`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/zenodo.json).
   * **License:** `Creative Commons Attribution 4.0 International (CC-BY-4.0)`
   * **Keywords:** `Model Context Protocol`, `MCP Proxy`, `AI Agent Security`, `Transactional Rollbacks`, `Copy-on-Write`, `RFC 8785`, `Ed25519`, `Merkle Trajectory Graphs`, `OWASP LLM Top 10`.
4. **References Section (Add the 10 Formal Citations below):**
5. Click **Save draft** &rarr; **Publish**!

---

## **5. Formal Academic References Included in Publication**

Every mechanism in Bartholomew v2.4 is grounded in established cryptographic and distributed systems literature:

1. **Canonical JSON Serialization:**
   > Bray, T. (2020). *JSON Canonicalization Scheme (JCS)*. RFC 8785, Internet Engineering Task Force. https://doi.org/10.17487/RFC8785  
   *Grounds our bit-level payload hashing before cryptographic signing.*

2. **Edwards-Curve Digital Signatures:**
   > Josefsson, S., & Liusvaara, I. (2017). *Edwards-Curve Digital Signature Algorithm (EdDSA)*. RFC 8032, Internet Engineering Task Force. https://doi.org/10.17487/RFC8032  
   *Grounds our 64-byte Ed25519 digital attestations with zero nonces reuse vulnerability.*

3. **Tool Protocol Specification:**
   > Anthropic. (2024). *The Model Context Protocol (MCP) Specification*. https://modelcontextprotocol.io  
   *Grounds our inline JSON-RPC proxy interface for Claude Desktop and Cursor.*

4. **Cryptographic Hash Trees:**
   > Merkle, R. C. (1987). *A Digital Signature Based on a Conventional Encryption Function*. Advances in Cryptology — CRYPTO '87, LNCS vol 293, pp. 369–378. Springer. https://doi.org/10.1007/3-540-48184-2_32  
   *Grounds our Chained Merkle Trajectory Graph ($H_i = \text{SHA256}(H_{i-1} \parallel \text{JCS}(\text{receipt}_i))$).*

5. **Empirical AI Safety Framework:**
   > OWASP Foundation. (2025). *OWASP Top 10 for Large Language Model Applications (v2.0)*. https://owasp.org/www-project-top-10-for-large-language-model-applications/  
   *Grounds our AST invariant gates targeting LLM02 (Sensitive Information Disclosure) and LLM05 (Improper Output Handling).*

6. **Logical Clock Ordering:**
   > Lamport, L. (1978). *Time, Clocks, and the Ordering of Events in a Distributed System*. Communications of the ACM, 21(7), 558–565. https://doi.org/10.1145/359545.359563  
   *Grounds our temporal validity window and monotonic sequence constraints.*

7. **Transactional Memory Primitives:**
   > Shavit, N., & Touitou, N. (1997). *Software Transactional Memory*. Distributed Computing, 10(2), 99–116. https://doi.org/10.1007/s004460050028  
   *Grounds our in-memory Copy-on-Write micro-snapshotting runtime.*

8. **Distributed Filesystem Semantics:**
   > Howard, J. H., et al. (1988). *Scale and Performance in a Distributed File System*. ACM Transactions on Computer Systems (TOCS), 6(1), 51–81.  
   *Grounds our workspace root boundary containment checks (`os.path.commonpath`).*

9. **Software Architectural Styles:**
   > Garlan, D., & Shaw, M. (1993). *An Introduction to Software Architecture*. Advances in Software Engineering and Knowledge Engineering, 1–39.  
   *Grounds our transparent proxy / interceptor architecture.*

10. **Bartholomew Core Specification:**
    > Alemayehu, I. (2026). *Bartholomew Trust Protocol (BTP v2.4): Formal Architectural Specification and Empirical Performance Benchmarks*. Bartholomew AI Labs Research Preprints.
