#!/usr/bin/env bash
# ==============================================================================
# Bartholomew Cloud — Custom Domain & SSL Provisioning Script
# ==============================================================================
# Automates mapping `cloud.bartholomew.info` to the Google Cloud Run service
# with automatic Google-managed SSL/TLS certificates.
# ==============================================================================

set -euo pipefail

SERVICE_NAME="bartolomew-cloud-engine"
DOMAIN="cloud.bartholomew.info"
REGION="us-central1"
PROJECT_ID="acn-26670"

echo "===================================================================="
echo "  Bartholomew Cloud Custom Domain & SSL Setup"
echo "===================================================================="
echo "[*] Service: $SERVICE_NAME"
echo "[*] Domain:  $DOMAIN"
echo "[*] Region:  $REGION"
echo "[*] Project: $PROJECT_ID"
echo ""

echo "[1/2] Attempting to create Cloud Run domain mapping..."
if gcloud beta run domain-mappings create \
    --service="$SERVICE_NAME" \
    --domain="$DOMAIN" \
    --region="$REGION" \
    --project="$PROJECT_ID" 2>&1; then
    echo "[SUCCESS] Domain mapping created successfully!"
else
    echo ""
    echo "[NOTE] Google Cloud requires domain ownership verification before mapping."
    echo "Follow these two quick steps in your DNS provider (Cloudflare, Namecheap, Google Domains):"
    echo ""
    echo "--- Option A: Cloudflare Proxy (Recommended - Instant Free SSL) ---"
    echo "1. Go to your Cloudflare DNS Dashboard for bartholomew.info"
    echo "2. Add a new CNAME Record:"
    echo "     Type:    CNAME"
    echo "     Name:    cloud"
    echo "     Target:  bartolomew-cloud-engine-322603900775.us-central1.run.app"
    echo "     Proxy:   Proxied (Orange Cloud ON)"
    echo "3. In SSL/TLS settings, ensure Encryption Mode is set to 'Full' or 'Full (strict)'."
    echo ""
    echo "--- Option B: Google Managed Certificate ---"
    echo "1. Run: gcloud domains verify bartholomew.info"
    echo "2. Add the provided TXT record to your DNS settings."
    echo "3. Re-run this script to bind the domain."
fi

echo ""
echo "===================================================================="
