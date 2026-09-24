# ==============================================================================
# Bartholomew Trust Protocol (BTP v5.4) - Windows PowerShell Installer
# https://bartholomew.info
#
# Usage:
#   irm https://bartholomew.info/install.ps1 | iex
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "    ____             __  __          __                               " -ForegroundColor Magenta
Write-Host "   / __ )____ ______/ /_/ /_  ____  / /___  ____ ___  ___  __  __     " -ForegroundColor Magenta
Write-Host "  / __  / __ `/ ___/ __/ __ \/ __ \/ / __ \/ __ `__ \/ _ \/ / / /     " -ForegroundColor Magenta
Write-Host " / /_/ / /_/ / /  / /_/ / / / /_/ / / /_/ / / / / / /  __/ /_/ /      " -ForegroundColor Magenta
Write-Host "/_____/\__,_/_/   \__/_/ /_/\____/_/\____/_/ /_/ /_/\___/\__,__/       " -ForegroundColor Magenta
Write-Host ""
Write-Host "Bartholomew Agentic Runtime Protection (ARP) -- BTP v5.4.20" -ForegroundColor White
Write-Host "Sub-35us deterministic execution firewall for autonomous AI agents." -ForegroundColor Gray
Write-Host ""

# 1. Check Python 3.10+
$pythonCmd = $null
foreach ($cmd in @("python", "py", "python3")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        try {
            $major = & $cmd -c "import sys; print(sys.version_info.major)" 2>$null
            $minor = & $cmd -c "import sys; print(sys.version_info.minor)" 2>$null
            if ([int]$major -ge 3 -and [int]$minor -ge 10) {
                $pythonCmd = $cmd
                Write-Host "[+] Found Python: $cmd (v$major.$minor)" -ForegroundColor Green
                break
            }
        } catch { }
    }
}

if (-not $pythonCmd) {
    Write-Host "[ERROR] Python 3.10 or higher was not found on your system." -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from https://python.org or via 'winget install Python.Python.3.12'" -ForegroundColor Yellow
    exit 1
}

# 2. Install / Upgrade btp-guard
Write-Host "[*] Installing/Upgrading btp-guard package..." -ForegroundColor Cyan
& $pythonCmd -m pip install --upgrade btp-guard

# 3. Setup configuration directory
$btpDir = Join-Path $env:USERPROFILE ".btp"
if (-not (Test-Path $btpDir)) {
    New-Item -ItemType Directory -Path $btpDir -Force | Out-Null
}

Write-Host ""
Write-Host "[SUCCESS] Bartholomew installed and verified successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Quickstart Commands:" -ForegroundColor White
Write-Host "  1. Test AST safety gate:   btp-guard try" -ForegroundColor Yellow
Write-Host "  2. Protect any process:    btp-guard run -- <your-agent-cmd>" -ForegroundColor Yellow
Write-Host "  3. Verify an MCP server:   btp-guard verify-mcp --url http://localhost:8000/sse" -ForegroundColor Yellow
Write-Host "  4. Python 1-line wrapper:  from btp_guard import protect_agent" -ForegroundColor Yellow
Write-Host ""
Write-Host "Docs & Architecture: https://bartholomew.info" -ForegroundColor Gray
