@echo off
setlocal EnableDelayedExpansion

:: ============================================================
::  ACN Node – Shutdown Script
::  Autonomous Circularity Network
:: ============================================================

title ACN Node — Shutdown

cls
echo.
echo   =======================================================
echo    AUTONOMOUS CIRCULARITY NETWORK  ^|  Shutdown
echo   =======================================================
echo.
echo   Stopping ACN Node processes...
echo.

:: ── Kill agy-node processes ──────────────────────────────────
set FOUND=0

for /f "tokens=2" %%P in ('tasklist /fi "imagename eq agy-node.exe" /fo csv /nh 2^>nul') do (
    set "PID=%%~P"
    if not "!PID!"=="" (
        taskkill /PID !PID! /F >nul 2>&1
        if !errorlevel! equ 0 (
            echo   [OK] Stopped agy-node process (PID !PID!)
            set FOUND=1
        )
    )
)

:: ── Also check node.exe wrappers launched from this project ──
for /f "tokens=2" %%P in ('tasklist /fi "imagename eq node.exe" /fo csv /nh 2^>nul') do (
    set "PID=%%~P"
)

:: ── WMIC fallback: find processes with index.ts in command line
for /f "skip=1 tokens=1" %%P in ('wmic process where "commandline like '%%src\\\\index.ts%%'" get processid 2^>nul') do (
    set "PID=%%P"
    if defined PID (
        taskkill /PID !PID! /F >nul 2>&1
        if !errorlevel! equ 0 (
            echo   [OK] Stopped related process (PID !PID!)
            set FOUND=1
        )
    )
)

echo.
if "!FOUND!"=="1" (
    echo   -------------------------------------------------------
    echo   ACN Node has been stopped successfully.
    echo   -------------------------------------------------------
) else (
    echo   No running ACN Node processes were found.
    echo   The node may already be stopped.
)

echo.
echo   To restart, run start.bat
echo.
pause
endlocal
