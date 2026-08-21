# Bartholomew Desktop 1-Click Installer for Windows (PowerShell)
# Usage: irm https://bartholomew.info/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  Installing Bartholomew Autonomous Trust Protocol (BTP v2.2.0)  " -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Cyan

$InstallDir = "$HOME\.bartholomew"
$BinDir = "$InstallDir\bin"

# 1. Create Directories
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir | Out-Null
}
if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir | Out-Null
}

Write-Host "[*] Setting up Bartholomew in: $InstallDir" -ForegroundColor Yellow

# 2. Check Python
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    Write-Host "[!] Python 3.10+ is required. Please install Python first." -ForegroundColor Red
    exit 1
}

# 3. Create Windows Batch Launcher
$BatchFile = "$BinDir\bartholomew.cmd"
$BatchContent = @"
@echo off
python -m src.cli %*
"@
Set-Content -Path $BatchFile -Value $BatchContent

# 4. Add to User PATH if not present
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$BinDir", "User")
    $env:Path += ";$BinDir"
    Write-Host "[*] Added $BinDir to User PATH environment variable." -ForegroundColor Green
}

Write-Host "`n[SUCCESS] Bartholomew Desktop CLI is installed!" -ForegroundColor Green
Write-Host "You can now run:" -ForegroundColor Cyan
Write-Host "  bartholomew version" -ForegroundColor White
Write-Host "  bartholomew init" -ForegroundColor White
Write-Host "  bartholomew daemon start" -ForegroundColor White
Write-Host "=================================================================" -ForegroundColor Cyan
