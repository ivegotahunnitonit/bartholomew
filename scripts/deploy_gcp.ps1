# Google Cloud Run Deployment Script for Autonomous Circularity Network
param(
    [string]$ProjectId = "acn-mainnet-prod",
    [string]$Region = "us-central1"
)

Write-Host "🚀 Preparing Autonomous Circularity Network (ACN) for Google Cloud Deployment..." -ForegroundColor Green

# Verify gcloud CLI installation
if (-not (Get-Command "gcloud" -ErrorAction SilentlyContinue)) {
    Write-Host "⚠️ Google Cloud SDK (gcloud) is not installed locally. Please install gcloud CLI to execute automated deployment." -ForegroundColor Yellow
    Write-Host "👉 You can run: gcloud builds submit --tag gcr.io/$ProjectId/acn-orchestrator" -ForegroundColor Cyan
    exit
}

Write-Host "📦 Submitting container build to Google Cloud Build (gcr.io/$ProjectId/acn-orchestrator)..." -ForegroundColor Cyan
gcloud builds submit --tag "gcr.io/$ProjectId/acn-orchestrator" .

Write-Host "⚡ Deploying to Google Cloud Run service (acn-orchestrator-service)..." -ForegroundColor Cyan
gcloud run deploy acn-orchestrator-service `
    --image "gcr.io/$ProjectId/acn-orchestrator" `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --port 8090

Write-Host "✅ Deployment Complete! Service is live on Google Cloud Run." -ForegroundColor Green
