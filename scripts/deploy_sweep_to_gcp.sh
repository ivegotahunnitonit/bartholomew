#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════
#  Deploy Treasury Sweep to GCP albyhub VM
#  Run this from your LOCAL machine (has gcloud configured).
#
#  Usage:
#    ./scripts/deploy_sweep_to_gcp.sh <YOUR_ELECTRUM_ADDRESS>
#
#  Example:
#    ./scripts/deploy_sweep_to_gcp.sh bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
# ══════════════════════════════════════════════════════════════════

set -euo pipefail

GCP_INSTANCE="albyhub"
GCP_ZONE="us-central1-a"
GCP_PROJECT="acn-26670"
REMOTE_SCRIPT_DIR="/opt/albyhub/scripts"
COLD_WALLET_ADDRESS="${1:-}"

if [[ -z "$COLD_WALLET_ADDRESS" ]]; then
  echo "Usage: $0 <electrum_cold_wallet_address>"
  echo "Example: $0 bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
  exit 1
fi

echo "📦 Copying sweep script to GCP VM..."
gcloud compute scp scripts/treasury_sweep.sh \
  "${GCP_INSTANCE}:${REMOTE_SCRIPT_DIR}/treasury_sweep.sh" \
  --zone="$GCP_ZONE" \
  --project="$GCP_PROJECT"

echo "🔧 Setting up on VM..."
gcloud compute ssh "$GCP_INSTANCE" \
  --zone="$GCP_ZONE" \
  --project="$GCP_PROJECT" \
  --command="
    sudo mkdir -p ${REMOTE_SCRIPT_DIR} /opt/albyhub/logs
    sudo chmod +x ${REMOTE_SCRIPT_DIR}/treasury_sweep.sh
    sudo chown -R \$(whoami) /opt/albyhub/scripts /opt/albyhub/logs

    # Set the cold wallet address in env
    sudo bash -c 'echo \"COLD_WALLET_ADDRESS=${COLD_WALLET_ADDRESS}\" >> /opt/albyhub/.env'

    # Install cron job: runs daily at midnight UTC
    (crontab -l 2>/dev/null; echo \"0 0 * * * COLD_WALLET_ADDRESS=${COLD_WALLET_ADDRESS} ${REMOTE_SCRIPT_DIR}/treasury_sweep.sh >> /opt/albyhub/logs/sweeps.log 2>&1\") | crontab -

    echo '✅ Cron job installed:'
    crontab -l | grep treasury_sweep
  "

echo ""
echo "✅ Treasury sweep deployed!"
echo "   Schedule : Daily at midnight UTC"
echo "   Threshold: 50,000 sats (configurable via SWEEP_THRESHOLD_SATS)"
echo "   Reserve  : 5,000 sats retained for routing"
echo "   Dest     : ${COLD_WALLET_ADDRESS}"
echo ""
echo "   Monitor logs: gcloud compute ssh ${GCP_INSTANCE} --zone=${GCP_ZONE} -- 'tail -f /opt/albyhub/logs/sweeps.log'"
