@echo off
setlocal EnableDelayedExpansion

:: ACN One-Click Installer Launcher
:: Autonomous Circularity Network

title ACN Node Setup Wizard

:: Check for administrative privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo   =======================================================
    echo    ACN Installer requires Administrative privileges.
    echo    Requesting User Account Control elevation...
    echo   =======================================================
    echo.
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: Run the interactive installer PowerShell script
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"

if %errorLevel% neq 0 (
    echo.
    echo   [ERROR] Installation script encountered a problem.
    echo.
    pause
)
