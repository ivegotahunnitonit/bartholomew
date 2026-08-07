#!/usr/bin/env pwsh
# inject_provider_key.ps1
# Generates a fresh Akash provider wallet key and injects it into the cluster secret
# Usage: Run this after the akash-provider-0 pod image has been pulled

$Namespace = "akash-services"
$KeyName = "acn-provider"
$KeyPass = "AcnProvider2024!"
$SecretName = "akash-provider-keys"

Write-Host "=== Step 1: Run keygen job to create fresh provider wallet ==="

# Create a one-shot keygen job using the provider image
$KeygenJob = @"
apiVersion: batch/v1
kind: Job
metadata:
  name: akash-keygen
  namespace: $Namespace
spec:
  ttlSecondsAfterFinished: 120
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: keygen
        image: ghcr.io/akash-network/provider:0.16.0
        command: ["/bin/bash", "-c"]
        args:
        - |
          set -e
          HOME_DIR=/tmp/akash-keys
          mkdir -p \$HOME_DIR
          KEY_NAME=$KeyName
          KEY_PASS='$KeyPass'
          echo \$KEY_PASS | provider-services keys add \$KEY_NAME \
            --home=\$HOME_DIR \
            --keyring-backend=test \
            --output=json
          ADDR=\$(provider-services keys show \$KEY_NAME -a --home=\$HOME_DIR --keyring-backend=test)
          echo "===PROVIDER_ADDRESS=\$ADDR==="
          echo "\$KEY_PASS" | provider-services keys export \$KEY_NAME \
            --home=\$HOME_DIR \
            --keyring-backend=test 2>&1 | tee /tmp/exported.txt
          echo "===ARMORED_KEY_START==="
          cat /tmp/exported.txt
          echo "===ARMORED_KEY_END==="
          echo "===KEY_PASS=\$KEY_PASS==="
"@

$KeygenJob | kubectl apply -f - 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create keygen job"
    exit 1
}

Write-Host "=== Step 2: Wait for keygen job to complete ==="
kubectl wait --for=condition=complete job/akash-keygen -n $Namespace --timeout=300s 2>&1

Write-Host "=== Step 3: Extract key material from job logs ==="
$Logs = kubectl logs job/akash-keygen -n $Namespace 2>&1
Write-Host $Logs

# Extract provider address
$AddrMatch = $Logs | Select-String '===PROVIDER_ADDRESS=(.+)==='
if ($AddrMatch) {
    $ProviderAddr = $AddrMatch.Matches[0].Groups[1].Value.Trim()
    Write-Host "Provider Address: $ProviderAddr"
} else {
    Write-Error "Could not extract provider address from logs"
    $Logs
    exit 1
}

# Extract armored key
$StartIdx = $Logs.IndexOf("===ARMORED_KEY_START===")
$EndIdx = $Logs.IndexOf("===ARMORED_KEY_END===")
if ($StartIdx -ge 0 -and $EndIdx -gt $StartIdx) {
    $ArmoredKey = ($Logs[($StartIdx+1)..($EndIdx-1)] -join "`n").Trim()
    Write-Host "Armored key extracted (length: $($ArmoredKey.Length))"
} else {
    Write-Error "Could not extract armored key from logs"
    $Logs
    exit 1
}

Write-Host "=== Step 4: Inject key material into Kubernetes secret ==="
$KeyB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($ArmoredKey))
$PassB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($KeyPass))

$SecretPatch = @"
{
  "data": {
    "key.txt": "$KeyB64",
    "key-pass.txt": "$PassB64"
  }
}
"@

$SecretPatch | kubectl patch secret $SecretName -n $Namespace --type=merge -p - 2>&1
Write-Host "Secret patched successfully"

Write-Host "=== Step 5: Update Helm values with new provider address ==="
& 'C:\Users\User\AppData\Local\Programs\helm.exe' upgrade akash-provider `
  'c:\Users\User\.gemini\antigravity\scratch\autonomous-circularity-network\akash-helm-charts\helm-charts-main\charts\akash-provider' `
  --namespace $Namespace `
  --reuse-values `
  --set "from=$KeyName" `
  --set "provider.address=$ProviderAddr" 2>&1

Write-Host "=== Step 6: Restart pod to pick up new keys ==="
kubectl delete pod akash-provider-0 -n $Namespace 2>&1
Write-Host "Pod restarted. New provider address: $ProviderAddr"
Write-Host ""
Write-Host "IMPORTANT: Fund this address with AKT for gas fees:"
Write-Host "  Address: $ProviderAddr"
Write-Host "  Minimum needed: ~0.5 AKT for bid deposits + gas"
