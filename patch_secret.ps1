$keyContent = "-----BEGIN TENDERMINT PRIVATE KEY-----`nkdf: argon2`nsalt: E195A630D4D377D93F9A855DD7A45644`ntype: secp256k1`n`nxYOFMZ9fAiA70+KUacqYHHOXoLIO0YV/UGlrOcpI02wb/jn9DSs+QPcxwa12tRDy`nl91wJrI=`n=VB9w`n-----END TENDERMINT PRIVATE KEY-----`n"
$passContent = "providerpass"

$keyB64  = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($keyContent))
$passB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($passContent))

Write-Host "Key B64: $keyB64"
Write-Host "Pass B64: $passB64"

# Write secret YAML
$secretYaml = @"
apiVersion: v1
kind: Secret
metadata:
  name: akash-provider-keys
  namespace: akash-services
type: Opaque
data:
  key.txt: $keyB64
  key-pass.txt: $passB64
"@

$secretYaml | Out-File -FilePath "provider-keys-secret.yaml" -Encoding UTF8
Write-Host "Secret YAML written"

# Apply it
kubectl apply -f provider-keys-secret.yaml 2>&1
Write-Host "Secret applied, exit code: $LASTEXITCODE"

if ($LASTEXITCODE -eq 0) {
    # Helm upgrade with correct from/address values
    Write-Host "Upgrading Helm release..."
    & 'C:\Users\User\AppData\Local\Programs\helm.exe' upgrade akash-provider `
        'c:\Users\User\.gemini\antigravity\scratch\autonomous-circularity-network\akash-helm-charts\helm-charts-main\charts\akash-provider' `
        --namespace akash-services `
        --reuse-values `
        --set from=provider `
        --set provider.address=akash1y557yjut3zxlfpd3p0elet4t2w5hermd69p8k7 2>&1
    
    Write-Host "Restarting provider pod..."
    Start-Sleep -Seconds 3
    kubectl delete pod akash-provider-0 -n akash-services 2>&1
    Write-Host "Done. Pod will restart with new wallet key."
} else {
    Write-Error "Failed to apply secret YAML"
}
