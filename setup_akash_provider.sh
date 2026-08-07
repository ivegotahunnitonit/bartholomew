#!/bin/bash
# ===========================================================
# ACN Akash Provider Setup Script
# Run this on a Linux machine or via Cloud Shell after GKE cluster is ready
# ===========================================================

set -e

CLUSTER_NAME="acn-provider-cluster"
ZONE="us-central1-a"
AKASH_WALLET="akash1rlhstdys7sjxpv9en397mpeskzha9ukj9yy4fg"
PROVIDER_DOMAIN="acn-provider.run.app"

echo "==> Step 1: Get GKE credentials"
gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE

echo "==> Step 2: Install Helm"
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

echo "==> Step 3: Add Akash Helm repo"
helm repo add akash https://akash-network.github.io/helm-charts
helm repo update

echo "==> Step 4: Install cert-manager (required for Akash TLS)"
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
kubectl rollout status deployment cert-manager -n cert-manager --timeout=120s

echo "==> Step 5: Create Akash provider namespace"
kubectl create namespace akash-services 2>/dev/null || true

echo "==> Step 6: Install Akash Provider via Helm"
helm install akash-provider akash/provider \
  --namespace akash-services \
  --set "provider.address=$AKASH_WALLET" \
  --set "provider.domain=$PROVIDER_DOMAIN" \
  --set "provider.attributes[0].key=region" \
  --set "provider.attributes[0].value=us-central" \
  --set "provider.attributes[1].key=tier" \
  --set "provider.attributes[1].value=community" \
  --set "bidprice_cpu_scale=0.001" \
  --set "bidprice_memory_scale=0.0005" \
  --set "bidprice_storage_scale=0.00001" \
  --set "bidprice_endpoint_scale=0" \

echo "==> Step 7: Check provider pod status"
kubectl get pods -n akash-services

echo ""
echo "=============================="
echo "Akash Provider Setup Complete!"
echo "Wallet: $AKASH_WALLET"
echo "Domain: $PROVIDER_DOMAIN"
echo "=============================="
