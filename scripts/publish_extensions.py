"""
Bartholomew Extension Marketplace Publisher
===========================================
Publishes Bartholomew Guard and Keystone Passkey to:
1. Microsoft Visual Studio Code Marketplace
2. Open-VSX Registry (Cursor, Windsurf, VSCodium)

Usage:
  python scripts/publish_extensions.py --vsce-pat <TOKEN>
  python scripts/publish_extensions.py --ovsx-pat <TOKEN>
  python scripts/publish_extensions.py --all --vsce-pat <TOKEN> --ovsx-pat <TOKEN>
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

EXTENSIONS = [
    {
        "id": "bartholomew-guard-vscode",
        "dir": BASE_DIR / "packages" / "vscode-extension",
        "vsix": BASE_DIR / "packages" / "vscode-extension" / "bartholomew-guard-vscode-5.4.21.vsix"
    },
    {
        "id": "bartholomew-keystone",
        "dir": BASE_DIR / "packages" / "bartholomew-keystone",
        "vsix": BASE_DIR / "packages" / "bartholomew-keystone" / "bartholomew-keystone-5.4.21.vsix"
    }
]

def ensure_packaged():
    print("[*] Ensuring latest VSIX packages are built...")
    pkg_script = BASE_DIR / "scripts" / "package_all_vsix.py"
    res = subprocess.run([sys.executable, str(pkg_script)], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Packaging failed:\n{res.stderr}")
        sys.exit(1)
    print("[+] VSIX packages verified.")

def publish_vsce(pat: str):
    print("\n" + "=" * 60)
    print("  PUBLISHING TO MICROSOFT VS CODE MARKETPLACE")
    print("=" * 60)
    
    for ext in EXTENSIONS:
        vsix_path = ext["vsix"]
        if not vsix_path.exists():
            print(f"[!] Error: {vsix_path} not found.")
            continue

        print(f"[*] Uploading {ext['id']} ({vsix_path.name}) to VS Code Marketplace...")
        cmd = ["npx", "-y", "@vscode/vsce", "publish", "--packagePath", str(vsix_path), "--pat", pat]
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                print(f"[OK] Successfully published {ext['id']} to VS Code Marketplace!")
            else:
                print(f"[!] VSCE publish response for {ext['id']}:\n{res.stdout}\n{res.stderr}")
        except Exception as e:
            print(f"[!] Exception during publish: {e}")

def publish_ovsx(pat: str):
    print("\n" + "=" * 60)
    print("  PUBLISHING TO OPEN-VSX REGISTRY (CURSOR / WINDSURF)")
    print("=" * 60)

    for ext in EXTENSIONS:
        vsix_path = ext["vsix"]
        if not vsix_path.exists():
            print(f"[!] Error: {vsix_path} not found.")
            continue

        print(f"[*] Uploading {ext['id']} ({vsix_path.name}) to Open-VSX...")
        cmd = ["npx", "-y", "ovsx", "publish", str(vsix_path), "--pat", pat]
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                print(f"[OK] Successfully published {ext['id']} to Open-VSX!")
            else:
                print(f"[!] OVSX publish response for {ext['id']}:\n{res.stdout}\n{res.stderr}")
        except Exception as e:
            print(f"[!] Exception during publish: {e}")

def main():
    parser = argparse.ArgumentParser(description="Bartholomew Extension Marketplace Publisher")
    parser.add_argument("--vsce-pat", default=os.getenv("VSCE_PAT"), help="Microsoft VS Code Marketplace Personal Access Token")
    parser.add_argument("--ovsx-pat", default=os.getenv("OVSX_PAT"), help="Open-VSX Personal Access Token")
    parser.add_argument("--package-only", action="store_true", help="Only build packages without uploading")
    args = parser.parse_args()

    ensure_packaged()

    if args.package_only:
        print("[+] Packages are ready in packages/ directory.")
        return

    if not args.vsce_pat and not args.ovsx_pat:
        print("\n[NOTE] No PAT tokens provided via CLI or environment variables.")
        print("To publish immediately, run:")
        print("  python scripts/publish_extensions.py --vsce-pat <YOUR_AZURE_DEVOPS_TOKEN>")
        print("  python scripts/publish_extensions.py --ovsx-pat <YOUR_OPEN_VSX_TOKEN>")
        return

    if args.vsce_pat:
        publish_vsce(args.vsce_pat)

    if args.ovsx_pat:
        publish_ovsx(args.ovsx_pat)

if __name__ == "__main__":
    main()