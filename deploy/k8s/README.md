# Bartholomew Trust Protocol (BTP Guard v5.4.10) — Kubernetes Deployment

Enterprise deployment package for running Bartholomew Guard as an in-process sidecar or cluster-wide Layer-7 execution gateway.

## Architecture

```text
[Agent Pod / Swarm Worker] 
        │
        ▼ (Local IPC / localhost:8080)
[Bartholomew Guard Sidecar (v5.4.10)]  <── Sub-35µs AST Invariant Gate & Merkle Receipts
        │
        ├─► [ALLOW] ──► OS Syscall / External LLM API
        └─► [VETO]  ──► Drops execution, issues signed compliance receipt
```

## Quickstart: Helm Installation

### 1. Deploy via Helm

```bash
helm upgrade --install bartholomew-guard ./k8s \
  --namespace btp-security \
  --create-namespace \
  --set image.tag="5.4.10" \
  --set policy.spendCapUsd=500.00
```

### 2. Verify Pod Status

```bash
kubectl get pods -n btp-security -l app.kubernetes.io/name=bartholomew-guard
```

### 3. Check Liveness & Metrics

```bash
kubectl port-forward svc/bartholomew-guard 8080:8080 -n btp-security
curl http://localhost:8080/health
```

---

## Standalone Docker / VPC Deployment

For isolated VPC deployments (AWS ECS, Google Cloud Run private, Docker Compose):

```bash
docker run -d \
  --name btp-guard-sidecar \
  -p 8080:8080 \
  -e BTP_STRICT_MODE=true \
  -e BTP_MAX_SPEND_CAP_USD=100.00 \
  ghcr.io/bartholomew-ai/bartholomew-sidecar:5.4.10
```

## Support & Enterprise Consultation

For custom VPC architectures, AWS PrivateLink, or SOC 2 Type II audit packs:

- Email: `security@bartholomew.info`
- Web: [https://bartholomew.info](https://bartholomew.info)
