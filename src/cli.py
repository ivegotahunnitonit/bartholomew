"""
Bartholomew Protocol CLI Gateway (v5.4.22)
"""
import sys
import os

# Ensure btp_guard is accessible
pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if pkg_root not in sys.path:
    sys.path.insert(0, pkg_root)

from btp_guard.cli import main

if __name__ == "__main__":
    main()
