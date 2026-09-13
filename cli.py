#!/usr/bin/env python3
"""
Bartholomew Autonomous Trust Protocol (BTP) Root CLI
====================================================
Primary developer entrypoint for running Bartholomew audits, models,
companion, daemon, and policy verification directly from the repository root.
"""

import sys
import os

# Ensure repo root and src are on sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
src_dir = os.path.join(root_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from src.cli import main

if __name__ == "__main__":
    main()
