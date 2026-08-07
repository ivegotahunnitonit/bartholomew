@echo off
setlocal enabledelayedexpansion
REM ===================================================================
REM   Bartholomew Security Engine — Google Cloud Run Deployment Script
REM ===================================================================
echo [Bartholomew GCP Deploy] Checking Google Cloud CLI setup...

where gcloud >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Google Cloud SDK 'gcloud' CLI is not installed or not in PATH.
    echo Please install gcloud SDK or deploy using Docker/Render.
    exit /b 1
)

echo [Bartholomew GCP Deploy] Submitting container build to Google Cloud...
call gcloud builds submit --config=cloudbuild.yaml .

if %errorlevel% neq 0 (
    echo [ERROR] Google Cloud Build failed. Check gcloud permissions or cloudbuild.yaml.
    exit /b 1
)

echo [Bartholomew GCP Deploy] Fetching active Cloud Run URL...
call gcloud run services describe agentic-eval-service --platform=managed --region=us-central1 --format="value(status.url)"

echo [SUCCESS] Bartholomew Enterprise Engine deployed successfully to Google Cloud Run!
