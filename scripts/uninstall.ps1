#Requires -RunAsAdministrator
<#
.SYNOPSIS
    ACN Node Uninstaller - Autonomous Circularity Network
.DESCRIPTION
    Removes the "ACN-Node" Windows Task Scheduler task and stops any running ACN processes.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$TASK_NAME = "ACN-Node"

# ─────────────────────────────────────────────────────────
#  Banner
# ─────────────────────────────────────────────────────────
Clear-Host
Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════╗" -ForegroundColor DarkYellow
Write-Host "  ║   Autonomous Circularity Network  •  Uninstaller ║" -ForegroundColor DarkYellow
Write-Host "  ╚══════════════════════════════════════════════════╝" -ForegroundColor DarkYellow
Write-Host ""

# ─────────────────────────────────────────────────────────
#  Step 1 – Stop running ACN processes
# ─────────────────────────────────────────────────────────
Write-Host "  [1/2] Stopping any running ACN Node processes..." -ForegroundColor Yellow

$agynodeProcs = Get-Process -Name "agy-node" -ErrorAction SilentlyContinue
if ($agynodeProcs) {
    $agynodeProcs | Stop-Process -Force
    Write-Host "  ✔  Stopped $($agynodeProcs.Count) agy-node process(es)." -ForegroundColor Green
} else {
    Write-Host "  –  No running ACN Node processes found." -ForegroundColor DarkGray
}

# Also catch cmd wrappers that may have launched it
$cmdProcs = Get-WmiObject Win32_Process -Filter "CommandLine LIKE '%src\\index.ts%'" -ErrorAction SilentlyContinue
if ($cmdProcs) {
    foreach ($p in $cmdProcs) {
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  ✔  Stopped $($cmdProcs.Count) wrapper process(es)." -ForegroundColor Green
}

# ─────────────────────────────────────────────────────────
#  Step 2 – Remove Scheduled Task
# ─────────────────────────────────────────────────────────
Write-Host "  [2/2] Removing scheduled task '$TASK_NAME'..." -ForegroundColor Yellow

$task = Get-ScheduledTask -TaskName $TASK_NAME -ErrorAction SilentlyContinue

if ($task) {
    Unregister-ScheduledTask -TaskName $TASK_NAME -Confirm:$false
    Write-Host "  ✔  Scheduled task '$TASK_NAME' removed." -ForegroundColor Green
} else {
    Write-Host "  –  Task '$TASK_NAME' was not found (already removed?)." -ForegroundColor DarkGray
}

# ─────────────────────────────────────────────────────────
#  Done
# ─────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "  ║         ACN Node uninstalled successfully.       ║" -ForegroundColor Green
Write-Host "  ╚══════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  Your .env and data/ folder have been preserved." -ForegroundColor DarkGray
Write-Host "  To reinstall, run install.ps1 again." -ForegroundColor DarkGray
Write-Host ""
