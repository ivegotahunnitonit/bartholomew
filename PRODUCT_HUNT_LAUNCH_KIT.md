# Product Hunt Launch Kit: Bartholomew v2.4

Use this kit to schedule or launch Bartholomew on Product Hunt: [https://www.producthunt.com/posts/new](https://www.producthunt.com/posts/new)

---

## 1. Core Listing Metadata

* **Product Name**: Bartholomew
* **Tagline** (max 60 characters):
  ```text
  The sub-5µs transactional execution harness for AI agents
  ```
* **Links**:
  * Website: `https://bartholomew.info`
  * GitHub: `https://github.com/ivegotahunnitonit/bartholomew`
  * npm: `https://www.npmjs.com/package/btp-guard`
  * PyPI: `https://pypi.org/project/btp-guard/`
* **Pricing**: Free / Open Source (Apache-2.0)
* **Topics / Tags**: Developer Tools, Artificial Intelligence, Open Source, Security, Tech

---

## 2. Short Description (max 260 characters)

```text
Prompt guardrails fail when models get smart. Bartholomew is an inline execution harness for AI agents (Claude, Cursor) that provides atomic 2µs filesystem micro-rollbacks, in-flight secret scrubbing, and offline Merkle audit trails before your OS is touched.
```

---

## 3. First Maker Comment (To post immediately upon launch)

```text
Hey Product Hunt community!

We built Bartholomew because we were tired of watching coding agents (like Claude and Cursor) break development environments.

Existing safety tools treat agent actions like web requests: they slap the model with a 403 Forbidden error. Because LLMs lack execution context, they interpret this as a puzzle to solve—panicking into infinite retry loops, attempting slightly obfuscated variants of the same command, or leaving half-written dirty files behind.

We approached this from database transaction theory: What if agent execution was treated like an atomic database transaction with BEGIN and ROLLBACK?

Bartholomew operates directly between the model and your operating system:
1. In-Memory Micro-Rollbacks (<2.3µs): Before any mutating tool runs, it captures an in-memory byte snapshot. If a boundary check or AST invariant trips, pristine disk state is restored in 2.3 microseconds with zero orphaned files.
2. Constructive Diagnostics: Instead of an opaque crash, the harness returns structured JSON-RPC remediation hints so the model legitimately changes its plan instead of trying to hack around the gate.
3. In-Flight Secret Scrubbing (0.82µs): Inbound tool args and outbound stdout streams are scrubbed in-flight for OpenAI, Anthropic, AWS, and GitHub keys before reaching context logs.
4. Offline Merkle Receipts: Every action is chained and signed with Ed25519 (Hi = SHA256(Hi-1 || Receipt_i)), verifiable 100% offline.

You can inspect the entire simulation right now in your terminal without installing anything:
$ npx btp-guard

Or install via Python:
$ pip install btp-guard

Everything is 100% open source under Apache 2.0. We'd love to hear how you manage dirty workspace state and runaway agent loops in your workflows!
```

---

## 4. Media & Asset Checklist
* Thumbnail: `web/dist/favicon.svg` or `web/dist/founder_avatar.jpg`
* Gallery Image 1: Hero Banner (`web/dist/assets/hero-banner.png` or screenshot of `https://bartholomew.info`)
* Gallery Image 2: Terminal showcase running `npx btp-guard`
* Gallery Image 3: Interactive Playground from `https://bartholomew.info#playground`
