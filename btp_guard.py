#!/usr/bin/env python3
"""
Bartholomew Protocol (BTP Guard) Root Module & CLI Alias
========================================================
Convenience root entrypoint and import shim for btp_guard runtime.
"""

import sys
import os

root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
src_dir = os.path.join(root_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from btp_guard.cli import main

if __name__ == "__main__":
    main()
