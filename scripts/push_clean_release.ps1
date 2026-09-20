# Push Clean v1.0.0 Release & Purge Historical Bloated Tags
# ============================================================

Write-Host "`n[*] Purging 17 historical bloated draft tags from GitHub..." -ForegroundColor Cyan

$bloatedTags = @(
    "btp-v2.2-frozen",
    "v2.2.0",
    "v2.3.0",
    "v2.4.0",
    "v2.4.3",
    "v3.0.0",
    "v4",
    "v4.0.0",
    "v5.4.10",
    "v5.4.11",
    "v5.4.12",
    "v5.4.14",
    "v5.4.15",
    "v5.4.4",
    "v5.4.5",
    "v5.4.6",
    "v5.4.7"
)

foreach ($tag in $bloatedTags) {
    Write-Host "[-] Deleting remote tag: $tag" -ForegroundColor Yellow
    git push origin --delete $tag 2>$null
}

Write-Host "`n[*] Pushing squashed, institutional main branch to origin..." -ForegroundColor Cyan
git push origin main --force

Write-Host "`n[*] Pushing official production release tag v1.0.0..." -ForegroundColor Cyan
git push origin v1.0.0 --force

Write-Host "`n[+] Repository synchronization complete! Only v1.0.0 is active." -ForegroundColor Green
