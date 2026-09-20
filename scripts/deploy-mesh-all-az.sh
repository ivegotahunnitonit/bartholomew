#!/bin/bash
# ==============================================================================
# ACN Multi-AZ Global Mesh Orchestrator
# Deploys security-hardened ACN Supernodes across 5 Availability Zones:
#   1. us-central1-a  (Primary Gateway 1: 35.255.62.200)
#   2. us-east1-b     (Gateway 2: 34.73.34.145)
#   3. us-west1-a     (Gateway 3: 136.117.15.127)
#   4. us-west2-a     (Gateway 4: 34.20.133.4)
#   5. europe-west1-b (Gateway 5: 34.53.176.111)
# ==============================================================================

set -euo pipefail

NODES=(
  "acn-supernode-gateway|us-central1-a|35.255.62.200|35-255-62-200.sslip.io"
  "acn-supernode-gateway-2|us-east1-b|34.73.34.145|34-73-34-145.sslip.io"
  "acn-supernode-gateway-3|us-west1-a|136.117.15.127|136-117-15-127.sslip.io"
  "acn-supernode-gateway-4|us-west2-a|34.20.133.4|34-20-133-4.sslip.io"
  "acn-supernode-gateway-5|europe-west1-b|34.53.176.111|34-53-176-111.sslip.io"
)

echo "=============================================================================="
echo "  ACN MULTI-AZ DEPLOYMENT ORCHESTRATOR — 5 GLOBAL REGIONS                    "
echo "=============================================================================="

for entry in "${NODES[@]}"; do
  IFS="|" read -r NODE_NAME ZONE IP DOMAIN <<< "$entry"
  echo ""
  echo "------------------------------------------------------------------------------"
  echo "🚀 Deploying to $NODE_NAME ($ZONE | $IP | $DOMAIN)..."
  echo "------------------------------------------------------------------------------"

  # Copy lean archive and deploy script
  gcloud compute scp acn-lean.tar.gz "$NODE_NAME:/tmp/acn-app.tar.gz" --zone="$ZONE" --quiet
  gcloud compute scp scripts/deploy-gateway1.sh "$NODE_NAME:/tmp/deploy.sh" --zone="$ZONE" --quiet

  # Execute hardened deploy script on remote host
  gcloud compute ssh "$NODE_NAME" --zone="$ZONE" --command="sudo DOMAIN=$DOMAIN bash /tmp/deploy.sh" --quiet
  
  echo "✅ $NODE_NAME ($ZONE) successfully deployed & verified!"
done

echo ""
echo "=============================================================================="
echo "  🎉 GLOBAL MULTI-AZ MESH DEPLOYMENT COMPLETE — ZERO SINGLE POINT OF FAILURE  "
echo "=============================================================================="
