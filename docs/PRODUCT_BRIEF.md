# Bartholomew Product Brief

## Positioning

Bartholomew is the authorization and policy layer for autonomous agents.

It evaluates whether an agent is allowed to take an action before execution, enforces policy, records proof of the decision, and emits telemetry for auditability and downstream governance.

## Problem

Autonomous agents can act on real systems, APIs, databases, shell commands, and external tools without a trustworthy gate at the action boundary. Traditional prompt guardrails are too late because they inspect text rather than execution.

## Solution

Bartholomew sits at the point of action.

It inspects the action payload, checks it against policy and risk rules, and decides:

- ALLOW
- DENY
- reason
- rule identifier
- latency
- receipt hash

This gives developers and operators a clear, auditable decision point before autonomous execution proceeds.

## Core capability

The current MVP supports:

- destructive shell detection
- dangerous SQL detection
- secret leakage detection
- prompt injection detection
- blocked action types under policy
- verdict and receipt output
- telemetry emission

## Value

Bartholomew reduces operational risk for autonomous systems by enforcing policy at the execution boundary.

This creates value in four ways:

1. Safety: risky actions are denied before they run.
2. Trust: decisions are recorded with proof.
3. Observability: telemetry can show how agents are behaving over time.
4. Governance: policy can be centralized and adapted for team or enterprise control.

## Strategic direction

The next step is not to expand into a broad platform prematurely. The right direction is to deepen the core product around:

- agent authorization
- policy enforcement
- proof and auditability
- usage telemetry
- hosted policy controls for teams and enterprises

Later, delegated spend controls and machine-to-machine settlement can be layered on top of the trust model once the authorization layer is mature.

## Current state

The MVP is working and verified.

The core authorization gate passes its tests and demonstrates safe and unsafe action handling in a minimal end-to-end flow.

## Revenue path

The revenue path is not telemetry alone. The revenue path is a trusted authorization and governance layer for autonomous execution.

That can lead to:

- developer or team subscriptions
- hosted policy service
- enterprise governance and audit reporting
- usage-based control planes
- later delegated spend controls and machine-to-machine payment flows

## Bottom line

Bartholomew’s strongest product identity is not "security suite" or "platform." It is "the authorization layer for autonomous agents."
