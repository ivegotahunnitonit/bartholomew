"""
Bartholomew Desktop Portable Bundle Builder (Direct Fast Streamer)
=================================================================
Packages clean Bartholomew desktop bundle directly into web/public/
"""

import os
import sys
import zipfile
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT_DIR, "web", "public")
DIST_ZIP = os.path.join(OUTPUT_DIR, "bartholomew-desktop-windows-v2.2.0.zip")
LATEST_ZIP = os.path.join(OUTPUT_DIR, "bartholomew-desktop.zip")

FILES = [
    "cli.py",
    "mcp_server.py",
    "mcp_installer.py",
    "install.bat",
    "install.ps1",
    "install.sh",
    "requirements.txt",
    "pyproject.toml",
    "README.md",
    "LICENSE.md",
]

DIRS = [
    "src",
    "daemon",
    "dashboard",
    "policies",
]

LAUNCHER_BAT = """@echo off
title Bartholomew BTP Guard v2.2.0 (Local Control Plane)
color 0A
echo ==============================================================================
echo       BARTHOLOMEW (BTP v2.2.0) - THE SEATBELT FOR AUTONOMOUS AI AGENTS
echo ==============================================================================
echo [*] Initializing sovereign cryptographic trust root...
python cli.py init
echo.
echo [*] Starting Local Invariant Daemon & Web Control Center on http://127.0.0.1:8080...
start http://127.0.0.1:8080/dashboard
python cli.py daemon start
pause
"""

def build():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"[*] Packaging standalone desktop zip to {DIST_ZIP}...")

    with zipfile.ZipFile(DIST_ZIP, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add root files
        for fname in FILES:
            fpath = os.path.join(ROOT_DIR, fname)
            if os.path.exists(fpath):
                zipf.write(fpath, os.path.join("bartholomew", fname))

        # Add launcher
        zipf.writestr("bartholomew/launch_bartholomew.bat", LAUNCHER_BAT)

        # Add directories
        for dname in DIRS:
            dpath = os.path.join(ROOT_DIR, dname)
            if not os.path.exists(dpath):
                continue
            for root, _, files in os.walk(dpath):
                if "__pycache__" in root or ".git" in root:
                    continue
                for file in files:
                    if file.endswith((".pyc", ".png", ".jpg")):
                        continue
                    full_file = os.path.join(root, file)
                    rel = os.path.relpath(full_file, ROOT_DIR)
                    zipf.write(full_file, os.path.join("bartholomew", rel))

    shutil.copy2(DIST_ZIP, LATEST_ZIP)
    size_kb = os.path.getsize(DIST_ZIP) / 1024
    print(f"[OK] Standalone Desktop Bundle generated: {size_kb:.2f} KB")

if __name__ == "__main__":
    build()
