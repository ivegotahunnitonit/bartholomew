# Bartholomew Security Engine — Google Cloud Run Deployment Script (PowerShell)

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "  Bartholomew Enterprise AI Security Engine — GCP Deployer" -ForegroundColor Cyan
Write-Host "===================================================================" -ForegroundColor Cyan

if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Google Cloud SDK 'gcloud' CLI is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

Write-Host "[Bartholomew GCP Deploy] Submitting container build to Cloud Build..." -ForegroundColor Yellow
gcloud builds submit --config=cloudbuild.yaml .

if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Service deployed! Active Cloud Run URL:" -ForegroundColor Green
    gcloud run services describe agentic-eval-service --platform=managed --region=us-central1 --format="value(status.url)"
} else {
    Write-Host "[ERROR] Cloud Build failed. Check gcloud credentials." -ForegroundColor Red
}
