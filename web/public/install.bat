@echo off
title Bartholomew 1-Click Desktop Installer
echo =================================================================
echo   Installing Bartholomew Autonomous Trust Protocol (BTP v2.2.0)  
echo =================================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/ivegotahunnitonit/bartholomew/main/install.ps1 | iex"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Running fallback direct installer...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$InstallDir = '$HOME\.bartholomew'; $BinDir = '$InstallDir\bin'; if (-not (Test-Path $BinDir)) { New-Item -ItemType Directory -Path $BinDir -Force | Out-Null }; Set-Content -Path '$BinDir\bartholomew.cmd' -Value '@echo off`npython -m src.cli %*'; [Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path', 'User') + ';$BinDir', 'User'); Write-Host '[SUCCESS] Bartholomew installed!' -ForegroundColor Green"
)

echo.
pause
