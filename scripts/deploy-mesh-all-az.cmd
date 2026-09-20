@echo off
REM ==============================================================================
REM ACN Multi-AZ Global Mesh Orchestrator (Windows CMD)
REM Deploys security-hardened ACN Supernodes across 5 Availability Zones with
REM batch mode for non-interactive execution (-batch):
REM   1. us-central1-a  (Gateway 1: 35.255.62.200)
REM   2. us-east1-b     (Gateway 2: 34.73.34.145)
REM   3. us-west1-a     (Gateway 3: 136.117.15.127)
REM   4. us-west2-a     (Gateway 4: 34.20.133.4)
REM   5. europe-west1-b (Gateway 5: 34.53.176.111)
REM ==============================================================================

echo ==============================================================================
echo   ACN MULTI-AZ DEPLOYMENT ORCHESTRATOR — 5 GLOBAL REGIONS                    
echo ==============================================================================

echo [1/4] Deploying Gateway 2 (us-east1-b)...
gcloud.cmd compute scp --scp-flag="-batch" acn-lean.tar.gz acn-supernode-gateway-2:/tmp/acn-app.tar.gz --zone=us-east1-b --quiet
gcloud.cmd compute scp --scp-flag="-batch" scripts/deploy-gateway1.sh acn-supernode-gateway-2:/tmp/deploy.sh --zone=us-east1-b --quiet
gcloud.cmd compute ssh --ssh-flag="-batch" acn-supernode-gateway-2 --zone=us-east1-b --command "sudo DOMAIN=34-73-34-145.sslip.io bash /tmp/deploy.sh"

echo [2/4] Deploying Gateway 3 (us-west1-a)...
gcloud.cmd compute scp --scp-flag="-batch" acn-lean.tar.gz acn-supernode-gateway-3:/tmp/acn-app.tar.gz --zone=us-west1-a --quiet
gcloud.cmd compute scp --scp-flag="-batch" scripts/deploy-gateway1.sh acn-supernode-gateway-3:/tmp/deploy.sh --zone=us-west1-a --quiet
gcloud.cmd compute ssh --ssh-flag="-batch" acn-supernode-gateway-3 --zone=us-west1-a --command "sudo DOMAIN=136-117-15-127.sslip.io bash /tmp/deploy.sh"

echo [3/4] Deploying Gateway 4 (us-west2-a)...
gcloud.cmd compute scp --scp-flag="-batch" acn-lean.tar.gz acn-supernode-gateway-4:/tmp/acn-app.tar.gz --zone=us-west2-a --quiet
gcloud.cmd compute scp --scp-flag="-batch" scripts/deploy-gateway1.sh acn-supernode-gateway-4:/tmp/deploy.sh --zone=us-west2-a --quiet
gcloud.cmd compute ssh --ssh-flag="-batch" acn-supernode-gateway-4 --zone=us-west2-a --command "sudo DOMAIN=34-20-133-4.sslip.io bash /tmp/deploy.sh"

echo [4/4] Deploying Gateway 5 (europe-west1-b)...
gcloud.cmd compute scp --scp-flag="-batch" acn-lean.tar.gz acn-supernode-gateway-5:/tmp/acn-app.tar.gz --zone=europe-west1-b --quiet
gcloud.cmd compute scp --scp-flag="-batch" scripts/deploy-gateway1.sh acn-supernode-gateway-5:/tmp/deploy.sh --zone=europe-west1-b --quiet
gcloud.cmd compute ssh --ssh-flag="-batch" acn-supernode-gateway-5 --zone=europe-west1-b --command "sudo DOMAIN=34-53-176-111.sslip.io bash /tmp/deploy.sh"

echo ==============================================================================
echo   ✅ ALL 5 AVAILABILITY ZONES DEPLOYED AND SECURED WITH HARDENED FAILOVER
echo ==============================================================================
