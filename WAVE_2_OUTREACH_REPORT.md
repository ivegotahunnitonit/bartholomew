# Bartholomew Wave 2 Community & HN Outreach Report

- **Dispatched At**: 2026-09-11 20:22:48 UTC
- **Total Recipients**: 5
- **Audience**: Hacker News AI builders, runtime security tool authors, YC S25 founders
- **Focus**: Dev-to-dev peer collaboration, open-source feedback, runtime benchmarking

---

### 1. dshapi

- **Email / Contact**: `dshapi@users.noreply.github.com`
- **Subject**: `Fellow HN builder: loved your post on runtime security for AI agents`
- **Status**: `DISPATCHED`

```text
Hey dshapi,

Saw your Show HN on runtime security for AI agents (preventing tool abuse and data exfiltration) on Hacker News.

We tackled this by moving the boundary directly inside the process memory (<35us AST gating before tool dispatch) rather than external LLM filters.

We open-sourced the kernel on PyPI (`pip install btp-guard`) and built a zero-setup in-browser playground where you can test simulated tool attacks and spend caps in sub-35 microseconds:
https://bartholomew.info/cookbook?ref=385d7775&source=hn

Zero pitch -- just wanted to connect dev-to-dev and see what you think of our approach to deterministic runtime gating. Would love to swap notes whenever you have a moment!

Best,
Alex
github.com/ivegotahunnitonit/bartholomew
```

**Interactive Playground Link**: [https://bartholomew.info/cookbook?ref=385d7775&source=hn](https://bartholomew.info/cookbook?ref=385d7775&source=hn)

---

### 2. thomaslwang

- **Email / Contact**: `thomaslwang@users.noreply.github.com`
- **Subject**: `Fellow HN builder: stopping AI agents from doing dumb things`
- **Status**: `DISPATCHED`

```text
Hey thomaslwang,

Saw your post on building runtime guardrails that stop AI agents from doing dumb things on Hacker News.

Loved the pragmatic approach. We took a similar deterministic angle with btp-guard to physically block catastrophic commands like DROP TABLE and rm -rf in Python before execution.

We open-sourced the kernel on PyPI (`pip install btp-guard`) and built a zero-setup in-browser playground where you can test simulated tool attacks and spend caps in sub-35 microseconds:
https://bartholomew.info/cookbook?ref=61dc0dd2&source=hn

Zero pitch -- just wanted to connect dev-to-dev and see what you think of our approach to deterministic runtime gating. Would love to swap notes whenever you have a moment!

Best,
Alex
github.com/ivegotahunnitonit/bartholomew
```

**Interactive Playground Link**: [https://bartholomew.info/cookbook?ref=61dc0dd2&source=hn](https://bartholomew.info/cookbook?ref=61dc0dd2&source=hn)

---

### 3. chendev2

- **Email / Contact**: `chendev2@users.noreply.github.com`
- **Subject**: `ClawCare & runtime agent skills security -- fellow builder`
- **Status**: `DISPATCHED`

```text
Hey chendev2,

Saw your Show HN on ClawCare (security scanner and runtime guard for AI agent skills) on Hacker News.

Really impressed with how you structured skill scanning. We built an in-process AST gating and Merkle receipt verification layer (btp-guard) and would love to see if there is potential for interoperability.

We open-sourced the kernel on PyPI (`pip install btp-guard`) and built a zero-setup in-browser playground where you can test simulated tool attacks and spend caps in sub-35 microseconds:
https://bartholomew.info/cookbook?ref=2b379849&source=hn

Zero pitch -- just wanted to connect dev-to-dev and see what you think of our approach to deterministic runtime gating. Would love to swap notes whenever you have a moment!

Best,
Alex
github.com/ivegotahunnitonit/bartholomew
```

**Interactive Playground Link**: [https://bartholomew.info/cookbook?ref=2b379849&source=hn](https://bartholomew.info/cookbook?ref=2b379849&source=hn)

---

### 4. windsor

- **Email / Contact**: `windsor@users.noreply.github.com`
- **Subject**: `Dedalus Labs (YC S25) -- agent sandboxing & execution safety`
- **Status**: `DISPATCHED`

```text
Hey windsor,

Saw your Launch HN for Dedalus Labs (Vercel for Agents) on Hacker News.

Scaling agent infrastructure requires both OS-level sandboxing and in-process tool safety so agents don't corrupt mounted state or drain API budgets.

We open-sourced the kernel on PyPI (`pip install btp-guard`) and built a zero-setup in-browser playground where you can test simulated tool attacks and spend caps in sub-35 microseconds:
https://bartholomew.info/cookbook?ref=4e1937f7&source=hn

Zero pitch -- just wanted to connect dev-to-dev and see what you think of our approach to deterministic runtime gating. Would love to swap notes whenever you have a moment!

Best,
Alex
github.com/ivegotahunnitonit/bartholomew
```

**Interactive Playground Link**: [https://bartholomew.info/cookbook?ref=4e1937f7&source=hn](https://bartholomew.info/cookbook?ref=4e1937f7&source=hn)

---

### 5. nivedit-jain

- **Email / Contact**: `nivedit-jain@users.noreply.github.com`
- **Subject**: `Scaling AI agents reliably -- fellow HN builder`
- **Status**: `DISPATCHED`

```text
Hey nivedit-jain,

Saw your Ask HN on scaling AI agents reliably in production on Hacker News.

The biggest reliability bottleneck we kept hitting was approval fatigue vs unconstrained runaway loops, which led us to build deterministic in-process AST safety bounds.

We open-sourced the kernel on PyPI (`pip install btp-guard`) and built a zero-setup in-browser playground where you can test simulated tool attacks and spend caps in sub-35 microseconds:
https://bartholomew.info/cookbook?ref=9aead5af&source=hn

Zero pitch -- just wanted to connect dev-to-dev and see what you think of our approach to deterministic runtime gating. Would love to swap notes whenever you have a moment!

Best,
Alex
github.com/ivegotahunnitonit/bartholomew
```

**Interactive Playground Link**: [https://bartholomew.info/cookbook?ref=9aead5af&source=hn](https://bartholomew.info/cookbook?ref=9aead5af&source=hn)

---

