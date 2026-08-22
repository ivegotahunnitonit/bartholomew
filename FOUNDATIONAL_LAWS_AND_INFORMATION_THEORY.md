# Foundational Laws, Information Theory & Epistemic Grounding

## 1. The Probabilistic Dilemma: Information Theory & Entropy Bounds

Large Language Models (LLMs) are autoregressive token predictors operating over conditional probability distributions:

$$P(w_t \mid w_1, w_2, \dots, w_{t-1}) = \text{softmax}(W \cdot h_t)$$

Because token selection is inherently probabilistic (governed by temperature sampling and top-$p$ nucleus distributions), an LLM does not function as a deterministic finite automaton (DFA). 

### The Inevitability of Stochastic Hallucination
For any non-trivial generation sequence of length $N$, the joint probability of generating a non-conforming or fabricated state token $\epsilon$ is strictly non-zero:

$$P(\text{Hallucination}) = 1 - \prod_{t=1}^N (1 - P(\text{Error}_t)) > 0$$

Hallucinations are not merely "bugs" to be patched with prompt engineering; they are an inherent thermodynamic and statistical property of generative predictive text.

### Bartholomew as Shannon's Deterministic Error-Correcting Filter
By Shannon's Noisy-Channel Coding Theorem, reliable transmission can be achieved across a noisy channel if and only if an appropriate error-detecting and error-correcting code is applied.

Bartholomew serves as this deterministic channel code:
1. **Input**: Stochastic, high-entropy LLM tool proposal.
2. **Deterministic Filter**: AST parsing, threshold gating, and epistemic grounding.
3. **Output**: Verified, RFC 8785 canonical Ed25519-signed execution receipt.

---

## 2. Epistemic Grounding & Retrieval-Augmented Attestation (RAA)

Traditional Retrieval-Augmented Generation (RAG) injects unstructured context into an LLM prompt. However, standard RAG cannot guarantee that the model will not fabricate new entity IDs during mutation phases.

Bartholomew implements **Retrieval-Augmented Attestation (RAA)**:

### The Read-Before-Write Provenance Invariant
1. **Grounded Read Phase**: When an agent performs read actions (e.g. database select, file read), Bartholomew registers the returned entity IDs and cryptographic hashes into the agent's active provenance pool.
2. **Mutation Verification Phase**: When the agent proposes a write or mutation action (`UPDATE`, `DELETE`, `TRANSFER`), Bartholomew verifies that all target identifiers exist within the verified provenance pool.
3. **Ungrounded Denial**: If an agent attempts to mutate an entity ID that was never retrieved in verified context, the action is blocked as an `UNGROUNDED_FABRICATION_DENIAL`.

---

## 3. Fundamental Laws Governing Agent Evolution

### Law 1: Ashby's Law of Requisite Variety
> *"Only variety can destroy variety."*

To control an agent whose internal state space $S$ can generate diverse tool proposals, the invariant security gate must possess a variety of declarative rules $V_{\text{gate}}$ that is equal to or greater than the disturbance variety $V_{\text{agent}}$:

$$V_{\text{gate}} \ge V_{\text{agent}}$$

Bartholomew satisfies this through composable declarative YAML policy rules that evaluate spend caps, AST syntax trees, path containment, and rate distributions simultaneously.

---

### Law 2: The Law of Diminishing Marginal Utility (LDMU)
> *"As an agent repeats an identical exploratory action, the marginal informational utility of each subsequent attempt decays exponentially."*

$$MU(n) = e^{-\lambda \cdot (n - 1)}$$

* $\lambda$: Action fatigue decay constant (default: $0.35$).
* $n$: Attempt counter for identical action signatures.
* **Invariant Thresholds**:
  * $MU \ge 0.40 \implies \text{ALLOW}$
  * $0.15 \le MU < 0.40 \implies \text{THROTTLE}$ (Prevents rate-limit exhaustion)
  * $MU < 0.15 \implies \text{CO\_SIGN\_REQUIRED}$ (Halts runaway retry loops)

---

### Law 3: Landauer's Principle & Epistemic Irreversibility
> *"The erasure of information or remediation of unauthorized side effects requires physical thermodynamic work."*

Preventing an invalid action at the pre-flight gate requires negligible computational work ($<50 \text{ }\mu\text{s}$ CPU time). Once an ungrounded or destructive command commits side effects to a production database or remote API, the thermodynamic and financial cost of data recovery approaches infinity.

---

### Law 4: Rice's Theorem & The Halting Boundary
> *"Any non-trivial semantic property of a universal computer program is undecidable."*

Because an LLM cannot self-verify whether its own generated code will halt safely or respect security boundaries, security gating must be decoupled from the model and executed by deterministic external supervisors (AST compilers, eBPF filters, and hermetic sandboxes).
