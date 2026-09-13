@echo off
title Bartholomew 1-Click Desktop Installer
echo =================================================================
echo   Installing Bartholomew Autonomous Trust Protocol (BTP v2.2.0)  
echo =================================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://bartholomew.info/install.ps1 | iex"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Installation encountered an issue. Falling back to local setup...
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
)

echo.
pause
