#!/usr/bin/env bash
# ==============================================================================
# Bartholomew Cloud — 1-Command Google Cloud Run Deployment Script
# ==============================================================================
# Deploys the high-throughput SaaS Ingestion Engine to Google Cloud Run,
# configured for maximum capital efficiency with min-instances = 0.
# All compute costs will be absorbed directly by your Google Cloud credit pool.
# ==============================================================================

set -euo pipefail

SERVICE_NAME="bartolomew-cloud-engine"
REGION="${GCP_REGION:-us-central1}"
PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || echo '')}"

echo "===================================================================="
echo "  Deploying Bartholomew Cloud Ingestion Engine to Cloud Run"
echo "===================================================================="

if [ -z "$PROJECT_ID" ]; then
    echo "[ERROR] GCP Project ID not detected. Set GCP_PROJECT_ID or run 'gcloud config set project <ID>'."
    exit 1
fi

echo "[*] GCP Project: $PROJECT_ID"
echo "[*] Region:      $REGION"
echo "[*] Service:     $SERVICE_NAME"
echo ""

# Enable required Google Cloud APIs
echo "[1/3] Ensuring required GCP APIs are enabled..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    bigquery.googleapis.com \
    --project="$PROJECT_ID"

# Build and deploy container directly from source using Cloud Build
echo "[2/3] Deploying container directly to Google Cloud Run (scale-to-zero)..."
gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --region "$REGION" \
    --project "$PROJECT_ID" \
    --platform managed \
    --allow-unauthenticated \
    --min-instances 0 \
    --max-instances 10 \
    --concurrency 80 \
    --memory 512Mi \
    --cpu 1 \
    --timeout 15 \
    --set-env-vars="ENV=production,BTP_TIER=ENTERPRISE_CLOUD"

# Retrieve public Cloud Run URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --project "$PROJECT_ID" --format 'value(status.url)')

echo ""
echo "===================================================================="
echo "  [SUCCESS] Bartholomew Cloud Engine is LIVE!"
echo "===================================================================="
echo "  Public Service URL: $SERVICE_URL"
echo "  Health Endpoint:    $SERVICE_URL/health"
echo "  Telemetry Ingest:   $SERVICE_URL/api/v1/telemetry/ingest"
echo "  SOC 2 Dossier:      $SERVICE_URL/api/v1/compliance/soc2-export"
echo "===================================================================="
