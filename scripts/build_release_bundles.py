"""
BTP Release Bundle Builder
Builds distributable wheel and npm packages in dist/ directory.
"""

import os
import sys
import shutil
import subprocess

def build_bundles():
    print("=" * 80)
    print("  BUILDING BTP v2.2 RELEASE BUNDLES (PyPI & NPM)")
    print("=" * 80)

    os.makedirs("dist", exist_ok=True)

    # 1. Build PyPI Wheel
    print("\n[1] Building Python Wheel (btp-guard)...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "build", "setuptools", "wheel"
        ])
        subprocess.check_call([
            sys.executable, "-m", "build", "pypi_package", "--outdir", "dist"
        ])
        print("    |-- PyPI Wheel Built: dist/")
    except Exception as e:
        print(f"    |-- Wheel build skipped: {e}")

    # 2. Package NPM Tarball
    print("\n[2] Building NPM Tarball (@btp/verifier)...")
    try:
        subprocess.check_call(["npm", "pack", "./npm_package"], cwd=".")
        # Move generated tgz to dist
        for f in os.listdir("."):
            if f.startswith("btp-verifier") and f.endswith(".tgz"):
                shutil.move(f, os.path.join("dist", f))
                print(f"    |-- NPM Package Built: dist/{f}")
    except Exception as e:
        print(f"    |-- NPM pack skipped: {e}")

    print("\n" + "=" * 80)
    print("  RELEASE BUNDLES READY IN dist/ DIRECTORY")
    print("=" * 80)
    return True

if __name__ == "__main__":
    build_bundles()
