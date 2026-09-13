@echo off
setlocal EnableDelayedExpansion

:: ============================================================
::  Bartholomew Node Launcher
::  Autonomous Circularity Network
::  Auto-restart on crash — press Ctrl+C TWICE to fully exit.
:: ============================================================

title Bartholomew — ACN Node

cls
echo.
echo   =======================================================
echo    BARTHOLOMEW  ^|  Autonomous Circularity Network v1.0
echo    Auto-restart ENABLED. Ctrl+C twice to stop.
echo   =======================================================
echo.

:: ── Locate agy-node ─────────────────────────────────────────
set "AGY_CMD=%APPDATA%\Antigravity\bin\agy-node.cmd"
if not exist "%AGY_CMD%" (
    set "AGY_CMD=%APPDATA%\Antigravity\agy-node.cmd"
)

if not exist "%AGY_CMD%" (
    echo   [ERROR] Antigravity IDE not found.
    echo   Expected: %APPDATA%\Antigravity\bin\agy-node.cmd
    echo.
    pause
    exit /b 1
)

:: ── Resolve project root ──────────────────────────────────────
set "PROJECT_DIR=%~dp0"
set "ENTRY=%PROJECT_DIR%src\index.ts"

if not exist "%ENTRY%" (
    echo   [ERROR] Entry point not found: %ENTRY%
    pause
    exit /b 1
)

:: ── Copy .env if missing ──────────────────────────────────────
if not exist "%PROJECT_DIR%.env" (
    if exist "%PROJECT_DIR%.env.example" (
        copy /Y "%PROJECT_DIR%.env.example" "%PROJECT_DIR%.env" >nul
        echo   [INFO] Created .env from .env.example
    )
)

:: ── Track first launch (open browser once only) ───────────────
set "FIRST_LAUNCH=1"

:: ════════════════════════════════════════════════════════════
:RESTART
:: ════════════════════════════════════════════════════════════

if "%FIRST_LAUNCH%"=="1" (
    echo   [BARTHOLOMEW] Initializing node...
    echo   Dashboard → http://localhost:8080  (opens in 3s)
    echo.
    start "" /B cmd /C "timeout /nobreak /t 3 >nul && start http://localhost:8080"
    set "FIRST_LAUNCH=0"
) else (
    echo.
    echo   ┌─────────────────────────────────────────────┐
    echo   │  [AUTO-RESTART] Node exited. Restarting...  │
    echo   └─────────────────────────────────────────────┘
    timeout /nobreak /t 3 >nul
    echo   [BARTHOLOMEW] Restarting node process...
    echo.
)

echo   -------------------------------------------------------
echo   Press Ctrl+C TWICE to permanently stop the node.
echo   -------------------------------------------------------
echo.

call "%AGY_CMD%" --experimental-strip-types "%ENTRY%"

:: ── If we reach here, node exited — loop ─────────────────────
goto RESTART
