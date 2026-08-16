@echo off
echo =================================================
echo  ACN Akash Provider - Helm Deployment
echo =================================================

echo.
echo [1/6] Getting GKE credentials...
gcloud container clusters get-credentials acn-provider-cluster --zone us-central1-a

echo.
echo [2/6] Verifying cluster nodes...
kubectl get nodes

echo.
echo [3/6] Installing cert-manager (Akash TLS requirement)...
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
timeout /t 30 /nobreak

echo.
echo [4/6] Creating Akash services namespace...
kubectl create namespace akash-services 2>nul || echo "Namespace already exists, continuing..."

echo.
echo [5/6] Adding Akash Helm repo...
helm repo add akash https://akash-network.github.io/helm-charts
helm repo update

echo.
echo [6/6] Deploying Akash Provider via Helm...
helm install akash-provider akash/provider ^
  --namespace akash-services ^
  --set "provider.address=akash1rlhstdys7sjxpv9en397mpeskzha9ukj9yy4fg" ^
  --set "provider.domain=acn-backend-444129982305.us-central1.run.app" ^
  --set "bidprice_cpu_scale=0.001" ^
  --set "bidprice_memory_scale=0.0005" ^
  --set "bidprice_storage_scale=0.00001" ^
  --set "bidprice_endpoint_scale=0"

echo.
echo [Done] Checking provider pod status...
kubectl get pods -n akash-services

echo.
echo =================================================
echo  Akash Provider Deployed!
echo  Wallet: akash1rlhstdys7sjxpv9en397mpeskzha9ukj9yy4fg
echo =================================================
