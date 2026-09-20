"""
Bartholomew Release Publisher (v2.3)
=====================================
Automated publishing helper for PyPI and npm package registries.

Usage:
  # Publish Python Wheel & Source to PyPI:
  python scripts/publish_release.py --pypi

  # Publish TypeScript / JS Package to npm:
  python scripts/publish_release.py --npm

  # Publish Both:
  python scripts/publish_release.py --all
"""

import sys
import os
import subprocess
import argparse

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def publish_pypi(version: str = "4.1.0"):
    print(f"[*] Publishing btp-guard v{version} to PyPI...")
    cmd = [sys.executable, "-m", "twine", "upload", f"dist/btp_guard-{version}*"]
    res = subprocess.run(cmd)
    if res.returncode == 0:
        print("[OK] PyPI release published successfully: pip install btp-guard")
    else:
        print("[!] PyPI upload failed or was cancelled.")


def publish_npm():
    print("[*] Publishing @bartholomew/guard to npm...")
    cmd = ["npm", "publish", "--access", "public"]
    res = subprocess.run(cmd, cwd="npm_package", shell=True)
    if res.returncode == 0:
        print("[OK] npm package published successfully: npm install @bartholomew/guard")
    else:
        print("[!] npm publish failed or was cancelled.")


def main():
    parser = argparse.ArgumentParser(description="Bartholomew Registry Release Publisher")
    parser.add_argument("--version", default="4.1.0", help="Release version to publish (default: 4.1.0)")
    parser.add_argument("--pypi", action="store_true", help="Publish to PyPI")
    parser.add_argument("--npm", action="store_true", help="Publish to npm")
    parser.add_argument("--all", action="store_true", help="Publish to both PyPI and npm")
    args = parser.parse_args()

    if args.all or args.pypi:
        publish_pypi(version=args.version)
    if args.all or args.npm:
        publish_npm()
    if not (args.all or args.pypi or args.npm):
        parser.print_help()


if __name__ == "__main__":
    main()
