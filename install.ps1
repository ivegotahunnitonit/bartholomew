#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ACN Node Installer - Autonomous Circularity Network
.DESCRIPTION
    Installs and registers the ACN Node as a Windows login-time scheduled task.
    Supports interactive CLI wizard and silent installations.
#>

param(
    [switch]$Silent = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ─────────────────────────────────────────────────────────
#  Banner
# ─────────────────────────────────────────────────────────
Clear-Host
Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║   Autonomous Circularity Network  •  Installer   ║" -ForegroundColor Cyan
Write-Host "  ║                     ACN Node v1.0                ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ─────────────────────────────────────────────────────────
#  Constants & Paths
# ─────────────────────────────────────────────────────────
$TASK_NAME      = "ACN-Node"
$PROJECT_DIR    = $PSScriptRoot
$ENTRY_POINT    = Join-Path $PROJECT_DIR "src\index.ts"

# Fix the agy-node path bug by checking the bin directory first
$AGY_CMD = Join-Path $env:APPDATA "Antigravity\bin\agy-node.cmd"
if (-not (Test-Path $AGY_CMD)) {
    $AGY_CMD = Join-Path $env:APPDATA "Antigravity\agy-node.cmd"
}

# ─────────────────────────────────────────────────────────
#  Step 1 – Verify Antigravity IDE
# ─────────────────────────────────────────────────────────
Write-Host "  [1/4] Checking for Antigravity IDE..." -ForegroundColor Yellow

if (-not (Test-Path $AGY_CMD)) {
    Write-Host ""
    Write-Host "  ✖  Antigravity IDE not found." -ForegroundColor Red
    Write-Host "     Expected: $env:APPDATA\Antigravity\bin\agy-node.cmd" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Please install Antigravity IDE from https://antigravity.dev" -ForegroundColor DarkYellow
    Write-Host "  and re-run this installer." -ForegroundColor DarkYellow
    Write-Host ""
    exit 1
}

Write-Host "  ✔  Antigravity IDE found at: $AGY_CMD" -ForegroundColor Green

# ─────────────────────────────────────────────────────────
#  Step 2 – Interactive Configuration
# ─────────────────────────────────────────────────────────
Write-Host "  [2/4] Configuring ACN Node..." -ForegroundColor Yellow

# Load existing .env configurations if present
$EnvFile = Join-Path $PROJECT_DIR ".env"
$ExistingConfigs = @{}

if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        $Line = $_.Trim()
        if ($Line -and -not $Line.StartsWith("#")) {
            $Parts = $Line.Split("=", 2)
            if ($Parts.Count -eq 2) {
                $ExistingConfigs[$Parts[0].Trim()] = $Parts[1].Trim()
            }
        }
    }
}

# Setup defaults
$DefaultPort      = "8080"
if ($ExistingConfigs.ContainsKey("PORT")) { $DefaultPort = $ExistingConfigs["PORT"] }

$DefaultLat       = "40.7128"
if ($ExistingConfigs.ContainsKey("LAT")) { $DefaultLat = $ExistingConfigs["LAT"] }

$DefaultLng       = "-74.0060"
if ($ExistingConfigs.ContainsKey("LNG")) { $DefaultLng = $ExistingConfigs["LNG"] }

$DefaultNodeName  = "ACN-Node-Local"
if ($ExistingConfigs.ContainsKey("NODE_NAME")) { $DefaultNodeName = $ExistingConfigs["NODE_NAME"] }

$DefaultFeeRate   = "0.02"
if ($ExistingConfigs.ContainsKey("FEE_RATE")) { $DefaultFeeRate = $ExistingConfigs["FEE_RATE"] }

$DefaultPeers     = ""
if ($ExistingConfigs.ContainsKey("BOOTSTRAP_PEERS")) { $DefaultPeers = $ExistingConfigs["BOOTSTRAP_PEERS"] }

$NodeId           = [guid]::NewGuid().ToString()
if ($ExistingConfigs.ContainsKey("NODE_ID")) { $NodeId = $ExistingConfigs["NODE_ID"] }

$WalletAddress    = ""
if ($ExistingConfigs.ContainsKey("WALLET_ADDRESS")) { $WalletAddress = $ExistingConfigs["WALLET_ADDRESS"] }

if (-not $WalletAddress) {
    $Seed = $NodeId.Replace("-", "").Substring(0, 20)
    $WalletAddress = "lnbc1acn${Seed}wallet"
}

$Port     = $DefaultPort
$Lat      = $DefaultLat
$Lng      = $DefaultLng
$NodeName = $DefaultNodeName
$FeeRate  = $DefaultFeeRate
$Peers    = $DefaultPeers

if (-not $Silent) {
    Write-Host "  Press Enter to accept defaults, or enter custom values:" -ForegroundColor Gray
    
    $InputPort = Read-Host "  Node Web Port [$DefaultPort]"
    if ($InputPort) { $Port = $InputPort.Trim() }

    $InputNodeName = Read-Host "  Node Name [$DefaultNodeName]"
    if ($InputNodeName) { $NodeName = $InputNodeName.Trim() }

    $InputLat = Read-Host "  Facility Latitude (proximity weight) [$DefaultLat]"
    if ($InputLat) { $Lat = $InputLat.Trim() }

    $InputLng = Read-Host "  Facility Longitude (proximity weight) [$DefaultLng]"
    if ($InputLng) { $Lng = $InputLng.Trim() }

    $InputFeeRate = Read-Host "  Match Fee Rate (e.g. 0.02 = 2%) [$DefaultFeeRate]"
    if ($InputFeeRate) { $FeeRate = $InputFeeRate.Trim() }

    $InputPeers = Read-Host "  Bootstrap Peer URLs (comma-separated, optional)"
    if ($InputPeers) { $Peers = $InputPeers.Trim() }
}

# Write out the persistent configuration
$EnvContent = @(
    "# Autonomous Circularity Network Node Config",
    "NODE_ID=$NodeId",
    "PORT=$Port",
    "LAT=$Lat",
    "LNG=$Lng",
    "MAX_RADIUS_KM=50.0",
    "FEE_RATE=$FeeRate",
    "BOOTSTRAP_PEERS=$Peers",
    "WALLET_ADDRESS=$WalletAddress",
    "NODE_NAME=$NodeName"
)

$EnvContent | Set-Content $EnvFile -Encoding utf8
Write-Host "  ✔  Configuration saved successfully to .env" -ForegroundColor Green

# ─────────────────────────────────────────────────────────
#  Step 3 – Create / Update Scheduled Task
# ─────────────────────────────────────────────────────────
Write-Host "  [3/4] Registering scheduled task '$TASK_NAME'..." -ForegroundColor Yellow

$existingTask = Get-ScheduledTask -TaskName $TASK_NAME -ErrorAction SilentlyContinue
if ($existingTask) {
    Unregister-ScheduledTask -TaskName $TASK_NAME -Confirm:$false
    Write-Host "  ↻  Updated existing Task Scheduler configuration." -ForegroundColor DarkGray
}

$taskAction = New-ScheduledTaskAction `
    -Execute  $AGY_CMD `
    -Argument "--experimental-strip-types `"$ENTRY_POINT`"" `
    -WorkingDirectory $PROJECT_DIR

$taskTrigger = New-ScheduledTaskTrigger -AtLogOn

$taskSettings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -MultipleInstances IgnoreNew `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

$taskPrincipal = New-ScheduledTaskPrincipal `
    -UserId    "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel  Highest

Register-ScheduledTask `
    -TaskName  $TASK_NAME `
    -Action    $taskAction `
    -Trigger   $taskTrigger `
    -Settings  $taskSettings `
    -Principal $taskPrincipal `
    -Force | Out-Null

Write-Host "  ✔  Scheduled task '$TASK_NAME' registered (runs at login)." -ForegroundColor Green

# ─────────────────────────────────────────────────────────
#  Step 4 – Launch Node & Dashboard
# ─────────────────────────────────────────────────────────
Write-Host "  [4/4] Activating ACN Node..." -ForegroundColor Yellow

$DashboardUrl = "http://localhost:$Port"

# Launch the node process
Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/c `"$AGY_CMD`" --experimental-strip-types `"$ENTRY_POINT`"" `
    -WorkingDirectory $PROJECT_DIR `
    -WindowStyle Normal

Start-Sleep -Seconds 3

# Open dashboard URL
Start-Process $DashboardUrl

Write-Host "  ✔  ACN Node is active and running." -ForegroundColor Green

# ─────────────────────────────────────────────────────────
#  Done
# ─────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "  ║            Installation Complete! 🎉             ║" -ForegroundColor Green
Write-Host "  ╚══════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  Node Name      : " -NoNewline -ForegroundColor White
Write-Host $NodeName -ForegroundColor Cyan
Write-Host "  Dashboard URL  : " -NoNewline -ForegroundColor White
Write-Host $DashboardUrl -ForegroundColor Cyan
Write-Host "  Task Name      : " -NoNewline -ForegroundColor White
Write-Host $TASK_NAME -ForegroundColor Cyan
Write-Host "  Auto-start     : " -NoNewline -ForegroundColor White
Write-Host "Enabled (on login)" -ForegroundColor Cyan
Write-Host "  To uninstall   : " -NoNewline -ForegroundColor White
Write-Host "Run uninstall.ps1" -ForegroundColor DarkYellow
Write-Host ""
